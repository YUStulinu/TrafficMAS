"""The three baselines the negotiation controller is compared against."""
from __future__ import annotations

from typing import TYPE_CHECKING

from trafficmas.control.base import BaseController, movement_pressure

if TYPE_CHECKING:
    from trafficmas.agents.intersection import IntersectionAgent


class FixedTimeController(BaseController):
    """Pre-timed plan: every phase gets the same green, in a fixed cycle."""


    def __init__(self, green: float = 30.0) -> None:
        self.green = green

    def decide(self, agent: IntersectionAgent, now: float) -> int | None:
        if agent.phase_elapsed(now) >= self.green:
            return (agent.phase + 1) % len(agent.phases)
        return None


class ActuatedController(BaseController):
    """Vehicle-actuated control: extend the green while vehicles keep arriving.

    The green lasts at least `min_green`, is extended while the current phase still
    has a queue or a vehicle within `gap` seconds of the stop line, and ends at
    `max_green`. Phases without demand are skipped.
    """


    def __init__(self, min_green: float = 8.0, max_green: float = 30.0, gap: float = 3.0) -> None:
        self.min_green = min_green
        self.max_green = max_green
        self.gap = gap

    def _next_with_demand(self, agent: IntersectionAgent, now: float) -> int | None:
        n = len(agent.phases)
        for k in range(1, n):
            p = (agent.phase + k) % n
            if agent.phase_demand(p, now) > 0:
                return p
        return None

    def decide(self, agent: IntersectionAgent, now: float) -> int | None:
        el = agent.phase_elapsed(now)
        if el < self.min_green:
            return None
        nxt = self._next_with_demand(agent, now)
        if nxt is None:
            return None
        if el >= self.max_green:
            return nxt
        cur = agent.phase
        if agent.phase_queue(cur) > 0 or agent.approaching(cur, now, self.gap) > 0:
            return None
        return nxt


class MaxPressureController(BaseController):
    """Max-pressure control (Varaiya, 2013): green for the phase with the largest pressure.

    Decisions are taken every `min_green` seconds at the earliest. Max-pressure is
    fully decentralised and needs no communication; it is the strongest baseline.
    """


    def __init__(self, min_green: float = 20.0) -> None:
        self.min_green = min_green

    @staticmethod
    def pressure(agent: IntersectionAgent, p: int) -> float:
        return sum(m.sat_rate * movement_pressure(m) for m in agent.phases[p])

    def decide(self, agent: IntersectionAgent, now: float) -> int | None:
        if agent.phase_elapsed(now) < self.min_green:
            return None
        scores = [self.pressure(agent, p) for p in range(len(agent.phases))]
        best = max(range(len(scores)), key=lambda p: (scores[p], p == agent.phase))
        if best != agent.phase and scores[best] > scores[agent.phase]:
            return best
        return None
