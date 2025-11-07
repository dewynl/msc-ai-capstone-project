#!/usr/bin/env python3
"""
Figure 1: Prerequisite Accuracy Distribution

Shows the distribution of prerequisite accuracy across all successful syllabi.
Key finding: 70.4% of syllabi have 0% prerequisite accuracy.
"""

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for headless environment
import matplotlib.pyplot as plt
import pandas as pd
from config import COLORS, DATA_PATH, OUTPUT_DIR, STYLE


def create_prerequisite_distribution():
    """Create stacked bar chart showing prerequisite accuracy distribution."""
    df = pd.read_csv(DATA_PATH)
    successful = df[df["pipeline_success"] == 1]

    total = len(successful)
    perfect = len(successful[successful["prerequisite_accuracy"] == 1.0])
    partial = len(
        successful[
            (successful["prerequisite_accuracy"] > 0)
            & (successful["prerequisite_accuracy"] < 1.0)
        ]
    )
    none = len(successful[successful["prerequisite_accuracy"] == 0.0])

    perfect_pct = (perfect / total) * 100
    partial_pct = (partial / total) * 100
    none_pct = (none / total) * 100

    print("=" * 80)
    print("PREREQUISITE ACCURACY DISTRIBUTION")
    print("=" * 80)
    print(f"Total successful syllabi: {total}")
    print(f"Perfect (100% accuracy): {perfect} ({perfect_pct:.1f}%)")
    print(f"Partial (1-99% accuracy): {partial} ({partial_pct:.1f}%)")
    print(f"None (0% accuracy): {none} ({none_pct:.1f}%)")
    print()
    print(f"Mean accuracy: {successful['prerequisite_accuracy'].mean():.1%}")
    print(f"Median accuracy: {successful['prerequisite_accuracy'].median():.1%}")
    print("=" * 80)

    plt.style.use("seaborn-v0_8-darkgrid")
    fig, ax = plt.subplots(figsize=STYLE["figure_size"], dpi=STYLE["dpi"])

    categories = ["All Syllabi"]
    perfect_bar = ax.barh(
        categories,
        [perfect_pct],
        color=COLORS["success"],
        label=f"Perfect (100%): {perfect} syllabi",
    )
    partial_bar = ax.barh(
        categories,
        [partial_pct],
        left=[perfect_pct],
        color=COLORS["warning"],
        label=f"Partial (1-99%): {partial} syllabi",
    )
    none_bar = ax.barh(
        categories,
        [none_pct],
        left=[perfect_pct + partial_pct],
        color=COLORS["danger"],
        label=f"None (0%): {none} syllabi",
    )

    for bars, percentage in [
        (perfect_bar, perfect_pct),
        (partial_bar, partial_pct),
        (none_bar, none_pct),
    ]:
        if percentage > 5:
            for bar in bars:
                width = bar.get_width()
                if width > 5:
                    ax.text(
                        bar.get_x() + width / 2,
                        bar.get_y() + bar.get_height() / 2,
                        f"{percentage:.1f}%",
                        ha="center",
                        va="center",
                        fontweight="bold",
                        fontsize=STYLE["label_size"],
                        color="white",
                    )

    ax.set_xlabel(
        "Percentage of Syllabi (%)", fontsize=STYLE["label_size"], fontweight="bold"
    )
    ax.set_title(
        "Prerequisite Accuracy Distribution Across Generated Syllabi",
        fontsize=STYLE["title_size"],
        fontweight="bold",
        pad=20,
    )
    ax.set_xlim(0, 100)
    ax.legend(loc="upper right", fontsize=10, framealpha=0.9)
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()

    output_path = OUTPUT_DIR / "fig1_prerequisite_distribution.png"
    plt.savefig(output_path, dpi=STYLE["dpi"], bbox_inches="tight")
    print(f"\n✅ Saved: {output_path}")

    plt.close()

    return output_path


if __name__ == "__main__":
    create_prerequisite_distribution()
