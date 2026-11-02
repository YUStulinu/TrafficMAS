"""Download a real road network from OpenStreetMap and save it as a small JSON file.

    python scripts/fetch_osm.py --place "Craiova" --lat 44.3195 --lon 23.7960 --dist 900 --out data/craiova_center.json

Only the main roads are kept (primary, secondary, tertiary and their links). The
graph is projected to metres, nearby nodes of one junction are merged and only the
largest strongly connected component is kept, so every gateway can reach every
other one. The simulator reads the JSON with `trafficmas.network.osm` and does not
need OSMnx at run time.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import networkx as nx
import osmnx as ox

ROAD_FILTER = '["highway"~"primary|primary_link|secondary|secondary_link|tertiary|tertiary_link"]'
DEFAULT_LANES = {"primary": 2, "secondary": 2, "tertiary": 1}
DEFAULT_SPEED_KMH = {"primary": 50, "secondary": 50, "tertiary": 40}


def first(value):
    return value[0] if isinstance(value, list) else value


def as_number(value, default: float) -> float:
    try:
        return float(str(first(value)).split()[0].split(";")[0])
    except (TypeError, ValueError, IndexError):
        return default


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--place", default="Craiova")
    ap.add_argument("--lat", type=float, default=44.3195)
    ap.add_argument("--lon", type=float, default=23.7960)
    ap.add_argument("--dist", type=float, default=900.0, help="radius of the area in metres")
    ap.add_argument("--tolerance", type=float, default=20.0, help="junction merge distance in metres")
    ap.add_argument("--out", default="data/craiova_center.json")
    args = ap.parse_args()

    g = ox.graph_from_point((args.lat, args.lon), dist=args.dist, custom_filter=ROAD_FILTER,
                            simplify=True, retain_all=False)
    g = ox.project_graph(g)
    g = ox.consolidate_intersections(g, tolerance=args.tolerance, rebuild_graph=True, dead_ends=True)
    largest = max(nx.strongly_connected_components(g), key=len)
    g = g.subgraph(largest).copy()

    xs = [d["x"] for _, d in g.nodes(data=True)]
    ys = [d["y"] for _, d in g.nodes(data=True)]
    x0, y0 = min(xs), min(ys)
    nodes = [{"id": str(n), "x": round(d["x"] - x0, 1), "y": round(d["y"] - y0, 1)} for n, d in g.nodes(data=True)]

    edges = {}
    for u, v, d in g.edges(data=True):
        if u == v:
            continue
        hw = str(first(d.get("highway", "tertiary"))).replace("_link", "")
        lanes = as_number(d.get("lanes"), DEFAULT_LANES.get(hw, 1))
        if not d.get("oneway", False):
            lanes = max(1.0, lanes / 2)   # OSM counts the lanes of both directions
        speed = as_number(d.get("maxspeed"), DEFAULT_SPEED_KMH.get(hw, 40))
        key = (str(u), str(v))
        edge = {"u": key[0], "v": key[1], "length": round(float(d["length"]), 1),
                "lanes": int(max(1, min(3, round(lanes)))), "speed_kmh": speed, "highway": hw,
                "name": str(first(d.get("name", "")))}
        if key not in edges or edge["length"] < edges[key]["length"]:
            edges[key] = edge

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"place": args.place, "center": [args.lat, args.lon], "radius_m": args.dist,
                               "source": "OpenStreetMap contributors (ODbL)",
                               "nodes": nodes, "edges": list(edges.values())}, indent=1), encoding="utf-8")
    print(f"saved {len(nodes)} nodes and {len(edges)} links to {out}")


if __name__ == "__main__":
    main()
