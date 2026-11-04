"""Command line interface.

    python -m trafficmas run scenarios/grid_rush_hour.yaml --controller negotiation_coord --live
    python -m trafficmas compare scenarios/grid_heavy.yaml --seeds 3
    python -m trafficmas experiment experiments/main.yaml
    python -m trafficmas analyze results/main
    python -m trafficmas list
"""
from __future__ import annotations

import argparse
import json
import statistics

import yaml

from trafficmas.config import ROOT, load_scenario
from trafficmas.control import CONTROLLERS
from trafficmas.sim.engine import Simulation

SHOWN = [("completed", "completed", "{:.0f}"), ("unfinished", "unfinished", "{:.0f}"),
         ("avg_time_in_system", "time in system (s)", "{:.1f}"), ("avg_wait_time", "wait (s)", "{:.1f}"),
         ("avg_queue", "queue (veh)", "{:.2f}"), ("spillback_link_s", "spillback (link-s)", "{:.0f}"),
         ("jain_fairness", "fairness", "{:.3f}"), ("co2_g_per_trip", "CO2/trip (g)", "{:.0f}"),
         ("ev_response_time", "ambulance (s)", "{:.1f}"), ("messages_per_agent_min", "msgs/agent/min", "{:.1f}")]


def parse_assignments(items: list[str] | None) -> dict:
    """key=value pairs; dotted keys build nested dicts (bus.latency=0.5)."""
    out: dict = {}
    for item in items or []:
        key, _, value = item.partition("=")
        node = out
        parts = key.split(".")
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = yaml.safe_load(value)
    return out


def cmd_run(args) -> None:
    scenario = load_scenario(args.scenario)
    sim = Simulation(scenario, args.controller, seed=args.seed, controller_params=parse_assignments(args.param),
                     overrides=parse_assignments(args.set), base_dir=ROOT)
    if args.live or args.record:
        from trafficmas.viz.live import LiveView
        view = LiveView(sim, speed=args.speed, record=args.record, record_seconds=args.record_seconds,
                        headless=bool(args.record and not args.live), start_at=args.start_at)
        summary = view.run()
    else:
        summary = sim.run()
    if args.json:
        print(json.dumps(summary, indent=2))
        return
    print(f"{sim.name} | controller={sim.controller_name} | seed={sim.seed} | "
          f"simulated {summary['sim_time'] / 60:.0f} min in {summary['wall_time']:.1f} s")
    for key, label, f in SHOWN:
        v = summary.get(key)
        if v is not None and v == v:
            print(f"  {label:22s} {f.format(v)}")


def cmd_compare(args) -> None:
    scenario = load_scenario(args.scenario)
    controllers = args.controllers or list(CONTROLLERS)
    cols = [("avg_time_in_system", "time in system"), ("avg_wait_time", "wait"), ("avg_queue", "queue"),
            ("spillback_link_s", "spillback"), ("jain_fairness", "fairness"), ("ev_response_time", "ambulance"),
            ("messages_per_agent_min", "msgs/agent/min")]
    print(f"{scenario.get('name')} - mean over {args.seeds} seeds")
    print(f"{'controller':18s}" + "".join(f"{c[1]:>16s}" for c in cols))
    for c in controllers:
        res = [Simulation(scenario, c, seed=s, base_dir=ROOT).run() for s in range(1, args.seeds + 1)]
        cells = []
        for key, _ in cols:
            vals = [r[key] for r in res if r.get(key) == r.get(key)]
            cells.append(f"{statistics.fmean(vals):16.2f}" if vals else f"{'-':>16s}")
        print(f"{c:18s}" + "".join(cells), flush=True)


def cmd_experiment(args) -> None:
    from trafficmas.experiments import analyze, run_experiment
    out = run_experiment(args.experiment, workers=args.workers, seeds=args.seeds)
    analyze(out, docs_dir=args.docs)


def cmd_analyze(args) -> None:
    from trafficmas.experiments import analyze
    analyze(args.results, docs_dir=args.docs)


def cmd_list(_args) -> None:
    print("controllers:", ", ".join(CONTROLLERS))
    print("scenarios:")
    for p in sorted((ROOT / "scenarios").glob("*.yaml")):
        print("  ", p.relative_to(ROOT).as_posix())
    print("experiments:")
    for p in sorted((ROOT / "experiments").glob("*.yaml")):
        print("  ", p.relative_to(ROOT).as_posix())


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="trafficmas", description="TrafficMAS+: negotiating traffic lights")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="run one simulation")
    r.add_argument("scenario")
    r.add_argument("--controller", "-c", default="negotiation_coord", choices=list(CONTROLLERS))
    r.add_argument("--seed", type=int, default=1)
    r.add_argument("--param", "-p", action="append", help="controller parameter, e.g. -p credits=false")
    r.add_argument("--set", "-s", action="append", help="scenario override, e.g. -s demand.rate=9000")
    r.add_argument("--live", action="store_true", help="open the Pygame view")
    r.add_argument("--speed", type=float, default=8.0, help="simulated seconds per real second in the live view")
    r.add_argument("--record", help="save a GIF of the live view (runs headless unless --live)")
    r.add_argument("--record-seconds", type=float, default=120.0)
    r.add_argument("--start-at", type=float, default=0.0, help="simulate this many seconds before showing")
    r.add_argument("--json", action="store_true", help="print the full summary as JSON")
    r.set_defaults(func=cmd_run)

    c = sub.add_parser("compare", help="all controllers on one scenario, averaged over seeds")
    c.add_argument("scenario")
    c.add_argument("--seeds", type=int, default=3)
    c.add_argument("--controllers", nargs="*")
    c.set_defaults(func=cmd_compare)

    e = sub.add_parser("experiment", help="run an experiment file and analyse it")
    e.add_argument("experiment")
    e.add_argument("--workers", type=int)
    e.add_argument("--seeds", type=int, help="override the number of seeds")
    e.add_argument("--docs", help="write the figures to this folder instead of the results folder")
    e.set_defaults(func=cmd_experiment)

    a = sub.add_parser("analyze", help="statistics and figures for finished runs")
    a.add_argument("results")
    a.add_argument("--docs")
    a.set_defaults(func=cmd_analyze)

    lst = sub.add_parser("list", help="list controllers, scenarios and experiments")
    lst.set_defaults(func=cmd_list)

    args = ap.parse_args(argv)
    args.func(args)
