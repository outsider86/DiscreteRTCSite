"""Compare base DiscreteRTC (data/dd) vs inpainting-finetuned variant (data/finetuned).

Builds the complete figure in one pass: averages (left) + 3x4 per-env grid (right).
No PNG injection — every panel is a real matplotlib axes in the same figure.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from plot_comparison_grid import (
    _blend_with_gray,
    _rename_and_prefix_methods,
    load_results,
)
from plot_comparison_grid_episode_length import _add_normalized_episode_length

BASE = pathlib.Path(__file__).resolve().parent
DATA_DIR = BASE.parent / "data"
OUTPUT_STEM = BASE / "FinetuneApp"

LEVEL_ORDER = [
    "chain_lander", "grasp_easy", "hard_lunar_lander", "mjc_half_cheetah",
    "trampoline", "cartpole_thrust", "car_launch", "catapult",
    "catcher_v3", "h17_unicycle", "mjc_swimmer", "mjc_walker",
]


def _prepare_base():
    df_base = _rename_and_prefix_methods(
        load_results(DATA_DIR / "dd" / "results.csv"),
        prefix="base", rename_map={"discrete_rtc": "RTC"},
    )
    df_ft = _rename_and_prefix_methods(
        load_results(DATA_DIR / "finetuned" / "results.csv"),
        prefix="finetuned", rename_map={"discrete_rtc": "RTC"},
    )
    df_base["source"] = "base"
    df_ft["source"] = "finetuned"

    df = pd.concat([df_base, df_ft], ignore_index=True)
    df["s"] = df["delay"].apply(lambda d: max(1, d))
    df = df[df["execute_horizon"] == df["s"]].copy()

    df["variant"] = df["method"].map(lambda m: m.replace("base", "").replace("finetuned", ""))
    df = df[df["variant"].isin({"RTC", "bid", "naive"})].copy()
    return df


def _prepare_solve():
    return _prepare_base()


def _prepare_throughput():
    return _add_normalized_episode_length(_prepare_base(), pathlib.Path("."))


def _linestyle_for_method(method):
    variant = method.replace("base", "").replace("finetuned", "").lower()
    if "rtc" in variant: return "-"
    if "bid" in variant: return (0, (5, 2))
    if "naive" in variant: return (0, (1, 1.5))
    return "-"


def _alpha_for_method(method):
    m = method.lower().replace("finetuned", "").replace("base", "")
    if "rtc" in m: return 1.0
    if "bid" in m: return 0.7
    if "naive" in m: return 0.4
    return 0.6


def _legend_label(method, source):
    variant = method.replace("base", "").replace("finetuned", "")
    prefix = "DiscreteRTC" if source == "base" else "DiscreteRTC (FT)"
    if variant == "RTC": return prefix
    if variant == "bid": return f"{prefix} BID"
    if variant == "naive": return f"{prefix} Naive"
    return method


def _color_alpha(method, source):
    a = _alpha_for_method(method)
    base = "1a8c1a" if source == "base" else "9467bd"
    return _blend_with_gray(base, a), a


def _plot_series(ax, x, y, method, source, label=None):
    color, alpha = _color_alpha(method, source)
    ax.plot(
        x, y,
        marker="o", color=color, alpha=alpha, label=label,
        linewidth=3 if alpha == 1.0 else 2,
        markersize=9 if alpha == 1.0 else 7,
        markerfacecolor=color, markeredgecolor="white", markeredgewidth=1.5,
        linestyle=_linestyle_for_method(method), solid_capstyle="round",
    )


def _plot_average(ax, df, metric, methods, *, title, xlabel, ylabel, ylim, show_legend):
    seen = set()
    for method in methods:
        src = "base" if method.startswith("base") else "finetuned"
        subset = df[df["method"] == method]
        if subset.empty:
            continue
        label = _legend_label(method, src)
        lbl = None if label in seen else label
        if lbl:
            seen.add(label)
        delays = sorted(subset["delay"].unique())
        means = [subset[subset["delay"] == d].groupby("level_short")[metric].mean().mean() for d in delays]
        _plot_series(ax, delays, means, method, src, label=lbl)
    ax.set_title(title, fontsize=32, fontweight="bold")
    ax.set_xticks([0, 1, 2, 3, 4])
    ax.set_ylim(ylim)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis="both", labelsize=26)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=28, fontweight="bold")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=30, fontweight="bold")
    else:
        ax.set_xlabel("")
        ax.tick_params(axis="x", labelbottom=False)
    if show_legend:
        ax.legend(loc="best", fontsize=22, framealpha=0.7,
                  handlelength=2.0, handletextpad=0.5, borderpad=0.4)


def _plot_env(ax, df, metric, level, methods):
    for method in methods:
        src = "base" if method.startswith("base") else "finetuned"
        subset = df[(df["level_short"] == level) & (df["method"] == method)]
        if subset.empty:
            continue
        agg = subset.groupby("delay")[metric].mean().reset_index().sort_values("delay")
        _plot_series(ax, agg["delay"], agg[metric], method, src)
    ax.set_title(level, fontsize=28, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis="both", labelbottom=False, labelleft=False, length=0)


def main():
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.weight": "bold",
        "axes.labelweight": "bold",
        "axes.titleweight": "bold",
        "axes.grid": True,
        "grid.alpha": 0.3,
    })

    df_solve = _prepare_solve()
    df_tp = _prepare_throughput()
    methods = sorted(df_solve["method"].unique())

    available = set(df_solve["level_short"].unique())
    ordered_levels = [lv for lv in LEVEL_ORDER if lv in available]
    ordered_levels += [lv for lv in sorted(available) if lv not in LEVEL_ORDER]
    ordered_levels = ordered_levels[:12]

    fig = plt.figure(figsize=(26, 12))

    outer = fig.add_gridspec(
        1, 2, width_ratios=[1, 3.0],
        wspace=0.05, left=0.05, right=0.99, top=0.94, bottom=0.09,
    )

    left_gs = outer[0, 0].subgridspec(2, 1, hspace=0.25)
    ax_solve = fig.add_subplot(left_gs[0, 0])
    ax_tp = fig.add_subplot(left_gs[1, 0])

    _plot_average(
        ax_solve, df_solve, "returned_episode_solved", methods,
        title="Average Solve Rate", xlabel="", ylabel="Solve Rate",
        ylim=(0.30, 0.95), show_legend=True,
    )
    _plot_average(
        ax_tp, df_tp, "episode_length_reciprocal", methods,
        title="Average Throughputs", xlabel="Inference Delay, d",
        ylabel="Throughput", ylim=(3.0, 4.4), show_legend=False,
    )

    right_gs = outer[0, 1].subgridspec(3, 4, hspace=0.28, wspace=0.08)
    for idx, level in enumerate(ordered_levels):
        ax = fig.add_subplot(right_gs[idx // 4, idx % 4])
        _plot_env(ax, df_solve, "returned_episode_solved", level, methods)

    for ext in [".png", ".svg", ".pdf"]:
        out = OUTPUT_STEM.with_suffix(ext)
        plt.savefig(out, dpi=200, bbox_inches="tight", pad_inches=0.05)
        print(f"Saved {out}")
    plt.close(fig)


if __name__ == "__main__":
    main()
