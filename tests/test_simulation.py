"""End-to-end runs of the whole system (shared by the team)."""
import pytest

from trafficmas.control import CONTROLLERS
from trafficmas.sim.engine import Simulation

from .conftest import scenario


@pytest.mark.parametrize("controller", list(CONTROLLERS))
def test_every_controller_serves_light_demand(controller):
    s = Simulation(scenario(rate=1500), controller, seed=3).run()
    assert s["spawned"] > 150
    assert s["unfinished"] == 0
    assert s["completed"] == s["spawned"]
    assert 20 < s["avg_travel_time"] < 300


def test_same_seed_same_result():
    a = Simulation(scenario(rate=2500), "negotiation_coord", seed=7).run()
    b = Simulation(scenario(rate=2500), "negotiation_coord", seed=7).run()
    c = Simulation(scenario(rate=2500), "negotiation_coord", seed=8).run()
    keys = ["completed", "avg_travel_time", "avg_wait_time", "messages"]
    assert [a[k] for k in keys] == [b[k] for k in keys]
    assert [a[k] for k in keys] != [c[k] for k in keys]


def test_coordinator_broadcasts_congestion():
    sim = Simulation(scenario(rate=3000), "negotiation_coord", seed=1)
    s = sim.run()
    assert s["msg_congestion"] > 0 and s["msg_status"] > 0
    assert sim.board.version > 0
