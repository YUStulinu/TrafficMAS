"""Regression snapshot and CPU timing of the simulator, for speed-ups that must not change any result.

`snapshot` runs every configuration of the experiments in experiments/ (scenario x variant, each
distinct one once) and stores a hash of everything a run records: the summary, every trip, every
queue sample and the waits per approach. `--compare` checks the runs against an older snapshot, to
the last bit, and reports the CPU time. `time` runs the 16 standard configurations (4 scenarios x
4 controllers) one at a time, which is the precise way to measure CPU time.

    python scripts/benchmark.py snapshot before.json
    python scripts/benchmark.py snapshot after.json --compare before.json
    python scripts/benchmark.py time --repeat 3 --out after_time.json --compare before_time.json

To measure another version of the code, run the script with PYTHONPATH set to that checkout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from trafficmas.config import ROOT, load_scenario, load_yaml
from trafficmas.experiments.runner import expand
from trafficmas.sim.engine import Simulation

TIMED_SCENARIOS = ["grid_light", "grid_rush_hour", "grid_heavy", "craiova_center"]
TIMED_CONTROLLERS = ["fixed", "actuated", "max_pressure", "negotiation_coord"]


def _job(scenario: str, controller: str, params: dict, overrides: dict, seed: int, name: str) -> dict:
    key = json.dumps([scenario, controller, params, overrides, seed], sort_keys=True)
    return {"scenario": scenario, "controller": controller, "params": params, "overrides": overrides,
            "seed": seed, "key": key, "name": name}


def configurations(seeds: int, only: list[str]) -> list[dict]:
    """Every distinct (scenario, controller, params, overrides, seed) of the experiments."""
    jobs, seen = [], set()
    for path in sorted((ROOT / "experiments").glob("*.yaml")):
        cfg = load_yaml(path)
        cfg["seeds"] = seeds
        for j in expand(cfg):
            name = f"{Path(j['scenario']).stem}/{cfg['name']}:{j['label']}/seed{j['seed']}"
            job = _job(j["scenario"], j["controller"], j["params"], j["overrides"], j["seed"], name)
            if job["key"] not in seen and (not only or any(s in name for s in only)):
                seen.add(job["key"])
                jobs.append(job)
    return jobs


def timed_configurations(only: list[str]) -> list[dict]:
    return [_job(f"scenarios/{s}.yaml", c, {}, {}, 1, f"{s}/{c}")
            for s in TIMED_SCENARIOS for c in TIMED_CONTROLLERS if not only or any(o in f"{s}/{c}" for o in only)]


def run(job: dict) -> dict:
    sim = Simulation(load_scenario(job["scenario"]), job["controller"], seed=job["seed"],
                     controller_params=job["params"], overrides=job["overrides"], base_dir=ROOT)
    t0 = time.process_time()
    summary = sim.run()
    cpu = time.process_time() - t0
    del summary["wall_time"]
    m = sim.metrics
    record = repr((summary, m.trips, m.ev_trips, m.samples, sorted(m.approach_wait.items())))
    return {"name": job["name"], "key": job["key"], "hash": hashlib.sha256(record.encode()).hexdigest(), "cpu": cpu}


def compare(rows: list[dict], old_path: Path, per_run: bool) -> int:
    """Print what changed against an older file of rows; 1 if any result differs."""
    old = {r["key"]: r for r in json.loads(old_path.read_text(encoding="utf-8"))}
    both = [r for r in rows if r["key"] in old]
    if not both:
        print(f"no run in common with {old_path.name}: nothing compared")
        return 1
    changed = [r["name"] for r in both if r["hash"] != old[r["key"]]["hash"]]
    if per_run:
        print(f"{'run':40} {'before s':>9} {'after s':>9} {'saved':>7}")
        for r in both:
            b = old[r["key"]]["cpu"]
            print(f"{r['name']:40} {b:9.2f} {r['cpu']:9.2f} {1 - r['cpu'] / b:7.1%}")
    cpu_old = sum(old[r["key"]]["cpu"] for r in both)
    cpu_new = sum(r["cpu"] for r in both)
    print(f"{len(both) - len(changed)}/{len(both)} runs identical to {old_path.name}; "
          f"CPU {cpu_old:.1f} s -> {cpu_new:.1f} s ({1 - cpu_new / max(cpu_old, 1e-9):.1%} saved)")
    for name in changed:
        print(f"  DIFFERENT: {name}")
    return 1 if changed else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    snap = sub.add_parser("snapshot", help="every experiment configuration, in parallel")
    snap.add_argument("out", type=Path)
    snap.add_argument("--seeds", type=int, default=1)
    snap.add_argument("--only", default="", help="comma-separated parts of run names to keep")
    snap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    snap.add_argument("--compare", type=Path)
    tim = sub.add_parser("time", help="the 16 standard configurations, one at a time")
    tim.add_argument("--repeat", type=int, default=3, help="the fastest of this many runs counts")
    tim.add_argument("--only", default="", help="comma-separated parts of run names to keep")
    tim.add_argument("--out", type=Path)
    tim.add_argument("--compare", type=Path)
    args = ap.parse_args(argv)
    only = [s for s in args.only.split(",") if s]

    if args.cmd == "snapshot":
        jobs = configurations(args.seeds, only)
        print(f"{len(jobs)} runs on {args.workers} processes", flush=True)
        t0 = time.perf_counter()
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            rows = list(pool.map(run, jobs, chunksize=1))
        print(f"done in {time.perf_counter() - t0:.0f} s")
    else:
        rows = []
        for job in timed_configurations(only):
            runs = [run(job) for _ in range(args.repeat)]
            if len({r["hash"] for r in runs}) != 1:
                print(f"{job['name']}: repeated runs differ, the simulation is not deterministic")
                return 1
            rows.append(min(runs, key=lambda r: r["cpu"]))
            print(f"{job['name']:40} {rows[-1]['cpu']:7.2f} s", flush=True)
    out = getattr(args, "out", None)
    if out is not None:
        out.write_text(json.dumps(rows, indent=1), encoding="utf-8")
    if args.compare is not None:
        return compare(rows, args.compare, per_run=args.cmd == "time")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
