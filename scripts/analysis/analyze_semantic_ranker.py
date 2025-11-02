#!/usr/bin/env python3
"""Analyze semantic ranker performance from evaluation results."""

import sys
from pathlib import Path

import pandas as pd


def load_evaluation_data():
    """Load evaluation results CSV."""
    csv_path = Path("data/evaluation/evaluation_results.csv")
    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} test cases from {csv_path}")
    return df


def analyze_ranker_metrics(df):
    """Analyze semantic ranker performance metrics."""
    successful = df[df["pipeline_success"] == 1]
    n_success = len(successful)

    print("\n" + "=" * 70)
    print("SEMANTIC RANKER ANALYSIS")
    print("=" * 70)

    print(f"\n📊 Dataset: {n_success} successful test cases (out of {len(df)} total)")

    print("\n### RAG Pipeline Filtering")
    print("-" * 70)

    available = successful["num_modules_available"]
    filtered = successful["num_modules_filtered"]
    ranked = successful["num_modules_ranked"]

    print(
        f"Average modules available:  {available.mean():.1f} (σ={available.std():.1f})"
    )
    print(f"Average modules filtered:   {filtered.mean():.1f} (σ={filtered.std():.1f})")
    print(f"Average modules ranked:     {ranked.mean():.1f} (σ={ranked.std():.1f})")

    filter_rate = ((available - filtered) / available * 100).mean()
    print(f"\n✓ Filtering efficiency: {filter_rate:.1f}% of modules removed")
    print(f"  (970 modules → {filtered.mean():.0f} after domain/difficulty filter)")

    print("\n### Semantic Ranking Performance")
    print("-" * 70)

    ranking_time = successful["semantic_ranking_time_sec"]
    print(
        f"Average ranking time: {ranking_time.mean():.3f}s (σ={ranking_time.std():.3f}s)"
    )
    print(f"Min ranking time:     {ranking_time.min():.3f}s")
    print(f"Max ranking time:     {ranking_time.max():.3f}s")
    print(
        f"\n✓ Efficient ranking: ~{ranking_time.mean() / filtered.mean() * 1000:.1f}ms per component"
    )

    print("\n### Data Availability Check")
    print("-" * 70)

    missing_scores = True

    if missing_scores:
        print("⚠️  MISSING DATA: ranking_stats.avg_score not saved to CSV")
        print("   Required for score distribution and correlation analysis")
        print("   Solution: Modify metrics.py to save avg_score, min_score, max_score")

    print("\n### Pedagogical Boosting Impact")
    print("-" * 70)

    beginner_courses = successful[successful["level"] == "beginner"]
    other_courses = successful[successful["level"] != "beginner"]

    print(f"Beginner courses:     {len(beginner_courses)}")
    print(f"Non-beginner courses: {len(other_courses)}")

    if len(beginner_courses) > 0:
        beginner_prereq = beginner_courses["prerequisite_accuracy"].mean()
        other_prereq = (
            other_courses["prerequisite_accuracy"].mean()
            if len(other_courses) > 0
            else 0
        )

        print("\nPrerequisite accuracy:")
        print(f"  Beginner:     {beginner_prereq:.1%}")
        print(f"  Other levels: {other_prereq:.1%}")

        if beginner_prereq > other_prereq:
            print(
                f"  ✓ Boosting appears effective (+{(beginner_prereq - other_prereq)*100:.1f}% improvement)"
            )
        else:
            print("  ⚠️ No clear boosting benefit")

    print("\n### Ranker Contribution to Quality (Limited Analysis)")
    print("-" * 70)

    print("Cannot compute avg_score → quality correlation (data not available)")
    print("Alternative: Check if ranking_time correlates with quality")

    correlation = (
        successful[["semantic_ranking_time_sec", "overall_quality_score"]]
        .corr()
        .iloc[0, 1]
    )
    print(f"\nRanking time vs quality correlation: r={correlation:.3f}")

    if abs(correlation) < 0.3:
        print("  → Weak correlation (expected)")

    return successful


def generate_summary_report(df):
    """Generate summary for dissertation."""
    successful = df[df["pipeline_success"] == 1]

    print("\n" + "=" * 70)
    print("SUMMARY FOR DISSERTATION CHAPTER 6")
    print("=" * 70)

    print("\n### Key Findings:")
    print(
        f"1. Filtering: 970 → {successful['num_modules_filtered'].mean():.0f} modules "
        f"({(1 - successful['num_modules_filtered'].mean()/970)*100:.1f}% reduction)"
    )
    print(
        f"2. Ranking speed: {successful['semantic_ranking_time_sec'].mean():.2f}s average"
    )
    print(
        f"3. Top-K selection: {successful['num_modules_ranked'].mean():.0f} modules for generation"
    )
    print("4. Missing analysis: Similarity score distribution")

    print("\n### Recommended Actions:")
    print("1. ✓ Fig 4 (RAG pipeline Sankey)")
    print("2. ✓ Fig 11 (pedagogical boosting)")
    print("3. ⚠️ Fig 9 (score distribution) - needs avg_score")
    print("4. ⚠️ Fig 10 (correlation) - needs avg_score")


def main():
    """Main analysis entry point."""
    print("Semantic Ranker Performance Analysis")
    print("=" * 70)

    # Load data
    df = load_evaluation_data()

    # Analyze ranker metrics
    successful_df = analyze_ranker_metrics(df)

    # Generate summary
    generate_summary_report(df)

    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
