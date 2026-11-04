"""Negotiating signal controller: the original contribution of TrafficMAS+.

Every intersection plays two roles in a Contract Net that runs continuously
between neighbours:

* **Manager** of its own green time. While the current phase is green, it opens a
  round every `cfp_interval` seconds by sending a call for proposals (CFP) to the
  upstream neighbours that feed it. At each decision point it scores every phase
  and settles the round: the bids on links served by the phase that stays or
  becomes green are accepted (and paid for), the others are rejected.
* **Contractor** for its downstream neighbours. When a neighbour N calls for
  proposals, the agent bids for green on its own link into N if that link is
  filling up and vehicles at its stop lines are waiting to enter it. Such vehicles
  are about to be blocked, so the bid is a request to prevent spillback.

Bids are paid with **credits**. Every agent earns credits at a fixed rate up to a
cap, and an accepted bid costs its value. A neighbour that over-bids, for example
a selfish one that inflates its urgency, runs out of credits and cannot dominate
the others for long. This is the incentive mechanism measured in the selfish-agent
experiment.

The agent's architecture is a simplified BDI loop:

* beliefs: own queues, the occupancy of the downstream links, the bids of this
  round, platoon notices from upstream neighbours, coordinator directives;
* desires: low pressure, no spillback into neighbours, serve arriving platoons;
* intention: the current green phase. When a phase turns green the agent
  commits to it until the queue it found has been served (at most `max_commit`
  seconds), and afterwards revises it only when another phase scores clearly
  better (hysteresis). Every switch costs an intergreen of lost time, so an agent
  that reconsiders too often loses capacity exactly when traffic is heaviest.

**Platoons.** When a green ends, the agent tells each signalised downstream
neighbour how many vehicles it just released towards it and when they will
arrive. The neighbour adds the expected arrivals to the score of the phase that
serves them. Green waves along busy corridors then emerge from these local
messages alone, without any central offset plan.

**Coordinator directives** (only with `coordination=True`). When a zone
coordinator sees a link spilling back, it asks the downstream agent to drain the
link and the upstream agent to meter (hold back) traffic into it.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from trafficmas.contracts import TOPIC_BID, TOPIC_CFP, TOPIC_PLATOON, Message
from trafficmas.control.base import BaseController, clearance_time, movement_pressure

if TYPE_CHECKING:
    from trafficmas.agents.intersection import IntersectionAgent


@dataclass
class Platoon:
    link: str
    t_from: float
    t_to: float
    size: int

    def expected_in(self, now: float, horizon: float) -> float:
        """Vehicles of the platoon expected to arrive in [now, now + horizon]."""
        lo, hi = max(self.t_from, now), min(self.t_to, now + horizon)
        if hi < lo:
            return 0.0
        return self.size * (hi - lo + 1.0) / (self.t_to - self.t_from + 1.0)


class NegotiationController(BaseController):

    def __init__(self, min_green: float = 5.0, max_green: float = 60.0, max_red: float = 90.0,
                 hysteresis: float = 1.0, commit: bool = True, max_commit: float = 40.0,
                 arrival_weight: float = 1.0, arrival_horizon: float = 4.0,
                 # Contract Net
                 use_bids: bool = True, cfp_interval: float = 4.0, cfp_lead: float = 2.0, bid_weight: float = 0.4,
                 urgency_threshold: float = 0.5, bid_scale: float = 4.0, invite_threshold: float = 0.5,
                 # credits
                 credits: bool = True, credit_init: float = 40.0, credit_rate: float = 0.25,
                 credit_cap: float = 80.0,
                 # platoons
                 use_platoons: bool = True, platoon_min: int = 4, platoon_weight: float = 0.5,
                 platoon_horizon: float = 10.0,
                 # coordinator directives
                 coordination: bool = False, drain_weight: float = 1.0, meter_weight: float = 1.0,
                 # manipulation experiment: multiply this agent's bids
                 selfish_factor: float = 1.0) -> None:
        self.min_green = min_green
        self.max_green = max_green
        self.max_red = max_red
        self.hysteresis = hysteresis
        self.commit = commit
        self.arrival_weight = arrival_weight
        self.arrival_horizon = arrival_horizon
        self.max_commit = max_commit
        self.commit_until = 0.0
        self.use_bids = use_bids
        self.cfp_interval = cfp_interval
        self.cfp_lead = cfp_lead
        self.bid_weight = bid_weight
        self.urgency_threshold = urgency_threshold
        self.bid_scale = bid_scale
        self.invite_threshold = invite_threshold
        self.use_credits = credits
        self.credit_rate = credit_rate
        self.credit_cap = credit_cap
        self.credits = credit_init
        self.use_platoons = use_platoons
        self.platoon_min = platoon_min
        self.platoon_weight = platoon_weight
        self.platoon_horizon = platoon_horizon
        self.coordination = coordination
        self.drain_weight = drain_weight
        self.meter_weight = meter_weight
        self.selfish_factor = selfish_factor
        # manager state
        self.round = 0
        self.round_open = False                         # bids are only taken while a round is open
        self.next_cfp = 0.0
        self.bids: dict[str, tuple[str, float]] = {}   # bidder -> (link id, value)
        self.platoons: list[Platoon] = []
        self.upstream: list[tuple[str, str]] = []      # (neighbour id, link id from it)
        self._resolved = False
        # statistics
        self.rounds = 0
        self.bids_sent = 0
        self.bids_received = 0
        self.bids_won = 0
        self.credits_spent = 0.0
        self.platoons_sent = 0

    # ------------------------------------------------------------------ setup
    def _resolve_neighbours(self, agent: IntersectionAgent) -> None:
        if self._resolved:
            return
        self._resolved = True
        for link in agent.in_links:
            other = agent.sim.agents.get(link.u)
            if other is not None and other.signalized and isinstance(other.controller, NegotiationController):
                self.upstream.append((other.id, link.id))

    # ------------------------------------------------------------------ manager role
    def on_tick(self, agent: IntersectionAgent, now: float, dt: float) -> None:
        if self.use_credits:
            self.credits = min(self.credit_cap, self.credits + self.credit_rate * dt)
        if self.platoons:
            self.platoons = [p for p in self.platoons if p.t_to >= now]

    def on_green_start(self, agent: IntersectionAgent, now: float) -> None:
        if self.commit:
            hold = clearance_time(agent.phases[agent.phase])
            self.commit_until = now + min(self.max_commit, max(self.min_green, hold))

    def score(self, agent: IntersectionAgent, p: int, now: float) -> float:
        s = 0.0
        coord = self.coordination
        for m in agent.phases[p]:
            if coord and agent.meter.get(m.outbound.id, -1.0) > now:
                s -= self.meter_weight * m.sat_rate * len(m.queue)
            else:
                s += m.sat_rate * movement_pressure(m)
        links = agent.phase_links[p]
        if self.arrival_weight > 0:
            s += self.arrival_weight * 0.5 * agent.approaching(p, now, self.arrival_horizon)
        if self.bids:
            s += self.bid_weight * sum(v for lid, v in self.bids.values() if lid in links)
        if self.platoons:
            s += self.platoon_weight * 0.5 * sum(
                pl.expected_in(now, self.platoon_horizon) for pl in self.platoons if pl.link in links)
        if coord:
            for lid in links:
                if agent.drain.get(lid, -1.0) > now:
                    s += self.drain_weight * 0.5 * agent.sim.net.links[lid].queued
        return s

    def _open_round(self, agent: IntersectionAgent, now: float) -> None:
        self._settle(agent, agent.phase)
        self.next_cfp = now + self.cfp_interval
        # a neighbour only has something to bid for if its link into us is filling up
        invited = [(n, lid) for n, lid in self.upstream
                   if agent.sim.net.links[lid].occupancy_ratio > self.invite_threshold]
        if not invited:
            return
        self.round += 1
        self.rounds += 1
        self.round_open = True
        for neighbour, link_id in invited:
            agent.send(neighbour, "CFP", TOPIC_CFP, {"round": self.round, "link": link_id},
                       conversation=f"{agent.id}#{self.round}")

    def _settle(self, agent: IntersectionAgent, winner: int) -> None:
        self.round_open = False
        if not self.bids:
            return
        links = agent.phase_links[winner]
        for bidder, (lid, value) in self.bids.items():
            conv = f"{agent.id}#{self.round}"
            if lid in links:
                agent.send(bidder, "ACCEPT", TOPIC_BID, {"round": self.round, "value": value}, conv)
            else:
                agent.send(bidder, "REJECT", TOPIC_BID, {"round": self.round}, conv)
        self.bids = {}

    def decide(self, agent: IntersectionAgent, now: float) -> int | None:
        self._resolve_neighbours(agent)
        el = agent.phase_elapsed(now)
        cur = agent.phase
        committed = now < self.commit_until and agent.phase_queue(cur) > 0
        if (self.use_bids and self.upstream and el >= self.min_green - self.cfp_lead
                and now >= self.commit_until - self.cfp_lead and now >= self.next_cfp):
            self._open_round(agent, now)
        if el < self.min_green:
            return None
        n = len(agent.phases)
        # fairness guard: a phase with waiting vehicles is never starved
        starving = [p for p in range(n) if p != cur and agent.phase_queue(p) > 0
                    and agent.red_time(p, now) >= self.max_red]
        if starving:
            return self._switch(agent, max(starving, key=lambda p: agent.red_time(p, now)))
        if committed:
            return None
        scores = [self.score(agent, p, now) for p in range(n)]
        if el >= self.max_green:
            others = [p for p in range(n) if p != cur and agent.phase_demand(p, now) > 0]
            if others:
                return self._switch(agent, max(others, key=lambda p: scores[p]))
        best = max(range(n), key=lambda p: (scores[p], p == cur))
        if best != cur and scores[best] > scores[cur] + self.hysteresis:
            return self._switch(agent, best)
        return None

    def _switch(self, agent: IntersectionAgent, p: int) -> int:
        self._settle(agent, p)
        self.next_cfp = 0.0
        return p

    def on_green_end(self, agent: IntersectionAgent, now: float, released: dict[str, int]) -> None:
        if not self.use_platoons:
            return
        for lid, count in released.items():
            if count < self.platoon_min:
                continue
            link = agent.sim.net.links[lid]
            other = agent.sim.agents.get(link.v)
            if other is None or not other.signalized or not isinstance(other.controller, NegotiationController):
                continue
            self.platoons_sent += 1
            agent.send(other.id, "INFORM", TOPIC_PLATOON,
                       {"link": lid, "t_from": agent.green_start + link.free_time,
                        "t_to": now + link.free_time, "size": count})

    # ------------------------------------------------------------------ contractor role
    def urgency(self, agent: IntersectionAgent, link_id: str) -> float:
        """How badly this agent needs the downstream neighbour to drain `link_id`.

        Zero while the link is at most half full; then the number of vehicles waiting
        at this agent's stop lines to enter the link, scaled by how full it is.
        """
        link = agent.sim.net.links[link_id]
        fill = (link.occupancy_ratio - 0.5) / 0.5
        if fill <= 0.0:
            return 0.0
        waiting = sum(len(m.queue) for m in agent.node.movements if m.outbound is link)
        return min(1.0, fill) * waiting

    def on_message(self, agent: IntersectionAgent, msg: Message) -> None:
        if msg.topic == TOPIC_CFP:
            u = self.urgency(agent, msg.payload["link"]) * self.selfish_factor
            if u < self.urgency_threshold:
                return   # no interest: refusing silently saves a message
            value = self.bid_scale * u
            if self.use_credits:
                value = min(self.credits, value)
            if value <= 0.0:
                return
            self.bids_sent += 1
            agent.send(msg.sender, "PROPOSE", TOPIC_BID,
                       {"round": msg.payload["round"], "link": msg.payload["link"], "value": value},
                       msg.conversation)
        elif msg.topic == TOPIC_BID:
            if msg.performative == "PROPOSE":
                if self.round_open and msg.payload["round"] == self.round:
                    self.bids_received += 1
                    self.bids[msg.sender] = (msg.payload["link"], msg.payload["value"])
            elif msg.performative == "ACCEPT":
                self.bids_won += 1
                value = msg.payload["value"]
                self.credits_spent += value
                if self.use_credits:
                    self.credits = max(0.0, self.credits - value)
        elif msg.topic == TOPIC_PLATOON:
            p = msg.payload
            self.platoons.append(Platoon(p["link"], p["t_from"], p["t_to"], p["size"]))

    def stats(self) -> dict:
        return {"rounds": self.rounds, "bids_sent": self.bids_sent, "bids_received": self.bids_received,
                "bids_won": self.bids_won, "credits_spent": self.credits_spent,
                "platoons_sent": self.platoons_sent}
