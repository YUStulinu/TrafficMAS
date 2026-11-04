"""Static figures for the report and the README (Matplotlib)."""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# Categorical palette in a fixed order: a variant keeps its colour in every figure.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e4e3df"


def _style(ax) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=TEXT_2, labelsize=9)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def grouped_bars(groups: list[str], data: dict[str, list[tuple[float, float]]], ylabel: str, title: str,
                 out: Path, highlight: str | None = None) -> None:
    """Small multiples: one panel per group (scenario) with its own y axis, one bar per series.

    Whiskers are 95% confidence intervals. Scenarios differ by an order of magnitude,
    so a shared axis would flatten the differences that matter inside each one.
    """
    labels = list(data)
    n = len(labels)
    cols = len(groups)
    fig, axes = plt.subplots(1, cols, figsize=(max(6.5, 2.3 * cols + 0.4 * n), 3.9), dpi=150, squeeze=False)
    fig.patch.set_facecolor(SURFACE)
    for g, ax in enumerate(axes[0]):
        _style(ax)
        for i, lab in enumerate(labels):
            m, c = data[lab][g]
            m = 0.0 if math.isnan(m) else m
            c = 0.0 if math.isnan(c) else c
            ax.bar(i, m, 0.82, color=SERIES[i % len(SERIES)], label=lab,
                   edgecolor=TEXT if lab == highlight else SURFACE, linewidth=1.2 if lab == highlight else 0.6,
                   yerr=c, error_kw={"ecolor": TEXT_2, "elinewidth": 0.9, "capsize": 2})
        ax.set_xticks([])
        ax.set_xlabel(groups[g], color=TEXT, fontsize=9)
        ax.set_ylim(0, ax.get_ylim()[1] * 1.05)
    axes[0][0].set_ylabel(ylabel, color=TEXT_2, fontsize=9)
    if title:
        fig.suptitle(title, color=TEXT, fontsize=11, x=0.01, ha="left")
    handles, names = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, names, frameon=False, fontsize=8, ncol=min(n, 7), loc="lower center", labelcolor=TEXT_2)
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor=SURFACE)
    plt.close(fig)


def time_series(series: dict[str, tuple[list[float], list[float]]], ylabel: str, title: str, out: Path,
                xlabel: str = "simulation time (min)") -> None:
    fig, ax = plt.subplots(figsize=(7.0, 3.6), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    _style(ax)
    for i, (lab, (xs, ys)) in enumerate(series.items()):
        ax.plot(xs, ys, color=SERIES[i % len(SERIES)], linewidth=1.8, label=lab)
    ax.set_xlabel(xlabel, color=TEXT_2, fontsize=9)
    ax.set_ylabel(ylabel, color=TEXT_2, fontsize=9)
    if title:
        ax.set_title(title, color=TEXT, fontsize=11, loc="left")
    ax.legend(frameon=False, fontsize=8, labelcolor=TEXT_2)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor=SURFACE)
    plt.close(fig)
