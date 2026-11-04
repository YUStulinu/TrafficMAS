"""Road network model: links with per-movement queues, movements and signal phases.

The traffic model is mesoscopic. A vehicle crosses a link at free-flow speed and then
joins a point queue at the stop line, one queue per outgoing movement. Queues are
served at saturation flow while their movement is green, but only if the downstream
link has storage left, which is how congestion spills back across intersections.
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field

VEHICLE_SPACING = 7.5   # m of road taken by one vehicle in a jam
SAT_FLOW_PER_LANE = 0.5  # veh/s discharged per lane at saturation (1800 veh/h)


@dataclass(eq=False)
class Link:
    id: str
    u: str
    v: str
    length: float
    lanes: int
    speed: float
    road_class: str = "local"
    capacity_factor: float = 1.0   # < 1 while an incident blocks part of the link
    closed: bool = False           # no vehicle may enter while closed
    travellers: dict = field(default_factory=dict)  # vehicles driving towards the stop line, by id
    queues: dict[str, deque] = field(default_factory=dict)
    cap_credit: float = 0.0
    bearing: float = 0.0           # direction of travel, degrees, counter-clockwise from east

    def __post_init__(self) -> None:
        self.storage = max(3, int(self.length * self.lanes / VEHICLE_SPACING))
        self.free_time = self.length / self.speed

    @property
    def running(self) -> int:
        return len(self.travellers)

    @property
    def queued(self) -> int:
        return sum(len(q) for q in self.queues.values())

    @property
    def occupancy(self) -> int:
        return self.running + self.queued

    @property
    def occupancy_ratio(self) -> float:
        return self.occupancy / self.storage

    @property
    def sat_cap(self) -> float:
        """Total discharge rate of the link at the stop line, veh/s."""
        return SAT_FLOW_PER_LANE * self.lanes * self.capacity_factor

    def has_space(self) -> bool:
        return not self.closed and self.occupancy < self.storage

    def __repr__(self) -> str:
        return f"Link({self.id}, occ={self.occupancy}/{self.storage})"


@dataclass(eq=False)
class Movement:
    inbound: Link
    outbound: Link
    turn: str          # "through", "left" or "right"
    sat_rate: float    # veh/s
    credit: float = 0.0

    @property
    def key(self) -> tuple[str, str]:
        return (self.inbound.id, self.outbound.id)

    @property
    def queue(self) -> deque:
        return self.inbound.queues[self.outbound.id]

    def __repr__(self) -> str:
        return f"Movement({self.inbound.id} => {self.outbound.id}, {self.turn})"


@dataclass(eq=False)
class Node:
    id: str
    x: float
    y: float
    gateway: bool = False          # vehicles can enter and leave the network here
    side: str = ""                 # compass side of a gateway (grid networks)
    signalized: bool = False
    force_signal: bool | None = None
    movements: list[Movement] = field(default_factory=list)
    phases: list[list[Movement]] = field(default_factory=list)
    phase_of: dict[tuple[str, str], int] = field(default_factory=dict)


def _bearing(a: Node, b: Node) -> float:
    return math.degrees(math.atan2(b.y - a.y, b.x - a.x)) % 360.0


def _turn(in_bearing: float, out_bearing: float) -> str:
    diff = (out_bearing - in_bearing + 180.0) % 360.0 - 180.0
    if abs(diff) <= 40.0:
        return "through"
    return "left" if diff > 0 else "right"


def _axis_distance(a: float, b: float) -> float:
    d = abs(a - b) % 180.0
    return min(d, 180.0 - d)


class RoadNetwork:
    def __init__(self, name: str) -> None:
        self.name = name
        self.nodes: dict[str, Node] = {}
        self.links: dict[str, Link] = {}
        self._out: dict[str, list[Link]] = {}
        self._in: dict[str, list[Link]] = {}

    # ---------------------------------------------------------------- building
    def add_node(self, nid: str, x: float, y: float, gateway: bool = False, side: str = "",
                 signalized: bool | None = None) -> Node:
        node = Node(nid, x, y, gateway=gateway, side=side, force_signal=signalized)
        self.nodes[nid] = node
        self._out[nid] = []
        self._in[nid] = []
        return node

    def add_link(self, u: str, v: str, lanes: int = 2, speed: float = 13.9,
                 length: float | None = None, road_class: str = "local") -> Link:
        a, b = self.nodes[u], self.nodes[v]
        if length is None:
            length = math.hypot(b.x - a.x, b.y - a.y)
        link = Link(f"{u}->{v}", u, v, max(length, 15.0), lanes, speed, road_class,
                    bearing=_bearing(a, b))
        self.links[link.id] = link
        self._out[u].append(link)
        self._in[v].append(link)
        return link

    def add_road(self, u: str, v: str, **kw) -> tuple[Link, Link]:
        return self.add_link(u, v, **kw), self.add_link(v, u, **kw)

    def finalize(self, left_turn_phases: bool = False) -> RoadNetwork:
        """Create movements and signal phases once all links are known."""
        for node in self.nodes.values():
            node.movements.clear()
            for lin in self._in[node.id]:
                lin.queues = {}
                for lout in self._out[node.id]:
                    if lout.v == lin.u:          # no U-turns
                        continue
                    turn = _turn(lin.bearing, lout.bearing)
                    lanes = lin.lanes if turn == "through" else 1
                    node.movements.append(Movement(lin, lout, turn, SAT_FLOW_PER_LANE * lanes))
                    lin.queues[lout.id] = deque()
            neighbours = {link.u for link in self._in[node.id]} | {link.v for link in self._out[node.id]}
            if node.force_signal is not None:
                node.signalized = node.force_signal and bool(node.movements)
            else:
                node.signalized = len(neighbours) >= 3 and bool(node.movements)
            node.phases = self._build_phases(node, left_turn_phases) if node.signalized else (
                [list(node.movements)] if node.movements else [])
            node.phase_of = {m.key: i for i, ph in enumerate(node.phases) for m in ph}
        return self

    def _build_phases(self, node: Node, left_turn_phases: bool) -> list[list[Movement]]:
        inbound = self._in[node.id]
        major = max(inbound, key=lambda link: (link.lanes, link.speed))
        groups: list[list[Movement]] = [[], []]
        for m in node.movements:
            g = 0 if _axis_distance(m.inbound.bearing, major.bearing) <= 45.0 else 1
            groups[g].append(m)
        phases: list[list[Movement]] = []
        for group in groups:
            if not group:
                continue
            lefts = [m for m in group if m.turn == "left"]
            if left_turn_phases and lefts and len(lefts) < len(group):
                phases.append([m for m in group if m.turn != "left"])
                phases.append(lefts)
            else:
                phases.append(group)
        return phases

    # ---------------------------------------------------------------- queries
    def link(self, u: str, v: str) -> Link:
        return self.links[f"{u}->{v}"]

    def out_links(self, nid: str) -> list[Link]:
        return self._out[nid]

    def in_links(self, nid: str) -> list[Link]:
        return self._in[nid]

    def movements_from(self, link: Link) -> list[Movement]:
        return [m for m in self.nodes[link.v].movements if m.inbound is link]

    @property
    def gateways(self) -> list[Node]:
        return [n for n in self.nodes.values() if n.gateway]

    @property
    def signalized(self) -> list[Node]:
        return [n for n in self.nodes.values() if n.signalized]

    def bbox(self) -> tuple[float, float, float, float]:
        xs = [n.x for n in self.nodes.values()]
        ys = [n.y for n in self.nodes.values()]
        return min(xs), min(ys), max(xs), max(ys)

    def max_speed(self) -> float:
        return max(link.speed for link in self.links.values())
