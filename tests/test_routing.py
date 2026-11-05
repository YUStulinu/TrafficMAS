"""Time-dependent A* routing (part 3)."""
from trafficmas.routing.router import Router, TrafficInfoBoard


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
