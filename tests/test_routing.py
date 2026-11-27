"""Time-dependent A* routing and the traffic information board (part 3)."""
import heapq
import math
import random
from pathlib import Path

import pytest

from trafficmas.network.braess import build_braess
from trafficmas.network.grid import build_grid
from trafficmas.network.osm import build_osm
from trafficmas.network.road import RoadNetwork
from trafficmas.routing.router import AHEAD, SLOT, Router, TrafficInfoBoard, _round6

ROOT = Path(__file__).resolve().parent.parent


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
    assert router.link_cost(link, 0.0) - link.free_time == pytest.approx(60.0)
    assert router.link_cost(link, 50.0) - link.free_time == pytest.approx(30.0)
    assert router.link_cost(link, 150.0) - link.free_time == pytest.approx(0.0)


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


# ------------------------------------------------------------------ A* against an exhaustive reference
def random_network(rng: random.Random, n: int = 14) -> RoadNetwork:
    """Random directed network whose link lengths have nothing to do with the node coordinates."""
    net = RoadNetwork("random")
    for i in range(n):
        net.add_node(f"x{i}", rng.uniform(0, 1000), rng.uniform(0, 1000), gateway=i < 4)
    pairs = sorted((a, b) for a in range(n) for b in range(n) if a != b)
    for a, b in rng.sample(pairs, 3 * n):
        net.add_link(f"x{a}", f"x{b}", lanes=rng.choice([1, 2, 3]), speed=rng.choice([8.0, 13.9, 16.7, 25.0]),
                     length=rng.uniform(20, 900))
    return net.finalize()


def reference(router: Router, starts, dest, speed_factor=1.0, delay_weight=1.0):
    """Plain Dijkstra over links with the router's cost function and no heuristic."""
    best = {link.id: t for link, t in starts}
    heap = [(t, link.id) for link, t in starts]
    heapq.heapify(heap)
    while heap:
        t, lid = heapq.heappop(heap)
        if t > best[lid]:
            continue
        if router.net.links[lid].v == dest:
            return t
        for nxt in router.next_links[lid]:
            if nxt.closed:
                continue
            t2 = t + router.link_cost(nxt, t, speed_factor, delay_weight)
            if t2 < best.get(nxt.id, math.inf):
                best[nxt.id] = t2
                heapq.heappush(heap, (t2, nxt.id))
    return None


@pytest.mark.parametrize("seed", range(40))
def test_astar_is_optimal_on_random_networks(seed):
    rng = random.Random(seed)
    net = random_network(rng)
    board = TrafficInfoBoard()
    router = Router(net, board, horizon=600.0)
    for _ in range(12):
        # reported delays below the horizon keep the costs first-in-first-out, where Dijkstra is exact
        board.publish({lid: rng.uniform(0, 500) for lid in rng.sample(sorted(net.links), 10)}, rng.uniform(0, 300))
        for link in rng.sample(list(net.links.values()), 3):
            link.closed = rng.random() < 0.5
        now = rng.uniform(300, 900)
        origin, dest = rng.sample(sorted(net.nodes), 2)
        sf, dw = rng.choice([1.0, 1.25]), rng.choice([0.0, 0.3, 1.0])
        starts = [(link, now + router.link_cost(link, now, sf, dw))
                  for link in net.out_links(origin) if not link.closed]
        res = router.route(starts, dest, sf, dw)
        expected = reference(router, starts, dest, sf, dw)
        if expected is None:
            assert res is None
            continue
        path, arrival = res
        assert arrival == pytest.approx(expected, abs=1e-4)      # labels are compared to the microsecond
        assert path[0].u == origin and path[-1].v == dest
        assert not any(link.closed for link in path)
        for a, b in zip(path, path[1:], strict=False):
            assert a.v == b.u and b.v != a.u            # connected, no U-turn
        t = next(t for link, t in starts if link is path[0])
        for link in path[1:]:
            t += router.link_cost(link, t, sf, dw)
        assert t == pytest.approx(arrival, abs=1e-6)     # the reported arrival time is the cost of the path


@pytest.mark.parametrize("name", ["grid", "braess", "braess_no_shortcut", "craiova"])
def test_heuristic_is_the_exact_free_flow_time_on_every_network(name):
    """A straight-line heuristic overestimates on Braess, whose links are shorter than the drawn distance."""
    net = {"grid": lambda: build_grid(rows=4, cols=4, arterial_rows=(1,), arterial_cols=(2,)),
           "braess": build_braess, "braess_no_shortcut": lambda: build_braess(shortcut=False),
           "craiova": lambda: build_osm(ROOT / "data" / "craiova_center.json")}[name]()
    router = Router(net, TrafficInfoBoard())
    rng = random.Random(1)
    for dest in [n.id for n in net.gateways]:
        rem = router.remaining(dest)
        for link in rng.sample(list(net.links.values()), min(25, len(net.links))):
            expected = reference(router, [(link, 0.0)], dest)
            if expected is None:
                assert link.id not in rem
            else:
                assert rem[link.id] == pytest.approx(expected, abs=1e-9)


def test_braess_free_flow_route_uses_the_shortcut():
    router = Router(build_braess(), TrafficInfoBoard())
    path, t = router.route_from_origin("S", "E", 0.0)
    assert [link.id for link in path] == ["S->A", "A->B", "B->X", "X->E"]
    assert t == pytest.approx(sum(link.free_time for link in path))


def test_unreachable_destination_returns_none():
    router = Router(build_braess(), TrafficInfoBoard())
    assert router.route_from_origin("E", "S", 0.0) is None     # one-way network


# ------------------------------------------------------------------ announced intentions
def test_board_counts_announcements_and_forgets_them():
    board = TrafficInfoBoard()
    rng = random.Random(3)
    plans = {}
    for step in range(2000):
        vid = f"v{rng.randrange(60)}"
        if rng.random() < 0.3:
            board.release(vid)
            plans.pop(vid, None)
        else:
            plans[vid] = [(f"l{rng.randrange(8)}", rng.uniform(0, 600)) for _ in range(rng.randrange(1, 6))]
            board.book(vid, plans[vid])
        if step % 100 == 0:
            expected = {}
            for plan in plans.values():
                for lid, t in plan:
                    expected[(lid, int(t // SLOT))] = expected.get((lid, int(t // SLOT)), 0) + 1
            assert {k: v for k, v in board.announced.items() if v} == expected
    for vid in list(plans):
        board.release(vid)
    assert not any(board.announced.values()) and not board.plans


def test_announced_vehicles_make_a_link_more_expensive(grid):
    board = TrafficInfoBoard()
    router = Router(grid, board)
    link = grid.link("n1_0", "n1_1")
    base = router.link_cost(link, 100.0)
    board.book("a", [(link.id, 100.0 + link.free_time)])
    board.book("b", [(link.id, 100.0 + link.free_time)])
    rate = link.sat_cap * 0.5                                   # two phases: served half of the time
    assert router.link_cost(link, 100.0) == pytest.approx(base + AHEAD * 2 / rate)
    assert router.link_cost(link, 100.0 + 10 * SLOT) == pytest.approx(base)        # another slot is unaffected
    assert router.link_cost(link, 100.0, delay_weight=0.0) == pytest.approx(base)  # uninformed drivers ignore it
    board.release("a")
    board.release("b")
    assert router.link_cost(link, 100.0) == pytest.approx(base)


def test_board_ignores_late_and_out_of_order_announcements():
    from trafficmas.contracts import Message
    board = TrafficInfoBoard()

    def announce(sent_at, link):
        msg = Message("v1", board.id, "INFORM", "intention", {"plan": [(link, 100.0)]})
        msg.sent_at = sent_at
        board.on_message(msg)

    announce(10.0, "new")
    announce(5.0, "old")                                   # delayed on the bus: must not replace the newer plan
    assert board.plans["v1"] == [("new", int(100.0 // SLOT))]
    board.retire("v1")
    announce(11.0, "late")                                 # arrives after the trip ended
    assert not board.plans and not board.announced


def test_equally_fast_routes_are_shared_between_drivers():
    """Without this, every uninformed driver takes the same one of many equal routes."""
    net = build_grid(rows=4, cols=4)
    router = Router(net, TrafficInfoBoard())
    routes, times = set(), set()
    for seed in range(40):
        path, t = router.route_from_origin("W0", "N3", 0.0, rng=random.Random(seed))
        routes.add(tuple(link.id for link in path))
        times.add(round(t, 6))
    assert len(times) == 1 and len(routes) >= 5        # same travel time, many different routes
    first = router.route_from_origin("W0", "N3", 0.0, rng=random.Random(7))[0]
    again = router.route_from_origin("W0", "N3", 0.0, rng=random.Random(7))[0]
    assert first == again                              # and the choice is reproducible per driver


# ------------------------------------------------------------------ guards of the search speed-ups
# The search is tuned for speed (inlined costs, a faster rounding, pruned heap entries); results must stay exact.

def load_board(rng: random.Random, net: RoadNetwork, board: TrafficInfoBoard) -> None:
    """Random reported delays, announced intentions and closures, as a run produces them."""
    board.publish({lid: rng.uniform(0, 500) for lid in rng.sample(sorted(net.links), 10)}, rng.uniform(0, 300))
    for i in range(60):
        board.book(f"v{i}", [(lid, rng.uniform(300, 1500)) for lid in rng.sample(sorted(net.links), 6)])
    for link in rng.sample(list(net.links.values()), 3):
        link.closed = rng.random() < 0.5
    for link in rng.sample(list(net.links.values()), 10):
        link.capacity_factor = rng.choice([1.0, 0.35, 0.6])     # an incident narrows the road


def random_queries(seed: int, n: int = 10):
    rng = random.Random(seed)
    net = random_network(rng)
    board = TrafficInfoBoard()
    router = Router(net, board)
    for _ in range(n):
        load_board(rng, net, board)
        now = rng.uniform(300, 900)
        origin, dest = rng.sample(sorted(net.nodes), 2)
        sf, dw = rng.choice([1.0, 1.25]), rng.choice([0.0, 0.3, 1.0])
        starts = [(link, now + router.link_cost(link, now, sf, dw))
                  for link in net.out_links(origin) if not link.closed]
        yield router, starts, dest, now, sf, dw


@pytest.mark.parametrize("seed", range(20))
def test_bounded_search_is_the_unbounded_one_cut_at_the_limit(seed):
    """Re-planning stops the search at `limit`: it must return the unbounded answer or nothing, never another route."""
    for router, starts, dest, now, sf, dw in random_queries(seed):
        full = router.route(starts, dest, sf, dw)
        if full is None:
            assert router.route(starts, dest, sf, dw, limit=now + 1e6) is None
            continue
        f = round(full[1], 6)
        for limit in (f - 1.0, f - 1e-6, f, f + 1e-6, f + 50.0):
            assert router.route(starts, dest, sf, dw, limit=limit) == (full if f <= limit else None)


@pytest.mark.parametrize("seed", range(10))
def test_reported_arrival_is_exactly_the_cost_of_the_route(seed):
    """The search inlines link_cost; the inlined arithmetic must give the same doubles, bit for bit."""
    for router, starts, dest, now, sf, dw in random_queries(100 + seed):
        res = router.route(starts, dest, sf, dw)
        if res is None:
            continue
        path, arrival = res
        t = next(t for link, t in starts if link is path[0])
        for link in path[1:]:
            t += router.link_cost(link, t, sf, dw)
        assert t == arrival
        assert router.drive(path, now, sf, dw) == arrival


def test_fast_rounding_is_round():
    """The heap is keyed on round(f, 6) through a faster equivalent, which must agree on every value."""
    rng = random.Random(5)
    values = [rng.uniform(0, 10 ** rng.randint(0, 6)) for _ in range(20000)]
    values += [(k + 0.5) / 1e6 for k in range(0, 10 ** 7, 99991)]          # exactly half-way in decimal
    values += [0.0, -3.25, 1e-7, 5e-7, 123.4565, 1e5 + 5e-7, 2e11, math.inf]
    assert all(_round6(x) == round(x, 6) for x in values)


def test_drive_on_a_closed_link_and_without_delays(grid):
    board = TrafficInfoBoard()
    router = Router(grid, board)
    path = [grid.link("W1", "n1_0"), grid.link("n1_0", "n1_1")]
    board.publish({path[1].id: 100.0}, path[0].free_time)                       # reported as it is entered
    free = path[0].free_time + path[1].free_time
    assert router.drive(path, 0.0, delay_weight=0.0) == pytest.approx(free)        # uninformed: free flow
    assert router.drive(path, 0.0) == pytest.approx(free + 100.0)
    path[1].closed = True
    assert router.drive(path, 0.0) == math.inf                                     # a closed road is never reached
    times = []
    router.drive(path, 0.0, times=times)                                           # an announced plan still lists it
    assert [lid for lid, _ in times] == [link.id for link in path]


def test_astar_expands_far_fewer_links_than_dijkstra(monkeypatch):
    """Efficiency: the exact free-flow heuristic must keep searches well below a plain Dijkstra."""
    import trafficmas.routing.router as router_module
    pops = [0]

    def counting_pop(heap):
        pops[0] += 1
        return heapq.heappop(heap)

    monkeypatch.setattr(router_module, "heapq", type("H", (), {"heappush": heapq.heappush, "heappop": counting_pop}))
    astar = dijkstra = 0
    for seed in range(10):
        for router, starts, dest, _now, sf, dw in random_queries(200 + seed, n=20):
            router.remaining(dest)                    # the heuristic's own reverse search is not part of the query
            pops[0] = 0
            router.route(starts, dest, sf, dw)
            astar += pops[0]
            dijkstra += dijkstra_pops(router, starts, dest, sf, dw)
    assert astar <= 0.7 * dijkstra                  # about 0.3 with delays only, 0.55 with announcements


def dijkstra_pops(router: Router, starts, dest, sf, dw) -> int:
    """Heap pops of `reference` for the same query."""
    best = {link.id: t for link, t in starts}
    heap = [(t, link.id) for link, t in starts]
    heapq.heapify(heap)
    pops = 0
    while heap:
        t, lid = heapq.heappop(heap)
        pops += 1
        if t > best[lid]:
            continue
        if router.net.links[lid].v == dest:
            return pops
        for nxt in router.next_links[lid]:
            if not nxt.closed:
                t2 = t + router.link_cost(nxt, t, sf, dw)
                if t2 < best.get(nxt.id, math.inf):
                    best[nxt.id] = t2
                    heapq.heappush(heap, (t2, nxt.id))
    return pops
