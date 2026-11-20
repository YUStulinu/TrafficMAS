"""Time-dependent A* routing on links, fed by the traffic information board."""
from __future__ import annotations

import heapq
import itertools
import math
import random

from trafficmas.contracts import Message
from trafficmas.network.road import Link, RoadNetwork

SLOT = 30.0             # s, resolution of the announced intentions
AHEAD = 0.5             # share of the vehicles announced for a slot that arrive before a given one
MIN_SERVICE_RATE = 0.05  # veh/s, floor for the discharge rate of a link


class TrafficInfoBoard:
    """What vehicles know about traffic.

    * **Reported delays**: the last queueing delay per link broadcast by the coordinators.
      They describe the present.
    * **Announced intentions**: informed vehicles tell the board which links they plan to
      use and when (see `Vehicle.announce`). The board counts them per link and 30 s slot.
      They describe the future, and they are what keeps informed drivers from all
      switching to the same alternative route at once.

    The board is addressed on the message bus as `intentions`.
    """

    id = "intentions"

    def __init__(self) -> None:
        self.delay: dict[str, float] = {}
        self.updated: dict[str, float] = {}
        self.version = 0
        self.announced: dict[tuple[str, int], int] = {}        # (link id, slot) -> vehicles
        self.plans: dict[str, list[tuple[str, int]]] = {}      # vehicle id -> its (link id, slot) entries
        self.latest: dict[str, float] = {}                     # vehicle id -> send time of its newest plan

    def publish(self, delays: dict[str, float], now: float) -> None:
        self.delay.update(delays)
        for lid in delays:
            self.updated[lid] = now
        self.version += 1

    def on_message(self, msg: Message) -> None:
        if msg.sent_at >= self.latest.get(msg.sender, -math.inf):   # ignore plans that arrive out of order
            self.latest[msg.sender] = msg.sent_at
            self.book(msg.sender, msg.payload["plan"])

    def book(self, vid: str, plan: list[tuple[str, float]]) -> None:
        """Replace the announced plan of a vehicle: (link id, time it reaches the end of the link)."""
        self.release(vid)
        entries = [(lid, int(t // SLOT)) for lid, t in plan]
        announced = self.announced
        for key in entries:
            announced[key] = announced.get(key, 0) + 1
        self.plans[vid] = entries

    def release(self, vid: str) -> None:
        announced = self.announced
        for key in self.plans.pop(vid, ()):
            if announced[key] > 1:
                announced[key] -= 1
            else:
                del announced[key]

    def retire(self, vid: str) -> None:
        """The vehicle has arrived: withdraw its plan and ignore announcements still on their way."""
        self.release(vid)
        self.latest[vid] = math.inf


class Router:
    """A* over links, so turn restrictions (no U-turns) are respected.

    The cost of a link entered at time t is its free-flow time plus the expected delay
    at its stop line, which has two parts:

    * the delay last reported for the link. It is a snapshot, so it fades linearly to
      zero over `horizon` seconds: a queue seen now matters less to a vehicle that will
      only get there in ten minutes;
    * the time to serve the vehicles that announced the same link for the same 30 s
      slot and are expected to arrive first (half of them, on average).

    The search labels links with arrival times, so costs may depend on the time of
    entry. The heuristic is the exact free-flow time from each link to the destination
    (one reverse Dijkstra per destination, cached). It never overestimates, whatever the
    geometry of the network, and with no congestion the search walks straight down the
    best route.
    """

    def __init__(self, net: RoadNetwork, board: TrafficInfoBoard, horizon: float = 600.0) -> None:
        self.net = net
        self.board = board
        self.horizon = horizon
        self.next_links: dict[str, list[Link]] = {
            lid: [m.outbound for m in net.movements_from(link)] for lid, link in net.links.items()}
        self.prev_links: dict[str, list[Link]] = {lid: [] for lid in net.links}
        for lid, nexts in self.next_links.items():
            for nxt in nexts:
                self.prev_links[nxt.id].append(net.links[lid])
        # share of the time a link is served: one phase out of the junction's phases
        self.green_share = {lid: 1.0 / max(1, len(net.nodes[link.v].phases)) for lid, link in net.links.items()}
        self._remaining: dict[str, dict[str, float]] = {}
        self._succ: dict[str, dict[str, list]] = {}

    # ------------------------------------------------------------------ costs
    def link_cost(self, link: Link, t: float, speed_factor: float = 1.0, delay_weight: float = 1.0) -> float:
        """Time to drive `link` and clear its stop line when it is entered at time `t`."""
        free = link.free_time / speed_factor
        if delay_weight == 0.0:
            return free
        board = self.board
        lid = link.id
        delay = board.delay.get(lid, 0.0)
        if delay > 0.0:                                   # reported queue, fading with the age of the report
            age = t - board.updated.get(lid, t)
            if age > 0.0:
                delay *= max(0.0, 1.0 - age / self.horizon)
        n = board.announced.get((lid, int((t + free) // SLOT)))
        if n:                                             # vehicles announced for the same slot, served first
            delay += AHEAD * n / max(MIN_SERVICE_RATE, link.sat_cap * self.green_share[lid])
        return free + delay_weight * delay

    def drive(self, links: list[Link], t: float, speed_factor: float = 1.0, delay_weight: float = 1.0,
              times: list | None = None) -> float:
        """Time the end of the last of `links` is reached, driving them in order from time `t`
        (`link_cost` summed, inlined). `times` collects (link id, time its end is reached);
        a closed link makes the result infinite when `times` is None."""
        board = self.board
        dget, uget, aget = board.delay.get, board.updated.get, board.announced.get
        horizon, share = self.horizon, self.green_share
        for link in links:
            if times is None and link.closed:
                return math.inf
            lid = link.id
            free = link.free_time / speed_factor
            if delay_weight == 0.0:
                t += free
            else:
                delay = dget(lid, 0.0)
                if delay > 0.0:
                    age = t - uget(lid, t)
                    if age > 0.0:
                        delay *= max(0.0, 1.0 - age / horizon)
                n = aget((lid, int((t + free) // SLOT)))
                if n:
                    delay += AHEAD * n / max(MIN_SERVICE_RATE, link.sat_cap * share[lid])
                t += free + delay_weight * delay
            if times is not None:
                times.append((lid, t))
        return t

    def remaining(self, dest: str) -> dict[str, float]:
        """Free-flow time from the end of every link to node `dest`; links that cannot reach it are absent."""
        rem = self._remaining.get(dest)
        if rem is None:
            rem = {link.id: 0.0 for link in self.net.in_links(dest)}
            heap = [(0.0, lid) for lid in rem]
            while heap:
                d, lid = heapq.heappop(heap)
                if d > rem[lid]:
                    continue
                d2 = d + self.net.links[lid].free_time
                for prev in self.prev_links[lid]:
                    if d2 < rem.get(prev.id, math.inf):
                        rem[prev.id] = d2
                        heapq.heappush(heap, (d2, prev.id))
            self._remaining[dest] = rem
        return rem

    def successors(self, dest: str) -> dict[str, list]:
        """For every link, the successors that can still reach `dest`, with what the search reads of them:
        (link, id, end node, free-flow time, free-flow time from its end to `dest`). Cached per destination."""
        succ = self._succ.get(dest)
        if succ is None:
            rem = self.remaining(dest)
            succ = {lid: [(n, n.id, n.v, n.free_time, rem[n.id]) for n in nexts if n.id in rem]
                    for lid, nexts in self.next_links.items()}
            self._succ[dest] = succ
        return succ

    # ------------------------------------------------------------------ search
    def route(self, starts: list[tuple[Link, float]], dest: str, speed_factor: float = 1.0,
              delay_weight: float = 1.0, avoid: frozenset[str] = frozenset(),
              rng: random.Random | None = None, limit: float = math.inf) -> tuple[list[Link], float] | None:
        """Best route from any of `starts` (link, time its end is reached) to node `dest`.

        Returns the list of links (starting with the chosen start link) and the
        predicted arrival time, or None if the destination cannot be reached
        (or not by `limit`: the search then stops as soon as it knows this).
        Routes that are equally fast (to the microsecond) are told apart by `rng`, so
        that drivers spread over them; without it the first one found wins.
        """
        # The loop below inlines `link_cost` with the same floating-point operations in the
        # same order, so routes and arrival times are bit-identical to calling it.
        rem = self.remaining(dest)
        cnext = itertools.count().__next__
        tie = rng.random if rng is not None else None
        unit = speed_factor == 1.0                       # x / 1.0 == x exactly, so skip the division
        heap: list = []
        push, pop = heapq.heappush, heapq.heappop
        best: dict[str, float] = {}
        bget = best.get
        parent: dict[str, str | None] = {}
        inf = math.inf
        for link, t_end in starts:
            h = rem.get(link.id)
            if h is not None and t_end < bget(link.id, inf):
                best[link.id] = t_end
                parent[link.id] = None
                push(heap, (round(t_end + (h if unit else h / speed_factor), 6), tie() if tie else 0.0, cnext(),
                            t_end, link))
        succ = self.successors(dest)
        informed = delay_weight != 0.0
        board = self.board
        dget, uget, aget = board.delay.get, board.updated.get, board.announced.get
        horizon, share = self.horizon, self.green_share
        while heap:
            f, _, _, t, link = pop(heap)
            if f > limit:   # f is a lower bound of the arrival time of every route left
                return None
            lid = link.id
            if t > best[lid]:
                continue
            if link.v == dest:
                return self._path(link, parent), t
            for nxt, nid, nv, ft, h in succ[lid]:
                if nxt.closed or (avoid and nv in avoid and nv != dest):
                    continue
                free = ft if unit else ft / speed_factor
                if informed:
                    delay = dget(nid, 0.0)
                    if delay > 0.0:
                        age = t - uget(nid, t)
                        if age > 0.0:
                            delay *= max(0.0, 1.0 - age / horizon)
                    n = aget((nid, int((t + free) // SLOT)))
                    if n:
                        delay += AHEAD * n / max(MIN_SERVICE_RATE, nxt.sat_cap * share[nid])
                    t2 = t + (free + delay_weight * delay)
                else:
                    t2 = t + free
                if t2 < bget(nid, inf):
                    best[nid] = t2
                    parent[nid] = lid
                    push(heap, (round(t2 + (h if unit else h / speed_factor), 6), tie() if tie else 0.0, cnext(),
                                t2, nxt))
        return None

    def _path(self, last: Link, parent: dict[str, str | None]) -> list[Link]:
        links = self.net.links
        path = [last]
        while parent[path[-1].id] is not None:
            path.append(links[parent[path[-1].id]])
        return path[::-1]

    def route_from_origin(self, origin: str, dest: str, now: float, speed_factor: float = 1.0,
                          delay_weight: float = 1.0, rng: random.Random | None = None):
        starts = [(link, now + self.link_cost(link, now, speed_factor, delay_weight))
                  for link in self.net.out_links(origin) if not link.closed]
        return self.route(starts, dest, speed_factor, delay_weight, rng=rng)
