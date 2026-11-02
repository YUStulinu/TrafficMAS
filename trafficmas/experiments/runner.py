"""Experiment runner: scenario x variant x seed, in parallel processes.

An experiment file lists scenarios and variants. A variant is a controller with
optional controller parameters and scenario overrides:

    name: ablation
    seeds: 10
    reference: full
    scenarios: [scenarios/grid_heavy.yaml]
    variants:
      - {label: full, controller: negotiation_coord}
      - {label: no_credits, controller: negotiation_coord, params: {credits: false}}
      - {label: latency_1s, controller: negotiation_coord, overrides: {bus: {latency: 1.0}}}

`controllers: [fixed, actuated]` is a shorthand for variants labelled by controller.
Every run is reproducible from (scenario, variant, seed); results go to
results/<name>/runs.csv, one row per run.
"""
from __future__ import annotations

import csv
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import yaml

from trafficmas.config import ROOT, load_scenario, load_yaml
from trafficmas.sim.engine import Simulation


def expand(cfg: dict) -> list[dict]:
    variants = [dict(v) for v in cfg.get("variants", [])]
    variants += [{"label": c, "controller": c} for c in cfg.get("controllers", [])]
    seeds = cfg.get("seeds", 10)
    seeds = list(range(1, seeds + 1)) if isinstance(seeds, int) else list(seeds)
    jobs = []
    for scen in cfg["scenarios"]:
        for v in variants:
            for seed in seeds:
                jobs.append({"scenario": scen, "label": v["label"], "controller": v["controller"],
                             "params": v.get("params") or {}, "overrides": v.get("overrides") or {},
                             "seed": seed})
    return jobs


def run_job(job: dict) -> dict:
    scenario = load_scenario(job["scenario"])
    sim = Simulation(scenario, job["controller"], seed=job["seed"], controller_params=job["params"],
                     overrides=job["overrides"], base_dir=ROOT)
    row = sim.run()
    row["label"] = job["label"]
    row["scenario_file"] = job["scenario"]
    return row


def run_experiment(path: str | Path, workers: int | None = None, seeds: int | None = None,
                   out_dir: str | Path | None = None) -> Path:
    cfg = load_yaml(path)
    if seeds is not None:
        cfg["seeds"] = seeds
    jobs = expand(cfg)
    out = Path(out_dir) if out_dir else ROOT / "results" / cfg["name"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "experiment.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    workers = workers or max(1, (os.cpu_count() or 2) - 1)
    print(f"{cfg['name']}: {len(jobs)} runs on {workers} processes")
    t0 = time.perf_counter()
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for i, row in enumerate(pool.map(run_job, jobs, chunksize=1), 1):
            rows.append(row)
            if i % max(1, len(jobs) // 10) == 0 or i == len(jobs):
                print(f"  {i}/{len(jobs)} runs done ({time.perf_counter() - t0:.0f} s)", flush=True)
    keys: list[str] = []
    for row in rows:
        for k in row:
            if k not in keys:
                keys.append(k)
    with open(out / "runs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out / 'runs.csv'}")
    return out
