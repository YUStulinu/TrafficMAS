"""Signal control and negotiation (intersection agents, controllers, Contract Net, corridors)."""
import pytest

from trafficmas.agents.intersection import INTERGREEN, IntersectionAgent
from trafficmas.contracts import Message
from trafficmas.control import make_controller
from trafficmas.control.base import clearance_time, movement_pressure
from trafficmas.control.negotiation import NegotiationController
from trafficmas.sim.engine import Simulation

from .conftest import scenario


class Dummy:
    """A queued vehicle stand-in that records where the intersection sends it."""

    is_emergency = False
    priority = 0

    def __init__(self, vid="d", queued_at=0.0):
        self.id = vid
        self.queued_at = queued_at
        self.crossed_to = None

    def cross(self, out_link, now):
        self.crossed_to = out_link


def make_sim(controller="negotiation", params=None, **extra):
    return Simulation(scenario(rate=0, **extra), controller, seed=1, controller_params=params)


def movement(agent: IntersectionAgent, turn="through", phase=None):
    phase = agent.phase if phase is None else phase
    return next(m for m in agent.phases[phase] if m.turn == turn)


def occupy(link, n):
    """Put n vehicles far from the stop line on `link` (they only take storage)."""
    for i in range(n):
        d = Dummy(f"x{i}")
        d.stopline_at = 1e9
        link.travellers[d.id] = d


def fill(m, n, start=0):
    for i in range(n):
        m.queue.append(Dummy(f"d{start + i}"))


def test_discharge_at_saturation_flow():
    sim = make_sim("fixed")
    agent = sim.agents["n0_0"]
    m = movement(agent)
    fill(m, 10)
    for t in range(5):
        agent.discharge(float(t), 1.0)
    assert len(m.queue) == 10 - 5 * int(min(m.sat_rate, m.inbound.sat_cap))


def test_full_downstream_link_blocks_discharge():
    sim = make_sim("fixed")
    agent = sim.agents["n0_0"]
    m = movement(agent)
    fill(m, 3)
    occupy(m.outbound, m.outbound.storage)
    agent.discharge(0.0, 1.0)
    assert len(m.queue) == 3
    assert sim.metrics.blocked_events >= 1


def test_intergreen_then_switch():
    sim = make_sim("fixed")
    agent = sim.agents["n0_0"]
    m_next = movement(agent, phase=1)
    fill(m_next, 2)
    agent.switch_to(1, 0.0)
    for t in range(int(INTERGREEN) - 1):
        agent.step(float(t), 1.0)
        assert agent.in_intergreen
    agent.step(INTERGREEN, 1.0)
    assert agent.phase == 1 and not agent.in_intergreen


def test_max_pressure_prefers_longer_queue():
    sim = make_sim("max_pressure", {"min_green": 1})
    agent = sim.agents["n0_0"]
    fill(movement(agent, phase=1), 8)
    fill(movement(agent, phase=0), 1)
    assert agent.controller.decide(agent, 10.0) == 1


def test_pressure_is_zero_into_a_full_link():
    sim = make_sim("max_pressure")
    m = movement(sim.agents["n0_0"])
    fill(m, 5)
    assert movement_pressure(m) == 5
    occupy(m.outbound, m.outbound.storage)
    assert movement_pressure(m) == 0


def test_actuated_extends_while_queue_remains():
    sim = make_sim("actuated")
    agent = sim.agents["n0_0"]
    fill(movement(agent, phase=0), 3)
    fill(movement(agent, phase=1), 3)
    assert agent.controller.decide(agent, 10.0) is None       # queue on green: extend
    movement(agent, phase=0).queue.clear()
    assert agent.controller.decide(agent, 10.0) == 1          # gap out
    fill(movement(agent, phase=0), 3, start=10)
    assert agent.controller.decide(agent, 31.0) == 1          # max green reached


def test_negotiation_commits_until_initial_queue_is_served():
    sim = make_sim("negotiation")
    agent = sim.agents["n0_0"]
    ctrl: NegotiationController = agent.controller
    m0 = movement(agent, phase=0)
    fill(m0, 20)
    ctrl.on_green_start(agent, 0.0)
    assert ctrl.commit_until == pytest.approx(min(ctrl.max_commit, clearance_time(agent.phases[0])))
    fill(movement(agent, phase=1), 40, start=100)
    assert ctrl.decide(agent, 10.0) is None                  # committed despite more pressure elsewhere
    assert ctrl.decide(agent, ctrl.commit_until + 1) == 1


def test_negotiation_starvation_guard():
    sim = make_sim("negotiation", {"commit": False})
    agent = sim.agents["n0_0"]
    fill(movement(agent, phase=0), 30)
    fill(movement(agent, phase=1), 1, start=100)
    agent.last_green[1] = 0.0
    assert agent.controller.decide(agent, 50.0) is None
    assert agent.controller.decide(agent, 95.0) == 1          # waited longer than max_red


def test_contract_net_round_with_credits():
    """Upstream n0_0 bids for green on its link into n0_1, wins and pays credits."""
    sim = make_sim("negotiation", {"commit": False})
    up, down = sim.agents["n0_0"], sim.agents["n0_1"]
    link = sim.net.link("n0_0", "n0_1")
    # the link into the manager is nearly full and the contractor has vehicles waiting for it
    occupy(link, int(0.9 * link.storage))
    waiting = next(m for m in up.node.movements if m.outbound is link)
    fill(waiting, 6)
    up.phase = 1 - up.node.phase_of[waiting.key]            # keep them waiting (red) at n0_0
    serving = down.node.phase_of[(link.id, sim.net.link("n0_1", "E0").id)]
    down.phase = 1 - serving                                 # the link is currently red at n0_1
    credits_before = up.controller.credits
    ctrl = down.controller
    ctrl._resolve_neighbours(down)
    ctrl._open_round(down, 0.0)
    sim.env.run(until=1.0)                                   # CFP and PROPOSE travel over the bus
    assert up.controller.bids_sent == 1 and link.id in {lid for lid, _ in ctrl.bids.values()}
    bid_value = next(v for lid, v in ctrl.bids.values() if lid == link.id)
    assert bid_value <= credits_before
    ctrl._settle(down, serving)                              # the phase serving the link wins
    sim.env.run(until=2.0)
    assert up.controller.bids_won == 1
    assert up.controller.credits == pytest.approx(credits_before - bid_value, abs=1.0)   # paid, minus regeneration


def test_no_bid_when_link_has_room():
    sim = make_sim("negotiation")
    up = sim.agents["n0_0"]
    link = sim.net.link("n0_0", "n0_1")
    assert up.controller.urgency(up, link.id) == 0.0


def test_selfish_bids_are_capped_by_credits():
    sim = make_sim("negotiation", {"selfish_factor": 50.0})
    up = sim.agents["n0_0"]
    link = sim.net.link("n0_0", "n0_1")
    occupy(link, link.storage - 1)
    fill(next(m for m in up.node.movements if m.outbound is link), 10)
    up.controller.credits = 7.0
    sent = []
    up.send = lambda *a, **k: sent.append(a)
    up.controller.on_message(up, Message("n0_1", "n0_0", "CFP", "green_cfp", {"round": 1, "link": link.id}))
    assert sent and sent[0][3]["value"] == pytest.approx(7.0)


def corridor_request(ev, in_link, out_link, eta, priority):
    return Message(ev, "n0_0", "REQUEST", "corridor",
                   {"in_link": in_link, "out_link": out_link, "eta": eta, "priority": priority}, conversation=ev)


def test_corridor_conflict_resolved_by_priority():
    sim = make_sim("negotiation")
    agent = sim.agents["n0_0"]
    replies = []
    agent.send = lambda receiver, perf, topic, payload, conv="": replies.append((receiver, perf))
    a = movement(agent, phase=0)
    b = movement(agent, phase=1)
    agent.on_message(corridor_request("ev1", a.inbound.id, a.outbound.id, 100.0, 1))
    agent.on_message(corridor_request("ev2", b.inbound.id, b.outbound.id, 105.0, 1))   # same priority: refused
    agent.on_message(corridor_request("ev3", b.inbound.id, b.outbound.id, 102.0, 2))   # higher: displaces ev1
    assert replies == [("ev1", "ACCEPT"), ("ev2", "REJECT"), ("ev1", "REJECT"), ("ev3", "ACCEPT")]
    assert set(agent.reservations) == {"ev3"}


def test_reservation_overrides_controller_before_eta():
    sim = make_sim("fixed")
    agent = sim.agents["n0_0"]
    b = movement(agent, phase=1)
    agent.send = lambda *a, **k: None
    agent.on_message(corridor_request("ev1", b.inbound.id, b.outbound.id, 50.0, 1))
    assert agent.emergency_target(10.0) is None              # too early
    assert agent.emergency_target(45.0) == 1                 # within the lead time
    agent.ev_passed("ev1")
    assert agent.emergency_target(46.0) is None


def test_registry_rejects_unknown_controller():
    with pytest.raises(KeyError):
        make_controller("does_not_exist")
