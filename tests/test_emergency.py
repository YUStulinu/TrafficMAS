"""Ambulances, rerouting around closures and random emergencies (part 3)."""
import pytest

from trafficmas.config import ROOT, load_scenario
from trafficmas.sim.engine import Simulation

from .conftest import scenario


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


def test_random_ambulances_only_between_connected_gateways():
    sc = load_scenario("scenarios/braess.yaml")   # one-way network: only S -> E is possible
    ov = {"demand": {"duration": 300}, "emergency": {"random": {"count": 3, "start": 30, "interval": 30}}}
    s = Simulation(sc, "fixed", seed=4, overrides=ov, base_dir=ROOT).run()
    assert s["ev_count"] == 3 and s["unroutable"] == 0
