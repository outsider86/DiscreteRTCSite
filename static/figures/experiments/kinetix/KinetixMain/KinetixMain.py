"""Standalone figure: Average Solve Rate and Average Throughput side by side (Kinetix main result)."""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from plot_comparison_grid import (
    _blend_with_gray,
    _rename_and_prefix_methods,
    _short_level_name,
    load_results,
)
from plot_comparison_grid_episode_length import _add_normalized_episode_length

BASE = pathlib.Path(__file__).resolve().parent
DATA_DIR = BASE.parent / "data"
OUTPUT_STEM = BASE / "KinetixMain"


def _prepare_base():
    df_dd = pd.read_csv(DATA_DIR / "dd" / "results.csv")
    df_dd = df_dd[df_dd["method"] != "discrete_rtc"]
    df_dd["method"] = df_dd["method"].replace("adaptive_discrete_rtc", "discrete_rtc")
    df_dd["level_short"] = df_dd["level"].map(_short_level_name)

    df_flow = load_results(DATA_DIR / "flow" / "results.csv")

    df_cont = _rename_and_prefix_methods(df_flow, prefix="continuous", rename_map={"realtime": "RTC"})
    df_cont = df_cont[df_cont["method"] != "continuoushard_masking"]
    df_disc = _rename_and_prefix_methods(df_dd, prefix="discrete", rename_map={"discrete_rtc": "RTC"})

    df_cont["source"] = "continuous"
    df_disc["source"] = "discrete"

    df = pd.concat([df_cont, df_disc], ignore_index=True)
    df["s"] = df["delay"].apply(lambda d: max(1, d))
    df = df[df["execute_horizon"] == df["s"]].copy()
    return df


def _prepare_solve():
    return _prepare_base()


def _prepare_throughput():
    return _add_normalized_episode_length(_prepare_base(), pathlib.Path("."))


def _linestyle_for_method(method):
    m = method.lower()
    if "rtc" in m: return "-"
    if "bid" in m: return (0, (5, 2))
    if "naive" in m: return (0, (1, 1.5))
    if "sync" in m: return (0, (3, 1.5, 1, 1.5))
    return "-"


def _alpha_for_method(method):
    m = method.lower()
    if "rtc" in m: return 1.0
    if "sync" in m: return 1.0
    if "bid" in m: return 0.7
    if "naive" in m: return 0.4
    return 0.6


def _legend_label(method, source):
    m = method.lower()
    prefix = "Continuous" if source == "continuous" else "Discrete"
    if "rtc" in m: return f"{prefix}-RTC"
    if "bid" in m: return f"{prefix}-BID"
    if "naive" in m: return f"{prefix}-Naive"
    if "sync" in m: return f"{prefix}-Sync"
    return method


def _color_alpha(method, source):
    a = _alpha_for_method(method)
    base = "cc9900" if source == "continuous" else "1a8c1a"
    return _blend_with_gray(base, a), a


def _plot_average(ax, df, metric, methods, *, title, xlabel, ylabel, ylim, show_legend):
    seen = set()
    for method in methods:
        for source in ["continuous", "discrete"]:
            subset = df[(df["method"] == method) & (df["source"] == source)]
            if subset.empty:
                continue
            color, alpha = _color_alpha(method, source)
            label = _legend_label(method, source)
            lbl = None if label in seen else label
            if lbl:
                seen.add(label)
            delays = sorted(subset["delay"].unique())
            means = [subset[subset["delay"] == d].groupby("level_short")[metric].mean().mean() for d in delays]
            ax.plot(
                delays, means,
                marker="o", color=color, alpha=alpha, label=lbl,
                linewidth=3 if alpha == 1.0 else 2,
                markersize=9 if alpha == 1.0 else 7,
                markerfacecolor=color, markeredgecolor="white", markeredgewidth=1.5,
                linestyle=_linestyle_for_method(method), solid_capstyle="round",
            )
    ax.set_title(title, fontsize=26, fontweight="bold", fontfamily="Nimbus Roman")
    ax.set_xticks([0, 1, 2, 3, 4])
    ax.set_ylim(ylim)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis="both", labelsize=20)
    for lbl_ in ax.get_xticklabels() + ax.get_yticklabels():
        lbl_.set_fontfamily("Nimbus Roman")
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=22, fontweight="bold", fontfamily="Nimbus Roman")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=24, fontweight="bold", fontfamily="Nimbus Roman")
    if show_legend:
        leg = ax.legend(loc="best", fontsize=16, framealpha=0.7, handlelength=2.0, handletextpad=0.5, borderpad=0.4)
        for txt in leg.get_texts():
            txt.set_fontfamily("Nimbus Roman")


def main():
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Nimbus Roman", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.weight": "bold",
        "axes.labelweight": "bold",
        "axes.titleweight": "bold",
        "axes.grid": True,
        "grid.alpha": 0.3,
    })

    df_solve = _prepare_solve()
    df_tp = _prepare_throughput()
    methods = sorted(df_solve["method"].unique())

    fig, (ax_solve, ax_tp) = plt.subplots(1, 2, figsize=(15, 6.5))

    _plot_average(
        ax_solve, df_solve, "returned_episode_solved", methods,
        title="Average Solve Rate in Kinetix",
        xlabel="Inference Delay, d", ylabel="Solve Rate", ylim=(0.45, 0.95),
        show_legend=True,
    )
    leg = ax_solve.get_legend()
    if leg is not None:
        handles, labels = ax_solve.get_legend_handles_labels()
        leg.remove()
        clean = [(h, l.replace("-", "")) for h, l in zip(handles, labels)]
        order = ["DiscreteRTC", "DiscreteBID", "DiscreteNaive",
                 "ContinuousRTC", "ContinuousBID", "ContinuousNaive"]
        by_label = {l: h for h, l in clean}
        ordered = [(by_label[l], l) for l in order if l in by_label]
        ordered += [(h, l) for h, l in clean if l not in order]
        new_handles = [h for h, _ in ordered]
        new_labels = [l for _, l in ordered]
        leg = ax_solve.legend(
            new_handles, new_labels,
            loc="lower left", bbox_to_anchor=(-0.04, -0.04),
            fontsize=22, frameon=False,
            handlelength=2.4, handletextpad=0.6, borderpad=0.6,
        )
        for txt in leg.get_texts():
            txt.set_fontfamily("Nimbus Roman")

    _plot_average(
        ax_tp, df_tp, "episode_length_reciprocal", methods,
        title="Average Throughput in Kinetix",
        xlabel="Inference Delay, d", ylabel="Throughput", ylim=(3.1, 4.4),
        show_legend=False,
    )

    for ax in (ax_solve, ax_tp):
        ax.title.set_fontsize(30)
        ax.xaxis.label.set_fontsize(28)
        ax.yaxis.label.set_fontsize(26)

    plt.tight_layout()

    for ext in [".png", ".svg", ".pdf"]:
        out = OUTPUT_STEM.with_suffix(ext)
        plt.savefig(out, dpi=200, bbox_inches="tight", pad_inches=0.05)
        print(f"Saved {out}")
    plt.close()


if __name__ == "__main__":
    main()
