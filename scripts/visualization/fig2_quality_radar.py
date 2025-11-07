#!/usr/bin/env python3
"""
Figure 2: Quality Metrics Radar Chart

Shows balanced view of model performance across 5 key dimensions:
- Prerequisite accuracy (weakest: 29.6%)
- Semantic relevance (strongest: 81.4%)
- Difficulty progression (good: 77.7%)
- Topic diversity (moderate: 64.3%)
- Bloom's taxonomy (moderate: 58.4%)
"""

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for headless environment
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from config import COLORS, DATA_PATH, OUTPUT_DIR, STYLE


def create_quality_radar():
    """Create radar chart showing balanced performance across quality dimensions."""
    df = pd.read_csv(DATA_PATH)
    successful = df[df["pipeline_success"] == 1]

    # Calculate mean scores for each dimension (0-1 scale)
    metrics = {
        "Prerequisite\nAccuracy": successful["prerequisite_accuracy"].mean(),
        "Semantic\nRelevance": successful["semantic_avg_score"].mean(),
        "Difficulty\nProgression": successful["difficulty_progression"].mean(),
        "Topic\nDiversity": successful["topic_diversity"].mean(),
        "Bloom's\nTaxonomy": successful["blooms_taxonomy_coverage"].mean(),
    }

    print("=" * 80)
    print("QUALITY METRICS RADAR")
    print("=" * 80)
    for metric, value in metrics.items():
        metric_clean = metric.replace("\n", " ")
        print(f"{metric_clean:25s}: {value:.1%}")
    print("=" * 80)

    categories = list(metrics.keys())
    values = list(metrics.values())

    # Close the radar chart by repeating first value
    values += values[:1]

    # Compute angle for each axis
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]

    plt.style.use("seaborn-v0_8-darkgrid")
    fig, ax = plt.subplots(
        figsize=STYLE["figure_size"],
        subplot_kw=dict(projection="polar"),
        dpi=STYLE["dpi"],
    )

    # Plot data
    ax.plot(
        angles,
        values,
        "o-",
        linewidth=2,
        color=COLORS["primary"],
        label="Model Performance",
    )
    ax.fill(angles, values, alpha=0.25, color=COLORS["primary"])

    # Add reference circle at 80% (good performance threshold)
    reference = [0.8] * len(angles)
    ax.plot(
        angles,
        reference,
        "--",
        linewidth=1,
        color=COLORS["secondary"],
        alpha=0.5,
        label="Good (80%)",
    )

    # Customize
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=STYLE["label_size"])
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["20%", "40%", "60%", "80%", "100%"], fontsize=10)
    ax.set_title(
        "Model Performance Across Quality Dimensions",
        fontsize=STYLE["title_size"],
        fontweight="bold",
        pad=20,
    )
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    output_path = OUTPUT_DIR / "fig2_quality_radar.png"
    plt.savefig(output_path, dpi=STYLE["dpi"], bbox_inches="tight")
    print(f"\n✅ Saved: {output_path}")

    plt.close()

    return output_path


if __name__ == "__main__":
    create_quality_radar()
