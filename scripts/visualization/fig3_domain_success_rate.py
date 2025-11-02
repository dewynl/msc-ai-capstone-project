#!/usr/bin/env python3
"""
Figure 3: Domain Success Rate Analysis

Shows success rate by domain, highlighting:
- Computer Science, Math, Physics: 100% success
- Engineering: 0% success (complexity handling failure)
- Interdisciplinary: 0% success (integration failure)
"""

import matplotlib.pyplot as plt
import pandas as pd
from config import COLORS, DATA_PATH, OUTPUT_DIR, STYLE


def create_domain_success_rate():
    """Create grouped bar chart showing success rate by domain."""
    df = pd.read_csv(DATA_PATH)

    # Calculate success rate by domain
    domain_stats = (
        df.groupby("domain")
        .agg(total=("test_id", "count"), successful=("pipeline_success", "sum"))
        .reset_index()
    )

    domain_stats["success_rate"] = (
        domain_stats["successful"] / domain_stats["total"]
    ) * 100

    # Sort by success rate
    domain_stats = domain_stats.sort_values("success_rate", ascending=False)

    print("=" * 80)
    print("DOMAIN SUCCESS RATE ANALYSIS")
    print("=" * 80)
    for _, row in domain_stats.iterrows():
        domain = row["domain"].replace("_", " ").title()
        print(
            f"{domain:20s}: {row['successful']:2.0f}/{row['total']:2.0f} ({row['success_rate']:5.1f}%)"
        )
    print("=" * 80)

    plt.style.use("seaborn-v0_8-darkgrid")
    fig, ax = plt.subplots(figsize=STYLE["figure_size"], dpi=STYLE["dpi"])

    # Create bars with color coding
    colors = []
    for rate in domain_stats["success_rate"]:
        if rate == 100:
            colors.append(COLORS["success"])
        elif rate > 50:
            colors.append(COLORS["warning"])
        else:
            colors.append(COLORS["danger"])

    bars = ax.bar(
        range(len(domain_stats)),
        domain_stats["success_rate"],
        color=colors,
        edgecolor="black",
        linewidth=1,
    )

    # Add value labels on bars
    for bar, value, total, successful in zip(
        bars,
        domain_stats["success_rate"],
        domain_stats["total"],
        domain_stats["successful"],
    ):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 2,
            f"{value:.0f}%\n({successful:.0f}/{total:.0f})",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    # Customize
    ax.set_xlabel("Domain", fontsize=STYLE["label_size"], fontweight="bold")
    ax.set_ylabel("Success Rate (%)", fontsize=STYLE["label_size"], fontweight="bold")
    ax.set_title(
        "Syllabus Generation Success Rate by Domain",
        fontsize=STYLE["title_size"],
        fontweight="bold",
        pad=20,
    )
    ax.set_xticks(range(len(domain_stats)))
    ax.set_xticklabels(
        [d.replace("_", " ").title() for d in domain_stats["domain"]],
        rotation=45,
        ha="right",
    )
    ax.set_ylim(0, 110)
    ax.axhline(y=100, color=COLORS["secondary"], linestyle="--", alpha=0.5, linewidth=1)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    output_path = OUTPUT_DIR / "fig3_domain_success_rate.png"
    plt.savefig(output_path, dpi=STYLE["dpi"], bbox_inches="tight")
    print(f"\n✅ Saved: {output_path}")

    plt.close()

    return output_path


if __name__ == "__main__":
    create_domain_success_rate()
