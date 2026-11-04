"""IntersectionAgent: runs the traffic lights of one junction.

The agent owns the signal state (current phase, intergreen), serves the queues of
its green movements at saturation flow and talks to the rest of the system:

* its controller decides which phase is green next (fixed, actuated, max-pressure
  or negotiation - see `trafficmas.control`);
* emergency vehicles reserve time slots for their movement (corridor mode) or are
  detected on an approach (local pre-emption mode); an active reservation
  overrides the controller until the vehicle has crossed;
* every few seconds it reports its approach occupancies to its zone coordinator,
  which may answer with drain / meter directives when a link spills back.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from trafficmas.contracts import (
    TOPIC_CORRIDOR,
    TOPIC_DRAIN,
    TOPIC_ETA,
    TOPIC_METER,
    TOPIC_RELEASE,
    TOPIC_STATUS,
    Message,
)
from trafficmas.network.road import Link, Movement, Node

if TYPE_CHECKING:
    from trafficmas.sim.engine import Simulation

INTERGREEN = 4.0          # amber + all-red, s
RED_CROSS_DELAY = 8.0     # an emergency vehicle stuck at a red light crosses carefully after this, s
EV_TIMEOUT = 90.0         # a reservation is dropped if the vehicle is this late, s
EV_SLACK = 15.0           # a reservation window lasts this long after the ETA, s


@dataclass
class Reservation:
    ev_id: str
    in_link: str
    out_link: str
    phase: int
    eta: float
    priority: int
    local: bool = False   # created by local pre-emption (sensor) instead of a negotiated corridor


class IntersectionAgent:
    def __init__(self, sim: Simulation, node: Node, controller, zone: str) -> None:
        self.sim = sim
        self.id = node.id
        self.node = node
        self.coordinator_id = f"coord:{zone}"
        self.phases: list[list[Movement]] = node.phases
        self.signalized = node.signalized and len(self.phases) > 1
        self.controller = controller
        self.in_links: list[Link] = [link for link in sim.net.in_links(node.id) if link.queues]
        self.phase_links: list[set[str]] = [{m.inbound.id for m in ph} for ph in self.phases]
        self.phase = 0
        self.phase_start = 0.0
        self.green_start = 0.0
        self.intergreen_left = 0.0
        self.next_phase = 0
        self.last_green = [0.0] * len(self.phases)
        self.reservations: dict[str, Reservation] = {}
        self.ev_hold = False
        self.drain: dict[str, float] = {}   # link id -> until (coordinator directive)
        self.meter: dict[str, float] = {}   # out link id -> until (coordinator directive)
        self.released: dict[str, int] = {}  # out link id -> vehicles released during this green
        if controller is not None:
            controller.attach(self)

    # ------------------------------------------------------------------ state
    @property
    def in_intergreen(self) -> bool:
        return self.intergreen_left > 0.0

    def phase_elapsed(self, now: float) -> float:
        return now - self.phase_start

    def red_time(self, p: int, now: float) -> float:
        if p == self.phase and not self.in_intergreen:
            return 0.0
        return now - self.last_green[p]

    def phase_queue(self, p: int) -> int:
        return sum(len(m.queue) for m in self.phases[p])

    def approaching(self, p: int, now: float, horizon: float) -> int:
        """Vehicles that will reach a stop line of phase p within `horizon` seconds."""
        n = 0
        for lid in self.phase_links[p]:
            for v in self.sim.net.links[lid].travellers.values():
                if v.stopline_at - now <= horizon:
                    n += 1
        return n

    def phase_demand(self, p: int, now: float, horizon: float = 10.0) -> int:
        return self.phase_queue(p) + self.approaching(p, now, horizon)

    def is_green(self, m: Movement) -> bool:
        return not self.in_intergreen and self.node.phase_of.get(m.key) == self.phase

    def send(self, receiver: str, performative: str, topic: str, payload: dict, conversation: str = "") -> None:
        self.sim.bus.send(Message(self.id, receiver, performative, topic, payload, conversation=conversation))

    # ------------------------------------------------------------------ main loop
    def run(self, env):
        dt = self.sim.dt
        next_status = self.sim.status_interval
        while True:
            now = env.now
            self.step(now, dt)
            if now >= next_status:
                self.report_status()
                next_status = now + self.sim.status_interval
            yield env.timeout(dt)

    def step(self, now: float, dt: float) -> None:
        if self.controller is not None:
            self.controller.on_tick(self, now, dt)
        if self.in_intergreen:
            self.intergreen_left -= dt
            if self.intergreen_left <= 1e-9:
                self.intergreen_left = 0.0
                self.phase = self.next_phase
                self.phase_start = self.green_start = now
                self.released = {}
                if self.controller is not None:
                    self.controller.on_green_start(self, now)
        elif self.signalized:
            target = self.emergency_target(now)
            if target is None and self.controller is not None:
                target = self.controller.decide(self, now)
            if target is not None and target != self.phase:
                self.switch_to(target, now)
        self.discharge(now, dt)

    def switch_to(self, p: int, now: float) -> None:
        if self.controller is not None:
            self.controller.on_green_end(self, now, self.released)
        self.last_green[self.phase] = now
        self.next_phase = p
        self.intergreen_left = INTERGREEN

    # ------------------------------------------------------------------ queue service
    def discharge(self, now: float, dt: float) -> None:
        for link in self.in_links:
            if link.queued:
                link.cap_credit = min(link.cap_credit + link.sat_cap * dt, max(1.0, link.sat_cap * dt))
            else:
                link.cap_credit = 0.0
        if not self.in_intergreen and self.phases:
            # movements competing for the same space downstream merge first come, first served
            green = sorted((m for m in self.phases[self.phase] if m.queue), key=lambda m: m.queue[0].queued_at)
            for m in self.phases[self.phase]:
                if not m.queue:
                    m.credit = 0.0
            for m in green:
                self._serve(m, now, dt)
        # an emergency vehicle waiting at a red light crosses carefully after a while
        for m in self.node.movements:
            q = m.queue
            if q and q[0].is_emergency and not self.is_green(m) and now - q[0].queued_at >= RED_CROSS_DELAY:
                self._cross_vehicle(q.popleft(), m, now)

    def _serve(self, m: Movement, now: float, dt: float) -> None:
        q = m.queue
        rate = m.sat_rate * m.inbound.capacity_factor
        m.credit = min(m.credit + rate * dt, max(1.0, rate * dt))
        link = m.inbound
        while q and m.credit >= 1.0 and link.cap_credit >= 1.0:
            v = q[0]
            if not v.is_emergency and not m.outbound.has_space():
                self.sim.metrics.blocked_events += 1
                break
            q.popleft()
            m.credit -= 1.0
            link.cap_credit -= 1.0
            self._cross_vehicle(v, m, now)

    def _cross_vehicle(self, v, m: Movement, now: float) -> None:
        self.sim.metrics.discharged(m.inbound, now - v.queued_at)
        self.released[m.outbound.id] = self.released.get(m.outbound.id, 0) + 1
        if v.is_emergency:
            self.ev_passed(v.id)
        v.cross(m.outbound, now)

    # ------------------------------------------------------------------ emergency vehicles
    def ev_lead(self, r: Reservation) -> float:
        """How long before the ETA the corridor phase has to start, so the approach is empty."""
        link = self.sim.net.links[r.in_link]
        flush = link.queued / max(0.25, link.sat_cap)
        return min(40.0, max(8.0, INTERGREEN + flush + 4.0))

    def emergency_target(self, now: float) -> int | None:
        if not self.reservations:
            self.ev_hold = False
            return None
        active = []
        for ev_id, r in list(self.reservations.items()):
            if now > r.eta + EV_TIMEOUT:
                del self.reservations[ev_id]
                continue
            if r.local or now >= r.eta - self.ev_lead(r):
                active.append(r)
        self.ev_hold = bool(active)
        if not active:
            return None
        r = max(active, key=lambda r: (r.priority, -r.eta))
        return r.phase

    def ev_detected(self, ev, in_link: Link, out_link: Link, eta: float) -> None:
        """Local pre-emption: a sensor on the approach sees the emergency vehicle."""
        phase = self.node.phase_of.get((in_link.id, out_link.id))
        if phase is None or not self.signalized:
            return
        for other in self.reservations.values():
            if other.phase != phase and other.priority > ev.priority:
                return
        self.reservations[ev.id] = Reservation(ev.id, in_link.id, out_link.id, phase, eta, ev.priority, local=True)

    def ev_passed(self, ev_id: str) -> None:
        if self.reservations.pop(ev_id, None) is not None:
            self.sim.metrics.corridor_served += 1

    def _overlaps(self, a: Reservation, b: Reservation) -> bool:
        a0, a1 = a.eta - self.ev_lead(a), a.eta + EV_SLACK
        b0, b1 = b.eta - self.ev_lead(b), b.eta + EV_SLACK
        return a0 <= b1 and b0 <= a1

    def handle_corridor_request(self, msg: Message) -> None:
        p = msg.payload
        phase = self.node.phase_of[(p["in_link"], p["out_link"])]   # requests only name real movements
        new = Reservation(msg.sender, p["in_link"], p["out_link"], phase, p["eta"], p["priority"])
        conflicts = [r for r in self.reservations.values()
                     if r.ev_id != new.ev_id and r.phase != phase and self._overlaps(r, new)]
        if any(r.priority >= new.priority for r in conflicts):
            self.sim.metrics.corridor_conflicts += 1
            self.send(msg.sender, "REJECT", TOPIC_CORRIDOR, {"node": self.id, "reason": "conflict"}, msg.conversation)
            return
        for r in conflicts:   # lower-priority reservations are displaced
            self.sim.metrics.corridor_conflicts += 1
            del self.reservations[r.ev_id]
            self.send(r.ev_id, "REJECT", TOPIC_CORRIDOR, {"node": self.id, "reason": "displaced"}, r.ev_id)
        self.reservations[new.ev_id] = new
        self.send(msg.sender, "ACCEPT", TOPIC_CORRIDOR, {"node": self.id, "eta": new.eta}, msg.conversation)

    # ------------------------------------------------------------------ messages
    def on_message(self, msg: Message) -> None:
        if msg.topic == TOPIC_CORRIDOR and msg.performative == "REQUEST":
            self.handle_corridor_request(msg)
        elif msg.topic == TOPIC_ETA:
            r = self.reservations.get(msg.sender)
            if r is not None:
                r.eta = msg.payload["eta"]
        elif msg.topic == TOPIC_RELEASE:
            self.reservations.pop(msg.sender, None)
        elif msg.topic == TOPIC_DRAIN:
            self.drain[msg.payload["link"]] = msg.payload["until"]
        elif msg.topic == TOPIC_METER:
            self.meter[msg.payload["link"]] = msg.payload["until"]
        elif self.controller is not None:
            self.controller.on_message(self, msg)

    def report_status(self) -> None:
        links = {link.id: [link.queued, link.occupancy, link.storage] for link in self.in_links}
        out = {link.id: [link.queued, link.occupancy, link.storage] for link in self.sim.net.out_links(self.id)}
        self.send(self.coordinator_id, "INFORM", TOPIC_STATUS,
                  {"in": links, "out": out, "signalized": self.signalized, "phases": len(self.phases)})
