"""Time-dependent A* routing on links, fed by the congestion information board."""
from __future__ import annotations

import heapq
import itertools
import math

from trafficmas.network.road import Link, RoadNetwork


class TrafficInfoBoard:
    """What vehicles know about congestion: the last delay estimates broadcast by the coordinators."""

    def __init__(self) -> None:
        self.delay: dict[str, float] = {}
        self.updated: dict[str, float] = {}
        self.version = 0

    def publish(self, delays: dict[str, float], now: float) -> None:
        self.delay.update(delays)
        for lid in delays:
            self.updated[lid] = now
        self.version += 1


class Router:
    """A* over links, so turn restrictions (no U-turns) are respected.

    The cost of a link is its free-flow time plus the queueing delay last reported
    for it. The reported delay is a snapshot, so it is assumed to fade linearly back
    to zero over `horizon` seconds: a link that is congested now counts fully if the
    vehicle reaches it soon and less if it reaches it in ten minutes. This makes the
    search time-dependent: the cost of a link depends on the time it is entered.
    """

    def __init__(self, net: RoadNetwork, board: TrafficInfoBoard, horizon: float = 600.0) -> None:
        self.net = net
        self.board = board
        self.horizon = horizon
        self.vmax = net.max_speed()
        self.next_links: dict[str, list[Link]] = {
            lid: [m.outbound for m in net.movements_from(link)] for lid, link in net.links.items()}

    def predicted_delay(self, link: Link, t: float) -> float:
        d = self.board.delay.get(link.id, 0.0)
        if d <= 0.0:
            return 0.0
        age = t - self.board.updated.get(link.id, t)
        return d * max(0.0, 1.0 - max(0.0, age) / self.horizon)

    def link_cost(self, link: Link, t: float, speed_factor: float = 1.0, delay_weight: float = 1.0) -> float:
        return link.free_time / speed_factor + delay_weight * self.predicted_delay(link, t)

    def _heuristic(self, nid: str, dest: str, speed_factor: float) -> float:
        a, b = self.net.nodes[nid], self.net.nodes[dest]
        return math.hypot(a.x - b.x, a.y - b.y) / (self.vmax * speed_factor)

    def route(self, starts: list[tuple[Link, float]], dest: str, speed_factor: float = 1.0,
              delay_weight: float = 1.0, avoid: frozenset[str] = frozenset()) -> tuple[list[Link], float] | None:
        """Best route from any of `starts` (link, time its end is reached) to node `dest`.

        Returns the list of links (starting with the chosen start link) and the
        predicted arrival time, or None if the destination cannot be reached.
        """
        counter = itertools.count()
        heap: list = []
        best: dict[str, float] = {}
        parent: dict[str, str | None] = {}
        for link, t_end in starts:
            if link.v == dest:
                return [link], t_end
            if t_end < best.get(link.id, math.inf):
                best[link.id] = t_end
                parent[link.id] = None
                heapq.heappush(heap, (t_end + self._heuristic(link.v, dest, speed_factor), next(counter), t_end, link))
        while heap:
            _, _, t, link = heapq.heappop(heap)
            if t > best.get(link.id, math.inf):
                continue
            if link.v == dest:
                path = [link]
                while parent[path[-1].id] is not None:
                    path.append(self.net.links[parent[path[-1].id]])
                return path[::-1], t
            for nxt in self.next_links[link.id]:
                if nxt.closed or (nxt.v in avoid and nxt.v != dest):
                    continue
                t2 = t + self.link_cost(nxt, t, speed_factor, delay_weight)
                if t2 < best.get(nxt.id, math.inf):
                    best[nxt.id] = t2
                    parent[nxt.id] = link.id
                    heapq.heappush(heap, (t2 + self._heuristic(nxt.v, dest, speed_factor), next(counter), t2, nxt))
        return None

    def route_from_origin(self, origin: str, dest: str, now: float, speed_factor: float = 1.0,
                          delay_weight: float = 1.0):
        starts = [(link, now + self.link_cost(link, now, speed_factor, delay_weight))
                  for link in self.net.out_links(origin) if not link.closed]
        return self.route(starts, dest, speed_factor, delay_weight)
