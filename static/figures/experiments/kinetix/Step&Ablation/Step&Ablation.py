"""Side-by-side: Iterative Steps bar chart (left) + Flex Average Solve Rate (right)."""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from flex.flex import prepare_data, METHOD_ORDER, METHOD_COLORS, METHOD_LEGEND

BASE = pathlib.Path(__file__).resolve().parent
output_path = BASE / "Step&Ablation"


# --- Data for the steps bar chart (matches steps/steps.py) ---
delays = [0, 1, 2, 3, 4]
continuous_steps = [5, 5, 5, 5, 5]
discrete_steps = [5, 4, 3, 3, 2]


def plot_steps(ax):
    x = np.arange(len(delays))
    width = 0.35

    ax.bar(x - width / 2, continuous_steps, width, label="ContinuousRTC",
           color="#cc9900", edgecolor="white", linewidth=1.5)
    ax.bar(x + width / 2, discrete_steps, width, label="DiscreteRTC",
           color="#1a8c1a", edgecolor="white", linewidth=1.5)

    ax.plot(x, continuous_steps, linestyle="--", color="#8a6800",
            linewidth=2.5, alpha=0.5, zorder=3)
    ax.plot(x, discrete_steps, linestyle="--", color="#0f5c0f",
            linewidth=2.5, alpha=0.5, zorder=3)

    extend = 0.5
    cont_slope = continuous_steps[-1] - continuous_steps[-2]
    disc_slope = discrete_steps[-1] - discrete_steps[-2]
    cont_end = (x[-1] + extend, continuous_steps[-1] + cont_slope * extend)
    disc_end = (x[-1] + extend, discrete_steps[-1] + disc_slope * extend)

    ax.plot([x[-1], cont_end[0]], [continuous_steps[-1], cont_end[1]],
            linestyle="--", color="#8a6800", linewidth=2.5, alpha=0.5, zorder=3)
    ax.plot([x[-1], disc_end[0]], [discrete_steps[-1], disc_end[1]],
            linestyle="--", color="#0f5c0f", linewidth=2.5, alpha=0.5, zorder=3)

    ax.annotate("", xy=cont_end,
                xytext=(cont_end[0] - 0.01, cont_end[1] - cont_slope * 0.01),
                arrowprops=dict(arrowstyle="-|>", color="#8a6800",
                                linewidth=0, mutation_scale=25, alpha=0.5),
                zorder=4)
    ax.annotate("", xy=disc_end,
                xytext=(disc_end[0] - 0.01, disc_end[1] - disc_slope * 0.01),
                arrowprops=dict(arrowstyle="-|>", color="#0f5c0f",
                                linewidth=0, mutation_scale=25, alpha=0.5),
                zorder=4)

    ax.set_xlim(x[0] - 0.8, x[-1] + extend + 0.3)
    ax.set_ylim(0, 7)
    ax.set_xticks(x)
    ax.set_xticklabels([str(d) for d in delays])
    ax.grid(True, alpha=0.3, axis="y")

    ax.set_title("Iterative Steps per Policy", fontsize=30, fontweight="bold")
    ax.set_xlabel("Inference Delay, d", fontsize=28, fontweight="bold")
    ax.set_ylabel("Number of Steps", fontsize=26, fontweight="bold")
    ax.tick_params(axis="both", labelsize=18)

    leg = ax.legend(loc="upper right", fontsize=22, frameon=False,
                    handlelength=1.8, handletextpad=0.5, borderpad=0.6)
    for txt in leg.get_texts():
        txt.set_fontfamily("Nimbus Roman")


def plot_flex_average(ax, df, metric="returned_episode_solved"):
    all_methods = [m for m in METHOD_ORDER if m in df["method"].unique()]

    def get_color(method):
        return f"#{METHOD_COLORS.get(method, '808080')}"

    plot_order = [m for m in all_methods if m == "VLASH"] + \
                 [m for m in all_methods if m != "VLASH"]
    for method in plot_order:
        subset = df[df["method"] == method]
        if subset.empty:
            continue
        color = get_color(method)
        d_sorted = sorted(subset["delay"].unique())
        means = [subset[subset["delay"] == d].groupby("level_short")[metric].mean().mean() for d in d_sorted]
        ax.plot(
            d_sorted, means,
            marker="o", color=color, label=METHOD_LEGEND.get(method, method),
            linewidth=3, markersize=9,
            markerfacecolor=color, markeredgecolor="white", markeredgewidth=1.5,
            solid_capstyle="round",
        )

    ax.set_title("Average Solve Rate in Kinetix", fontsize=30, fontweight="bold")
    ax.set_xlabel("Inference Delay, d", fontsize=28, fontweight="bold")
    ax.set_ylabel("Solve Rate", fontsize=26, fontweight="bold")
    ax.set_xticks([0, 1, 2, 3, 4])
    ax.tick_params(axis="both", labelsize=18)
    ax.set_ylim(0.7, 0.95)
    ax.grid(True, alpha=0.3)

    leg = ax.legend(loc="lower left", fontsize=22, frameon=False,
                    handlelength=1.8, handletextpad=0.5, borderpad=0.6)
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

    df = prepare_data()

    fig, (ax_steps, ax_flex) = plt.subplots(1, 2, figsize=(15, 6.5))
    plot_steps(ax_steps)
    plot_flex_average(ax_flex, df)

    plt.tight_layout()

    for ext in [".png", ".svg", ".pdf"]:
        out = output_path.with_suffix(ext)
        plt.savefig(out, dpi=200, bbox_inches="tight", pad_inches=0.05)
        print(f"Saved to {out}")
    plt.close()


if __name__ == "__main__":
    main()
