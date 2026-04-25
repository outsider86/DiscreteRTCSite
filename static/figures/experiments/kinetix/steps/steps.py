"""Bar chart comparing iterative steps for ContinuousRTC vs DiscreteRTC across inference delays."""

import pathlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

OUTPUT_DIR = pathlib.Path(__file__).resolve().parent

delays = [0, 1, 2, 3, 4]
continuous_steps = [5, 5, 5, 5, 5]
discrete_steps = [5, 4, 3, 3, 2]

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

    x = np.arange(len(delays))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8.67, 6.19))

    bars_cont = ax.bar(x - width / 2, continuous_steps, width, label="ContinuousRTC",
                       color="#cc9900", edgecolor="white", linewidth=1.5)
    bars_disc = ax.bar(x + width / 2, discrete_steps, width, label="DiscreteRTC",
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

    ax.set_title("Iterative Steps", fontsize=22, fontweight="bold")
    ax.set_xlabel("Inference Delay, d", fontsize=18, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([str(d) for d in delays], fontsize=16)
    ax.tick_params(axis="y", labelsize=16)
    ax.set_ylim(0, 7)
    ax.legend(fontsize=15, framealpha=0.7)
    ax.grid(True, alpha=0.3, axis="y")

    output_path = OUTPUT_DIR / "steps"
    for ext in [".png", ".svg", ".pdf"]:
        plt.savefig(output_path.with_suffix(ext), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved to {output_path}.*")


if __name__ == "__main__":
    main()
