import pytest

from trafficmas.network.grid import build_grid
from trafficmas.network.road import RoadNetwork

SMALL_GRID = {"type": "grid", "rows": 2, "cols": 2, "block": 200}


@pytest.fixture
def grid() -> RoadNetwork:
    return build_grid(rows=3, cols=3)


def scenario(rate: float = 1500, duration: float = 600, **extra) -> dict:
    cfg = {"name": "test", "network": dict(SMALL_GRID), "demand": {"rate": rate, "duration": duration},
           "drain": 900}
    cfg.update(extra)
    return cfg
