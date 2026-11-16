"""Ambulances, rerouting around closures and random emergencies (part 3)."""
import pytest

from trafficmas.agents.intersection import IntersectionAgent
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


# ---------------------------------------------------------------------------------------------
# Whole-run checks: corridor reservations never leak, lost messages are survived, intentions help.

BUSY = {"type": "grid", "rows": 4, "cols": 4, "block": 200, "arterial_rows": [1], "arterial_cols": [2]}
BAD_RADIO = {"latency": 3.0, "loss": 0.5}


def busy(mode="corridor", bus=None, seed=1, rate=12000, duration=1200, **extra) -> Simulation:
    cfg = {"name": "busy", "network": dict(BUSY), "demand": {"rate": rate, "duration": duration}, "drain": 900,
           "bus": bus or {}, "emergency": {"mode": mode, "random": {"count": 8, "start": 100, "interval": 120}}}
    return Simulation({**cfg, **extra}, "negotiation_coord", seed=seed)


@pytest.mark.parametrize("bus", [{}, BAD_RADIO], ids=["good_radio", "bad_radio"])
@pytest.mark.parametrize("mode", ["corridor", "preemption"])
def test_no_junction_stays_held_for_an_ambulance_that_is_not_coming(mode, bus, monkeypatch):
    sim = busy(mode, bus)
    crossed = set()
    stale = [0]
    original_passed, original_step = IntersectionAgent.ev_passed, IntersectionAgent.step

    def ev_passed(agent, ev_id):
        crossed.add((agent.id, ev_id))
        original_passed(agent, ev_id)

    def step(agent, now, dt):
        original_step(agent, now, dt)
        if agent.ev_hold:
            def coming(r):
                v = sim.vehicles.get(r.ev_id)
                return (v is not None and not v.done and (agent.id, r.ev_id) not in crossed
                        and any(link.v == agent.id for link in v.route[v.idx:]))
            if not any(coming(r) for r in agent.reservations.values()):
                stale[0] += 1

    monkeypatch.setattr(IntersectionAgent, "ev_passed", ev_passed)
    monkeypatch.setattr(IntersectionAgent, "step", step)
    summary = sim.run()
    assert summary["ev_completed"] == summary["ev_count"] == 8
    assert len(crossed) >= 16
    assert stale[0] <= len(crossed)          # at most the one tick in which the ambulance crosses
    assert not any(a.reservations for a in sim.agents.values())
    assert not any(a.ev_queued for a in sim.agents.values())


def test_corridor_with_a_bad_radio_still_beats_no_priority():
    def delay(mode, bus):
        return sum(busy(mode, bus, seed=s).run()["ev_delay"] for s in (1, 2, 3)) / 3
    none, good, bad = delay("none", {}), delay("corridor", {}), delay("corridor", BAD_RADIO)
    assert good < 0.5 * none
    assert bad < 0.6 * none                  # the junction's own sensor covers for the lost reservations


def test_intention_sharing_stops_informed_drivers_from_herding():
    """With every driver informed, announcing routes must clearly shorten the trips."""
    def time_in_system(intentions):
        cfg = {"name": "herd", "network": dict(BUSY), "drain": 900,
               "demand": {"rate": 17000, "duration": 1500, "driver_profiles": {"aggressive": 1.0}},
               "routing": {"intentions": intentions}}
        runs = [Simulation(cfg, "negotiation_coord", seed=s).run() for s in (1, 2)]
        return sum(r["avg_time_in_system"] for r in runs) / 2, runs[0]
    with_sharing, run = time_in_system(True)
    without, run_off = time_in_system(False)
    assert with_sharing < 0.95 * without
    assert run["msg_intention"] > 1000 and "msg_intention" not in run_off


def test_announced_plans_are_withdrawn_when_trips_end():
    sim = busy("none", rate=8000, duration=600)
    summary = sim.run()
    assert summary["unfinished"] == 0 and summary["msg_intention"] > 0
    assert not sim.board.plans and not any(sim.board.announced.values())


def test_no_trip_is_faster_than_free_flow():
    sim = busy("none", rate=9000, duration=600)
    sim.run()
    assert len(sim.metrics.trips) > 1000
    assert min(t["delay"] for t in sim.metrics.trips) > -1e-6
