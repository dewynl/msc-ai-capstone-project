#!/usr/bin/env python3
"""
Phase 5: Comprehensive Evaluation with 4-Tier Success Metrics

Tests trained model on diverse scenarios and measures success across tiers:
- Tier 1 (80-90%): Perfect markdown + parseable indices
- Tier 2 (10-15%): Readable markdown, parser issues
- Tier 3 (5%): Partial output
- Tier 4 (<5%): Complete failure

Target: 90-95% total success rate (Tier 1 + Tier 2)
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List

import torch
from transformers import RobertaTokenizer, T5ForConditionalGeneration

# Import parser
sys.path.insert(0, str(Path(__file__).parent))
from markdown_syllabus_parser import MarkdownSyllabusParser


def create_test_cases() -> List[Dict]:
    """Create diverse test cases covering different scenarios."""

    test_cases = [
        # Beginner courses
        {
            "name": "Intro Programming (Beginner, CS)",
            "title": "Introduction to Programming",
            "domain": "computer_science",
            "level": "beginner",
            "duration": "semester",
            "available_modules": [
                {
                    "id": "mod-0",
                    "title": "Python Basics",
                    "estimated_hours": 40,
                    "difficulty": "beginner",
                },
                {
                    "id": "mod-1",
                    "title": "Advanced ML",
                    "estimated_hours": 80,
                    "difficulty": "advanced",
                },
                {
                    "id": "mod-2",
                    "title": "Data Structures",
                    "estimated_hours": 50,
                    "difficulty": "intermediate",
                },
                {
                    "id": "mod-3",
                    "title": "Variables and Types",
                    "estimated_hours": 20,
                    "difficulty": "beginner",
                },
            ],
            "available_activities": [
                {"id": "act-0", "title": "Coding Exercise 1", "estimated_hours": 5},
                {"id": "act-1", "title": "Advanced Project", "estimated_hours": 30},
            ],
            "available_assessments": [
                {"id": "ass-0", "title": "Midterm Exam", "assessment_type": "exam"},
            ],
        },
        # Advanced courses
        {
            "name": "Advanced ML (Advanced, CS)",
            "title": "Advanced Machine Learning",
            "domain": "computer_science",
            "level": "advanced",
            "duration": "semester",
            "available_modules": [
                {
                    "id": "mod-0",
                    "title": "Python Basics",
                    "estimated_hours": 40,
                    "difficulty": "beginner",
                },
                {
                    "id": "mod-1",
                    "title": "Deep Learning",
                    "estimated_hours": 80,
                    "difficulty": "advanced",
                },
                {
                    "id": "mod-2",
                    "title": "Neural Networks",
                    "estimated_hours": 70,
                    "difficulty": "advanced",
                },
                {
                    "id": "mod-3",
                    "title": "Reinforcement Learning",
                    "estimated_hours": 60,
                    "difficulty": "advanced",
                },
            ],
            "available_activities": [
                {"id": "act-0", "title": "Basic Tutorial", "estimated_hours": 5},
                {"id": "act-1", "title": "Research Project", "estimated_hours": 40},
                {"id": "act-2", "title": "Paper Review", "estimated_hours": 20},
            ],
            "available_assessments": [
                {
                    "id": "ass-0",
                    "title": "Final Presentation",
                    "assessment_type": "presentation",
                },
                {"id": "ass-1", "title": "Research Paper", "assessment_type": "essay"},
            ],
        },
        # Intermediate course
        {
            "name": "Database Systems (Intermediate, CS)",
            "title": "Database Systems",
            "domain": "computer_science",
            "level": "intermediate",
            "duration": "semester",
            "available_modules": [
                {
                    "id": "mod-0",
                    "title": "SQL Fundamentals",
                    "estimated_hours": 30,
                    "difficulty": "beginner",
                },
                {
                    "id": "mod-1",
                    "title": "Database Design",
                    "estimated_hours": 40,
                    "difficulty": "intermediate",
                },
                {
                    "id": "mod-2",
                    "title": "Query Optimization",
                    "estimated_hours": 50,
                    "difficulty": "advanced",
                },
                {
                    "id": "mod-3",
                    "title": "Transactions",
                    "estimated_hours": 35,
                    "difficulty": "intermediate",
                },
            ],
            "available_activities": [
                {"id": "act-0", "title": "SQL Lab", "estimated_hours": 10},
                {"id": "act-1", "title": "Database Project", "estimated_hours": 20},
            ],
            "available_assessments": [
                {"id": "ass-0", "title": "Practical Exam", "assessment_type": "exam"},
            ],
        },
        # Mathematics domain
        {
            "name": "Calculus I (Beginner, Math)",
            "title": "Calculus I",
            "domain": "mathematics",
            "level": "beginner",
            "duration": "semester",
            "available_modules": [
                {
                    "id": "mod-0",
                    "title": "Limits and Continuity",
                    "estimated_hours": 30,
                    "difficulty": "beginner",
                },
                {
                    "id": "mod-1",
                    "title": "Derivatives",
                    "estimated_hours": 40,
                    "difficulty": "beginner",
                },
                {
                    "id": "mod-2",
                    "title": "Advanced Topology",
                    "estimated_hours": 80,
                    "difficulty": "advanced",
                },
            ],
            "available_activities": [
                {"id": "act-0", "title": "Problem Set 1", "estimated_hours": 5},
                {"id": "act-1", "title": "Problem Set 2", "estimated_hours": 5},
            ],
            "available_assessments": [
                {"id": "ass-0", "title": "Midterm", "assessment_type": "exam"},
                {"id": "ass-1", "title": "Final Exam", "assessment_type": "exam"},
            ],
        },
        # Business domain
        {
            "name": "Business Strategy (Intermediate, Business)",
            "title": "Business Strategy",
            "domain": "business",
            "level": "intermediate",
            "duration": "quarter",
            "available_modules": [
                {
                    "id": "mod-0",
                    "title": "Strategic Analysis",
                    "estimated_hours": 30,
                    "difficulty": "intermediate",
                },
                {
                    "id": "mod-1",
                    "title": "Competitive Advantage",
                    "estimated_hours": 35,
                    "difficulty": "intermediate",
                },
                {
                    "id": "mod-2",
                    "title": "Market Research",
                    "estimated_hours": 25,
                    "difficulty": "beginner",
                },
            ],
            "available_activities": [
                {"id": "act-0", "title": "Case Study Analysis", "estimated_hours": 15},
                {
                    "id": "act-1",
                    "title": "Strategy Presentation",
                    "estimated_hours": 10,
                },
            ],
            "available_assessments": [
                {"id": "ass-0", "title": "Group Project", "assessment_type": "project"},
            ],
        },
        # Edge case: minimal modules
        {
            "name": "Short Workshop (Beginner, CS)",
            "title": "Python Crash Course",
            "domain": "computer_science",
            "level": "beginner",
            "duration": "workshop",
            "available_modules": [
                {
                    "id": "mod-0",
                    "title": "Python Basics",
                    "estimated_hours": 10,
                    "difficulty": "beginner",
                },
                {
                    "id": "mod-1",
                    "title": "Simple Projects",
                    "estimated_hours": 5,
                    "difficulty": "beginner",
                },
            ],
            "available_activities": [
                {"id": "act-0", "title": "Hands-on Coding", "estimated_hours": 3},
            ],
            "available_assessments": [
                {"id": "ass-0", "title": "Quiz", "assessment_type": "quiz"},
            ],
        },
        # Edge case: many modules
        {
            "name": "Full Stack Development (Advanced, CS)",
            "title": "Full Stack Web Development",
            "domain": "computer_science",
            "level": "advanced",
            "duration": "year",
            "available_modules": [
                {
                    "id": f"mod-{i}",
                    "title": f"Module {i}",
                    "estimated_hours": 30 + i * 5,
                    "difficulty": "intermediate",
                }
                for i in range(15)
            ],
            "available_activities": [
                {"id": f"act-{i}", "title": f"Activity {i}", "estimated_hours": 10}
                for i in range(10)
            ],
            "available_assessments": [
                {
                    "id": f"ass-{i}",
                    "title": f"Assessment {i}",
                    "assessment_type": "project",
                }
                for i in range(5)
            ],
        },
        # Science domain
        {
            "name": "Biology 101 (Beginner, Science)",
            "title": "Introduction to Biology",
            "domain": "science",
            "level": "beginner",
            "duration": "semester",
            "available_modules": [
                {
                    "id": "mod-0",
                    "title": "Cell Biology",
                    "estimated_hours": 35,
                    "difficulty": "beginner",
                },
                {
                    "id": "mod-1",
                    "title": "Genetics",
                    "estimated_hours": 40,
                    "difficulty": "intermediate",
                },
                {
                    "id": "mod-2",
                    "title": "Evolution",
                    "estimated_hours": 30,
                    "difficulty": "beginner",
                },
            ],
            "available_activities": [
                {"id": "act-0", "title": "Lab Work", "estimated_hours": 15},
                {"id": "act-1", "title": "Field Study", "estimated_hours": 10},
            ],
            "available_assessments": [
                {"id": "ass-0", "title": "Lab Report", "assessment_type": "report"},
            ],
        },
    ]

    return test_cases


def build_prompt(test_case: Dict) -> str:
    """Build prompt in same format as training data."""
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


def classify_result(generated: str, parse_result, test_case: Dict) -> Dict:
    """Classify result into one of 4 tiers."""

    result = {
        "tier": 4,  # Default: failure
        "tier_name": "Failure",
        "length": len(generated),
        "has_structure": False,
        "has_course_header": False,
        "has_objectives": False,
        "has_modules_section": False,
        "has_indices": False,
        "parseable": False,
        "readable": True,
        "selected_modules_count": 0,
        "issues": [],
    }

    # Basic checks
    result["has_course_header"] = bool(re.search(r"#\s+Course:", generated))
    result["has_structure"] = generated.count("##") >= 2
    result["has_objectives"] = (
        "Learning Objectives" in generated or "Objectives" in generated
    )
    result["has_modules_section"] = (
        "Selected Modules" in generated or "Modules" in generated
    )
    result["has_indices"] = bool(re.findall(r"\[(\d+)\]", generated))
    result["readable"] = not bool(
        re.search(r"(.)\1{20}", generated)
    )  # No 20+ repeated chars

    # Try parsing
    if parse_result.success:
        result["parseable"] = True
        result["selected_modules_count"] = len(parse_result.syllabus.get("modules", []))
    else:
        result["issues"].extend(parse_result.errors)

    # Tier classification
    if result["parseable"] and result["has_structure"] and result["length"] > 100:
        # Tier 1: Perfect - parseable with good structure
        result["tier"] = 1
        result["tier_name"] = "Perfect (Parseable + Structure)"

    elif result["readable"] and result["has_structure"] and result["length"] > 100:
        # Tier 2: Good - readable markdown but parser issues
        result["tier"] = 2
        result["tier_name"] = "Readable (Structure, Parser Issues)"
        if not result["parseable"]:
            result["issues"].append("Parser failed but output is readable")

    elif result["length"] > 50:
        # Tier 3: Partial output
        result["tier"] = 3
        result["tier_name"] = "Partial (Some Output)"
        result["issues"].append(f'Incomplete output ({result["length"]} chars)')

    else:
        # Tier 4: Failure
        result["tier"] = 4
        result["tier_name"] = "Failure"
        result["issues"].append(
            f'Very short or broken output ({result["length"]} chars)'
        )

    return result


def evaluate_model(model_path: str = "models/codet5-markdown-FULL"):
    """Run comprehensive evaluation."""
    print("=" * 80)
    print("PHASE 5: COMPREHENSIVE EVALUATION")
    print("=" * 80)
    print()
    print("🎯 Goal: Measure success across 4-tier system")
    print("📊 Target: 90-95% total success (Tier 1 + Tier 2)")
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
    test_cases = create_test_cases()
    print(f"🧪 Running {len(test_cases)} test cases...\n")

    results = []
    tier_counts = {1: 0, 2: 0, 3: 0, 4: 0}

    for i, test_case in enumerate(test_cases, 1):
        print(f"{'─'*80}")
        print(f"Test {i}/{len(test_cases)}: {test_case['name']}")
        print()

        # Build prompt
        prompt = build_prompt(test_case)

        # Generate
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

        # Classify
        classification = classify_result(generated, parse_result, test_case)

        tier_counts[classification["tier"]] += 1

        # Display
        print(f"Generated ({classification['length']} chars):")
        preview = generated[:300] + ("..." if len(generated) > 300 else "")
        print(preview)
        print()

        print(f"Result: {classification['tier_name']} (Tier {classification['tier']})")
        print(f"  ✓ Structure: {'✅' if classification['has_structure'] else '❌'}")
        print(
            f"  ✓ Course header: {'✅' if classification['has_course_header'] else '❌'}"
        )
        print(f"  ✓ Has indices: {'✅' if classification['has_indices'] else '❌'}")
        print(f"  ✓ Parseable: {'✅' if classification['parseable'] else '❌'}")

        if classification["parseable"]:
            print(f"  ✓ Selected modules: {classification['selected_modules_count']}")

        if classification["issues"]:
            print(f"  ⚠️  Issues: {'; '.join(classification['issues'])}")

        print()

        results.append(
            {
                "test_case": test_case["name"],
                "classification": classification,
                "generated": generated,
                "parse_result": parse_result,
            }
        )

    # Summary
    print("=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    print()

    total = len(test_cases)
    tier1_pct = (tier_counts[1] / total) * 100
    tier2_pct = (tier_counts[2] / total) * 100
    tier3_pct = (tier_counts[3] / total) * 100
    tier4_pct = (tier_counts[4] / total) * 100
    success_pct = tier1_pct + tier2_pct

    print("📊 Results by Tier:")
    print(
        f"   Tier 1 (Perfect): {tier_counts[1]}/{total} ({tier1_pct:.1f}%) - Target: 80-90%"
    )
    print(
        f"   Tier 2 (Readable): {tier_counts[2]}/{total} ({tier2_pct:.1f}%) - Target: 10-15%"
    )
    print(f"   Tier 3 (Partial): {tier_counts[3]}/{total} ({tier3_pct:.1f}%)")
    print(f"   Tier 4 (Failure): {tier_counts[4]}/{total} ({tier4_pct:.1f}%)")
    print()
    print(
        f"✅ Total Success Rate: {tier_counts[1] + tier_counts[2]}/{total} ({success_pct:.1f}%)"
    )
    print()

    # Decision
    if success_pct >= 90:
        print("🎉 EXCELLENT - Exceeds 90% success target!")
        decision = "PROCEED"
    elif success_pct >= 80:
        print("✅ GOOD - Meets minimum 80% threshold")
        decision = "PROCEED"
    elif success_pct >= 70:
        print("⚠️  ACCEPTABLE - Close to target (70-80%)")
        decision = "REVIEW"
    else:
        print("❌ BELOW TARGET - Under 70% success")
        decision = "DEBUG"

    print()
    print(f"Decision: {decision}")

    if decision == "PROCEED":
        print()
        print("Next step: python scripts/phase6_streamlit_integration.py")

    # Save detailed results
    output_path = Path("evaluation_results.json")
    with open(output_path, "w") as f:
        json.dump(
            {
                "summary": {
                    "total_tests": total,
                    "tier_counts": tier_counts,
                    "tier_percentages": {
                        "tier1": tier1_pct,
                        "tier2": tier2_pct,
                        "tier3": tier3_pct,
                        "tier4": tier4_pct,
                        "success": success_pct,
                    },
                    "decision": decision,
                },
                "results": [
                    {
                        "test_case": r["test_case"],
                        "tier": r["classification"]["tier"],
                        "tier_name": r["classification"]["tier_name"],
                        "length": r["classification"]["length"],
                        "parseable": r["classification"]["parseable"],
                        "issues": r["classification"]["issues"],
                        "generated": r["generated"],
                    }
                    for r in results
                ],
            },
            f,
            indent=2,
        )

    print()
    print(f"📄 Detailed results saved to: {output_path}")

    return decision == "PROCEED"


if __name__ == "__main__":
    print("Phase 5 - Comprehensive Evaluation")
    print()

    success = evaluate_model()

    exit(0 if success else 1)
