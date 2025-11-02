#!/usr/bin/env python3
"""
Extract top-quality syllabi from evaluation results to use as expert examples.

This creates the foundation for the feedback-enhanced RAG system (Option 3).
"""

import json
from pathlib import Path

import pandas as pd


def compute_composite_quality_score(row):
    """
    Compute composite quality score from evaluation metrics.

    Weights:
    - prerequisite_accuracy: 30% (most important for pedagogical soundness)
    - semantic_avg_score: 25% (component relevance)
    - difficulty_progression: 20% (logical sequencing)
    - topic_diversity: 15% (breadth of coverage)
    - blooms_taxonomy_coverage: 10% (learning objective quality)
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
        # Handle NaN values
        if pd.isna(value):
            value = 0.0
        score += value * weight

    # Convert to 0-10 scale
    return score * 10


def extract_expert_syllabi(
    evaluation_csv_path: str,
    test_suite_path: str,
    output_json_path: str,
    top_n: int = 10,
    min_quality_threshold: float = 7.0,
):
    """
    Extract top N high-quality syllabi from evaluation results.

    Args:
        evaluation_csv_path: Path to evaluation_results.csv
        test_suite_path: Path to evaluation_suite.json (for full requirements)
        output_json_path: Where to save expert_syllabi.json
        top_n: Number of expert examples to extract
        min_quality_threshold: Minimum quality score (0-10 scale)
    """
    print("=" * 80)
    print("EXTRACTING EXPERT SYLLABI FROM EVALUATION RESULTS")
    print("=" * 80)

    # Load evaluation results
    df = pd.read_csv(evaluation_csv_path)
    print(f"\n📊 Loaded {len(df)} test cases from evaluation")

    # Filter for successful generations only
    successful = df[df["pipeline_success"] == 1].copy()
    print(f"   ✓ {len(successful)} successful generations")

    if len(successful) == 0:
        print("\n❌ No successful test cases found!")
        return

    # Compute composite quality score
    successful["composite_quality"] = successful.apply(
        compute_composite_quality_score, axis=1
    )

    # Filter by minimum quality threshold
    high_quality = successful[successful["composite_quality"] >= min_quality_threshold]
    print(
        f"   ✓ {len(high_quality)} cases meet quality threshold (≥{min_quality_threshold}/10)"
    )

    if len(high_quality) == 0:
        print("\n⚠️  No cases meet threshold. Lowering to 5.0...")
        min_quality_threshold = 5.0
        high_quality = successful[
            successful["composite_quality"] >= min_quality_threshold
        ]
        print(f"   ✓ {len(high_quality)} cases meet lower threshold")

    # Sort by composite quality score
    high_quality = high_quality.sort_values("composite_quality", ascending=False)

    # Take top N
    top_cases = high_quality.head(top_n)
    print(f"\n🎓 Selected top {len(top_cases)} expert examples:")

    # Load test suite to get full requirements
    with open(test_suite_path) as f:
        test_suite = json.load(f)

    test_cases_by_id = {tc["test_id"]: tc for tc in test_suite["test_cases"]}

    # Build expert examples list
    expert_syllabi = []

    for idx, (_, row) in enumerate(top_cases.iterrows(), 1):
        test_id = row["test_id"]

        # Get full requirements from test suite
        test_case = test_cases_by_id.get(test_id, {})
        requirements = test_case.get("requirements", {})

        expert = {
            "expert_id": f"expert_{idx:02d}",
            "test_id": test_id,
            "requirements": {
                "title": row["course_title"],
                "domain": row["domain"],
                "level": row["level"],
                "description": requirements.get("description", ""),
                "duration": requirements.get("duration", "semester"),
            },
            "quality_metrics": {
                "composite_quality": float(row["composite_quality"]),
                "prerequisite_accuracy": float(row["prerequisite_accuracy"]),
                "semantic_avg_score": float(row["semantic_avg_score"]),
                "difficulty_progression": float(row["difficulty_progression"]),
                "topic_diversity": float(row["topic_diversity"]),
                "blooms_taxonomy_coverage": float(row["blooms_taxonomy_coverage"]),
            },
            "structure": {
                "num_modules": int(row["num_modules"]),
                "num_activities": int(row["num_activities"]),
                "num_assessments": int(row["num_assessments"]),
                "total_components": int(row["total_components"]),
            },
            "metadata": {
                "timestamp": row["timestamp"],
                "generation_time_sec": float(row["generation_time_sec"]),
            },
        }

        print(f"   {idx}. {row['course_title']}")
        print(f"      Quality: {row['composite_quality']:.2f}/10")
        print(f"      Prerequisites: {row['prerequisite_accuracy']:.1%}")
        print(f"      Semantic Match: {row['semantic_avg_score']:.3f}")

        expert_syllabi.append(expert)

    output_path = Path(output_json_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        "version": "1.0",
        "created_at": pd.Timestamp.now().isoformat(),
        "source": "evaluation_results.csv",
        "selection_criteria": {
            "min_quality_threshold": min_quality_threshold,
            "top_n": top_n,
            "quality_weights": {
                "prerequisite_accuracy": 0.30,
                "semantic_avg_score": 0.25,
                "difficulty_progression": 0.20,
                "topic_diversity": 0.15,
                "blooms_taxonomy_coverage": 0.10,
            },
        },
        "expert_syllabi": expert_syllabi,
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✅ Saved {len(expert_syllabi)} expert syllabi to: {output_path}")
    print(f"   Average quality score: {top_cases['composite_quality'].mean():.2f}/10")
    print(
        f"   Quality range: {top_cases['composite_quality'].min():.2f} - {top_cases['composite_quality'].max():.2f}"
    )

    return expert_syllabi


def main():
    """Extract expert syllabi from evaluation results."""
    base_dir = Path(__file__).parent.parent.parent

    evaluation_csv = base_dir / "data" / "evaluation" / "evaluation_results.csv"
    test_suite = base_dir / "configs" / "evaluation_suite.json"
    output_json = base_dir / "data" / "feedback" / "expert_syllabi.json"

    if not evaluation_csv.exists():
        print(f"❌ Evaluation results not found: {evaluation_csv}")
        return

    if not test_suite.exists():
        print(f"❌ Test suite not found: {test_suite}")
        return

    expert_syllabi = extract_expert_syllabi(
        str(evaluation_csv),
        str(test_suite),
        str(output_json),
        top_n=10,
        min_quality_threshold=7.0,
    )

    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. Expert syllabi extracted ✓")
    print("2. Next: Implement semantic similarity search for expert retrieval")
    print("3. Then: Add feedback collection UI to Streamlit")
    print("4. Finally: Implement periodic fine-tuning")


if __name__ == "__main__":
    main()
