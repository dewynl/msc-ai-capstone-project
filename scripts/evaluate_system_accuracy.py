#!/usr/bin/env python3
"""
RAG System Accuracy Evaluation
Comprehensive evaluation of syllabus generation quality and accuracy
"""

import json
import os
import re
import sys
from collections import defaultdict
from typing import Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.rag_system import generate_rag_syllabus


def evaluate_domain_accuracy(
    result: dict[str, Any], requirements: dict[str, Any]
) -> dict[str, float]:
    """Evaluate domain-specific accuracy"""

    required_domain = requirements.get("domain", "").lower()
    content = result.get("syllabus_content", "").lower()
    retrieved = result.get("retrieved_components", {})

    metrics = {}

    # 1. Domain Consistency - Are retrieved components from correct domain?
    total_components = sum(len(comps) for comps in retrieved.values())
    domain_matches = 0

    for comp_type, components in retrieved.items():
        for comp in components:
            comp_domain = comp.get("domain", "").lower()
            if required_domain in comp_domain or comp_domain in required_domain:
                domain_matches += 1

    metrics["domain_consistency"] = (
        domain_matches / total_components if total_components > 0 else 0
    )

    # 2. Content Domain Relevance - Does generated content mention correct domain?
    domain_keywords = {
        "computer science": [
            "algorithm",
            "data structure",
            "programming",
            "software",
            "coding",
        ],
        "data science": [
            "data",
            "analysis",
            "statistics",
            "machine learning",
            "visualization",
        ],
        "mathematics": ["equation", "function", "calculus", "algebra", "geometry"],
        "physics": ["force", "energy", "wave", "quantum", "electromagnetic"],
        "software development": [
            "development",
            "programming",
            "coding",
            "application",
            "software",
        ],
        "aws cloud": ["aws", "cloud", "ec2", "lambda", "s3"],
        "project management": [
            "project",
            "management",
            "planning",
            "resource",
            "timeline",
        ],
        "leadership": ["leadership", "team", "management", "communication", "decision"],
    }

    relevant_keywords = domain_keywords.get(required_domain, [])
    if relevant_keywords:
        keyword_matches = sum(1 for keyword in relevant_keywords if keyword in content)
        metrics["content_domain_relevance"] = keyword_matches / len(relevant_keywords)
    else:
        metrics["content_domain_relevance"] = 0.5  # Neutral for unknown domains

    return metrics


def evaluate_structural_quality(content: str) -> dict[str, float]:
    """Evaluate structural quality of generated syllabus"""

    metrics = {}

    # 1. Required sections presence
    required_sections = [
        "course description",
        "learning objectives",
        "weekly schedule",
        "assessment plan",
        "grading scale",
        "course policies",
    ]

    sections_found = 0
    for section in required_sections:
        if section.lower() in content.lower():
            sections_found += 1

    metrics["structural_completeness"] = sections_found / len(required_sections)

    # 2. Assessment table quality
    has_assessment_table = "|" in content and "percentage" in content.lower()
    metrics["assessment_table_present"] = 1.0 if has_assessment_table else 0.0

    # 3. Weekly schedule structure
    week_pattern = r"week \d+"
    weeks_found = len(re.findall(week_pattern, content.lower()))
    metrics["weekly_structure"] = min(weeks_found / 10, 1.0)  # Expect ~10 weeks

    # 4. Learning objectives quality
    objectives_section = re.search(
        r"learning objectives.*?(?=##|$)", content, re.IGNORECASE | re.DOTALL
    )
    if objectives_section:
        objectives_text = objectives_section.group()
        bullet_points = len(re.findall(r"[•\-\*]\s", objectives_text))
        metrics["learning_objectives_count"] = min(
            bullet_points / 5, 1.0
        )  # Expect ~5 objectives
    else:
        metrics["learning_objectives_count"] = 0.0

    return metrics


def evaluate_content_quality(
    content: str, retrieved: dict[str, list]
) -> dict[str, float]:
    """Evaluate content quality and coherence"""

    metrics = {}

    # 1. Content length appropriateness
    word_count = len(content.split())
    # Professional syllabus should be 1000-3000 words
    if 1000 <= word_count <= 3000:
        metrics["length_appropriateness"] = 1.0
    elif word_count < 500:
        metrics["length_appropriateness"] = 0.2  # Too short
    elif word_count > 5000:
        metrics["length_appropriateness"] = 0.6  # Too long
    else:
        metrics["length_appropriateness"] = 0.8  # Close to ideal

    # 2. Repetition detection
    lines = content.split("\n")
    unique_lines = set(line.strip() for line in lines if line.strip())
    metrics["content_uniqueness"] = (
        len(unique_lines) / len([l for l in lines if l.strip()]) if lines else 0
    )

    # 3. Component utilization - How well are retrieved components used?
    total_components = sum(len(comps) for comps in retrieved.values())
    component_mentions = 0

    for comp_type, components in retrieved.items():
        for comp in components:
            comp_title = comp.get("title", "")
            # Check if component concepts appear in content (loose matching)
            title_words = [word for word in comp_title.lower().split() if len(word) > 4]
            if any(
                word in content.lower() for word in title_words[:3]
            ):  # Check first 3 meaningful words
                component_mentions += 1

    metrics["component_utilization"] = (
        component_mentions / total_components if total_components > 0 else 0
    )

    return metrics


def evaluate_professional_formatting(content: str) -> dict[str, float]:
    """Evaluate professional formatting quality"""

    metrics = {}

    # 1. Markdown formatting quality
    headers = len(re.findall(r"^#+\s", content, re.MULTILINE))
    metrics["header_structure"] = min(headers / 8, 1.0)  # Expect ~8 main headers

    # 2. Table formatting
    tables = content.count("|")
    metrics["table_formatting"] = (
        min(tables / 20, 1.0) if tables > 0 else 0
    )  # Assessment table should have ~20+ pipes

    # 3. List formatting
    lists = len(re.findall(r"^[\-\*•]\s", content, re.MULTILINE))
    metrics["list_formatting"] = min(lists / 10, 1.0)  # Expect multiple lists

    # 4. No obvious AI artifacts
    ai_artifacts = [
        "as an ai",
        "i cannot",
        "i don't have",
        "generated with",
        "note:",
        "please note",
        "[insert",
        "placeholder",
    ]
    artifacts_found = sum(1 for artifact in ai_artifacts if artifact in content.lower())
    metrics["professional_tone"] = max(0, 1.0 - (artifacts_found * 0.3))

    return metrics


def run_comprehensive_evaluation(test_cases: list[dict[str, Any]]) -> dict[str, Any]:
    """Run comprehensive evaluation on multiple test cases"""

    print("🎯 Comprehensive RAG System Accuracy Evaluation")
    print("=" * 60)

    all_results = []
    overall_metrics = defaultdict(list)

    for i, requirements in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {requirements['title']}")
        print(f"Domain: {requirements['domain']}, Level: {requirements['level']}")

        try:
            # Generate syllabus
            result = generate_rag_syllabus(requirements)

            if "validation_error" in result:
                print(f"❌ Domain validation failed: {result['validation_error']}")
                continue

            content = result["syllabus_content"]
            retrieved = result["retrieved_components"]

            # Evaluate different aspects
            domain_metrics = evaluate_domain_accuracy(result, requirements)
            structural_metrics = evaluate_structural_quality(content)
            content_metrics = evaluate_content_quality(content, retrieved)
            formatting_metrics = evaluate_professional_formatting(content)

            # Combine metrics
            case_metrics = {
                "case": requirements,
                "domain": domain_metrics,
                "structure": structural_metrics,
                "content": content_metrics,
                "formatting": formatting_metrics,
            }

            all_results.append(case_metrics)

            # Aggregate for overall stats
            for category, metrics in case_metrics.items():
                if isinstance(metrics, dict):
                    for metric_name, value in metrics.items():
                        overall_metrics[f"{category}_{metric_name}"].append(value)

            # Print case summary
            domain_avg = sum(domain_metrics.values()) / len(domain_metrics)
            structural_avg = sum(structural_metrics.values()) / len(structural_metrics)
            content_avg = sum(content_metrics.values()) / len(content_metrics)
            formatting_avg = sum(formatting_metrics.values()) / len(formatting_metrics)

            overall_score = (
                domain_avg + structural_avg + content_avg + formatting_avg
            ) / 4

            print(
                f"  📊 Scores: Domain={domain_avg:.2f}, Structure={structural_avg:.2f}, Content={content_avg:.2f}, Format={formatting_avg:.2f}"
            )
            print(f"  🎯 Overall: {overall_score:.2f}/1.00")

        except Exception as e:
            print(f"❌ Error: {e}")

    # Calculate overall statistics
    print("\n📈 OVERALL SYSTEM ACCURACY")
    print("=" * 40)

    category_averages = {}
    for metric_name, values in overall_metrics.items():
        if values:
            category_averages[metric_name] = sum(values) / len(values)

    # Group by category
    categories = {"domain": [], "structure": [], "content": [], "formatting": []}
    for metric_name, avg_value in category_averages.items():
        for category in categories:
            if metric_name.startswith(category):
                categories[category].append(avg_value)

    overall_system_score = 0
    for category, scores in categories.items():
        if scores:
            category_avg = sum(scores) / len(scores)
            print(f"{category.title()} Accuracy: {category_avg:.3f}")
            overall_system_score += category_avg

    overall_system_score /= len([c for c in categories.values() if c])
    print(f"\n🎯 SYSTEM OVERALL ACCURACY: {overall_system_score:.3f}/1.000")

    # Save detailed results
    results_file = "evaluation_results.json"
    with open(results_file, "w") as f:
        json.dump(
            {
                "overall_score": overall_system_score,
                "category_scores": {
                    k: sum(v) / len(v) if v else 0 for k, v in categories.items()
                },
                "detailed_results": all_results,
                "metric_averages": category_averages,
            },
            f,
            indent=2,
        )

    print(f"\n📄 Detailed results saved to: {results_file}")

    return {
        "overall_score": overall_system_score,
        "category_scores": categories,
        "detailed_results": all_results,
    }


def main():
    """Run accuracy evaluation with diverse test cases"""

    # Diverse test cases covering different domains and complexity
    test_cases = [
        # High-resource domains
        {
            "title": "Data Science Fundamentals",
            "domain": "Data Science",
            "level": "undergraduate",
        },
        {
            "title": "Computer Science Theory",
            "domain": "Computer Science",
            "level": "graduate",
        },
        {
            "title": "Advanced Machine Learning",
            "domain": "Data Science",
            "level": "graduate",
        },
        # Medium-resource domains
        {
            "title": "Mathematical Analysis",
            "domain": "Mathematics",
            "level": "graduate",
        },
        {
            "title": "Physics Fundamentals",
            "domain": "Physics",
            "level": "undergraduate",
        },
        # Lower-resource domains
        {
            "title": "Web Development Bootcamp",
            "domain": "Software Development",
            "level": "professional",
        },
        {
            "title": "AWS Cloud Architecture",
            "domain": "AWS Cloud",
            "level": "professional",
        },
        {
            "title": "Project Management Essentials",
            "domain": "Project Management",
            "level": "professional",
        },
        # Edge cases
        {"title": "Leadership in Crisis", "domain": "Leadership", "level": "executive"},
        {
            "title": "Network Security Fundamentals",
            "domain": "Cisco Networking",
            "level": "professional",
        },
    ]

    run_comprehensive_evaluation(test_cases)


if __name__ == "__main__":
    main()
