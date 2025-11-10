#!/usr/bin/env python3
"""
Figure 6: Prerequisite Accuracy by Difficulty Level

Shows how prerequisite accuracy varies by course difficulty:
- Advanced: Lowest (33.3%) - struggles with complex prerequisite chains
- Beginner: Moderate (46.2%) - simpler prerequisite structures
- Intermediate: Highest (54.5%) - balanced complexity

Bar chart with sample sizes and percentage breakdown (perfect/partial/none).
Note: System supports only beginner/intermediate/advanced levels.
"""

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for headless environment
import matplotlib.pyplot as plt
import pandas as pd
from config import COLORS, DATA_PATH, OUTPUT_DIR, STYLE


def create_prerequisites_by_level():
    """Create bar chart showing prerequisite accuracy by difficulty level."""
    df = pd.read_csv(DATA_PATH)
    successful = df[df["pipeline_success"] == 1]

    # Order difficulty levels (system only supports these 3)
    difficulty_order = ["beginner", "intermediate", "advanced"]
    successful = successful[successful["level"].isin(difficulty_order)]
    successful["level"] = pd.Categorical(
        successful["level"], categories=difficulty_order, ordered=True
    )

    # Calculate statistics by level
    level_stats = successful.groupby("level").agg(
        {
            "prerequisite_accuracy": ["mean", "count"],
        }
    )

    # Count perfect/partial/none for each level
    breakdown = []
    for level in difficulty_order:
        level_data = successful[successful["level"] == level]
        total = len(level_data)
        if total > 0:
            perfect = len(level_data[level_data["prerequisite_accuracy"] == 1.0])
            none = len(level_data[level_data["prerequisite_accuracy"] == 0.0])
            partial = total - perfect - none
            breakdown.append(
                {
                    "level": level,
                    "perfect": perfect,
                    "partial": partial,
                    "none": none,
                    "total": total,
                    "mean": level_data["prerequisite_accuracy"].mean(),
                }
            )

    print("=" * 80)
    print("PREREQUISITE ACCURACY BY DIFFICULTY LEVEL")
    print("=" * 80)
    print(f"System supports 3 difficulty levels: {', '.join(difficulty_order)}")
    print("=" * 80)
    for item in breakdown:
        level = item["level"].capitalize()
        print(
            f"{level:15s}: Mean={item['mean']:.1%}, "
            f"Perfect={item['perfect']}/{item['total']}, "
            f"Partial={item['partial']}/{item['total']}, "
            f"None={item['none']}/{item['total']}"
        )
    print("=" * 80)

    plt.style.use("seaborn-v0_8-darkgrid")
    fig, ax = plt.subplots(figsize=STYLE["figure_size"], dpi=STYLE["dpi"])

    # Prepare data for all supported difficulty levels
    levels = [item["level"].capitalize() for item in breakdown]
    means = [item["mean"] for item in breakdown]
    totals = [item["total"] for item in breakdown]

    # Color code by performance
    colors_list = []
    for mean in means:
        if mean >= 0.5:
            colors_list.append(COLORS["success"])
        elif mean >= 0.4:
            colors_list.append(COLORS["warning"])
        else:
            colors_list.append(COLORS["danger"])

    # Create bars
    bars = ax.bar(
        range(len(levels)),
        means,
        color=colors_list,
        edgecolor="black",
        linewidth=1,
        alpha=0.8,
    )

    # Add value labels on bars
    for idx, (bar, mean, total) in enumerate(zip(bars, means, totals)):
        height = bar.get_height()
        # Show percentage and sample size
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.02,
            f"{mean:.1%}\n(N={total})",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

        # Show breakdown inside bar
        item = breakdown[idx]
        if height > 0.15:
            breakdown_text = (
                f"Perfect: {item['perfect']}\n"
                f"Partial: {item['partial']}\n"
                f"None: {item['none']}"
            )
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height / 2,
                breakdown_text,
                ha="center",
                va="center",
                fontsize=8,
                color="white",
                fontweight="bold",
            )

    # Reference line at 50% (acceptable threshold)
    ax.axhline(
        y=0.5,
        color=COLORS["secondary"],
        linestyle="--",
        alpha=0.5,
        linewidth=1.5,
        label="Acceptable (50%)",
    )

    # Customize
    ax.set_xlabel(
        "Course Difficulty Level", fontsize=STYLE["label_size"], fontweight="bold"
    )
    ax.set_ylabel(
        "Prerequisite Accuracy (%)",
        fontsize=STYLE["label_size"],
        fontweight="bold",
    )
    ax.set_title(
        "Prerequisite Accuracy by Course Difficulty Level",
        fontsize=STYLE["title_size"],
        fontweight="bold",
        pad=25,  # Increased padding
    )
    ax.set_xticks(range(len(levels)))
    ax.set_xticklabels(levels, fontsize=11)
    ax.set_ylim(0, 0.72)  # Increased slightly to accommodate labels above bars
    ax.set_yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
    ax.set_yticklabels(["0%", "10%", "20%", "30%", "40%", "50%", "60%", "70%"])
    ax.legend(loc="upper right", fontsize=10, framealpha=0.95)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    output_path = OUTPUT_DIR / "fig6_prerequisites_by_level.png"
    plt.savefig(output_path, dpi=STYLE["dpi"], bbox_inches="tight")
    print(f"\n✅ Saved: {output_path}")

    plt.close()

    return output_path


if __name__ == "__main__":
    create_prerequisites_by_level()
