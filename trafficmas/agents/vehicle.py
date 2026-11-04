"""VehicleAgent: drives from its origin gateway to its destination gateway.

The vehicle plans a route with time-dependent A* when it departs. Every time it
enters a new link, a compliant driver re-plans if the coordinators have broadcast
new congestion information since the last check, and switches route if the new
one is predicted to be clearly faster. Drivers who do not follow the advice take
their usual free-flow route. How likely a driver is to follow the advice and how
big the gain must be depend on its profile.
"""
from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

from trafficmas.network.road import Link

if TYPE_CHECKING:
    from trafficmas.sim.engine import Simulation

# profile -> (probability of following rerouting advice, minimum relative gain to switch)
PROFILES = {
    "conservative": (0.2, 0.30),
    "normal": (0.5, 0.15),
    "aggressive": (0.9, 0.05),
}


class Vehicle:
    is_emergency = False
    speed_factor = 1.0
    delay_weight = 1.0
    priority = 0

    def __init__(self, sim: Simulation, vid: str, origin: str, dest: str, profile: str, rng: random.Random) -> None:
        self.sim = sim
        self.id = vid
        self.origin = origin
        self.dest = dest
        self.profile = profile
        compliance, self.min_gain = PROFILES[profile]
        self.compliant = rng.random() < compliance
        self.route: list[Link] = []
        self.idx = 0
        self.link: Link | None = None
        self.depart = sim.env.now
        self.entered_network: float | None = None
        self.entered_at = 0.0
        self.stopline_at = 0.0
        self.queued_at = 0.0
        self.crossed = None
        self.wait = 0.0
        self.stops = 0
        self.distance = 0.0
        self.reroutes = 0
        self.free_flow = 0.0
        self.seen_version = -1
        self.done = False

    # ------------------------------------------------------------------ helpers
    def link_time(self, link: Link) -> float:
        return link.free_time / self.speed_factor

    def can_enter(self, link: Link) -> bool:
        return link.has_space()

    def plan(self, now: float) -> bool:
        # drivers who do not follow the congestion information drive their usual (free-flow) route
        weight = self.delay_weight if self.compliant else 0.0
        res = self.sim.router.route_from_origin(self.origin, self.dest, now, self.speed_factor, weight)
        if res is None:
            return False
        self.route = res[0]
        self.idx = 0
        return True

    def remaining_time(self, now: float) -> float:
        router = self.sim.router
        t = self.stopline_at
        for link in self.route[self.idx + 1:]:
            if link.closed:
                return math.inf
            t += router.link_cost(link, t, self.speed_factor, self.delay_weight)
        return t - now

    def replan(self, now: float, force: bool = False) -> bool:
        """Re-plan from the current link. Returns True if the route changed."""
        res = self.sim.router.route([(self.link, self.stopline_at)], self.dest, self.speed_factor,
                                    self.delay_weight)
        if res is None:
            return False
        path, arrival = res
        if path == self.route[self.idx:]:
            return False
        if not force and (arrival - now) > (1.0 - self.min_gain) * self.remaining_time(now):
            return False
        self.route = self.route[:self.idx] + path
        self.reroutes += 1
        return True

    # ------------------------------------------------------------------ lifecycle
    def run(self, env):
        if not self.plan(env.now):
            self.sim.metrics.unroutable += 1
            return
        t0 = env.now
        while not self.can_enter(self.route[0]):
            yield env.timeout(1.0)
            if self.route[0].closed or (self.compliant and int(env.now - t0) % 10 == 0):
                self.plan(env.now)
        self.wait += env.now - t0
        self.free_flow = sum(self.link_time(link) for link in self.route)
        self.entered_network = env.now
        self.enter(self.route[0], env.now, first=True)
        while True:
            yield env.timeout(max(0.0, self.stopline_at - env.now))
            link = self.link
            if link.v == self.dest:
                del link.travellers[self.id]
                self.finish(env.now)
                return
            nxt = self.route[self.idx + 1]
            while nxt.closed:
                if not self.replan(env.now, force=True):
                    yield env.timeout(5.0)   # nowhere else to go: wait for the road to reopen
                nxt = self.route[self.idx + 1]
            del link.travellers[self.id]
            self.queued_at = env.now
            self.crossed = env.event()
            self.join_queue(link, nxt)
            yield self.crossed
            waited = env.now - self.queued_at
            if waited >= 1.0:
                self.stops += 1
            self.wait += waited

    def join_queue(self, link: Link, nxt: Link) -> None:
        link.queues[nxt.id].append(self)

    def cross(self, out_link: Link, now: float) -> None:
        """Called by the intersection when the vehicle is discharged into `out_link`."""
        self.idx += 1
        self.enter(out_link, now)
        self.crossed.succeed()

    def enter(self, link: Link, now: float, first: bool = False) -> None:
        self.link = link
        link.travellers[self.id] = self
        self.entered_at = now
        self.stopline_at = now + self.link_time(link)
        self.distance += link.length
        if not first and self.compliant and self.sim.board.version != self.seen_version and link.v != self.dest:
            self.seen_version = self.sim.board.version
            self.replan(now)
        self.on_enter(link, now)

    def on_enter(self, link: Link, now: float) -> None:
        pass

    def finish(self, now: float) -> None:
        self.done = True
        self.sim.metrics.vehicle_done(self, now)
