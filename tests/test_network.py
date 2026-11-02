from pathlib import Path

from trafficmas.network.braess import build_braess
from trafficmas.network.grid import build_grid
from trafficmas.network.osm import build_osm
from trafficmas.network.road import VEHICLE_SPACING

ROOT = Path(__file__).resolve().parent.parent


def test_grid_shape(grid):
    assert len(grid.signalized) == 9
    assert len(grid.gateways) == 12
    # every interior junction has 4 approaches and 4 * 3 movements (no U-turns)
    node = grid.nodes["n1_1"]
    assert len(grid.in_links("n1_1")) == 4
    assert len(node.movements) == 12
    assert all(m.outbound.v != m.inbound.u for m in node.movements)


def test_two_phases_split_by_axis(grid):
    node = grid.nodes["n1_1"]
    assert len(node.phases) == 2
    for phase in node.phases:
        bearings = {round(m.inbound.bearing) % 180 for m in phase}
        assert len(bearings) == 1   # one phase per road axis


def test_left_turn_phases():
    net = build_grid(rows=3, cols=3, left_turn_phases=True)
    phases = net.nodes["n1_1"].phases
    assert len(phases) == 4
    assert any(all(m.turn == "left" for m in ph) for ph in phases)


def test_turn_classification(grid):
    node = grid.nodes["n1_1"]
    m = {(mv.inbound.u, mv.outbound.v): mv.turn for mv in node.movements}
    # coming from the west (n1_0), going east is through, north is left, south is right
    assert m[("n1_0", "n1_2")] == "through"
    assert m[("n1_0", "n2_1")] == "left"
    assert m[("n1_0", "n0_1")] == "right"


def test_link_storage_and_free_time(grid):
    link = grid.link("n1_1", "n1_2")
    assert link.storage == int(200 * 2 / VEHICLE_SPACING)
    assert abs(link.free_time - 200 / 13.9) < 1e-9


def test_arterials_get_more_lanes():
    net = build_grid(rows=3, cols=3, arterial_rows=(1,), arterial_lanes=3)
    assert net.link("n1_0", "n1_1").lanes == 3
    assert net.link("n0_0", "n0_1").lanes == 2


def test_braess_shortcut_toggle():
    with_sc = build_braess(shortcut=True)
    without = build_braess(shortcut=False)
    assert "A->B" in with_sc.links and "A->B" not in without.links
    assert with_sc.links["S->A"].sat_cap < with_sc.links["S->B"].sat_cap


def test_osm_network_loads():
    net = build_osm(ROOT / "data" / "craiova_center.json")
    assert len(net.signalized) > 10
    assert len(net.gateways) > 4
    assert all(link.storage >= 3 for link in net.links.values())
