"""Traffic demand: Poisson arrivals with a time-varying rate and an origin-destination matrix."""
from __future__ import annotations

import bisect
import itertools
import random
from typing import TYPE_CHECKING

from trafficmas.agents.vehicle import PROFILES

if TYPE_CHECKING:
    from trafficmas.sim.engine import Simulation

# (time s, rate multiplier) points, linearly interpolated
RATE_PROFILES = {
    "constant": [(0.0, 1.0)],
    "rush_hour": [(0.0, 0.6), (900.0, 1.0), (1800.0, 1.35), (2700.0, 1.0), (3600.0, 0.6)],
}


def profile_value(points: list[tuple[float, float]], t: float) -> float:
    if t <= points[0][0]:
        return points[0][1]
    for (t0, v0), (t1, v1) in itertools.pairwise(points):
        if t <= t1:
            return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
    return points[-1][1]


class DemandGenerator:
    """Spawns vehicles between gateways.

    `rate` is the mean number of vehicles per hour over the whole network, modulated
    by the rate profile. The OD matrix is uniform between gateways, trips between
    gateways on the same side are rarer, and `od_bias` entries such as
    {from: W, to: E, factor: 2} make some directions busier (e.g. the morning commute).
    Explicit `od_pairs` ([origin, destination, weight]) replace the generated matrix.
    """

    def __init__(self, sim: Simulation, rng: random.Random, rate: float, duration: float,
                 profile: str | list = "constant", od_bias: list[dict] | None = None,
                 od_pairs: list[list] | None = None, same_side_weight: float = 0.2,
                 profiles: dict[str, float] | None = None) -> None:
        self.sim = sim
        self.rng = rng
        self.rate = rate / 3600.0
        self.duration = duration
        self.points = RATE_PROFILES[profile] if isinstance(profile, str) else [tuple(p) for p in profile]
        self.peak = max(v for _, v in self.points)
        self.driver_profiles = profiles or {"conservative": 0.3, "normal": 0.5, "aggressive": 0.2}
        unknown_profiles = set(self.driver_profiles) - set(PROFILES)
        if unknown_profiles:
            raise ValueError(f"unknown driver profiles {sorted(unknown_profiles)}; known: {sorted(PROFILES)}")
        pairs: list[tuple[str, str, float]] = []
        if od_pairs:
            pairs = [(str(o), str(d), float(w)) for o, d, w in od_pairs]
            unknown = {n for o, d, _ in pairs for n in (o, d)} - set(sim.net.nodes)
            if unknown:
                raise ValueError(f"od_pairs name unknown nodes: {sorted(unknown)}")
        else:
            gws = sim.net.gateways
            for o in gws:
                for d in gws:
                    if o is d:
                        continue
                    w = same_side_weight if (o.side and o.side == d.side) else 1.0
                    for b in od_bias or []:
                        if o.side == b["from"] and d.side == b["to"]:
                            w *= float(b["factor"])
                    pairs.append((o.id, d.id, w))
        if not pairs or sum(w for _, _, w in pairs) <= 0:
            raise ValueError("the origin-destination matrix is empty")
        self.pairs = pairs
        self.cum = list(itertools.accumulate(w for _, _, w in pairs))
        names = list(self.driver_profiles)
        self.profile_names = names
        self.profile_cum = list(itertools.accumulate(self.driver_profiles[n] for n in names))
        self.count = 0

    def pick_od(self) -> tuple[str, str]:
        x = self.rng.random() * self.cum[-1]
        o, d, _ = self.pairs[bisect.bisect_right(self.cum, x)]
        return o, d

    def pick_profile(self) -> str:
        x = self.rng.random() * self.profile_cum[-1]
        return self.profile_names[min(len(self.profile_names) - 1, bisect.bisect_right(self.profile_cum, x))]

    def run(self, env):
        lam = self.rate * self.peak
        if lam <= 0:
            return
        while True:
            yield env.timeout(self.rng.expovariate(lam))
            if env.now >= self.duration:
                return
            if self.rng.random() * self.peak > profile_value(self.points, env.now):
                continue   # thinning: accept with probability rate(t) / peak rate
            o, d = self.pick_od()
            profile = self.pick_profile()
            self.count += 1
            self.sim.spawn_vehicle(f"v{self.count}", o, d, profile)
