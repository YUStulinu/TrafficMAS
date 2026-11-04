"""Base class and the shared pressure computation for signal controllers."""
from __future__ import annotations

from typing import TYPE_CHECKING

from trafficmas.contracts import Message
from trafficmas.network.road import Movement

if TYPE_CHECKING:
    from trafficmas.agents.intersection import IntersectionAgent


def movement_pressure(m: Movement) -> float:
    """Max-pressure weight of a movement: its queue minus the average queue it feeds into.

    A movement whose downstream link is full cannot discharge at all, so it gets no
    weight - giving it green would only waste the phase.
    """
    out = m.outbound
    if not out.has_space():
        return 0.0
    out_q = out.queued / len(out.queues) if out.queues else 0.0
    return len(m.queue) - out_q


def clearance_time(movements: list[Movement]) -> float:
    """Seconds needed to serve the vehicles queued now on `movements` at saturation flow."""
    per_link: dict[str, list] = {}
    t = 0.0
    for m in movements:
        q = len(m.queue)
        if q == 0:
            continue
        t = max(t, q / max(1e-6, m.sat_rate * m.inbound.capacity_factor))
        acc = per_link.setdefault(m.inbound.id, [0, m.inbound.sat_cap])
        acc[0] += q
    for q, cap in per_link.values():
        t = max(t, q / max(1e-6, cap))
    return t


class BaseController:
    def decide(self, agent: IntersectionAgent, now: float) -> int | None:
        return None

    def on_message(self, agent: IntersectionAgent, msg: Message) -> None:
        pass

    def on_tick(self, agent: IntersectionAgent, now: float, dt: float) -> None:
        pass

    def on_green_start(self, agent: IntersectionAgent, now: float) -> None:
        pass

    def on_green_end(self, agent: IntersectionAgent, now: float, released: dict[str, int]) -> None:
        pass

    def stats(self) -> dict:
        return {}
