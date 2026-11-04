"""Shared contracts between the four parts of the system.

Everything that crosses a team boundary is defined here: the message format used on
the bus, the agent interface and the signal controller interface. The modules of
each team member only depend on these definitions, never on each other's internals.
"""
from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, Protocol

if TYPE_CHECKING:
    import simpy

    from trafficmas.agents.intersection import IntersectionAgent

Performative = Literal["CFP", "PROPOSE", "ACCEPT", "REJECT", "REQUEST", "INFORM"]

# Topics used on the bus.
TOPIC_CFP = "green_cfp"            # manager intersection announces a green-time round
TOPIC_BID = "green_bid"            # upstream neighbour bids for green on its link
TOPIC_PLATOON = "platoon"          # a platoon was released towards a neighbour
TOPIC_STATUS = "status"            # intersection -> coordinator: link occupancies
TOPIC_CONGESTION = "congestion"    # coordinator -> vehicles: link delay estimates
TOPIC_DRAIN = "drain"              # coordinator -> intersection: serve a spilling link
TOPIC_METER = "meter"              # coordinator -> intersection: hold traffic out of a link
TOPIC_CORRIDOR = "corridor"        # emergency vehicle <-> intersection: slot reservation
TOPIC_ETA = "eta_update"           # emergency vehicle -> intersection: refreshed ETA
TOPIC_RELEASE = "corridor_release"  # emergency vehicle -> intersection: slot no longer needed

BROADCAST_VEHICLES = "vehicles"    # receiver id that reaches every vehicle subscriber


@dataclass
class Message:
    sender: str
    receiver: str                 # agent id, "zone:<k>" for a zone broadcast, or "vehicles"
    performative: Performative
    topic: str
    payload: dict[str, Any] = field(default_factory=dict)
    sent_at: float = 0.0
    conversation: str = ""       # groups the messages of one negotiation round / corridor


class Agent(Protocol):
    id: str

    def on_message(self, msg: Message) -> None: ...

    def run(self, env: simpy.Environment) -> Generator: ...


class Controller(Protocol):
    """Decides the signal phase of one intersection.

    `decide` is called once per simulation tick while no intergreen is running and
    returns the index of the phase that should be green next, or None to keep the
    current one. Controllers that negotiate also receive the bus messages addressed
    to their intersection through `on_message`.
    """

    def decide(self, agent: IntersectionAgent, now: float) -> int | None: ...

    def on_message(self, agent: IntersectionAgent, msg: Message) -> None: ...

    def on_tick(self, agent: IntersectionAgent, now: float, dt: float) -> None: ...

    def on_green_start(self, agent: IntersectionAgent, now: float) -> None: ...

    def on_green_end(self, agent: IntersectionAgent, now: float, released: dict[str, int]) -> None: ...

    def stats(self) -> dict: ...
