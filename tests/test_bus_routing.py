import random

import simpy

from trafficmas.bus.bus import MessageBus
from trafficmas.contracts import Message
from trafficmas.routing.router import Router, TrafficInfoBoard


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


def test_router_shortest_route(grid):
    router = Router(grid, TrafficInfoBoard())
    path, t = router.route_from_origin("W1", "E1", 0.0)
    assert [link.v for link in path] == ["n1_0", "n1_1", "n1_2", "E1"]
    assert abs(t - sum(link.free_time for link in path)) < 1e-9


def test_router_avoids_congestion_and_closures(grid):
    board = TrafficInfoBoard()
    router = Router(grid, board)
    board.publish({"n1_0->n1_1": 500.0}, 0.0)
    path, _ = router.route_from_origin("W1", "E1", 0.0)
    assert "n1_0->n1_1" not in [link.id for link in path]
    board.publish({"n1_0->n1_1": 0.0}, 0.0)
    grid.link("n1_1", "n1_2").closed = True
    path, _ = router.route_from_origin("W1", "E1", 0.0)
    assert "n1_1->n1_2" not in [link.id for link in path]


def test_router_delay_fades_with_time(grid):
    board = TrafficInfoBoard()
    router = Router(grid, board, horizon=100.0)
    link = grid.link("n1_1", "n1_2")
    board.publish({link.id: 60.0}, 0.0)
    assert router.predicted_delay(link, 0.0) == 60.0
    assert router.predicted_delay(link, 50.0) == 30.0
    assert router.predicted_delay(link, 150.0) == 0.0


def test_router_respects_no_u_turn(grid):
    router = Router(grid, TrafficInfoBoard())
    start = grid.link("n1_0", "n1_1")
    path, _ = router.route([(start, 0.0)], "W1")
    assert path[1].v != "n1_0"   # no U-turn straight back


def test_router_picks_the_faster_of_two_direct_start_links(grid):
    router = Router(grid, TrafficInfoBoard())
    slow, fast = grid.link("n1_0", "n1_1"), grid.link("n1_2", "n1_1")
    path, t = router.route([(slow, 50.0), (fast, 10.0)], "n1_1")
    assert path == [fast] and t == 10.0
