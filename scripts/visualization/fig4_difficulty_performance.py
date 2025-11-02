#!/usr/bin/env python3
"""
Figure 4: Difficulty Level vs Performance Analysis

Shows inverse relationship between course difficulty and model performance:
- Beginner: Highest quality (mean ~7.2/10)
- Intermediate: Moderate quality (mean ~6.5/10)
- Advanced: Lower quality (mean ~5.8/10)
- Postgraduate: Lowest quality (mean ~5.2/10)

Box plot shows distribution of composite quality scores by difficulty level.
"""

import matplotlib.pyplot as plt
import pandas as pd
from config import COLORS, DATA_PATH, OUTPUT_DIR, STYLE


def compute_composite_quality(row):
    """
    Compute composite quality score (0-10 scale).

    Same weights as extract_expert_syllabi.py:
    - prerequisite_accuracy: 30%
    - semantic_avg_score: 25%
    - difficulty_progression: 20%
    - topic_diversity: 15%
    - blooms_taxonomy_coverage: 10%
    """
    weights = {
        "prerequisite_accuracy": 0.30,
        "semantic_avg_score": 0.25,
        "difficulty_progression": 0.20,
        "topic_diversity": 0.15,
        "blooms_taxonomy_coverage": 0.10,
    }

    score = 0.0
    for metric, weight in weights.items():
        value = row.get(metric, 0.0)
        if pd.isna(value):
            value = 0.0
        score += value * weight

    return score * 10  # Convert to 0-10 scale


def create_difficulty_performance():
    """Create box plot showing quality distribution by difficulty level."""
    df = pd.read_csv(DATA_PATH)
    successful = df[df["pipeline_success"] == 1].copy()

    # Compute composite quality score
    successful["composite_quality"] = successful.apply(
        compute_composite_quality, axis=1
    )

    # Order difficulty levels
    difficulty_order = ["beginner", "intermediate", "advanced", "postgraduate"]
    successful["level"] = pd.Categorical(
        successful["level"], categories=difficulty_order, ordered=True
    )

    print("=" * 80)
    print("DIFFICULTY LEVEL VS PERFORMANCE")
    print("=" * 80)
    for level in difficulty_order:
        level_data = successful[successful["level"] == level]["composite_quality"]
        if len(level_data) > 0:
            print(
                f"{level.capitalize():15s}: Mean={level_data.mean():.2f}/10, "
                f"Median={level_data.median():.2f}/10, N={len(level_data)}"
            )
    print("=" * 80)

    plt.style.use("seaborn-v0_8-darkgrid")
    fig, ax = plt.subplots(figsize=STYLE["figure_size"], dpi=STYLE["dpi"])

    # Prepare data for box plot
    data_by_level = [
        successful[successful["level"] == level]["composite_quality"].tolist()
        for level in difficulty_order
    ]

    # Create box plot
    bp = ax.boxplot(
        data_by_level,
        labels=[level.capitalize() for level in difficulty_order],
        patch_artist=True,
        notch=True,
        widths=0.6,
    )

    # Color boxes by gradient (green -> orange -> red)
    colors_gradient = [
        COLORS["success"],
        COLORS["teal"],
        COLORS["warning"],
        COLORS["danger"],
    ]
    for patch, color in zip(bp["boxes"], colors_gradient):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
        patch.set_edgecolor("black")
        patch.set_linewidth(1)

    # Style whiskers, caps, medians
    for whisker in bp["whiskers"]:
        whisker.set(color="black", linewidth=1.5, linestyle="--")
    for cap in bp["caps"]:
        cap.set(color="black", linewidth=1.5)
    for median in bp["medians"]:
        median.set(color="darkred", linewidth=2)
    for flier in bp["fliers"]:
        flier.set(marker="o", markerfacecolor=COLORS["secondary"], alpha=0.5)

    # Add mean line overlay
    means = [
        successful[successful["level"] == level]["composite_quality"].mean()
        for level in difficulty_order
    ]
    ax.plot(
        range(1, len(difficulty_order) + 1),
        means,
        "D-",
        color=COLORS["purple"],
        linewidth=2,
        markersize=8,
        label="Mean Quality",
    )

    # Reference line at 7.0 (good quality threshold)
    ax.axhline(
        y=7.0,
        color=COLORS["secondary"],
        linestyle="--",
        alpha=0.5,
        linewidth=1.5,
        label="Good Quality (7.0)",
    )

    # Customize
    ax.set_xlabel(
        "Course Difficulty Level", fontsize=STYLE["label_size"], fontweight="bold"
    )
    ax.set_ylabel(
        "Composite Quality Score (0-10)",
        fontsize=STYLE["label_size"],
        fontweight="bold",
    )
    ax.set_title(
        "Model Performance vs Course Difficulty Level",
        fontsize=STYLE["title_size"],
        fontweight="bold",
        pad=20,
    )
    ax.set_ylim(0, 10)
    ax.legend(loc="upper right", fontsize=10, framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    output_path = OUTPUT_DIR / "fig4_difficulty_performance.png"
    plt.savefig(output_path, dpi=STYLE["dpi"], bbox_inches="tight")
    print(f"\n✅ Saved: {output_path}")

    plt.close()

    return output_path


if __name__ == "__main__":
    create_difficulty_performance()
