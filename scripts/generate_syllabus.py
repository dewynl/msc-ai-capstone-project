#!/usr/bin/env python3
"""
Complete syllabus generation pipeline.

Integrates: Filter → Generate → Parse → Enhance → Expand

This is the main entry point for the hybrid ML + rule-based system.
"""

from typing import Dict, List

from enhance_objectives import detect_generic_objectives, enhance_objectives
from markdown_syllabus_parser import (
    MarkdownSyllabusParser,
    expand_with_database_details,
)
from model_inference import SyllabusGenerator
from rag_filter import filter_components_by_difficulty, get_filter_stats


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

    prompt += "Available modules:\n"
    for i, mod in enumerate(modules[:20]):  # Limit to 20 to fit token budget
        title = mod.get("title", "Unknown")
        hours = mod.get("estimated_hours", 0)
        difficulty = mod.get("difficulty", "N/A")
        prompt += f"[{i}] {title} ({hours}h, {difficulty})\n"

    prompt += "\nAvailable activities:\n"
    for i, act in enumerate(activities[:15]):  # Limit to 15
        title = act.get("title", "Unknown")
        hours = act.get("estimated_hours", 0)
        prompt += f"[{i}] {title} ({hours}h)\n"

    prompt += "\nAvailable assessments:\n"
    for i, ass in enumerate(assessments[:5]):  # Limit to 5
        title = ass.get("title", "Unknown")
        atype = ass.get("assessment_type", "N/A")
        prompt += f"[{i}] {title} ({atype})\n"

    prompt += "\nSelect relevant components and generate markdown syllabus."

    return prompt


def generate_complete_syllabus(
    course_requirements: Dict, rag_database: Dict, generator: SyllabusGenerator = None
) -> Dict:
    """
    Complete pipeline: Filter → Generate → Parse → Enhance → Expand

    This is the main entry point for syllabus generation.

    Args:
        course_requirements: dict with title, domain, level, duration
        rag_database: dict with modules, activities, assessments
        generator: Optional pre-initialized generator (for efficiency)

    Returns:
        dict with:
            - success: bool
            - json: parsed syllabus structure
            - markdown_simple: model-generated markdown
            - markdown_rich: expanded markdown with details
            - warnings: list of warnings
            - metadata: generation statistics
    """

    # 1. Filter by difficulty (CRITICAL STEP - Rule-based)
    print("Step 1: Filtering components by difficulty...")
    filtered_modules = filter_components_by_difficulty(
        rag_database.get("modules", []),
        course_requirements.get("level", "beginner"),
        "modules",
    )

    # No filtering for activities and assessments
    filtered_activities = rag_database.get("activities", [])
    filtered_assessments = rag_database.get("assessments", [])

    # Get filter stats
    filter_stats = get_filter_stats(
        rag_database.get("modules", []),
        filtered_modules,
        course_requirements.get("level", "beginner"),
    )
    print(
        f"   Filtered {filter_stats['total_components']} → {filter_stats['filtered_components']} modules"
    )

    # Check if we have any modules
    if not filtered_modules:
        return {
            "success": False,
            "error": "No modules available for this difficulty level",
            "filter_stats": filter_stats,
        }

    # 2. Build prompt
    print("Step 2: Building prompt...")
    prompt = build_prompt(
        course_requirements, filtered_modules, filtered_activities, filtered_assessments
    )

    # 3. Generate markdown (ML-based)
    print("Step 3: Generating markdown with CodeT5...")
    if generator is None:
        generator = SyllabusGenerator()

    markdown_simple = generator.generate(prompt, max_length=400)
    print(f"   Generated {len(markdown_simple)} characters")

    # 4. Parse to JSON (Hybrid)
    print("Step 4: Parsing markdown to JSON...")
    parser = MarkdownSyllabusParser()

    # Build RAG context (MUST use same filtered modules!)
    rag_context = {
        "available_modules": filtered_modules,
        "available_activities": filtered_activities,
        "available_assessments": filtered_assessments,
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

    # 5. Enhance objectives (Rule-based - Bloom's Taxonomy)
    print("Step 5: Enhancing learning objectives...")
    if detect_generic_objectives(parse_result.syllabus.get("learning_objectives", [])):
        # Get full module objects from IDs
        selected_module_ids = parse_result.syllabus.get("modules", [])
        selected_modules = [
            mod for mod in filtered_modules if mod.get("id") in selected_module_ids
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

    # 6. Expand with rich details (Hybrid)
    print("Step 6: Expanding with database details...")
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
            "selected_modules_count": len(parse_result.syllabus.get("modules", [])),
            "selected_activities_count": len(
                parse_result.syllabus.get("activities", [])
            ),
            "selected_assessments_count": len(
                parse_result.syllabus.get("assessments", [])
            ),
        },
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
