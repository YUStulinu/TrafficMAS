"""The classic Braess network, used to measure the price of selfish rerouting.

    S --(bottleneck)--> A --(long road)---------------> E
    S --(long road)---> B --(bottleneck)--> X --------> E
                 A --(shortcut)--> B          (only when shortcut=True)

Both routes S-A-E and S-B-X-E combine one short bottleneck with one long, wide
road. With the shortcut, every selfish driver prefers S-A-B-X-E, which uses both
bottlenecks, and the average travel time can get worse for everybody. The node X
only exists so that the second bottleneck is served by a junction (vehicles leave
the network at a gateway without queueing).
"""
from __future__ import annotations

from trafficmas.network.road import RoadNetwork


def build_braess(shortcut: bool = True, bottleneck_length: float = 300.0, long_length: float = 1800.0,
                 bottleneck_capacity: float = 0.5, name: str = "braess") -> RoadNetwork:
    net = RoadNetwork(name if shortcut else f"{name}_no_shortcut")
    net.add_node("S", 0.0, 0.0, gateway=True, side="W", signalized=False)
    net.add_node("A", 500.0, 400.0, signalized=False)
    net.add_node("B", 500.0, -400.0, signalized=False)
    net.add_node("X", 900.0, -250.0, signalized=False)
    net.add_node("E", 1300.0, 0.0, gateway=True, side="E", signalized=False)
    net.add_link("S", "A", lanes=1, speed=13.9, length=bottleneck_length, road_class="bottleneck")
    net.add_link("B", "X", lanes=1, speed=13.9, length=bottleneck_length, road_class="bottleneck")
    net.add_link("X", "E", lanes=2, speed=13.9, length=100.0, road_class="arterial")
    net.add_link("S", "B", lanes=2, speed=13.9, length=long_length, road_class="arterial")
    net.add_link("A", "E", lanes=2, speed=13.9, length=long_length, road_class="arterial")
    if shortcut:
        net.add_link("A", "B", lanes=2, speed=16.7, length=150.0, road_class="arterial")
    net.finalize()
    for link in net.links.values():
        if link.road_class == "bottleneck":
            link.capacity_factor = bottleneck_capacity
    return net
