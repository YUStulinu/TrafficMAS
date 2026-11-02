"""CoordinatorAgent: one per zone, with a reactive and a deliberative layer.

* Information layer (always on): it collects the status reports of the
  intersections in its zone and periodically broadcasts link delay estimates to
  the vehicles, which use them for rerouting.
* Reactive layer (only when gating is enabled): when a link is close to full
  (spillback), it sends a DRAIN directive to the intersection at the end of the
  link and a METER directive to the intersection feeding it, for a limited time.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from trafficmas.contracts import BROADCAST_VEHICLES, TOPIC_CONGESTION, TOPIC_DRAIN, TOPIC_METER, TOPIC_STATUS, Message

if TYPE_CHECKING:
    from trafficmas.sim.engine import Simulation


class CoordinatorAgent:
    def __init__(self, sim: Simulation, zone: str, members: list[str], gating: bool = False,
                 info_interval: float = 30.0, spill_threshold: float = 0.85, directive_duration: float = 30.0) -> None:
        self.sim = sim
        self.zone = zone
        self.id = f"coord:{zone}"
        self.members = set(members)
        self.gating = gating
        self.info_interval = info_interval
        self.spill_threshold = spill_threshold
        self.directive_duration = directive_duration
        self.links: dict[str, list[int]] = {}       # link id -> [queued, occupancy, storage]
        self.green_share: dict[str, float] = {}     # link id -> share of time its node is green for it
        self.active: dict[tuple[str, str], float] = {}   # (kind, link) -> until
        self.spillbacks_detected = 0
        self.directives_sent = 0

    def on_message(self, msg: Message) -> None:
        if msg.topic != TOPIC_STATUS:
            return
        share = 1.0 / msg.payload["phases"] if msg.payload["signalized"] else 1.0
        for lid, vals in msg.payload["in"].items():
            self.links[lid] = vals
            self.green_share[lid] = share
        if self.gating:
            self._check_spillback(msg.payload["out"])

    def _check_spillback(self, out_links: dict[str, list[int]]) -> None:
        now = self.sim.env.now
        net = self.sim.net
        for lid, (_queued, occ, storage) in out_links.items():
            if occ < self.spill_threshold * storage:
                continue
            link = net.links[lid]
            until = now + self.directive_duration
            sent = False
            downstream = self.sim.agents.get(link.v)
            if downstream is not None and downstream.signalized and self.active.get(("drain", lid), -1) < now:
                self.active[("drain", lid)] = until
                self.sim.bus.send(Message(self.id, link.v, "REQUEST", TOPIC_DRAIN, {"link": lid, "until": until}))
                sent = True
            upstream = self.sim.agents.get(link.u)
            if upstream is not None and upstream.signalized and self.active.get(("meter", lid), -1) < now:
                self.active[("meter", lid)] = until
                self.sim.bus.send(Message(self.id, link.u, "REQUEST", TOPIC_METER, {"link": lid, "until": until}))
                sent = True
            if sent:
                self.spillbacks_detected += 1
                self.directives_sent += 1

    def delay_estimates(self) -> dict[str, float]:
        net = self.sim.net
        out = {}
        for lid, (queued, _occ, _storage) in self.links.items():
            cap = max(0.05, net.links[lid].sat_cap * self.green_share.get(lid, 1.0))
            out[lid] = queued / cap
        return out

    def run(self, env):
        yield env.timeout(self.info_interval)
        while True:
            if self.links:
                self.sim.bus.send(Message(self.id, BROADCAST_VEHICLES, "INFORM", TOPIC_CONGESTION,
                                          {"delays": self.delay_estimates()}))
            yield env.timeout(self.info_interval)
