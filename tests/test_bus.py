"""Message bus (part 1)."""
import random

import simpy

from trafficmas.bus.bus import MessageBus
from trafficmas.contracts import Message


class Inbox:
    def __init__(self, aid):
        self.id = aid
        self.got = []

    def on_message(self, msg):
        self.got.append((msg, msg.sent_at))


def test_bus_latency_and_counting():
    env = simpy.Environment()
    bus = MessageBus(env, random.Random(1), latency=0.5)
    a, b = Inbox("a"), Inbox("b")
    bus.register(a)
    bus.register(b)
    bus.send(Message("a", "b", "INFORM", "status", {"x": 1}))
    env.run(until=0.4)
    assert b.got == []
    env.run(until=0.6)
    assert len(b.got) == 1 and bus.sent == 1 and bus.by_topic["status"] == 1


def test_bus_zone_broadcast_skips_sender():
    env = simpy.Environment()
    bus = MessageBus(env, random.Random(1), latency=0.0)
    agents = [Inbox(f"x{i}") for i in range(3)]
    for ag in agents:
        bus.register(ag, zone="0")
    bus.send(Message("x0", "zone:0", "INFORM", "t"))
    env.run(until=1)
    assert [len(ag.got) for ag in agents] == [0, 1, 1]


def test_bus_loss_drops_messages():
    env = simpy.Environment()
    bus = MessageBus(env, random.Random(3), latency=0.0, loss=0.5)
    a, b = Inbox("a"), Inbox("b")
    bus.register(a)
    bus.register(b)
    for _ in range(1000):
        bus.send(Message("a", "b", "INFORM", "t"))
    env.run(until=1)
    assert 400 < len(b.got) < 600
    assert bus.dropped == 1000 - len(b.got)
