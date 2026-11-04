"""End-to-end runs: every controller, determinism, emergency vehicles, incidents, metrics."""
import pytest

from trafficmas.config import ROOT, load_scenario
from trafficmas.control import CONTROLLERS
from trafficmas.metrics.collector import jain_index
from trafficmas.sim.demand import RATE_PROFILES, profile_value
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


def test_demand_is_independent_of_controller():
    a = Simulation(scenario(rate=2000), "fixed", seed=5).run()
    b = Simulation(scenario(rate=2000), "negotiation", seed=5).run()
    assert a["spawned"] == b["spawned"]


@pytest.mark.parametrize("mode", ["none", "preemption", "corridor"])
def test_ambulance_arrives_in_every_mode(mode):
    cfg = scenario(rate=2500, emergency={"mode": mode, "vehicles": [{"depart": 200, "origin": "W0", "dest": "E1"}]})
    sim = Simulation(cfg, "negotiation_coord", seed=2)
    s = sim.run()
    assert s["ev_completed"] == 1
    assert s["ev_response_time"] < 200
    if mode != "none":
        assert s["corridor_served"] >= 1
    if mode == "corridor":
        assert s["msg_corridor"] >= 2


def test_ambulance_is_faster_with_corridor_than_without_priority():
    def resp(mode):
        cfg = scenario(rate=5000, duration=900,
                       emergency={"mode": mode, "random": {"count": 4, "start": 200, "interval": 150}})
        return sum(Simulation(cfg, "fixed", seed=s).run()["ev_delay"] for s in (1, 2, 3))
    assert resp("corridor") < resp("none")


def test_closed_link_is_never_used():
    cfg = scenario(rate=2000, incidents=[{"link": "n0_0->n0_1", "start": 0, "end": 10000, "closed": True}])
    sim = Simulation(cfg, "max_pressure", seed=1)
    seen = []
    orig = sim.spawn_vehicle

    def spy(*a, **k):
        v = orig(*a, **k)
        seen.append(v)
        return v
    sim.spawn_vehicle = spy
    s = sim.run()
    assert s["unfinished"] == 0
    assert all("n0_0->n0_1" not in [link.id for link in v.route] for v in seen)


def test_coordinator_broadcasts_congestion():
    sim = Simulation(scenario(rate=3000), "negotiation_coord", seed=1)
    s = sim.run()
    assert s["msg_congestion"] > 0 and s["msg_status"] > 0
    assert sim.board.version > 0


def test_braess_scenario_runs():
    sc = load_scenario("scenarios/braess.yaml")
    s = Simulation(sc, "fixed", seed=1, overrides={"demand": {"duration": 600}}, base_dir=ROOT).run()
    assert s["completed"] > 100


def test_osm_scenario_runs():
    sc = load_scenario("scenarios/craiova_center.yaml")
    s = Simulation(sc, "negotiation_coord", seed=1, overrides={"demand": {"duration": 300, "rate": 2000}},
                   base_dir=ROOT).run()
    assert s["completed"] > 50


def test_jain_index():
    assert jain_index([5, 5, 5]) == pytest.approx(1.0)
    assert jain_index([1, 0, 0, 0]) == pytest.approx(0.25)


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


def test_random_ambulances_only_between_connected_gateways():
    sc = load_scenario("scenarios/braess.yaml")   # one-way network: only S -> E is possible
    ov = {"demand": {"duration": 300}, "emergency": {"random": {"count": 3, "start": 30, "interval": 30}}}
    s = Simulation(sc, "fixed", seed=4, overrides=ov, base_dir=ROOT).run()
    assert s["ev_count"] == 3 and s["unroutable"] == 0
