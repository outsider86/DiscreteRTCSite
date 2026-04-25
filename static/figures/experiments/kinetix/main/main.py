"""Wrapper that uses adaptive_discrete_rtc as discrete_rtc, with custom colors and smaller legend."""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from plot_comparison_grid import (
    _blend_with_gray,
    _make_sync_baseline,
    _rename_and_prefix_methods,
    _short_level_name,
    load_results,
)

DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR = pathlib.Path(__file__).resolve().parent


def prepare_dd_csv() -> pathlib.Path:
    """Load dd/results.csv, replace discrete_rtc with adaptive_discrete_rtc, write a temp CSV."""
    df = pd.read_csv(DATA_DIR / "dd" / "results.csv")
    df = df[df["method"] != "discrete_rtc"]
    df["method"] = df["method"].replace("adaptive_discrete_rtc", "discrete_rtc")
    out = OUTPUT_DIR / "dd_adaptive_as_rtc.csv"
    df.to_csv(out, index=False)
    return out


def plot_comparison_grid_custom(
    continuous_csv,
    discrete_csv,
    metric="returned_episode_solved",
    output_path=None,
    show=True,
    show_sync=False,
):
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "font.weight": "bold",
            "axes.labelweight": "bold",
            "axes.titleweight": "bold",
            "axes.grid": True,
            "grid.alpha": 0.3,
            "axes.titlesize": 20,
            "axes.labelsize": 18,
            "xtick.labelsize": 16,
            "ytick.labelsize": 16,
            "legend.fontsize": 12,
        }
    )

    df_continuous_raw = load_results(continuous_csv)
    df_discrete_raw = load_results(discrete_csv)

    df_continuous = _rename_and_prefix_methods(
        df_continuous_raw, prefix="continuous", rename_map={"realtime": "RTC"}
    )
    df_continuous = df_continuous[df_continuous["method"] != "continuoushard_masking"]

    if show_sync:
        df_continuous = _make_sync_baseline(df_continuous, "continuousRTC", "continuousSync")

    df_discrete = _rename_and_prefix_methods(
        df_discrete_raw, prefix="discrete", rename_map={"discrete_rtc": "RTC"}
    )

    if show_sync:
        df_discrete = _make_sync_baseline(df_discrete, "discreteRTC", "discreteSync")

    df_continuous["source"] = "continuous"
    df_discrete["source"] = "discrete"

    df = pd.concat([df_continuous, df_discrete], ignore_index=True)
    df = df.copy()
    df["s"] = df["delay"].apply(lambda d: max(1, d))
    df = df[df["execute_horizon"] == df["s"]].copy()

    all_levels = sorted(df["level_short"].unique())
    all_methods = sorted(df["method"].unique())

    # --- Custom colors: Discrete=Green, Continuous=Yellow ---
    def _linestyle_for_method(method):
        m = method.lower()
        if "rtc" in m: return "-"
        if "bid" in m: return (0, (5, 2))
        if "naive" in m: return (0, (1, 1.5))
        if "sync" in m: return (0, (3, 1.5, 1, 1.5))
        return "-"

    def _alpha_for_method(method):
        m = method.lower()
        if "rtc" in m:
            return 1.0
        if "sync" in m:
            return 1.0
        if "bid" in m:
            return 0.7
        if "naive" in m:
            return 0.4
        return 0.6

    def _legend_label(method, source):
        m = method.lower()
        prefix = "Continuous" if source == "continuous" else "Discrete"
        if "rtc" in m:
            return f"{prefix}-RTC"
        if "bid" in m:
            return f"{prefix}-BID"
        if "naive" in m:
            return f"{prefix}-Naive"
        if "sync" in m:
            return f"{prefix}-Sync"
        return method

    def get_color_and_alpha(method, source):
        alpha = _alpha_for_method(method)
        if source == "continuous":
            base = "cc9900"  # yellow / golden
            return (_blend_with_gray(base, alpha), alpha)
        if source == "discrete":
            base = "1a8c1a"  # green
            return (_blend_with_gray(base, alpha), alpha)
        return ("#999999", alpha)

    # --- Plotting helper ---
    def _plot_env(ax, level):
        for method in all_methods:
            for source in ["continuous", "discrete"]:
                subset = df[(df["level_short"] == level) & (df["method"] == method) & (df["source"] == source)]
                if not subset.empty:
                    agg = subset.groupby("delay")[metric].mean().reset_index().sort_values("delay")
                    color, alpha = get_color_and_alpha(method, source)
                    ax.plot(
                        agg["delay"], agg[metric],
                        marker="o", color=color, alpha=alpha,
                        linewidth=3 if alpha == 1.0 else 2,
                        markersize=9 if alpha == 1.0 else 7,
                        markerfacecolor=color, markeredgecolor="white", markeredgewidth=1.5,
                        linestyle=_linestyle_for_method(method), solid_capstyle="round",
                    )
        ax.set_title(level, fontsize=28, fontweight="bold")
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis="both", labelbottom=False, labelleft=False, length=0)

    # --- Build 3x4 grid: all 12 environments (custom ordering) ---
    fig, axes = plt.subplots(3, 4, figsize=(16, 12))
    fig.subplots_adjust(hspace=0.22, wspace=0.08, left=0.02, right=0.98, top=0.95, bottom=0.02)

    level_order = [
        "chain_lander", "grasp_easy", "hard_lunar_lander", "mjc_half_cheetah",
        "trampoline", "cartpole_thrust", "car_launch", "catapult",
        "catcher_v3", "h17_unicycle", "mjc_swimmer", "mjc_walker",
    ]
    available = set(all_levels)
    ordered = [lv for lv in level_order if lv in available]
    ordered += [lv for lv in all_levels if lv not in level_order]
    for idx, level in enumerate(ordered[:12]):
        row = idx // 4
        col = idx % 4
        _plot_env(axes[row, col], level)

    if output_path:
        for ext in [".png", ".svg", ".pdf"]:
            plt.savefig(pathlib.Path(output_path).with_suffix(ext), dpi=150, bbox_inches="tight")
        # Standalone average figure
        p = pathlib.Path(output_path)
        avg_path = p.parent / (p.stem + "_average" + p.suffix)
        fig_avg, ax_solo = plt.subplots(figsize=(8, 5))
        added2 = set()
        for method in all_methods:
            for source in ["continuous", "discrete"]:
                subset = df[(df["method"] == method) & (df["source"] == source)]
                if not subset.empty:
                    color, alpha = get_color_and_alpha(method, source)
                    label = _legend_label(method, source)
                    lbl = None if label in added2 else label
                    if lbl:
                        added2.add(label)
                    delays = sorted(subset["delay"].unique())
                    means = [subset[subset["delay"] == d].groupby("level_short")[metric].mean().mean() for d in delays]
                    ax_solo.plot(
                        delays, means,
                        marker="o", color=color, alpha=alpha, label=lbl,
                        linewidth=3 if alpha == 1.0 else 2,
                        markersize=9 if alpha == 1.0 else 7,
                        markerfacecolor=color, markeredgecolor="white", markeredgewidth=1.5,
                        linestyle=_linestyle_for_method(method), solid_capstyle="round",
                    )
        ax_solo.set_title("Average Solve Rate", fontsize=26, fontweight="bold")
        ax_solo.set_xlabel("")
        ax_solo.set_xticks([0, 1, 2, 3, 4])
        ax_solo.tick_params(axis="both", labelsize=20, labelbottom=False)
        ax_solo.set_ylim(0.45, 0.95)
        ax_solo.grid(True, alpha=0.3)
        ax_solo.legend(loc="best", fontsize=20, framealpha=0.7, handlelength=2.0, handletextpad=0.6, borderpad=0.5)
        plt.savefig(avg_path, dpi=150, bbox_inches="tight")
        plt.close(fig_avg)
    if show:
        plt.show()
    plt.close()


def main():
    dd_csv = prepare_dd_csv()
    flow_csv = DATA_DIR / "flow" / "results.csv"
    plot_comparison_grid_custom(
        continuous_csv=flow_csv,
        discrete_csv=dd_csv,
        output_path=OUTPUT_DIR / "kinetix_main.png",
        show=False,
    )
    print(f"Saved to {OUTPUT_DIR / 'kinetix_main'}")


if __name__ == "__main__":
    main()
