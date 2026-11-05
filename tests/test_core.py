"""Simulation core: demand, scenario validation, OSM and Braess networks (part 1)."""
import pytest

from trafficmas.config import ROOT, load_scenario
from trafficmas.sim.demand import RATE_PROFILES, profile_value
from trafficmas.sim.engine import Simulation

from .conftest import scenario


def test_demand_is_independent_of_controller():
    a = Simulation(scenario(rate=2000), "fixed", seed=5).run()
    b = Simulation(scenario(rate=2000), "negotiation", seed=5).run()
    assert a["spawned"] == b["spawned"]


def test_braess_scenario_runs():
    sc = load_scenario("scenarios/braess.yaml")
    s = Simulation(sc, "fixed", seed=1, overrides={"demand": {"duration": 600}}, base_dir=ROOT).run()
    assert s["completed"] > 100


def test_osm_scenario_runs():
    sc = load_scenario("scenarios/craiova_center.yaml")
    s = Simulation(sc, "negotiation_coord", seed=1, overrides={"demand": {"duration": 300, "rate": 2000}},
                   base_dir=ROOT).run()
    assert s["completed"] > 50


def test_rush_hour_profile():
    pts = RATE_PROFILES["rush_hour"]
    assert profile_value(pts, 1800) == pytest.approx(1.35)
    assert profile_value(pts, 450) == pytest.approx(0.8)


@pytest.mark.parametrize("override, message", [
    ({"incidents": [{"link": "x->y", "start": 0}]}, "unknown link"),
    ({"emergency": {"vehicles": [{"depart": 10, "origin": "nowhere", "dest": "E0"}]}}, "not a node"),
    ({"demand": {"od_pairs": [["A", "Z", 1.0]]}}, "unknown nodes"),
    ({"demand": {"driver_profiles": {"reckless": 1.0}}}, "unknown driver profiles"),
    ({"demand": {"od_pairs": [["W0", "E0", 0.0]]}}, "matrix is empty"),
])
def test_bad_scenarios_fail_at_start(override, message):
    with pytest.raises(ValueError, match=message):
        Simulation(scenario(**override), "fixed", seed=1)
