"""Message bus between agents, with configurable latency and message loss."""
from __future__ import annotations

import random
from collections import Counter
from collections.abc import Callable

import simpy

from trafficmas.contracts import BROADCAST_VEHICLES, Message


class MessageBus:
    """Delivers `Message`s after a latency; each delivery can be lost independently.

    Receivers are agent ids, `zone:<k>` (every agent registered in zone k) or
    `vehicles` (every vehicle subscriber, a single radio broadcast). Every delivery
    attempt counts as one message, which is what the communication-cost metric uses.
    """

    def __init__(self, env: simpy.Environment, rng: random.Random, latency: float = 0.1,
                 jitter: float = 0.0, loss: float = 0.0, keep_log: bool = False) -> None:
        self.env = env
        self.rng = rng
        self.latency = latency
        self.jitter = jitter
        self.loss = loss
        self.agents: dict[str, object] = {}
        self.zones: dict[str, list[str]] = {}
        self.vehicle_subscribers: dict[str, Callable[[Message], None]] = {}
        self.sent = 0
        self.dropped = 0
        self.by_topic: Counter[str] = Counter()
        self.log: list[Message] | None = [] if keep_log else None

    def register(self, agent, zone: str | None = None) -> None:
        self.agents[agent.id] = agent
        if zone is not None:
            self.zones.setdefault(zone, []).append(agent.id)

    def subscribe_vehicle(self, vid: str, callback: Callable[[Message], None]) -> None:
        self.vehicle_subscribers[vid] = callback

    def unsubscribe_vehicle(self, vid: str) -> None:
        self.vehicle_subscribers.pop(vid, None)

    def send(self, msg: Message) -> None:
        msg.sent_at = self.env.now
        if self.log is not None:
            self.log.append(msg)
        if msg.receiver == BROADCAST_VEHICLES:
            self._count(msg)
            targets = list(self.vehicle_subscribers.values())
            self._schedule(msg, lambda m: [cb(m) for cb in targets])
            return
        if msg.receiver.startswith("zone:"):
            receivers = [a for a in self.zones.get(msg.receiver[5:], []) if a != msg.sender]
        else:
            receivers = [msg.receiver]
        for rid in receivers:
            agent = self.agents.get(rid)
            if agent is None:
                continue
            self._count(msg)
            if self.loss > 0 and self.rng.random() < self.loss:
                self.dropped += 1
                continue
            self._schedule(msg, agent.on_message)

    def _count(self, msg: Message) -> None:
        self.sent += 1
        self.by_topic[msg.topic] += 1

    def _schedule(self, msg: Message, handler: Callable[[Message], object]) -> None:
        delay = self.latency
        if self.jitter > 0:
            delay += self.rng.uniform(0.0, self.jitter)
        ev = self.env.timeout(delay)
        ev.callbacks.append(lambda _ev: handler(msg))
