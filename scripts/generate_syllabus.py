#!/usr/bin/env python3
"""
Complete syllabus generation pipeline.

Integrates: Filter → Rank → Generate → Parse → Enhance → Expand

This is the main entry point for the hybrid ML + rule-based system.
"""

import sys
from pathlib import Path
from typing import Dict, List

from enhance_objectives import detect_generic_objectives, enhance_objectives
from markdown_syllabus_parser import (
    MarkdownSyllabusParser,
    expand_with_database_details,
)
from model_inference import SyllabusGenerator
from rag_filter import filter_components_by_difficulty, get_filter_stats
from semantic_ranker import SemanticRanker

sys.path.append(str(Path(__file__).parent.parent / "src" / "inference"))
from quality_reranker import SyllabusQualityReranker


def build_prompt(
    course_requirements: Dict,
    modules: List[Dict],
    activities: List[Dict],
    assessments: List[Dict],
) -> str:
    """
    Build prompt in training format.

    Args:
        course_requirements: dict with title, domain, level, duration
        modules: Filtered list of modules
        activities: List of activities
        assessments: List of assessments

    Returns:
        Formatted prompt string
    """
    prompt = f"Generate syllabus for: {course_requirements['title']} | "
    prompt += f"{course_requirements.get('domain', 'general')} | "
    prompt += f"{course_requirements.get('level', 'beginner')}\n\n"

    # MATCH TRAINING DATA FORMAT: Training had 2-5 modules (avg 3.6), 2-4 activities, 1-3 assessments
    # Test shows model FAILS at 5 modules (generates garbage, incomplete output)
    # Use training AVERAGE (3-4) for reliable generation
    prompt += "Available modules:\n"
    for i, mod in enumerate(modules[:3]):  # Training avg ≈ 3.6, using 3 for stability
        title = mod.get("title", "Unknown")
        hours = mod.get("estimated_hours", 8)
        difficulty = mod.get("difficulty", "beginner")
        prompt += f"[{i}] {title} ({hours}h, {difficulty})\n"

    prompt += "\nAvailable activities:\n"
    for i, act in enumerate(activities[:3]):  # Training avg ≈ 3.1, using 3
        title = act.get("title", "Unknown")
        prompt += f"[{i}] {title}\n"

    prompt += "\nAvailable assessments:\n"
    for i, ass in enumerate(assessments[:2]):  # Training avg ≈ 2.0, using 2
        title = ass.get("title", "Unknown")
        prompt += f"[{i}] {title}\n"

    prompt += "\nSelect and sequence modules, generate objectives."

    # Debug: Print full prompt to verify format matches training
    print(f"   DEBUG: Full prompt ({len(prompt)} chars):")
    print("   " + "=" * 70)
    print(prompt)
    print("   " + "=" * 70)

    return prompt


def generate_complete_syllabus(
    course_requirements: Dict,
    rag_database: Dict,
    generator: SyllabusGenerator = None,
    ranker: SemanticRanker = None,
) -> Dict:
    """
    Complete pipeline: Filter → Rank → Generate → Parse → Enhance → Expand

    This is the main entry point for syllabus generation.

    Args:
        course_requirements: dict with title, domain, level, duration
        rag_database: dict with modules, activities, assessments
        generator: Optional pre-initialized generator (for efficiency)
        ranker: Optional pre-initialized semantic ranker (for efficiency)

    Returns:
        dict with:
            - success: bool
            - json: parsed syllabus structure
            - markdown_simple: model-generated markdown
            - markdown_rich: expanded markdown with details
            - warnings: list of warnings
            - metadata: generation statistics (includes ranking_stats)
    """

    # 1. Filter ALL components by domain AND difficulty (CRITICAL STEP - Rule-based)
    print("Step 1: Filtering components by domain + difficulty...")
    course_domain = course_requirements.get("domain")
    course_level = course_requirements.get("level", "beginner")

    filtered_modules = filter_components_by_difficulty(
        rag_database.get("modules", []),
        course_level,
        "modules",
        course_domain,
    )

    filtered_activities = filter_components_by_difficulty(
        rag_database.get("activities", []),
        course_level,
        "activities",
        course_domain,
    )

    filtered_assessments = filter_components_by_difficulty(
        rag_database.get("assessments", []),
        course_level,
        "assessments",
        course_domain,
    )

    # Get filter stats
    filter_stats = get_filter_stats(
        rag_database.get("modules", []),
        filtered_modules,
        course_requirements.get("level", "beginner"),
        course_requirements.get("domain"),  # Add domain to stats
    )

    domain_info = (
        f" ({filter_stats.get('course_domain', 'all domains')})"
        if course_requirements.get("domain")
        else ""
    )
    print(
        f"   Filtered modules: {filter_stats['total_components']} → {filter_stats['filtered_components']}{domain_info}"
    )
    print(
        f"   Filtered activities: {len(rag_database.get('activities', []))} → {len(filtered_activities)}{domain_info}"
    )
    print(
        f"   Filtered assessments: {len(rag_database.get('assessments', []))} → {len(filtered_assessments)}{domain_info}"
    )

    # Check if we have any modules
    if not filtered_modules:
        return {
            "success": False,
            "error": "No modules available for this difficulty level",
            "filter_stats": filter_stats,
        }

    # 2. Rank components by semantic similarity (ML-based)
    print("Step 2: Ranking components by semantic similarity...")
    if ranker is None:
        ranker = SemanticRanker()

    ranking_result = ranker.rank_all_components(
        modules=filtered_modules,
        activities=filtered_activities,
        assessments=filtered_assessments,
        course_requirements=course_requirements,
        top_k_modules=20,
        top_k_activities=15,
        top_k_assessments=5,
    )

    # Use ranked components for generation
    ranked_modules = ranking_result["modules"]
    ranked_activities = ranking_result["activities"]
    ranked_assessments = ranking_result["assessments"]
    ranking_stats = ranking_result["ranking_stats"]

    print(f"   Ranked modules: {len(filtered_modules)} → {len(ranked_modules)} (top K)")
    print(
        f"   Ranked activities: {len(filtered_activities)} → {len(ranked_activities)} (top K)"
    )
    print(
        f"   Ranked assessments: {len(filtered_assessments)} → {len(ranked_assessments)} (top K)"
    )

    # 3. Build prompt (using ranked components)
    print("Step 3: Building prompt...")
    prompt = build_prompt(
        course_requirements, ranked_modules, ranked_activities, ranked_assessments
    )

    # 4. Generate markdown with quality reranking (ML-based + Pedagogical Evaluation)
    print("Step 4: Generating markdown with CodeT5 + Quality Evaluation...")
    if generator is None:
        generator = SyllabusGenerator()

    # Initialize quality reranker
    reranker = SyllabusQualityReranker()

    # Extract module IDs in order they appear in prompt (for quality evaluation)
    available_module_ids = [m["id"] for m in ranked_modules]

    # Generate with quality-aware selection (3 candidates, best selected)
    (
        markdown_simple,
        quality_metrics,
        is_acceptable,
    ) = reranker.generate_with_quality_selection(
        model=generator.model,
        tokenizer=generator.tokenizer,
        input_text=prompt,
        available_module_ids=available_module_ids,
        num_candidates=3,
        temperature=0.8,
        max_length=1500,  # Increased to allow complete syllabi with activities/assessments
    )

    print(f"   Generated {len(markdown_simple)} characters")
    print(
        f"   Quality score: {quality_metrics.get('prerequisite_accuracy', 0):.0%} prerequisite coherence"
    )

    # 5. Parse to JSON (Hybrid)
    print("Step 5: Parsing markdown to JSON...")
    parser = MarkdownSyllabusParser()

    # Build RAG context (MUST use same ranked modules!)
    rag_context = {
        "available_modules": ranked_modules,
        "available_activities": ranked_activities,
        "available_assessments": ranked_assessments,
    }

    parse_result = parser.parse(markdown_simple, rag_context)

    if not parse_result.success:
        print(f"   ⚠️ Parsing failed: {parse_result.error}")
        return {
            "success": False,
            "error": f"Parsing failed: {parse_result.error}",
            "markdown_simple": markdown_simple,
            "warnings": parse_result.warnings,
        }

    print(f"   ✓ Parsed successfully with {len(parse_result.warnings)} warnings")

    # Add description from original requirements (model doesn't generate this)
    if "description" in course_requirements:
        parse_result.syllabus["course_info"]["description"] = course_requirements[
            "description"
        ]

    # 6. Enhance objectives (Rule-based - Bloom's Taxonomy)
    print("Step 6: Enhancing learning objectives...")
    if detect_generic_objectives(parse_result.syllabus.get("learning_objectives", [])):
        # Get full module objects from IDs
        selected_module_ids = parse_result.syllabus.get("modules", [])
        selected_modules = [
            mod for mod in ranked_modules if mod.get("id") in selected_module_ids
        ]

        enhanced_objectives = enhance_objectives(
            parse_result.syllabus["learning_objectives"],
            course_requirements,
            selected_modules,  # Pass full module objects, not IDs
        )
        parse_result.syllabus["learning_objectives"] = enhanced_objectives
        print(
            f"   ✓ Enhanced {len(enhanced_objectives)} objectives with Bloom's Taxonomy"
        )
    else:
        print("   ℹ️ Objectives already good, skipping enhancement")

    # 7. Expand with rich details (Hybrid)
    print("Step 7: Expanding with database details...")
    markdown_rich = expand_with_database_details(parse_result.syllabus, rag_context)
    print(f"   ✓ Expanded to {len(markdown_rich)} characters")

    # Return complete result
    return {
        "success": True,
        "json": parse_result.syllabus,
        "markdown_simple": markdown_simple,
        "markdown_rich": markdown_rich,
        "warnings": parse_result.warnings,
        "metadata": {
            "filter_stats": filter_stats,
            "ranking_stats": ranking_stats,
            "ranked_modules": ranked_modules,  # Top 20 ranked modules (after boost)
            "selected_modules_count": len(parse_result.syllabus.get("modules", [])),
            "selected_activities_count": len(
                parse_result.syllabus.get("activities", [])
            ),
            "selected_assessments_count": len(
                parse_result.syllabus.get("assessments", [])
            ),
        },
        # Add pedagogical quality metrics
        "quality_metrics": quality_metrics,
        "quality_acceptable": is_acceptable,
    }


if __name__ == "__main__":
    # Test the complete pipeline
    print("Testing complete syllabus generation pipeline...\n")
    print("=" * 80)

    # Mock RAG database
    mock_database = {
        "modules": [
            {
                "id": "mod-1",
                "title": "Python Basics",
                "description": "Introduction to Python programming",
                "estimated_hours": 40,
                "difficulty": "beginner",
                "key_concepts": ["variables", "functions", "loops"],
            },
            {
                "id": "mod-2",
                "title": "Data Structures",
                "description": "Common data structures in Python",
                "estimated_hours": 50,
                "difficulty": "intermediate",
                "key_concepts": ["lists", "dictionaries", "sets"],
            },
            {
                "id": "mod-3",
                "title": "Advanced ML",
                "description": "Machine learning algorithms",
                "estimated_hours": 60,
                "difficulty": "advanced",
                "key_concepts": ["neural networks", "deep learning"],
            },
            {
                "id": "mod-4",
                "title": "Control Flow",
                "description": "If statements and loops",
                "estimated_hours": 20,
                "difficulty": "beginner",
                "key_concepts": ["if", "for", "while"],
            },
        ],
        "activities": [
            {"id": "act-1", "title": "Coding Exercises", "estimated_hours": 5}
        ],
        "assessments": [
            {"id": "ass-1", "title": "Final Exam", "assessment_type": "exam"}
        ],
    }

    # Test course requirements
    test_course = {
        "title": "Introduction to Python Programming",
        "domain": "computer_science",
        "level": "beginner",
        "duration": "semester",
    }

    # Generate syllabus
    result = generate_complete_syllabus(test_course, mock_database)

    print("\n" + "=" * 80)
    print("RESULT:")
    print("=" * 80)

    if result["success"]:
        print("✓ SUCCESS\n")
        print("Metadata:")
        print(
            f"  - Filtered: {result['metadata']['filter_stats']['filtered_components']} modules"
        )
        print(f"  - Selected: {result['metadata']['selected_modules_count']} modules")
        print(f"  - Warnings: {len(result['warnings'])}")

        print("\nGenerated Markdown (Simple):")
        print("-" * 80)
        print(result["markdown_simple"][:500] + "...")

        print("\n\nEnhanced Objectives:")
        print("-" * 80)
        for obj in result["json"]["learning_objectives"]:
            print(f"  - {obj}")

        print("\n\n✓ Pipeline test completed successfully!")
    else:
        print(f"✗ FAILED: {result.get('error', 'Unknown error')}")
