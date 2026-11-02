"""Parametric Manhattan grid with gateways on all four sides."""
from __future__ import annotations

from trafficmas.network.road import RoadNetwork


def node_id(r: int, c: int) -> str:
    return f"n{r}_{c}"


def build_grid(rows: int = 4, cols: int = 4, block: float = 200.0, lanes: int = 2,
               speed: float = 13.9, arterial_rows: tuple[int, ...] = (), arterial_cols: tuple[int, ...] = (),
               arterial_lanes: int = 3, arterial_speed: float = 16.7, gateway_length: float = 150.0,
               left_turn_phases: bool = False, name: str = "grid") -> RoadNetwork:
    """Build a rows x cols grid of signalised intersections.

    Row 0 is the southern row and column 0 the western column. Every row and column
    ends in a gateway node on both sides (W<r>, E<r>, S<c>, N<c>) where vehicles
    enter and leave the network. Arterial rows/columns get more lanes and a higher
    speed limit, which makes the demand on the network uneven.
    """
    net = RoadNetwork(name)
    for r in range(rows):
        for c in range(cols):
            net.add_node(node_id(r, c), c * block, r * block)
    width, height = (cols - 1) * block, (rows - 1) * block
    for r in range(rows):
        net.add_node(f"W{r}", -gateway_length, r * block, gateway=True, side="W")
        net.add_node(f"E{r}", width + gateway_length, r * block, gateway=True, side="E")
    for c in range(cols):
        net.add_node(f"S{c}", c * block, -gateway_length, gateway=True, side="S")
        net.add_node(f"N{c}", c * block, height + gateway_length, gateway=True, side="N")

    def row_kw(r: int) -> dict:
        if r in arterial_rows:
            return {"lanes": arterial_lanes, "speed": arterial_speed, "road_class": "arterial"}
        return {"lanes": lanes, "speed": speed}

    def col_kw(c: int) -> dict:
        if c in arterial_cols:
            return {"lanes": arterial_lanes, "speed": arterial_speed, "road_class": "arterial"}
        return {"lanes": lanes, "speed": speed}

    for r in range(rows):
        net.add_road(f"W{r}", node_id(r, 0), **row_kw(r))
        for c in range(cols - 1):
            net.add_road(node_id(r, c), node_id(r, c + 1), **row_kw(r))
        net.add_road(node_id(r, cols - 1), f"E{r}", **row_kw(r))
    for c in range(cols):
        net.add_road(f"S{c}", node_id(0, c), **col_kw(c))
        for r in range(rows - 1):
            net.add_road(node_id(r, c), node_id(r + 1, c), **col_kw(c))
        net.add_road(node_id(rows - 1, c), f"N{c}", **col_kw(c))
    return net.finalize(left_turn_phases=left_turn_phases)
