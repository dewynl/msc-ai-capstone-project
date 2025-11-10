#!/usr/bin/env python3
"""
Figure 3: Quality Metrics Breakdown by Domain

Shows how different domains perform across quality dimensions:
- Computer Science: Strongest overall (66.7% prerequisite accuracy)
- Mathematics: Weakest prerequisites (30%), but good Bloom's (43.3%)
- Physics: Similar to Math, balanced across metrics

Grouped bar chart comparing 5 quality metrics across 3 domains.
"""

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for headless environment
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from config import COLORS, DATA_PATH, OUTPUT_DIR, STYLE


def create_quality_by_domain():
    """Create grouped bar chart showing quality metrics breakdown by domain."""
    df = pd.read_csv(DATA_PATH)
    successful = df[df["pipeline_success"] == 1]

    # Calculate mean scores by domain
    domain_quality = successful.groupby("domain").agg(
        {
            "prerequisite_accuracy": "mean",
            "semantic_avg_score": "mean",
            "difficulty_progression": "mean",
            "topic_diversity": "mean",
            "blooms_taxonomy_coverage": "mean",
        }
    )

    print("=" * 80)
    print("QUALITY METRICS BY DOMAIN")
    print("=" * 80)
    for domain in domain_quality.index:
        print(f"\n{domain.replace('_', ' ').title()}:")
        for metric in domain_quality.columns:
            value = domain_quality.loc[domain, metric]
            metric_name = metric.replace("_", " ").title()
            print(f"  {metric_name:30s}: {value:.1%}")
    print("=" * 80)

    # Prepare data for grouped bar chart
    domains = ["Computer\nScience", "Mathematics", "Physics"]
    metrics = [
        "Prerequisite\nAccuracy",
        "Semantic\nRelevance",
        "Difficulty\nProgression",
        "Topic\nDiversity",
        "Bloom's\nTaxonomy",
    ]

    data = domain_quality.values.T  # Transpose: metrics x domains

    plt.style.use("seaborn-v0_8-darkgrid")
    fig, ax = plt.subplots(figsize=STYLE["figure_size"], dpi=STYLE["dpi"])

    # Set up grouped bar positions
    x = np.arange(len(metrics))
    width = 0.25
    multiplier = 0

    # Color scheme for domains
    domain_colors = [COLORS["primary"], COLORS["teal"], COLORS["purple"]]

    # Create bars for each domain
    for idx, domain in enumerate(domains):
        offset = width * multiplier
        bars = ax.bar(
            x + offset,
            data[:, idx],
            width,
            label=domain,
            color=domain_colors[idx],
            edgecolor="black",
            linewidth=1,
        )

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.02,
                f"{height:.0%}",
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
            )

        multiplier += 1

    # Reference line at 70% (good performance threshold)
    ax.axhline(
        y=0.7,
        color=COLORS["secondary"],
        linestyle="--",
        alpha=0.5,
        linewidth=1.5,
        label="Good (70%)",
    )

    # Customize
    ax.set_xlabel("Quality Metric", fontsize=STYLE["label_size"], fontweight="bold")
    ax.set_ylabel("Performance (%)", fontsize=STYLE["label_size"], fontweight="bold")
    ax.set_title(
        "Quality Metrics Performance by Domain",
        fontsize=STYLE["title_size"],
        fontweight="bold",
        pad=25,  # Increased padding
    )
    ax.set_xticks(x + width)
    ax.set_xticklabels(metrics, fontsize=10)
    ax.set_ylim(0, 1.08)  # Increased to accommodate percentage labels
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0%", "20%", "40%", "60%", "80%", "100%"])
    ax.legend(
        loc="upper left", fontsize=10, framealpha=0.95, ncol=2
    )  # Moved to upper left to avoid overlap
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    output_path = OUTPUT_DIR / "fig3_quality_by_domain.png"
    plt.savefig(output_path, dpi=STYLE["dpi"], bbox_inches="tight")
    print(f"\n✅ Saved: {output_path}")

    plt.close()

    return output_path


if __name__ == "__main__":
    create_quality_by_domain()
