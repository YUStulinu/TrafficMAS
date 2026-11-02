"""Load a real road network exported by scripts/fetch_osm.py."""
from __future__ import annotations

import json
from pathlib import Path

from trafficmas.network.road import RoadNetwork


def build_osm(path: str | Path, gateway_margin: float = 0.12, left_turn_phases: bool = False,
              name: str | None = None) -> RoadNetwork:
    """Build a RoadNetwork from the JSON export.

    Nodes close to the border of the area (within `gateway_margin` of its extent)
    become gateways: that is where traffic enters from and leaves to the rest of the
    city. Junctions with three or more neighbours get traffic lights.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    xs = [n["x"] for n in data["nodes"]]
    ys = [n["y"] for n in data["nodes"]]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    mx, my = gateway_margin * (x1 - x0), gateway_margin * (y1 - y0)

    net = RoadNetwork(name or Path(path).stem)
    for n in data["nodes"]:
        x, y = n["x"], n["y"]
        side = ""
        if x <= x0 + mx:
            side = "W"
        elif x >= x1 - mx:
            side = "E"
        elif y <= y0 + my:
            side = "S"
        elif y >= y1 - my:
            side = "N"
        net.add_node(f"o{n['id']}", x, y, gateway=bool(side), side=side)
    for e in data["edges"]:
        road_class = "arterial" if e["highway"] in ("primary", "secondary") else "local"
        net.add_link(f"o{e['u']}", f"o{e['v']}", lanes=int(e["lanes"]), speed=float(e["speed_kmh"]) / 3.6,
                     length=float(e["length"]), road_class=road_class)
    return net.finalize(left_turn_phases=left_turn_phases)
