#!/usr/bin/env python3
"""
Master script to generate all dissertation figures.

Generates 4 essential figures for Chapter 6 evaluation:
1. Prerequisite accuracy distribution
2. Quality metrics radar chart
3. Domain success rate analysis
4. Difficulty vs performance analysis

All figures saved to docs/figures/ at 300 DPI publication quality.
"""

import time
from pathlib import Path

from fig1_prerequisite_distribution import create_prerequisite_distribution
from fig2_quality_radar import create_quality_radar
from fig3_domain_success_rate import create_domain_success_rate
from fig4_difficulty_performance import create_difficulty_performance


def main():
    """Generate all dissertation figures."""
    print("\n" + "=" * 80)
    print("GENERATING ALL DISSERTATION FIGURES")
    print("=" * 80)

    start_time = time.time()

    figures = [
        ("Figure 1: Prerequisite Distribution", create_prerequisite_distribution),
        ("Figure 2: Quality Radar", create_quality_radar),
        ("Figure 3: Domain Success Rate", create_domain_success_rate),
        ("Figure 4: Difficulty vs Performance", create_difficulty_performance),
    ]

    output_paths = []

    for i, (name, func) in enumerate(figures, 1):
        print(f"\n[{i}/{len(figures)}] Generating {name}...")
        print("-" * 80)

        try:
            output_path = func()
            output_paths.append(output_path)
            print(f"✅ {name} complete")
        except Exception as e:
            print(f"❌ Error generating {name}: {e}")
            continue

    elapsed_time = time.time() - start_time

    print("\n" + "=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)
    print(
        f"Generated {len(output_paths)}/{len(figures)} figures in {elapsed_time:.1f}s"
    )
    print(
        f"\nOutput directory: {Path(output_paths[0]).parent if output_paths else 'N/A'}"
    )

    if output_paths:
        print("\nGenerated files:")
        for path in output_paths:
            print(f"   ✓ {path.name}")

    print("\n🎓 Ready for Chapter 6 evaluation writing!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
