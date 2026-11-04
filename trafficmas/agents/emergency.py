"""EmergencyVehicleAgent: an ambulance that asks the traffic lights for priority.

Three modes are compared:

* ``none``: no priority. Other vehicles pull aside, so the ambulance goes to the
  head of the queue, but it waits for green (or crosses carefully after
  RED_CROSS_DELAY seconds at a red light).
* ``preemption``: classic local pre-emption. The intersection detects the
  ambulance once it is on the approach and switches to its phase immediately.
* ``corridor``: the ambulance plans its whole route at departure and reserves a
  time slot at every signalised intersection on it (FIPA Request protocol). Each
  intersection starts the green early enough to empty the approach before the
  ambulance arrives. ETAs are refreshed while driving, the slot is released once
  the ambulance has crossed, and conflicting requests are settled by priority. A
  rejected ambulance tries to re-plan around the intersection that refused it.

Vehicles have to pull aside on a crowded link, so the ambulance drives slower the
fuller the link is. This is why emptying the approach early pays off.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from trafficmas.agents.vehicle import Vehicle
from trafficmas.contracts import TOPIC_CORRIDOR, TOPIC_ETA, TOPIC_RELEASE, Message
from trafficmas.network.road import Link

if TYPE_CHECKING:
    from trafficmas.sim.engine import Simulation

EV_SPEED_FACTOR = 1.25     # faster than the speed limit on an empty road
PULL_ASIDE_PENALTY = 1.5   # travel time multiplier on a completely full link
ETA_UPDATES_AHEAD = 3      # refresh the ETA of this many reserved intersections ahead


class EmergencyVehicle(Vehicle):
    is_emergency = True
    speed_factor = EV_SPEED_FACTOR
    delay_weight = 0.3         # queues matter less to a vehicle that others make room for

    def __init__(self, sim: Simulation, vid: str, origin: str, dest: str, priority: int, mode: str, rng) -> None:
        super().__init__(sim, vid, origin, dest, "aggressive", rng)
        self.compliant = True   # always plans with the congestion information (see enter below)
        self.priority = priority
        self.mode = mode
        self.reserved: dict[str, float] = {}   # node id -> eta of the accepted reservation
        self.requested: set[str] = set()
        self.rejections = 0
        sim.bus.register(self)

    def link_time(self, link: Link) -> float:
        crowd = max(0, link.occupancy - (1 if self.id in link.travellers else 0)) / link.storage
        return link.free_time / self.speed_factor * (1.0 + PULL_ASIDE_PENALTY * min(1.0, crowd))

    def can_enter(self, link: Link) -> bool:
        return not link.closed

    def join_queue(self, link: Link, nxt: Link) -> None:
        link.queues[nxt.id].appendleft(self)   # the others pull aside

    # ------------------------------------------------------------------ corridor protocol
    def enter(self, link: Link, now: float, first: bool = False) -> None:
        # an ambulance keeps its planned (and reserved) route; it re-plans only when refused
        self.compliant = False
        super().enter(link, now, first)

    def plan(self, now: float) -> bool:
        if not super().plan(now):
            return False
        if self.mode == "corridor":
            self.request_corridor(now, start=0)
        return True

    def _etas(self, now: float, start: int) -> list[tuple[Link, Link, float]]:
        """(in link, out link, eta at the stop line) for every signalised node from route[start]."""
        out = []
        if self.entered_network is None:   # still at the origin
            t = now + self.route[start].free_time / self.speed_factor
        else:                              # driving on route[start]
            t = self.stopline_at
        for i in range(start, len(self.route) - 1):
            link = self.route[i]
            if i > start:
                t += link.free_time / self.speed_factor
            agent = self.sim.agents.get(link.v)
            if agent is not None and agent.signalized:
                out.append((link, self.route[i + 1], t))
        return out

    def request_corridor(self, now: float, start: int) -> None:
        for in_link, out_link, eta in self._etas(now, start):
            node = in_link.v
            self.requested.add(node)
            self.sim.bus.send(Message(self.id, node, "REQUEST", TOPIC_CORRIDOR,
                                      {"in_link": in_link.id, "out_link": out_link.id, "eta": eta,
                                       "priority": self.priority}, conversation=self.id))

    def on_message(self, msg: Message) -> None:
        if msg.topic != TOPIC_CORRIDOR or self.done:
            return
        node = msg.payload["node"]
        if msg.performative == "ACCEPT":
            self.reserved[node] = msg.payload["eta"]
            return
        if msg.performative != "REJECT":
            return
        self.rejections += 1
        self.reserved.pop(node, None)
        self.try_detour(node)

    def try_detour(self, refused: str) -> None:
        """Re-plan around an intersection that refused the corridor, if that is not much slower."""
        if self.link is None or self.link.v == refused:
            return
        now = self.sim.env.now
        res = self.sim.router.route([(self.link, self.stopline_at)], self.dest, self.speed_factor,
                                    self.delay_weight, frozenset({refused}))
        if res is None:
            return
        path, arrival = res
        if arrival - now > 1.3 * self.remaining_time(now):
            return
        old_nodes = {link.v for link in self.route[self.idx:]}
        self.route = self.route[:self.idx] + path
        new_nodes = {link.v for link in self.route[self.idx:]}
        for node in old_nodes - new_nodes:
            if node in self.reserved or node in self.requested:
                self.reserved.pop(node, None)
                self.sim.bus.send(Message(self.id, node, "INFORM", TOPIC_RELEASE, {}, conversation=self.id))
        self.request_corridor(now, start=self.idx)

    # ------------------------------------------------------------------ driving
    def on_enter(self, link: Link, now: float) -> None:
        if self.idx + 1 >= len(self.route):
            return
        nxt = self.route[self.idx + 1]
        if self.mode == "preemption":
            agent = self.sim.agents.get(link.v)
            if agent is not None and agent.signalized:
                agent.ev_detected(self, link, nxt, self.stopline_at)
        elif self.mode == "corridor":
            sent = 0
            for in_link, _out, eta in self._etas(now, self.idx):
                if sent >= ETA_UPDATES_AHEAD:
                    break
                if in_link.v in self.reserved:
                    self.reserved[in_link.v] = eta
                    self.sim.bus.send(Message(self.id, in_link.v, "INFORM", TOPIC_ETA, {"eta": eta},
                                              conversation=self.id))
                    sent += 1

    def finish(self, now: float) -> None:
        super().finish(now)
        self.sim.bus.agents.pop(self.id, None)
