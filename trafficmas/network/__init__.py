"""Road networks: the queue model and the builders for grid, Braess and OSM networks."""
from __future__ import annotations

from pathlib import Path

from trafficmas.network.braess import build_braess
from trafficmas.network.grid import build_grid
from trafficmas.network.osm import build_osm
from trafficmas.network.road import Link, Movement, Node, RoadNetwork

__all__ = ["Link", "Movement", "Node", "RoadNetwork", "build_network"]


def build_network(cfg: dict, base_dir: Path | None = None) -> RoadNetwork:
    cfg = dict(cfg)
    kind = cfg.pop("type", "grid")
    if kind == "grid":
        for key in ("arterial_rows", "arterial_cols"):
            if key in cfg:
                cfg[key] = tuple(cfg[key])
        return build_grid(**cfg)
    if kind == "braess":
        return build_braess(**cfg)
    if kind == "osm":
        path = Path(cfg.pop("path"))
        if not path.is_absolute() and base_dir is not None:
            path = base_dir / path
        return build_osm(path, **cfg)
    raise ValueError(f"unknown network type: {kind}")
