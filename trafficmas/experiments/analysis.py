"""Statistics and figures for an experiment: means with 95% CIs, non-parametric tests, bar charts."""
from __future__ import annotations

import csv
import math
import statistics
import warnings
from pathlib import Path

import yaml
from scipy import stats

from trafficmas.viz.plots import grouped_bars

METRICS = {
    "avg_time_in_system": ("Avg. time in system (s)", "lower"),
    "avg_travel_time": ("Avg. travel time, completed trips (s)", "lower"),
    "avg_wait_time": ("Avg. waiting time (s)", "lower"),
    "avg_queue": ("Avg. queue per approach (veh)", "lower"),
    "max_queue": ("Max. queue (veh)", "lower"),
    "spillback_link_s": ("Spillback (link-seconds)", "lower"),
    "throughput_vph": ("Throughput (veh/h)", "higher"),
    "completion_rate": ("Completed trips (share)", "higher"),
    "jain_fairness": ("Fairness (Jain index)", "higher"),
    "co2_g_per_trip": ("CO2 per trip (g)", "lower"),
    "messages_per_agent_min": ("Messages per agent per minute", "lower"),
    "ev_response_time": ("Ambulance response time (s)", "lower"),
    "ev_delay": ("Ambulance delay vs. free flow (s)", "lower"),
    "disruption_per_ev": ("Extra delay of other traffic per ambulance (veh-s)", "lower"),
    "selfish_node_wait": ("Waiting time at the selfish junction (s)", "lower"),
    "others_wait": ("Waiting time at the other junctions (s)", "lower"),
    "selfish_bid_share": ("Share of won bids taken by the selfish junction", "lower"),
}


def _float(x: str):
    try:
        return float(x)
    except (TypeError, ValueError):
        return x


def load_runs(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [{k: _float(v) for k, v in row.items()} for row in csv.DictReader(f)]


def mean_ci(xs: list[float]) -> tuple[float, float]:
    xs = [x for x in xs if isinstance(x, float) and not math.isnan(x)]
    if not xs:
        return float("nan"), float("nan")
    m = statistics.fmean(xs)
    if len(xs) < 2:
        return m, 0.0
    return m, stats.t.ppf(0.975, len(xs) - 1) * statistics.stdev(xs) / math.sqrt(len(xs))


def holm(pvals: list[float]) -> list[float]:
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj = [1.0] * len(pvals)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvals) - rank) * pvals[i]))
        adj[i] = running
    return adj


def add_paired_disruption(rows: list[dict], suffix: str) -> None:
    """Extra time spent by normal traffic because of the ambulances, per ambulance.

    Each run with ambulances is paired with the run of the same controller, scenario
    and seed without them (label ending in `suffix`); the demand is identical, so the
    difference in total time in the network is caused by the ambulances.
    """
    base = {(r["scenario"], r["label"], r["seed"]): r for r in rows if str(r["label"]).endswith(suffix)}
    for r in rows:
        if str(r["label"]).endswith(suffix):
            continue
        key = (r["scenario"], str(r["label"]).rsplit("/", 1)[0] + suffix, r["seed"])
        b = base.get(key)
        if b and r.get("ev_count"):
            r["disruption_per_ev"] = (r["total_time_in_system"] - b["total_time_in_system"]) / r["ev_count"]


def fmt(m: float, ci: float) -> str:
    if math.isnan(m):
        return "-"
    digits = 2 if abs(m) < 10 else 1 if abs(m) < 1000 else 0
    return f"{m:.{digits}f} ± {ci:.{digits}f}"


def analyze(result_dir: str | Path, docs_dir: str | Path | None = None) -> Path:
    warnings.filterwarnings("ignore", category=RuntimeWarning)   # tests on identical samples
    result_dir = Path(result_dir)
    cfg = yaml.safe_load((result_dir / "experiment.yaml").read_text(encoding="utf-8"))
    rows = load_runs(result_dir / "runs.csv")
    if cfg.get("paired_baseline"):
        add_paired_disruption(rows, cfg["paired_baseline"])
        rows_eval = [r for r in rows if not str(r["label"]).endswith(cfg["paired_baseline"])]
    else:
        rows_eval = rows
    labels = [v["label"] for v in cfg.get("variants", [])] + list(cfg.get("controllers", []))
    labels = [lab for lab in labels if any(r["label"] == lab for r in rows_eval)]
    scenarios = list(dict.fromkeys(r["scenario"] for r in rows_eval))
    metrics = [m for m in cfg.get("metrics", ["avg_time_in_system", "avg_wait_time", "avg_queue",
                                                "spillback_link_s", "jain_fairness", "messages_per_agent_min"])
               if any(isinstance(r.get(m), float) for r in rows_eval)]
    ref = cfg.get("reference")

    def values(scen, label, metric):
        return [r[metric] for r in rows_eval if r["scenario"] == scen and r["label"] == label
                and isinstance(r.get(metric), float) and not math.isnan(r[metric])]

    lines = [f"# Experiment `{cfg['name']}`", "",
             f"{len(rows)} runs, {len(set(r['seed'] for r in rows))} seeds per configuration. "
             "Values are means ± 95% confidence interval (Student t).", ""]
    if cfg.get("description"):
        lines += [cfg["description"].strip(), ""]
    for scen in scenarios:
        lines += [f"## {scen}", "", "| variant | " + " | ".join(METRICS.get(m, (m,))[0] for m in metrics) + " |",
                  "|---|" + "---:|" * len(metrics)]
        for lab in labels:
            cells = [fmt(*mean_ci(values(scen, lab, m))) for m in metrics]
            lines.append(f"| {'**' + lab + '**' if lab == ref else lab} | " + " | ".join(cells) + " |")
        lines.append("")
        if ref and len(labels) > 1:
            lines += [f"Tests against **{ref}**: Mann-Whitney U, two-sided, Holm-corrected per metric; "
                      "Kruskal-Wallis across all variants.", "",
                      "| metric | Kruskal-Wallis p | " + " | ".join(f"vs {lab}" for lab in labels if lab != ref) + " |",
                      "|---|---:|" + "---:|" * (len(labels) - 1)]
            for m in metrics:
                groups = [values(scen, lab, m) for lab in labels]
                groups_ok = [g for g in groups if len(g) >= 2]
                try:
                    kw = stats.kruskal(*groups_ok).pvalue if len(groups_ok) >= 2 else float("nan")
                except ValueError:
                    kw = float("nan")
                raw = []
                for lab in labels:
                    if lab == ref:
                        continue
                    a, b = values(scen, ref, m), values(scen, lab, m)
                    try:
                        raw.append(stats.mannwhitneyu(a, b, alternative="two-sided").pvalue if a and b else 1.0)
                    except ValueError:
                        raw.append(1.0)
                adj = holm(raw)
                lines.append(f"| {METRICS.get(m, (m,))[0]} | {kw:.3g} | " + " | ".join(f"{p:.3g}" for p in adj) + " |")
            lines.append("")
    (result_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")

    for fig in cfg.get("figures", []):
        m = fig["metric"]
        data = {lab: [mean_ci(values(s, lab, m)) for s in scenarios] for lab in labels}
        out = Path(docs_dir) / fig["file"] if docs_dir else result_dir / fig["file"]
        grouped_bars(scenarios, data, METRICS.get(m, (m,))[0], fig.get("title", ""), out,
                     highlight=ref)
    print(f"wrote {result_dir / 'summary.md'}")
    return result_dir / "summary.md"
