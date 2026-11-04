"""Simulation: builds the world from a scenario and runs it on a SimPy clock."""
from __future__ import annotations

import copy
import random
import time
from pathlib import Path

import simpy

from trafficmas.agents.coordinator import CoordinatorAgent
from trafficmas.agents.emergency import EmergencyVehicle
from trafficmas.agents.intersection import IntersectionAgent
from trafficmas.agents.vehicle import Vehicle
from trafficmas.bus.bus import MessageBus
from trafficmas.control import CONTROLLERS, NegotiationController, make_controller, uses_coordination
from trafficmas.metrics.collector import MetricsCollector
from trafficmas.network import build_network
from trafficmas.routing.router import Router, TrafficInfoBoard
from trafficmas.sim.demand import DemandGenerator

DEFAULTS = {
    "name": "scenario",
    "demand": {"rate": 1800, "duration": 3600, "profile": "constant"},
    "drain": 1200,
    "bus": {"latency": 0.1, "jitter": 0.0, "loss": 0.0},
    "coordinator": {"zones": 2, "status_interval": 10.0, "info_interval": 30.0, "spill_threshold": 0.85},
    "routing": {"horizon": 600.0},
    "emergency": {"mode": "corridor", "vehicles": []},
    "incidents": [],
    "selfish": None,
}


def deep_merge(base: dict, extra: dict | None) -> dict:
    out = copy.deepcopy(base)
    for k, v in (extra or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def _zones(nodes, k: int) -> dict[str, str]:
    """Split nodes into k vertical strips with (almost) the same number of nodes each."""
    k = max(1, k)
    ordered = sorted(nodes, key=lambda n: (n.x, n.y, n.id))
    return {n.id: str(min(k - 1, i * k // max(1, len(ordered)))) for i, n in enumerate(ordered)}


class Simulation:
    def __init__(self, scenario: dict, controller: str = "negotiation", seed: int = 0,
                 controller_params: dict | None = None, overrides: dict | None = None,
                 base_dir: Path | None = None) -> None:
        self.cfg = deep_merge(deep_merge(DEFAULTS, scenario), overrides)
        self.name = self.cfg["name"]
        self.controller_name = controller
        self.controller_params = controller_params or {}
        self.seed = seed
        self.dt = 1.0
        self.env = simpy.Environment()
        self.net = build_network(self.cfg.get("network") or {"type": "grid"}, base_dir)
        coord_cfg = self.cfg["coordinator"]
        self.status_interval = float(coord_cfg["status_interval"])

        self.bus = MessageBus(self.env, random.Random(seed * 7919 + 2), **self.cfg["bus"])
        self.board = TrafficInfoBoard()
        self.router = Router(self.net, self.board, horizon=float(self.cfg["routing"]["horizon"]))
        self.bus.subscribe_vehicle("radio", lambda m: self.board.publish(m.payload["delays"], self.env.now))
        self.metrics = MetricsCollector(self)
        self.vehicles: dict[str, Vehicle] = {}

        # intersection agents, grouped into zones
        nodes = [n for n in self.net.nodes.values() if n.movements]
        zone_of = _zones(nodes, int(coord_cfg["zones"]))
        selfish = self.cfg.get("selfish") or {}
        self.agents: dict[str, IntersectionAgent] = {}
        for node in nodes:
            ctrl = None
            if node.signalized and len(node.phases) > 1:
                params = dict(self.controller_params)
                if selfish and node.id == selfish.get("node") and CONTROLLERS[controller][0] is NegotiationController:
                    params["selfish_factor"] = float(selfish.get("factor", 4.0))
                ctrl = make_controller(controller, params)
            agent = IntersectionAgent(self, node, ctrl, zone_of[node.id])
            self.agents[node.id] = agent
            self.bus.register(agent, zone=zone_of[node.id])
        gating = uses_coordination(controller, self.controller_params)
        self.coordinators: list[CoordinatorAgent] = []
        for zone in sorted(set(zone_of.values())):
            c = CoordinatorAgent(self, zone, gating=gating,
                                 info_interval=float(coord_cfg["info_interval"]),
                                 spill_threshold=float(coord_cfg["spill_threshold"]))
            self.coordinators.append(c)
            self.bus.register(c)

        # processes
        for agent in self.agents.values():
            self.env.process(agent.run(self.env))
        for c in self.coordinators:
            self.env.process(c.run(self.env))
        d = self.cfg["demand"]
        self.duration = float(d["duration"])
        self.demand = DemandGenerator(self, random.Random(seed * 7919 + 1), rate=float(d["rate"]),
                                      duration=self.duration, profile=d.get("profile", "constant"),
                                      od_bias=d.get("od_bias"), od_pairs=d.get("od_pairs"),
                                      same_side_weight=float(d.get("same_side_weight", 0.2)),
                                      profiles=d.get("driver_profiles"))
        self.env.process(self.demand.run(self.env))
        self.emergency_mode = self.cfg["emergency"].get("mode", "corridor")
        self._schedule_emergencies(random.Random(seed * 7919 + 3))
        for inc in self.cfg["incidents"]:
            if inc["link"] not in self.net.links:
                raise ValueError(f"incident on unknown link {inc['link']!r} in scenario {self.name!r}")
            self.env.process(self._incident(inc))
        self.env.process(self.metrics.sampler(self.env))
        self.horizon = self.duration + float(self.cfg["drain"])
        self.wall_time = 0.0

    # ------------------------------------------------------------------ spawning
    def spawn_vehicle(self, vid: str, origin: str, dest: str, profile: str) -> Vehicle:
        v = Vehicle(self, vid, origin, dest, profile, random.Random(f"{self.seed}:{vid}"))
        self._start(v)
        return v

    def spawn_emergency(self, vid: str, origin: str, dest: str, priority: int = 1) -> EmergencyVehicle:
        rng = random.Random(f"{self.seed}:{vid}")
        v = EmergencyVehicle(self, vid, origin, dest, priority, self.emergency_mode, rng)
        self._start(v)
        return v

    def _start(self, v: Vehicle) -> None:
        self.vehicles[v.id] = v
        self.metrics.vehicle_spawned(v)

        def lifecycle(env):
            yield from v.run(env)
            if not v.done:   # could not be routed
                self.metrics.active.pop(v.id, None)
            self.vehicles.pop(v.id, None)

        self.env.process(lifecycle(self.env))

    def _schedule_emergencies(self, rng: random.Random) -> None:
        ecfg = self.cfg["emergency"]
        evs = [dict(e) for e in ecfg.get("vehicles", [])]
        rnd = ecfg.get("random")
        if rnd:
            gws = [g.id for g in self.net.gateways]
            t = float(rnd.get("start", 300))
            for _ in range(int(rnd.get("count", 3))):
                for _ in range(100):   # one-way networks: only some gateway pairs are connected
                    o, d = rng.sample(gws, 2)
                    if self.router.route_from_origin(o, d, 0.0) is not None:
                        break
                else:
                    raise ValueError(f"no connected gateway pair for ambulances in scenario {self.name!r}")
                evs.append({"depart": t, "origin": o, "dest": d, "priority": rng.choice([1, 2])})
                t += float(rnd.get("interval", 600))
        for i, e in enumerate(evs):
            for key in ("origin", "dest"):
                if e[key] not in self.net.nodes:
                    raise ValueError(f"ambulance {key} {e[key]!r} is not a node of scenario {self.name!r}")

            def go(env, e=e, i=i):
                yield env.timeout(float(e["depart"]))
                self.spawn_emergency(f"ev{i + 1}", e["origin"], e["dest"], int(e.get("priority", 1)))
            self.env.process(go(self.env))

    def _incident(self, inc: dict):
        link = self.net.links[inc["link"]]
        yield self.env.timeout(float(inc["start"]))
        before = link.capacity_factor
        if inc.get("closed"):
            link.closed = True
            self.board.publish({link.id: 1e6}, self.env.now)
        link.capacity_factor = float(inc.get("capacity_factor", before))
        if "end" in inc:
            yield self.env.timeout(float(inc["end"]) - float(inc["start"]))
            link.closed = False
            link.capacity_factor = before
            self.board.publish({link.id: 0.0}, self.env.now)

    # ------------------------------------------------------------------ running
    def _watch(self, env):
        yield env.timeout(self.duration)
        while env.now < self.horizon and self.metrics.active:
            yield env.timeout(10.0)

    def run(self) -> dict:
        t0 = time.perf_counter()
        self.env.run(until=self.env.process(self._watch(self.env)))
        self.wall_time = time.perf_counter() - t0
        return self.summary()

    def summary(self) -> dict:
        out = {"scenario": self.name, "controller": self.controller_name, "seed": self.seed,
               "emergency_mode": self.emergency_mode}
        out.update(self.metrics.summary())
        if self.cfg.get("selfish"):
            out.update(self._selfish_summary(self.cfg["selfish"]["node"]))
        out["wall_time"] = self.wall_time
        return out

    def _selfish_summary(self, node: str) -> dict:
        """Who profits when one junction inflates its bids: itself vs. everybody else."""
        waits = self.metrics.approach_wait
        own = {link.id for link in self.net.in_links(node)}
        mine = [waits[lid] for lid in own if lid in waits]
        others = [w for lid, w in waits.items() if lid not in own and self.net.nodes[self.net.links[lid].v].signalized]

        def avg(acc):
            n = sum(c for _, c in acc)
            return sum(s for s, _ in acc) / n if n else float("nan")

        won = {nid: a.controller.bids_won for nid, a in self.agents.items()
               if isinstance(a.controller, NegotiationController)}
        total = sum(won.values())
        out = {"selfish_node_wait": avg(mine), "others_wait": avg(others)}
        if won:
            out["selfish_bid_share"] = won.get(node, 0) / total if total else 0.0
        return out
