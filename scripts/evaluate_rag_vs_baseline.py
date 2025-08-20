#!/usr/bin/env python3
"""
RAG vs Baseline T5 Comparison Script
Compare RAG-enhanced generation with baseline T5 for syllabus generation
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
from typing import Any

from src.rag.rag_system import generate_rag_syllabus
from src.rag.rag_t5_generator import RAGEnhancedT5Generator


class BaselineT5Generator:
    """Baseline T5 generator without RAG enhancement"""

    def __init__(self, model_name: str = "t5-small"):
        self.generator = RAGEnhancedT5Generator(model_name)

    def generate_syllabus(self, requirements: dict[str, Any]) -> str:
        """Generate syllabus using only course requirements (no RAG)"""

        # Create simple prompt without retrieved components
        prompt = f"Generate syllabus for: {requirements.get('title', '')}\n"
        prompt += f"Domain: {requirements.get('domain', '')} Level: {requirements.get('level', '')}\n"
        prompt += f"Description: {requirements.get('description', '')}\n"

        return self.generator.generate_syllabus(prompt)


def compare_rag_vs_baseline():
    """Compare RAG-enhanced generation with baseline T5"""

    print("🔬 Starting RAG vs Baseline Comparison...")

    # Test cases covering different domains and levels
    test_cases = [
        {
            "title": "Data Structures and Algorithms",
            "domain": "Computer Science",
            "level": "undergraduate",
            "description": "Introduction to fundamental data structures and algorithmic problem solving",
        },
        {
            "title": "Project Management Fundamentals",
            "domain": "Leadership",
            "level": "professional",
            "description": "Essential project management principles and methodologies for business professionals",
        },
        {
            "title": "Machine Learning in Healthcare",
            "domain": "Data Science",
            "level": "graduate",
            "description": "Advanced machine learning techniques applied to healthcare data and medical diagnostics",
        },
        {
            "title": "Digital Marketing Strategy",
            "domain": "Business",
            "level": "undergraduate",
            "description": "Modern digital marketing approaches and social media strategy development",
        },
        {
            "title": "Linear Algebra for Engineers",
            "domain": "Mathematics",
            "level": "undergraduate",
            "description": "Mathematical foundations of linear algebra with engineering applications",
        },
    ]

    # Initialize baseline generator
    print("📊 Initializing baseline T5 generator...")
    baseline_generator = BaselineT5Generator()

    results = []
    total_start_time = time.time()

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}/{len(test_cases)}: {test_case['title']}")
        print(f"   Domain: {test_case['domain']} | Level: {test_case['level']}")

        # Generate with RAG system
        print("   🔍 Generating with RAG system...")
        rag_start_time = time.time()
        try:
            rag_result = generate_rag_syllabus(test_case)
            rag_generation_time = time.time() - rag_start_time
            rag_success = True
        except Exception as e:
            print(f"   ❌ RAG generation failed: {e}")
            rag_result = {
                "syllabus_content": f"ERROR: {str(e)}",
                "retrieved_components": {},
            }
            rag_generation_time = time.time() - rag_start_time
            rag_success = False

        # Generate with baseline system
        print("   🎯 Generating with baseline T5...")
        baseline_start_time = time.time()
        try:
            baseline_result = baseline_generator.generate_syllabus(test_case)
            baseline_generation_time = time.time() - baseline_start_time
            baseline_success = True
        except Exception as e:
            print(f"   ❌ Baseline generation failed: {e}")
            baseline_result = f"ERROR: {str(e)}"
            baseline_generation_time = time.time() - baseline_start_time
            baseline_success = False

        # Analyze retrieved components
        retrieved_stats = {}
        if rag_success and "retrieved_components" in rag_result:
            for comp_type, components in rag_result["retrieved_components"].items():
                retrieved_stats[comp_type] = {
                    "count": len(components),
                    "titles": [
                        comp.get("title", "N/A") for comp in components[:2]
                    ],  # First 2 titles
                }

        # Store results
        result = {
            "test_case": test_case,
            "rag_output": rag_result.get("syllabus_content", "")
            if rag_success
            else rag_result["syllabus_content"],
            "baseline_output": baseline_result,
            "retrieved_components_stats": retrieved_stats,
            "rag_prompt": rag_result.get("prompt", "") if rag_success else "",
            "performance": {
                "rag_generation_time": rag_generation_time,
                "baseline_generation_time": baseline_generation_time,
                "rag_success": rag_success,
                "baseline_success": baseline_success,
            },
            "quality_metrics": analyze_output_quality(
                rag_result.get("syllabus_content", "") if rag_success else "",
                baseline_result if baseline_success else "",
                test_case,
            ),
        }

        results.append(result)

        print(
            f"   ✅ RAG: {rag_generation_time:.2f}s | Baseline: {baseline_generation_time:.2f}s"
        )

    total_time = time.time() - total_start_time
    print(f"\n🎉 Comparison completed in {total_time:.2f}s")

    # Save detailed results
    output_file = "evaluation_results_rag_vs_baseline.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"📁 Detailed results saved to: {output_file}")

    # Print summary
    print_comparison_summary(results)

    return results


def analyze_output_quality(
    rag_output: str, baseline_output: str, test_case: dict[str, Any]
) -> dict[str, Any]:
    """Analyze quality metrics for both outputs"""

    def calculate_metrics(text: str) -> dict[str, Any]:
        if not text or text.startswith("ERROR:"):
            return {
                "length": 0,
                "word_count": 0,
                "contains_title": False,
                "contains_domain": False,
            }

        words = text.split()
        return {
            "length": len(text),
            "word_count": len(words),
            "contains_title": test_case["title"].lower() in text.lower(),
            "contains_domain": test_case["domain"].lower() in text.lower(),
            "repetition_score": calculate_repetition_score(text),
        }

    return {
        "rag_metrics": calculate_metrics(rag_output),
        "baseline_metrics": calculate_metrics(baseline_output),
    }


def calculate_repetition_score(text: str) -> float:
    """Calculate repetition score (0-1, lower is better)"""
    if not text:
        return 0.0

    words = text.split()
    if len(words) < 10:
        return 0.0

    # Count repeated phrases of 3+ words
    phrases = []
    for i in range(len(words) - 2):
        phrase = " ".join(words[i : i + 3])
        phrases.append(phrase)

    unique_phrases = set(phrases)
    repetition_ratio = 1.0 - (len(unique_phrases) / len(phrases)) if phrases else 0.0

    return min(repetition_ratio, 1.0)


def print_comparison_summary(results: list[dict[str, Any]]):
    """Print summary of comparison results"""

    print("\n" + "=" * 80)
    print("🏆 RAG vs BASELINE COMPARISON SUMMARY")
    print("=" * 80)

    rag_successes = sum(1 for r in results if r["performance"]["rag_success"])
    baseline_successes = sum(1 for r in results if r["performance"]["baseline_success"])

    print("📊 Success Rate:")
    print(
        f"   RAG System: {rag_successes}/{len(results)} ({rag_successes/len(results)*100:.1f}%)"
    )
    print(
        f"   Baseline:   {baseline_successes}/{len(results)} ({baseline_successes/len(results)*100:.1f}%)"
    )

    # Performance metrics
    rag_times = [
        r["performance"]["rag_generation_time"]
        for r in results
        if r["performance"]["rag_success"]
    ]
    baseline_times = [
        r["performance"]["baseline_generation_time"]
        for r in results
        if r["performance"]["baseline_success"]
    ]

    if rag_times and baseline_times:
        print("\n⏱️  Average Generation Time:")
        print(f"   RAG System: {sum(rag_times)/len(rag_times):.2f}s")
        print(f"   Baseline:   {sum(baseline_times)/len(baseline_times):.2f}s")

    # Quality comparison
    print("\n📝 Output Quality Analysis:")

    rag_word_counts = []
    baseline_word_counts = []
    rag_repetition_scores = []
    baseline_repetition_scores = []

    for result in results:
        if result["performance"]["rag_success"]:
            rag_metrics = result["quality_metrics"]["rag_metrics"]
            rag_word_counts.append(rag_metrics["word_count"])
            rag_repetition_scores.append(rag_metrics.get("repetition_score", 0))

        if result["performance"]["baseline_success"]:
            baseline_metrics = result["quality_metrics"]["baseline_metrics"]
            baseline_word_counts.append(baseline_metrics["word_count"])
            baseline_repetition_scores.append(
                baseline_metrics.get("repetition_score", 0)
            )

    if rag_word_counts:
        print(f"   RAG Average Words: {sum(rag_word_counts)/len(rag_word_counts):.1f}")
        print(
            f"   RAG Repetition Score: {sum(rag_repetition_scores)/len(rag_repetition_scores):.3f}"
        )

    if baseline_word_counts:
        print(
            f"   Baseline Average Words: {sum(baseline_word_counts)/len(baseline_word_counts):.1f}"
        )
        print(
            f"   Baseline Repetition Score: {sum(baseline_repetition_scores)/len(baseline_repetition_scores):.3f}"
        )

    # Component retrieval stats
    print("\n🔍 Retrieved Components Summary:")
    total_modules = sum(
        r["retrieved_components_stats"].get("modules", {}).get("count", 0)
        for r in results
    )
    total_activities = sum(
        r["retrieved_components_stats"].get("activities", {}).get("count", 0)
        for r in results
    )
    total_assessments = sum(
        r["retrieved_components_stats"].get("assessments", {}).get("count", 0)
        for r in results
    )

    print(f"   Total Modules Retrieved: {total_modules}")
    print(f"   Total Activities Retrieved: {total_activities}")
    print(f"   Total Assessments Retrieved: {total_assessments}")

    print("\n📄 Detailed Test Results:")
    print("-" * 80)

    for i, result in enumerate(results, 1):
        test_case = result["test_case"]
        print(f"\n{i}. {test_case['title']} ({test_case['domain']})")

        if result["performance"]["rag_success"]:
            rag_quality = result["quality_metrics"]["rag_metrics"]
            print(
                f"   RAG: {rag_quality['word_count']} words, repetition: {rag_quality.get('repetition_score', 0):.3f}"
            )
        else:
            print("   RAG: FAILED")

        if result["performance"]["baseline_success"]:
            baseline_quality = result["quality_metrics"]["baseline_metrics"]
            print(
                f"   Baseline: {baseline_quality['word_count']} words, repetition: {baseline_quality.get('repetition_score', 0):.3f}"
            )
        else:
            print("   Baseline: FAILED")

        # Show retrieved components
        if result["retrieved_components_stats"]:
            components_summary = []
            for comp_type, stats in result["retrieved_components_stats"].items():
                components_summary.append(f"{stats['count']} {comp_type}")
            print(f"   Retrieved: {', '.join(components_summary)}")


def main():
    """Main evaluation function"""
    try:
        results = compare_rag_vs_baseline()
        print("\n✅ Evaluation completed successfully!")
        print("📊 Results available in evaluation_results_rag_vs_baseline.json")
        return results
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
