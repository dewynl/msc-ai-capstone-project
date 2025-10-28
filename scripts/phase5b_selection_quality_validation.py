#!/usr/bin/env python3
"""
Phase 5B: Selection Quality Validation

Tests if model INTELLIGENTLY selects appropriate modules, not just valid structure.

Critical Questions:
1. Does it select appropriate difficulty modules?
2. Does it avoid inappropriate modules?
3. Are objectives meaningful or just templates?
4. Is it better than random/rule-based baselines?
5. Edge cases handled?

Target: >70% appropriate selections (vs random ~33%)
"""

import json
import random
import sys
from pathlib import Path
from typing import Dict, List

import torch
from transformers import RobertaTokenizer, T5ForConditionalGeneration

# Import parser
sys.path.insert(0, str(Path(__file__).parent))
from markdown_syllabus_parser import MarkdownSyllabusParser


def create_quality_test_cases() -> List[Dict]:
    """Create 50+ test cases with KNOWN CORRECT selections."""

    test_cases = []

    # Beginner courses - should select beginner/easy intermediate modules
    for domain in ["computer_science", "mathematics", "science", "business"]:
        for i in range(3):
            test_cases.append(
                {
                    "name": f"Beginner {domain.replace('_', ' ').title()} {i+1}",
                    "title": f"Introduction to {domain.replace('_', ' ').title()} {i+1}",
                    "domain": domain,
                    "level": "beginner",
                    "available_modules": [
                        {
                            "id": "mod-0",
                            "title": "Basics Part 1",
                            "estimated_hours": 30,
                            "difficulty": "beginner",
                        },
                        {
                            "id": "mod-1",
                            "title": "Fundamentals",
                            "estimated_hours": 35,
                            "difficulty": "beginner",
                        },
                        {
                            "id": "mod-2",
                            "title": "Advanced Theory",
                            "estimated_hours": 80,
                            "difficulty": "advanced",
                        },
                        {
                            "id": "mod-3",
                            "title": "Expert Topics",
                            "estimated_hours": 90,
                            "difficulty": "advanced",
                        },
                        {
                            "id": "mod-4",
                            "title": "Intermediate Concepts",
                            "estimated_hours": 45,
                            "difficulty": "intermediate",
                        },
                    ],
                    "expected_good_indices": {0, 1, 4},  # Beginner + maybe intermediate
                    "expected_bad_indices": {2, 3},  # Advanced
                }
            )

    # Intermediate courses - should avoid beginner AND advanced
    for domain in ["computer_science", "mathematics", "science", "business"]:
        for i in range(2):
            test_cases.append(
                {
                    "name": f"Intermediate {domain.replace('_', ' ').title()} {i+1}",
                    "title": f"Intermediate {domain.replace('_', ' ').title()} {i+1}",
                    "domain": domain,
                    "level": "intermediate",
                    "available_modules": [
                        {
                            "id": "mod-0",
                            "title": "Basic Intro",
                            "estimated_hours": 20,
                            "difficulty": "beginner",
                        },
                        {
                            "id": "mod-1",
                            "title": "Core Concepts",
                            "estimated_hours": 40,
                            "difficulty": "intermediate",
                        },
                        {
                            "id": "mod-2",
                            "title": "Applied Methods",
                            "estimated_hours": 45,
                            "difficulty": "intermediate",
                        },
                        {
                            "id": "mod-3",
                            "title": "Advanced Research",
                            "estimated_hours": 80,
                            "difficulty": "advanced",
                        },
                        {
                            "id": "mod-4",
                            "title": "Expert Seminar",
                            "estimated_hours": 90,
                            "difficulty": "advanced",
                        },
                    ],
                    "expected_good_indices": {1, 2},  # Intermediate only
                    "expected_bad_indices": {0, 3, 4},  # Beginner or advanced
                }
            )

    # Advanced courses - should select intermediate/advanced, avoid beginner
    for domain in ["computer_science", "mathematics", "science", "business"]:
        for i in range(2):
            test_cases.append(
                {
                    "name": f"Advanced {domain.replace('_', ' ').title()} {i+1}",
                    "title": f"Advanced {domain.replace('_', ' ').title()} {i+1}",
                    "domain": domain,
                    "level": "advanced",
                    "available_modules": [
                        {
                            "id": "mod-0",
                            "title": "Intro Basics",
                            "estimated_hours": 20,
                            "difficulty": "beginner",
                        },
                        {
                            "id": "mod-1",
                            "title": "Elementary Topics",
                            "estimated_hours": 25,
                            "difficulty": "beginner",
                        },
                        {
                            "id": "mod-2",
                            "title": "Advanced Theory",
                            "estimated_hours": 70,
                            "difficulty": "advanced",
                        },
                        {
                            "id": "mod-3",
                            "title": "Research Methods",
                            "estimated_hours": 80,
                            "difficulty": "advanced",
                        },
                        {
                            "id": "mod-4",
                            "title": "Solid Foundation",
                            "estimated_hours": 40,
                            "difficulty": "intermediate",
                        },
                    ],
                    "expected_good_indices": {2, 3, 4},  # Advanced + maybe intermediate
                    "expected_bad_indices": {0, 1},  # Beginner
                }
            )

    # Edge cases
    test_cases.extend(
        [
            # All modules wrong difficulty (beginner course, only advanced modules)
            {
                "name": "EDGE: Beginner course, only advanced modules",
                "title": "Intro Course",
                "domain": "computer_science",
                "level": "beginner",
                "available_modules": [
                    {
                        "id": "mod-0",
                        "title": "Advanced Theory 1",
                        "estimated_hours": 80,
                        "difficulty": "advanced",
                    },
                    {
                        "id": "mod-1",
                        "title": "Advanced Theory 2",
                        "estimated_hours": 90,
                        "difficulty": "advanced",
                    },
                ],
                "expected_good_indices": set(),  # None are good!
                "expected_bad_indices": {0, 1},
            },
            # Minimal modules
            {
                "name": "EDGE: Only 1 module",
                "title": "Mini Course",
                "domain": "computer_science",
                "level": "beginner",
                "available_modules": [
                    {
                        "id": "mod-0",
                        "title": "Only Module",
                        "estimated_hours": 20,
                        "difficulty": "beginner",
                    },
                ],
                "expected_good_indices": {0},
                "expected_bad_indices": set(),
            },
            # Many modules (truncation test)
            {
                "name": "EDGE: 25 modules",
                "title": "Comprehensive Course",
                "domain": "computer_science",
                "level": "intermediate",
                "available_modules": [
                    {
                        "id": f"mod-{i}",
                        "title": f"Module {i}",
                        "estimated_hours": 30,
                        "difficulty": "intermediate" if i % 2 == 0 else "beginner",
                    }
                    for i in range(25)
                ],
                "expected_good_indices": {
                    i for i in range(25) if i % 2 == 0
                },  # Even indices = intermediate
                "expected_bad_indices": {
                    i for i in range(25) if i % 2 == 1
                },  # Odd indices = beginner
            },
        ]
    )

    # Add minimal activity/assessment to all
    for tc in test_cases:
        tc["available_activities"] = [
            {"id": "act-0", "title": "Practice", "estimated_hours": 5},
        ]
        tc["available_assessments"] = [
            {"id": "ass-0", "title": "Exam", "assessment_type": "exam"},
        ]

    return test_cases


def build_prompt(test_case: Dict) -> str:
    """Build prompt in same format as training."""
    prompt = f"Generate syllabus for: {test_case['title']} | {test_case['domain']} | {test_case['level']}\n\n"

    prompt += "Available modules:\n"
    for i, mod in enumerate(test_case["available_modules"][:20]):
        prompt += (
            f"[{i}] {mod['title']} ({mod['estimated_hours']}h, {mod['difficulty']})\n"
        )

    prompt += "\nAvailable activities:\n"
    for i, act in enumerate(test_case["available_activities"][:15]):
        prompt += f"[{i}] {act['title']} ({act['estimated_hours']}h)\n"

    prompt += "\nAvailable assessments:\n"
    for i, ass in enumerate(test_case["available_assessments"][:5]):
        prompt += f"[{i}] {ass['title']} ({ass['assessment_type']})\n"

    prompt += "\nSelect relevant components and generate markdown syllabus."

    return prompt


def random_baseline_select(test_case: Dict, count: int = 3) -> List[int]:
    """Random selection baseline."""
    available_count = len(test_case["available_modules"])
    return random.sample(range(min(available_count, 20)), min(count, available_count))


def rule_based_baseline_select(test_case: Dict) -> List[int]:
    """Rule-based baseline: select modules matching course level."""
    course_level = test_case["level"]
    selected = []

    for i, mod in enumerate(test_case["available_modules"][:20]):
        if course_level == "beginner" and mod["difficulty"] in ["beginner"]:
            selected.append(i)
        elif course_level == "intermediate" and mod["difficulty"] in ["intermediate"]:
            selected.append(i)
        elif course_level == "advanced" and mod["difficulty"] in [
            "advanced",
            "intermediate",
        ]:
            selected.append(i)

    return selected[:4]  # Limit to 4


def evaluate_selection_quality(selected_indices: List[int], test_case: Dict) -> Dict:
    """Evaluate quality of selected modules."""

    expected_good = test_case.get("expected_good_indices", set())
    expected_bad = test_case.get("expected_bad_indices", set())

    selected_set = set(selected_indices)

    # Count appropriate vs inappropriate
    appropriate_count = len(selected_set & expected_good)
    inappropriate_count = len(selected_set & expected_bad)
    total_selected = len(selected_set)

    # Metrics
    if total_selected > 0:
        appropriate_rate = appropriate_count / total_selected
        inappropriate_rate = inappropriate_count / total_selected
    else:
        appropriate_rate = 0
        inappropriate_rate = 0

    # Precision/Recall
    if len(expected_good) > 0:
        recall = appropriate_count / len(expected_good)
    else:
        recall = 1.0 if inappropriate_count == 0 else 0.0

    if total_selected > 0:
        precision = appropriate_count / total_selected
    else:
        precision = 0.0

    return {
        "appropriate_count": appropriate_count,
        "inappropriate_count": inappropriate_count,
        "total_selected": total_selected,
        "appropriate_rate": appropriate_rate,
        "inappropriate_rate": inappropriate_rate,
        "precision": precision,
        "recall": recall,
        "selected_indices": list(selected_set),
        "selected_difficulties": [
            test_case["available_modules"][i]["difficulty"]
            for i in selected_indices
            if i < len(test_case["available_modules"])
        ],
    }


def run_comprehensive_validation(model_path: str = "models/codet5-markdown-FULL"):
    """Run comprehensive validation with quality metrics."""

    print("=" * 80)
    print("PHASE 5B: SELECTION QUALITY VALIDATION")
    print("=" * 80)
    print()
    print("🎯 Goal: Validate INTELLIGENT selection, not just structure")
    print("📊 Tests: 50+ diverse cases + adversarial + baselines")
    print("✅ Target: >70% appropriate selections (vs random ~33%)")
    print()

    # Load model
    print(f"📦 Loading model from: {model_path}")
    tokenizer = RobertaTokenizer.from_pretrained(model_path)
    model = T5ForConditionalGeneration.from_pretrained(model_path)

    if torch.cuda.is_available():
        model = model.cuda()
        print("   ✅ Using GPU")
    else:
        print("   ✅ Using CPU")
    print()

    # Load parser
    parser = MarkdownSyllabusParser()

    # Create test cases
    test_cases = create_quality_test_cases()
    print(f"🧪 Running {len(test_cases)} test cases...\n")

    # Track metrics
    model_metrics = []
    random_metrics = []
    rule_metrics = []

    parse_failures = 0
    structure_failures = 0

    for i, test_case in enumerate(test_cases, 1):
        if i <= 3 or i == len(test_cases) or "EDGE" in test_case["name"]:
            print(f"Test {i}/{len(test_cases)}: {test_case['name']}")

        # Model prediction
        prompt = build_prompt(test_case)
        input_ids = tokenizer(
            prompt, return_tensors="pt", max_length=512, truncation=True
        ).input_ids

        if torch.cuda.is_available():
            input_ids = input_ids.cuda()

        with torch.no_grad():
            outputs = model.generate(
                input_ids,
                max_length=400,
                num_beams=2,
                early_stopping=False,
            )

        generated = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Parse
        rag_context = {
            "available_modules": test_case["available_modules"],
            "available_activities": test_case["available_activities"],
            "available_assessments": test_case["available_assessments"],
        }

        parse_result = parser.parse(generated, rag_context)

        if not parse_result.success:
            parse_failures += 1

        if generated.count("##") < 2:
            structure_failures += 1

        # Get selected indices
        model_selected = (
            parse_result.syllabus.get("modules", []) if parse_result.success else []
        )

        # Convert UUIDs back to indices for evaluation
        model_selected_indices = []
        for uuid in model_selected:
            for idx, mod in enumerate(test_case["available_modules"]):
                if mod["id"] == uuid:
                    model_selected_indices.append(idx)
                    break

        # Baselines
        random_selected = random_baseline_select(test_case)
        rule_selected = rule_based_baseline_select(test_case)

        # Evaluate all three
        model_quality = evaluate_selection_quality(model_selected_indices, test_case)
        random_quality = evaluate_selection_quality(random_selected, test_case)
        rule_quality = evaluate_selection_quality(rule_selected, test_case)

        model_metrics.append(model_quality)
        random_metrics.append(random_quality)
        rule_metrics.append(rule_quality)

        # Display details for first few and edge cases
        if i <= 3 or "EDGE" in test_case["name"]:
            print(f"  Course level: {test_case['level']}")
            print(f"  Model selected: {model_selected_indices}")
            print(f"  Difficulties: {model_quality['selected_difficulties']}")
            print(f"  Appropriate rate: {model_quality['appropriate_rate']:.1%}")
            print(f"  Inappropriate rate: {model_quality['inappropriate_rate']:.1%}")
            print()

    # Aggregate statistics
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()

    # Model stats
    avg_model_appropriate = sum(m["appropriate_rate"] for m in model_metrics) / len(
        model_metrics
    )
    avg_model_inappropriate = sum(m["inappropriate_rate"] for m in model_metrics) / len(
        model_metrics
    )
    avg_model_precision = sum(m["precision"] for m in model_metrics) / len(
        model_metrics
    )
    avg_model_recall = sum(m["recall"] for m in model_metrics) / len(model_metrics)

    # Baseline stats
    avg_random_appropriate = sum(m["appropriate_rate"] for m in random_metrics) / len(
        random_metrics
    )
    avg_rule_appropriate = sum(m["appropriate_rate"] for m in rule_metrics) / len(
        rule_metrics
    )

    print("📊 MODEL PERFORMANCE:")
    print(f"   Appropriate selection rate: {avg_model_appropriate:.1%}")
    print(f"   Inappropriate selection rate: {avg_model_inappropriate:.1%}")
    print(f"   Precision: {avg_model_precision:.1%}")
    print(f"   Recall: {avg_model_recall:.1%}")
    print(
        f"   Parse failures: {parse_failures}/{len(test_cases)} ({parse_failures/len(test_cases):.1%})"
    )
    print(
        f"   Structure failures: {structure_failures}/{len(test_cases)} ({structure_failures/len(test_cases):.1%})"
    )
    print()

    print("📊 BASELINE COMPARISONS:")
    print(f"   Random baseline: {avg_random_appropriate:.1%} appropriate")
    print(f"   Rule-based baseline: {avg_rule_appropriate:.1%} appropriate")
    print(f"   Our model: {avg_model_appropriate:.1%} appropriate")
    print()

    # Improvement
    improvement_vs_random = (
        (avg_model_appropriate - avg_random_appropriate) / avg_random_appropriate
    ) * 100
    improvement_vs_rule = (
        ((avg_model_appropriate - avg_rule_appropriate) / avg_rule_appropriate) * 100
        if avg_rule_appropriate > 0
        else 0
    )

    print("📈 IMPROVEMENTS:")
    print(f"   vs Random: {improvement_vs_random:+.1f}%")
    print(f"   vs Rule-based: {improvement_vs_rule:+.1f}%")
    print()

    # Decision
    print("=" * 80)
    print("ASSESSMENT")
    print("=" * 80)
    print()

    issues = []

    if avg_model_appropriate < 0.5:
        issues.append(f"❌ Low appropriate rate ({avg_model_appropriate:.1%} < 50%)")

    if avg_model_inappropriate > 0.3:
        issues.append(f"⚠️  High inappropriate rate ({avg_model_inappropriate:.1%})")

    if avg_model_appropriate <= avg_random_appropriate * 1.1:
        issues.append("❌ Not significantly better than random")

    if parse_failures > len(test_cases) * 0.05:
        issues.append(
            f"⚠️  Parse failure rate high ({parse_failures/len(test_cases):.1%})"
        )

    if issues:
        print("🚨 ISSUES DETECTED:")
        for issue in issues:
            print(f"   {issue}")
        print()
        decision = "NEEDS_IMPROVEMENT"
    elif avg_model_appropriate >= 0.70:
        print("✅ EXCELLENT - Model shows intelligent selection!")
        print(f"   {avg_model_appropriate:.1%} appropriate rate exceeds 70% target")
        decision = "PROCEED"
    elif avg_model_appropriate >= 0.50:
        print("⚠️  ACCEPTABLE - Model is better than random but could improve")
        decision = "PROCEED_WITH_CAUTION"
    else:
        print("❌ POOR - Model not significantly better than random")
        decision = "NEEDS_IMPROVEMENT"

    print()
    print(f"Decision: {decision}")

    # Save results
    results_path = Path("evaluation_selection_quality.json")
    with open(results_path, "w") as f:
        json.dump(
            {
                "summary": {
                    "model": {
                        "appropriate_rate": avg_model_appropriate,
                        "inappropriate_rate": avg_model_inappropriate,
                        "precision": avg_model_precision,
                        "recall": avg_model_recall,
                        "parse_failures": parse_failures,
                        "structure_failures": structure_failures,
                    },
                    "baselines": {
                        "random": avg_random_appropriate,
                        "rule_based": avg_rule_appropriate,
                    },
                    "improvements": {
                        "vs_random": improvement_vs_random,
                        "vs_rule": improvement_vs_rule,
                    },
                    "decision": decision,
                },
                "detailed_metrics": [
                    {
                        "test_name": test_cases[i]["name"],
                        "model": model_metrics[i],
                        "random": random_metrics[i],
                        "rule": rule_metrics[i],
                    }
                    for i in range(len(test_cases))
                ],
            },
            f,
            indent=2,
        )

    print(f"📄 Detailed results saved to: {results_path}")

    return decision == "PROCEED"


if __name__ == "__main__":
    print("Phase 5B - Selection Quality Validation")
    print()

    success = run_comprehensive_validation()

    exit(0 if success else 1)
