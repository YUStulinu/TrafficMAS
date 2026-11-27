"""Signal control and negotiation (intersection agents, controllers, Contract Net, corridors)."""
import random

import pytest

from trafficmas.agents.intersection import EV_TIMEOUT, INTERGREEN, IntersectionAgent
from trafficmas.contracts import Message
from trafficmas.control import make_controller
from trafficmas.control.base import clearance_time, movement_pressure
from trafficmas.control.negotiation import PENDING_TIMEOUT, NegotiationController
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
    first = m.queue[0]
    for t in range(5):
        agent.discharge(float(t), 1.0)
    assert len(m.queue) == 10 - 5 * int(min(m.sat_rate, m.inbound.sat_cap))
    assert first.crossed_to is m.outbound


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


class Arriving(Dummy):
    """A vehicle driving towards the stop line, due there at `stopline_at`."""

    def __init__(self, vid, stopline_at):
        super().__init__(vid)
        self.stopline_at = stopline_at


def test_anticipation_serves_a_single_waiting_vehicle_when_the_green_is_idle():
    for anticipate, expected in ((True, 1), (False, None)):
        sim = make_sim("negotiation", {"anticipate": anticipate})
        agent = sim.agents["n0_0"]
        fill(movement(agent, phase=1), 1)                      # pressure 1.0 does not beat the hysteresis
        assert agent.controller.decide(agent, 20.0) == expected


def test_anticipation_keeps_the_green_for_a_platoon_about_to_arrive():
    sim = make_sim("negotiation")
    agent = sim.agents["n0_0"]
    ctrl = agent.controller
    fill(movement(agent, phase=1), 1)
    link = movement(agent, phase=0).inbound
    for i in range(4):                                         # four vehicles 1-4 s from the green stop line
        link.travellers[f"p{i}"] = Arriving(f"p{i}", 20.0 + 1 + i)
    assert ctrl.service_rate(agent, 0, 20.0, 0.0) == pytest.approx(4 / 4.0)
    assert ctrl.service_rate(agent, 1, 20.0, INTERGREEN) == pytest.approx(1 / (INTERGREEN + 1.0))
    assert ctrl.decide(agent, 20.0) is None


def test_service_rate_ignores_vehicles_the_downstream_link_cannot_take():
    sim = make_sim("negotiation")
    agent = sim.agents["n0_0"]
    m = next(mv for mv in agent.phases[1] if mv.outbound.queues)   # leads to another junction, not a gateway
    fill(m, 6)
    full = agent.controller.service_rate(agent, 1, 0.0, INTERGREEN)
    occupy(m.outbound, m.outbound.storage - 2)
    assert agent.controller.service_rate(agent, 1, 0.0, INTERGREEN) < full
    occupy_all = m.outbound.storage - m.outbound.occupancy
    for i in range(occupy_all):
        m.outbound.travellers[f"z{i}"] = Arriving(f"z{i}", 1e9)
    assert agent.controller.service_rate(agent, 1, 0.0, INTERGREEN) == 0.0


def test_service_rate_is_zero_into_a_closed_link():
    sim = make_sim("negotiation")
    agent = sim.agents["n0_0"]
    m = movement(agent, phase=1)
    fill(m, 5)
    assert agent.controller.service_rate(agent, 1, 0.0, INTERGREEN) > 0
    m.outbound.closed = True
    assert agent.controller.service_rate(agent, 1, 0.0, INTERGREEN) == 0.0


def test_service_rate_counts_arrivals_only_for_the_phase_that_serves_their_turn():
    sim = make_sim("negotiation", network={"type": "grid", "rows": 3, "cols": 3, "left_turn_phases": True})
    agent = sim.agents["n1_1"]
    assert len(agent.phases) == 4 and agent.shared_links
    left_phase = next(p for p, ph in enumerate(agent.phases) if all(m.turn == "left" for m in ph))
    left = agent.phases[left_phase][0]
    main_phase = next(p for p, ph in enumerate(agent.phases)
                      if p != left_phase and any(m.inbound is left.inbound for m in ph))
    through = next(m for m in agent.phases[main_phase] if m.inbound is left.inbound and m.turn == "through")
    for i, m in enumerate([left, through, through]):            # one car turning left, two going straight
        v = Arriving(f"a{i}", 1.0 + i)
        v.route, v.idx = [m.inbound, m.outbound], 0
        m.inbound.travellers[v.id] = v
    ctrl = agent.controller
    assert ctrl.service_rate(agent, left_phase, 0.0, 0.0) == pytest.approx(1 / 1.0)
    assert ctrl.service_rate(agent, main_phase, 0.0, 0.0) == pytest.approx(2 / 3.0)


def test_sensor_does_not_replace_a_reserved_slot():
    sim = make_sim("fixed")
    agent = sim.agents["n0_0"]
    agent.send = lambda *a, **k: None
    b = movement(agent, phase=1)
    agent.on_message(corridor_request("ev1", b.inbound.id, b.outbound.id, 50.0, 1))
    ev = Dummy("ev1")
    ev.priority = 1
    agent.ev_detected(ev, b.inbound, b.outbound, 12.0)
    assert not agent.reservations["ev1"].local and agent.reservations["ev1"].eta == 50.0


# ---------------------------------------------------------------------------------------------
# Whole-run invariants on a saturated grid with short blocks (spillback, hundreds of bids).

TIGHT = {"type": "grid", "rows": 3, "cols": 3, "block": 60}
MIN_GREEN = {"fixed": 30, "actuated": 8, "max_pressure": 20, "negotiation": 5, "negotiation_coord": 5}


def tight_sim(controller, params=None, rate=14000, duration=900, seed=3, **extra) -> Simulation:
    cfg = {"name": "tight", "network": dict(TIGHT), "demand": {"rate": rate, "duration": duration}, "drain": 600}
    return Simulation({**cfg, **extra}, controller, seed=seed, controller_params=params)


def runs_of(states):
    """Collapse a per-tick list into [state, number of ticks] runs."""
    out = []
    for s in states:
        if out and out[-1][0] == s:
            out[-1][1] += 1
        else:
            out.append([s, 1])
    return out


@pytest.mark.parametrize("controller", list(MIN_GREEN))
def test_signal_timing_is_respected_for_a_whole_run(controller, monkeypatch):
    sim = tight_sim(controller)
    log = {aid: [] for aid, a in sim.agents.items() if a.signalized}
    original = IntersectionAgent.step

    def step(agent, now, dt):
        original(agent, now, dt)
        if agent.signalized:
            log[agent.id].append((agent.phase, agent.in_intergreen))

    monkeypatch.setattr(IntersectionAgent, "step", step)
    summary = sim.run()
    assert summary["completed"] > 1500
    switches = 0
    for states in log.values():
        periods = runs_of(states)
        for i, ((phase, intergreen), ticks) in enumerate(periods[:-1]):   # the last period is cut off by the end
            if intergreen:
                assert ticks == INTERGREEN                   # amber + all-red always lasts exactly 4 s
                assert periods[i + 1][0][0] != phase         # and leads to a different phase
                switches += 1
            elif controller == "fixed":
                assert ticks == 30
            else:
                assert ticks >= MIN_GREEN[controller]
    assert switches > 100


def test_negotiation_never_starves_a_waiting_phase(monkeypatch):
    sim = tight_sim("negotiation_coord")
    ctrl = next(a.controller for a in sim.agents.values() if a.signalized)
    bound = ctrl.max_red + ctrl.min_green + INTERGREEN + 1
    worst = [0.0]
    original = IntersectionAgent.step

    def step(agent, now, dt):
        original(agent, now, dt)
        if agent.signalized:
            for p in range(len(agent.phases)):
                if agent.phase_queue(p) > 0:
                    worst[0] = max(worst[0], agent.red_time(p, now))

    monkeypatch.setattr(IntersectionAgent, "step", step)
    sim.run()
    assert 30 < worst[0] <= bound


def test_contract_net_protocol_and_credit_accounting(monkeypatch):
    """Every bid answers a call, gets at most one answer, and accepted bids are paid exactly once."""
    sim = tight_sim("negotiation_coord")
    sent = []
    original = IntersectionAgent.send

    def send(agent, receiver, performative, topic, payload, conversation=""):
        sent.append((sim.env.now, agent.id, receiver, performative, topic, dict(payload), conversation))
        original(agent, receiver, performative, topic, payload, conversation)

    credit_range = [float("inf"), float("-inf")]
    original_step = IntersectionAgent.step

    def step(agent, now, dt):
        original_step(agent, now, dt)
        if agent.signalized:
            credit_range[0] = min(credit_range[0], agent.controller.credits)
            credit_range[1] = max(credit_range[1], agent.controller.credits)

    monkeypatch.setattr(IntersectionAgent, "send", send)
    monkeypatch.setattr(IntersectionAgent, "step", step)
    sim.run()

    calls = {(conv, receiver) for _, _, receiver, perf, _, _, conv in sent if perf == "CFP"}
    proposals, answers = {}, {}
    for t, sender, receiver, perf, topic, payload, conv in sent:
        if perf == "PROPOSE":
            assert (conv, sender) in calls                       # a bid only answers a call for proposals
            assert (conv, sender) not in proposals               # one bid per round
            assert payload["value"] > 0
            proposals[(conv, sender)] = payload["value"]
        elif topic == "green_bid":                               # ACCEPT or REJECT
            assert conv.startswith(sender + "#")                 # only the manager of the round answers
            assert (conv, receiver) in proposals and (conv, receiver) not in answers
            if perf == "ACCEPT":
                assert payload["value"] == proposals[(conv, receiver)]
            answers[(conv, receiver)] = (t, perf)
    assert len(proposals) > 100
    assert len(answers) >= 0.95 * len(proposals)                 # the rest arrived after their round closed
    controllers = [a.controller for a in sim.agents.values() if a.signalized]
    end = sim.env.now
    accepted = [proposals[k] for k, (t, perf) in answers.items() if perf == "ACCEPT" and t < end - 1]
    assert sum(c.bids_won for c in controllers) >= len(accepted)
    assert sum(c.credits_spent for c in controllers) == pytest.approx(
        sum(proposals[k] for k, (t, perf) in answers.items() if perf == "ACCEPT" and t <= end - 0.1), rel=0.02)
    cap = controllers[0].credit_cap
    assert 0.0 <= credit_range[0] and credit_range[1] <= cap     # credits never go negative or above the cap


def test_selfish_junction_cannot_outspend_its_credit_income(monkeypatch):
    sim = tight_sim("negotiation_coord", selfish={"node": "n1_1", "factor": 5.0})
    summary = sim.run()
    cheat = sim.agents["n1_1"].controller
    income = cheat.credit_rate * summary["sim_time"] + 40.0      # regeneration plus the initial credits
    assert cheat.selfish_factor == 5.0 and cheat.bids_sent > 0
    assert cheat.credits_spent <= income + 1e-6


def test_coordinator_directives_only_with_gating_and_never_repeated_early(monkeypatch):
    for controller, expect in (("negotiation", False), ("negotiation_coord", True)):
        sim = tight_sim(controller)
        directives = []
        original = sim.bus.send

        def send(msg, directives=directives, original=original, sim=sim):
            if msg.topic in ("drain", "meter"):
                directives.append((sim.env.now, msg.topic, msg.payload["link"], msg.payload["until"]))
            original(msg)

        sim.bus.send = send
        sim.run()
        assert bool(directives) == expect
        active = {}
        for now, topic, link, until in directives:
            assert active.get((topic, link), -1.0) < now             # the previous directive has expired
            assert until == pytest.approx(now + 30.0)
            active[(topic, link)] = until


# ---------------------------------------------------------------------------------------------
# Messages, reservations and credits that the whole-run tests rarely reach.

def test_reservation_is_dropped_when_the_ambulance_is_far_too_late():
    sim = make_sim("fixed")
    agent = sim.agents["n0_0"]
    agent.send = lambda *a, **k: None
    b = movement(agent, phase=1)
    agent.on_message(corridor_request("ev1", b.inbound.id, b.outbound.id, 50.0, 1))
    assert agent.emergency_target(60.0) == 1
    assert agent.emergency_target(50.0 + EV_TIMEOUT + 1) is None    # nobody holds the junction for a lost ambulance
    assert not agent.reservations and not agent.ev_hold


def test_sensor_yields_to_a_higher_priority_reservation_on_another_phase():
    sim = make_sim("fixed")
    agent = sim.agents["n0_0"]
    agent.send = lambda *a, **k: None
    a, b = movement(agent, phase=0), movement(agent, phase=1)
    agent.on_message(corridor_request("ev1", a.inbound.id, a.outbound.id, 50.0, 2))
    low = Dummy("ev2")
    low.priority = 1
    agent.ev_detected(low, b.inbound, b.outbound, 40.0)
    assert set(agent.reservations) == {"ev1"}
    agent.ev_passed("ev1")
    agent.ev_detected(low, b.inbound, b.outbound, 40.0)        # without it, the sensor does switch
    assert agent.reservations["ev2"].local and agent.reservations["ev2"].phase == 1


def test_release_eta_and_coordinator_directives_reach_the_junction():
    sim = make_sim("negotiation_coord")
    agent = sim.agents["n0_0"]
    agent.send = lambda *a, **k: None
    b = movement(agent, phase=1)
    agent.on_message(corridor_request("ev1", b.inbound.id, b.outbound.id, 50.0, 1))
    agent.on_message(Message("ev1", agent.id, "INFORM", "eta_update", {"eta": 70.0}))
    agent.on_message(Message("ev9", agent.id, "INFORM", "eta_update", {"eta": 10.0}))   # no reservation: ignored
    assert agent.reservations["ev1"].eta == 70.0 and set(agent.reservations) == {"ev1"}
    agent.on_message(Message("ev1", agent.id, "INFORM", "corridor_release", {}))
    assert not agent.reservations
    agent.on_message(Message("coord:0", agent.id, "REQUEST", "drain", {"link": b.inbound.id, "until": 99.0}))
    agent.on_message(Message("coord:0", agent.id, "REQUEST", "meter", {"link": b.outbound.id, "until": 98.0}))
    assert agent.drain == {b.inbound.id: 99.0} and agent.meter == {b.outbound.id: 98.0}


def test_credits_held_by_an_unanswered_bid_are_freed_after_the_timeout():
    """A bid whose answer is lost must not lock the credits for ever, and a late answer must not charge them."""
    sim = make_sim("negotiation")
    up = sim.agents["n0_0"]
    ctrl = up.controller
    link = sim.net.link("n0_0", "n0_1")
    occupy(link, link.storage - 1)
    fill(next(m for m in up.node.movements if m.outbound is link), 10)
    ctrl.credits = 7.0
    sent = []
    up.send = lambda *a, **k: sent.append(a)

    def cfp(conv):
        msg = Message("n0_1", up.id, "CFP", "green_cfp", {"round": 1, "link": link.id}, conversation=conv)
        ctrl.on_message(up, msg)

    cfp("a")
    cfp("b")                                    # the 7 credits are held by the first bid
    assert len(sent) == 1 and sent[0][3]["value"] == pytest.approx(7.0)
    ctrl.on_tick(up, PENDING_TIMEOUT + 1, 1.0)  # no answer came: the hold expires
    cfp("c")
    assert len(sent) == 2 and sent[1][3]["value"] == pytest.approx(7.25)   # plus one tick of regeneration
    ctrl.on_message(up, Message("n0_1", up.id, "ACCEPT", "green_bid", {"round": 1, "value": 7.0}, conversation="a"))
    assert ctrl.bids_won == 0 and ctrl.credits == pytest.approx(7.25)       # late answer: nothing charged


def test_without_credits_bids_are_not_capped_and_cost_nothing():
    sim = make_sim("negotiation", {"credits": False, "selfish_factor": 50.0})
    up = sim.agents["n0_0"]
    ctrl = up.controller
    link = sim.net.link("n0_0", "n0_1")
    occupy(link, link.storage - 1)
    fill(next(m for m in up.node.movements if m.outbound is link), 10)
    ctrl.credits = 7.0
    sent = []
    up.send = lambda *a, **k: sent.append(a)
    ctrl.on_message(up, Message("n0_1", up.id, "CFP", "green_cfp", {"round": 1, "link": link.id}, conversation="a"))
    value = sent[0][3]["value"]
    assert value > 7.0
    ctrl.on_message(up, Message("n0_1", up.id, "ACCEPT", "green_bid", {"round": 1, "value": value}, conversation="a"))
    assert ctrl.bids_won == 1 and ctrl.credits_spent == value and ctrl.credits == 7.0


def test_max_pressure_equals_the_sum_of_movement_pressures():
    """The per-decision cache of downstream queues must not change the pressure of any phase."""
    sim = make_sim("max_pressure")
    agent = sim.agents["n0_0"]
    rng = random.Random(4)
    for i, m in enumerate(agent.node.movements):
        fill(m, rng.randrange(6), start=10 * i)
        if m.outbound.queues and rng.random() < 0.3:
            occupy(m.outbound, m.outbound.storage)
    outs = {}
    for p, ph in enumerate(agent.phases):
        expected = sum(m.sat_rate * movement_pressure(m) for m in ph)
        assert agent.controller.pressure(agent, p) == expected
        assert agent.controller.pressure(agent, p, outs) == expected


# ---------------------------------------------------------------------------------------------
# The shortcuts of the per-second loop: they must skip only work whose result is already known.

def test_negotiation_skips_service_rates_that_cannot_win(monkeypatch):
    sim = make_sim("negotiation")
    agent = sim.agents["n0_0"]
    ctrl = agent.controller
    calls = []
    original = NegotiationController.service_rate
    monkeypatch.setattr(NegotiationController, "service_rate",
                        lambda self, a, p, now, setup: calls.append(p) or original(self, a, p, now, setup))
    fill(movement(agent, phase=0), 1)                         # demand only on the green phase
    assert ctrl.decide(agent, 20.0) is None
    assert calls == [1]                                       # the green phase's own rate is not needed
    calls.clear()
    assert ctrl.decide(agent, ctrl.max_green + 1) is None     # past max green, nothing anywhere else
    assert calls == []
    movement(agent, phase=0).queue.clear()
    fill(movement(agent, phase=1), 1, start=50)
    assert ctrl.decide(agent, 20.0) == 1                      # an idle green still gives way to a waiting vehicle


def test_idle_junction_still_clears_the_credit_of_a_new_green():
    """An empty junction skips its queue loop, but a phase change must still reset the leftover credit."""
    sim = make_sim("fixed")
    agent = sim.agents["n0_0"]
    for t in range(3):
        agent.discharge(float(t), 1.0)                        # idle at phase 0
    m1 = movement(agent, phase=1)
    m1.credit = 0.7
    agent.phase = 1
    agent.discharge(3.0, 1.0)
    assert m1.credit == 0.0
    fill(m1, 3)
    agent.discharge(4.0, 1.0)
    assert len(m1.queue) == 3 - int(min(m1.sat_rate, m1.inbound.sat_cap))   # served from a zero credit
