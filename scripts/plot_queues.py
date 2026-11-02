"""Queued vehicles over time for each controller on one scenario (docs/rush_hour_queues.png).

The curves are 2-minute moving averages of the 10-second samples.

    python scripts/plot_queues.py scenarios/grid_rush_hour.yaml --seed 1 --out docs/rush_hour_queues.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

from trafficmas.config import ROOT, load_scenario
from trafficmas.control import CONTROLLERS
from trafficmas.sim.engine import Simulation
from trafficmas.viz.plots import time_series


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario", nargs="?", default="scenarios/grid_rush_hour.yaml")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", default="docs/rush_hour_queues.png")
    args = ap.parse_args()
    scenario = load_scenario(args.scenario)
    series = {}
    for name in [c for c in CONTROLLERS if c != "negotiation"]:   # same curve as negotiation_coord here
        sim = Simulation(scenario, name, seed=args.seed, base_dir=ROOT)
        sim.run()
        samples = sim.metrics.samples
        q = [s["queued"] for s in samples]
        smooth = [sum(q[max(0, i - 11):i + 1]) / len(q[max(0, i - 11):i + 1]) for i in range(len(q))]
        series[name] = ([s["t"] / 60 for s in samples], smooth)
    time_series(series, "vehicles queued at traffic lights", f"{scenario['name']}: queues over time (seed {args.seed})",
                Path(args.out))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
