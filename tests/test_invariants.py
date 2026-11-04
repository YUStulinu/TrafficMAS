"""Randomised check of the simulation invariants over many short configurations.

While each run is going, every vehicle discharge and a snapshot every 5 s are
checked: nothing is served on red (ambulances excepted), no approach discharges
faster than its saturation flow, no link holds more vehicles than its storage,
and every vehicle is in exactly one place and is never lost.
Set TRAFFICMAS_STRESS=250 to run more configurations.
"""
import math
import os
import random

import pytest

from trafficmas.agents.intersection import IntersectionAgent
from trafficmas.config import ROOT, load_scenario
from trafficmas.control import CONTROLLERS
from trafficmas.sim.engine import Simulation

SCENARIOS = ["grid_light", "grid_heavy", "grid_rush_hour", "grid_incident", "grid_emergency", "craiova_center",
             "braess"]
N = int(os.environ.get("TRAFFICMAS_STRESS", "14"))


def random_config(rng: random.Random):
    name = rng.choice(SCENARIOS)
    sc = load_scenario(f"scenarios/{name}.yaml")
    ctrl = rng.choice(list(CONTROLLERS))
    params = rng.choice([{}, {"credits": False}, {"use_bids": False}, {"commit": False}, {"selfish_factor": 5.0}])
    if not ctrl.startswith("negotiation"):
        params = {}
    ov = {"demand": {"duration": rng.choice([300, 600]), "rate": sc["demand"]["rate"] * rng.choice([0.3, 1.0, 1.6])},
          "bus": {"latency": rng.choice([0.0, 0.1, 2.0]), "loss": rng.choice([0.0, 0.3]),
                  "jitter": rng.choice([0.0, 0.5])},
          "emergency": {"mode": rng.choice(["none", "preemption", "corridor"]),
                        "random": {"count": rng.randint(0, 4), "start": 60, "interval": 90}},
          "coordinator": {"zones": rng.choice([1, 2, 3])}}
    if name in ("grid_light", "grid_heavy", "grid_rush_hour") and rng.random() < 0.4:
        ov["network"] = {"left_turn_phases": True, "rows": rng.choice([2, 3, 5]), "cols": rng.choice([2, 4])}
    if name == "braess":
        ov["network"] = {"shortcut": rng.random() < 0.5}
    return sc, ctrl, params, ov, rng.randint(1, 10_000)


@pytest.mark.parametrize("i", range(N))
def test_invariants(i, monkeypatch):
    sc, ctrl, params, ov, seed = random_config(random.Random(1000 + i))
    sim = Simulation(sc, ctrl, seed=seed, controller_params=params, overrides=ov, base_dir=ROOT)
    problems: list[str] = []
    served: dict = {}
    original = IntersectionAgent._cross_vehicle

    def checked(agent, v, m, now):
        if not v.is_emergency:
            if not agent.is_green(m):
                problems.append(f"{v.id} served on red at {agent.id}")
            served[(now, m.inbound.id)] = served.get((now, m.inbound.id), 0) + 1
            if served[(now, m.inbound.id)] > max(1, math.ceil(m.inbound.sat_cap)):
                problems.append(f"{m.inbound.id} above saturation flow")
        original(agent, v, m, now)

    monkeypatch.setattr(IntersectionAgent, "_cross_vehicle", checked)

    def snapshot(env):
        while True:
            yield env.timeout(5.0)
            seen: dict[str, int] = {}
            for link in sim.net.links.values():
                here = list(link.travellers.values()) + [v for q in link.queues.values() for v in q]
                for v in here:
                    seen[v.id] = seen.get(v.id, 0) + 1
                    if v.link is not link:
                        problems.append(f"{v.id} is on {link.id} but believes it is on {v.link.id}")
                if link.occupancy > link.storage + sum(v.is_emergency for v in here):
                    problems.append(f"{link.id} holds more than its storage")
            problems.extend(f"{vid} is in {n} places" for vid, n in seen.items() if n != 1)
            problems.extend(f"{v.id} vanished" for v in sim.vehicles.values()
                            if v.entered_network is not None and not v.done and v.id not in seen)

    sim.env.process(snapshot(sim.env))
    s = sim.run()
    m = sim.metrics
    assert s["spawned"] == len(m.trips) + len(m.ev_trips) + len(m.active) + s["unroutable"]
    assert s["unroutable"] == 0
    assert all(0 <= t["wait_time"] <= t["travel_time"] + 1e-6 for t in m.trips + m.ev_trips)
    assert not problems, problems[:5]
