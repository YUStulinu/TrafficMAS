"""Time-dependent A* routing on links, fed by the traffic information board."""
from __future__ import annotations

import heapq
import itertools
import math

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

    # ------------------------------------------------------------------ search
    def route(self, starts: list[tuple[Link, float]], dest: str, speed_factor: float = 1.0,
              delay_weight: float = 1.0, avoid: frozenset[str] = frozenset()) -> tuple[list[Link], float] | None:
        """Best route from any of `starts` (link, time its end is reached) to node `dest`.

        Returns the list of links (starting with the chosen start link) and the
        predicted arrival time, or None if the destination cannot be reached.
        """
        rem = self.remaining(dest)
        counter = itertools.count()
        heap: list = []
        best: dict[str, float] = {}
        parent: dict[str, str | None] = {}
        for link, t_end in starts:
            h = rem.get(link.id)
            if h is not None and t_end < best.get(link.id, math.inf):
                best[link.id] = t_end
                parent[link.id] = None
                heapq.heappush(heap, (t_end + h / speed_factor, next(counter), t_end, link))
        links, next_links, cost = self.net.links, self.next_links, self.link_cost
        while heap:
            _, _, t, link = heapq.heappop(heap)
            if t > best[link.id]:
                continue
            if link.v == dest:
                path = [link]
                while parent[path[-1].id] is not None:
                    path.append(links[parent[path[-1].id]])
                return path[::-1], t
            for nxt in next_links[link.id]:
                h = rem.get(nxt.id)
                if h is None or nxt.closed or (nxt.v in avoid and nxt.v != dest):
                    continue
                t2 = t + cost(nxt, t, speed_factor, delay_weight)
                if t2 < best.get(nxt.id, math.inf):
                    best[nxt.id] = t2
                    parent[nxt.id] = link.id
                    heapq.heappush(heap, (t2 + h / speed_factor, next(counter), t2, nxt))
        return None

    def route_from_origin(self, origin: str, dest: str, now: float, speed_factor: float = 1.0,
                          delay_weight: float = 1.0):
        starts = [(link, now + self.link_cost(link, now, speed_factor, delay_weight))
                  for link in self.net.out_links(origin) if not link.closed]
        return self.route(starts, dest, speed_factor, delay_weight)
