"""Collects trip records and network samples, and turns them into the evaluation metrics."""
from __future__ import annotations

import statistics
from typing import TYPE_CHECKING

from trafficmas.network.road import Link

if TYPE_CHECKING:
    from trafficmas.agents.vehicle import Vehicle
    from trafficmas.sim.engine import Simulation

# Simple CO2 estimate for a petrol passenger car in urban traffic.
CO2_G_PER_M = 0.15        # 150 g/km while driving
CO2_G_PER_S_IDLE = 0.5    # idling at a stop line
CO2_G_PER_STOP = 10.0     # extra fuel to accelerate again after a stop


def jain_index(values: list[float]) -> float:
    """Jain's fairness index: 1 when all values are equal, 1/n when one gets everything."""
    values = [v for v in values if v >= 0]
    if not values or sum(values) == 0:
        return 1.0
    return sum(values) ** 2 / (len(values) * sum(v * v for v in values))


def co2_grams(distance: float, wait: float, stops: int) -> float:
    return CO2_G_PER_M * distance + CO2_G_PER_S_IDLE * wait + CO2_G_PER_STOP * stops


class MetricsCollector:
    def __init__(self, sim: Simulation, sample_interval: float = 10.0) -> None:
        self.sim = sim
        self.sample_interval = sample_interval
        self.trips: list[dict] = []
        self.ev_trips: list[dict] = []
        self.active: dict[str, Vehicle] = {}
        self.spawned = 0
        self.blocked_events = 0
        self.corridor_served = 0
        self.corridor_conflicts = 0
        self.approach_wait: dict[str, list[float]] = {}
        self.samples: list[dict] = []
        self.link_queue_sum: dict[str, float] = {}
        self.spill_link_samples = 0
        self.co2_g = 0.0

    # ------------------------------------------------------------------ events
    def vehicle_spawned(self, v: Vehicle) -> None:
        self.spawned += 1
        self.active[v.id] = v

    def vehicle_done(self, v: Vehicle, now: float) -> None:
        self.active.pop(v.id, None)
        rec = {"id": v.id, "origin": v.origin, "dest": v.dest, "depart": v.depart, "arrive": now,
               "travel_time": now - v.depart, "wait_time": v.wait, "stops": v.stops,
               "distance": v.distance, "free_flow": v.free_flow, "delay": now - v.depart - v.free_flow,
               "reroutes": v.reroutes, "profile": v.profile}
        self.co2_g += co2_grams(v.distance, v.wait, v.stops)
        if v.is_emergency:
            rec.update(priority=v.priority, rejections=v.rejections, replans=v.replans)
            self.ev_trips.append(rec)
        else:
            self.trips.append(rec)

    def discharged(self, link: Link, wait: float) -> None:
        acc = self.approach_wait.setdefault(link.id, [0.0, 0])
        acc[0] += wait
        acc[1] += 1

    # ------------------------------------------------------------------ sampling
    def sampler(self, env):
        net = self.sim.net
        approaches = [link for link in net.links.values() if link.queues and net.nodes[link.v].signalized]
        while True:
            queued = 0
            max_q = 0
            spill = 0
            for link in approaches:
                q = link.queued
                queued += q
                max_q = max(max_q, q)
                self.link_queue_sum[link.id] = self.link_queue_sum.get(link.id, 0.0) + q
            for link in net.links.values():
                if link.queues and link.occupancy >= 0.95 * link.storage:
                    spill += 1
            self.spill_link_samples += spill
            self.samples.append({"t": env.now, "queued": queued, "mean_queue": queued / max(1, len(approaches)),
                                 "max_queue": max_q, "in_network": len(self.active), "spill_links": spill,
                                 "completed": len(self.trips)})
            yield env.timeout(self.sample_interval)

    # ------------------------------------------------------------------ results
    def summary(self) -> dict:
        sim = self.sim
        end = sim.env.now
        trips = self.trips
        tt = [t["travel_time"] for t in trips]
        unfinished = [v for v in self.active.values() if not v.is_emergency]
        in_system = tt + [end - v.depart for v in unfinished]
        co2 = self.co2_g + sum(co2_grams(v.distance, v.wait, v.stops) for v in self.active.values())
        waits = [s / n for s, n in self.approach_wait.values() if n >= 5]
        n_samples = max(1, len(self.samples))
        n_agents = len(sim.agents) + len(sim.coordinators)
        minutes = max(1.0, end / 60.0)
        evs = self.ev_trips
        ev_unfinished = [v for v in self.active.values() if v.is_emergency]

        def mean(xs):
            return statistics.fmean(xs) if xs else float("nan")

        out = {
            "spawned": self.spawned,
            "completed": len(trips),
            "unfinished": len(unfinished),
            "completion_rate": len(trips) / max(1, len(trips) + len(unfinished)),
            "avg_travel_time": mean(tt),
            "p95_travel_time": sorted(tt)[int(0.95 * (len(tt) - 1))] if tt else float("nan"),
            "avg_wait_time": mean([t["wait_time"] for t in trips]),
            "avg_delay": mean([t["delay"] for t in trips]),
            "avg_stops": mean([t["stops"] for t in trips]),
            "avg_time_in_system": mean(in_system),
            "total_time_in_system": sum(in_system),
            "throughput_vph": len(trips) / (end / 3600.0) if end > 0 else 0.0,
            "avg_queue": mean([s["mean_queue"] for s in self.samples]),
            "max_queue": max((s["max_queue"] for s in self.samples), default=0),
            "spillback_link_s": self.spill_link_samples * self.sample_interval,
            "blocked_events": self.blocked_events,
            "jain_fairness": jain_index(waits),
            "co2_kg": co2 / 1000.0,
            "co2_g_per_trip": co2 / max(1, len(trips) + len(unfinished)),
            "avg_reroutes": mean([t["reroutes"] for t in trips]),
            "messages": sim.bus.sent,
            "messages_dropped": sim.bus.dropped,
            "messages_per_agent_min": sim.bus.sent / n_agents / minutes,
            "ev_count": len(evs) + len(ev_unfinished),
            "ev_completed": len(evs),
            "ev_response_time": mean([t["travel_time"] for t in evs]),
            "ev_delay": mean([t["delay"] for t in evs]),
            "ev_rejections": sum(t["rejections"] for t in evs),
            "corridor_served": self.corridor_served,
            "corridor_conflicts": self.corridor_conflicts,
            "sim_time": end,
            "n_samples": n_samples,
        }
        for topic, n in sorted(sim.bus.by_topic.items()):
            out[f"msg_{topic}"] = n
        agg: dict[str, float] = {}
        for agent in sim.agents.values():
            if agent.controller is not None:
                for k, v in agent.controller.stats().items():
                    agg[k] = agg.get(k, 0) + v
        for k, v in agg.items():
            out[f"neg_{k}"] = v
        return out
