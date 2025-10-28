#!/usr/bin/env python3
"""
Template-based fallback syllabus generator.

Used when ML model fails or produces unparseable output.
Ensures 100% reliability by falling back to simple rule-based generation.
"""

from typing import Dict, List

from enhance_objectives import enhance_objectives
from markdown_syllabus_parser import expand_with_database_details


def generate_fallback_syllabus(course_requirements: Dict, rag_database: Dict) -> Dict:
    """
    Template-based fallback for reliability.

    Uses simple rule-based selection when model generation fails.

    Args:
        course_requirements: dict with title, domain, level, duration
        rag_database: dict with modules, activities, assessments

    Returns:
        dict with json, markdown_simple, markdown_rich, warnings
    """
    from rag_filter import filter_components_by_difficulty

    print("⚠️ Using fallback template-based generation")

    # 1. Filter by difficulty (same as main pipeline)
    filtered_modules = filter_components_by_difficulty(
        rag_database.get("modules", []),
        course_requirements.get("level", "beginner"),
        "modules",
    )

    filtered_activities = rag_database.get("activities", [])
    filtered_assessments = rag_database.get("assessments", [])

    # 2. Select components using simple heuristics
    # Sort by estimated hours and select appropriate count
    sorted_modules = sorted(filtered_modules, key=lambda x: x.get("estimated_hours", 0))

    # Select 3-4 modules based on duration
    duration = course_requirements.get("duration", "semester")
    if duration == "week":
        num_modules = 2
    elif duration == "semester":
        num_modules = 4
    else:  # year
        num_modules = 5

    selected_modules = sorted_modules[: min(num_modules, len(sorted_modules))]

    # Select 2-3 activities
    selected_activities = filtered_activities[: min(3, len(filtered_activities))]

    # Select 1-2 assessments
    selected_assessments = filtered_assessments[: min(2, len(filtered_assessments))]

    # 3. Build structured syllabus (JSON) - match parser format
    course_info = {
        "title": course_requirements.get("title", "Untitled Course"),
        "domain": course_requirements.get("domain", "general"),
        "level": course_requirements.get("level", "beginner"),
        "duration": duration,
    }

    syllabus = {
        "course_info": course_info,
        "learning_objectives": generate_template_objectives(course_requirements),
        "modules": [mod.get("id") for mod in selected_modules],
        "activities": [act.get("id") for act in selected_activities],
        "assessments": [ass.get("id") for ass in selected_assessments],
    }

    # 4. Enhance objectives with Bloom's Taxonomy
    enhanced_objectives = enhance_objectives(
        syllabus["learning_objectives"], course_requirements, selected_modules
    )
    syllabus["learning_objectives"] = enhanced_objectives

    # 5. Generate simple markdown
    markdown_simple = build_template_markdown(syllabus, selected_modules)

    # 6. Expand with rich details
    rag_context = {
        "available_modules": filtered_modules,
        "available_activities": filtered_activities,
        "available_assessments": filtered_assessments,
    }

    markdown_rich = expand_with_database_details(syllabus, rag_context)

    return {
        "success": True,
        "json": syllabus,
        "markdown_simple": markdown_simple,
        "markdown_rich": markdown_rich,
        "warnings": ["Generated using template fallback"],
        "metadata": {
            "generation_method": "template_fallback",
            "filtered_modules_count": len(filtered_modules),
            "total_modules_count": len(rag_database.get("modules", [])),
            "selected_modules_count": len(selected_modules),
        },
    }


def generate_template_objectives(course_requirements: Dict) -> List[str]:
    """Generate generic template objectives (will be enhanced later)."""
    title = course_requirements.get("title", "this course")
    return [
        f"Master {title} fundamentals and concepts",
        f"Apply {title} knowledge to practical problems",
        f"Demonstrate proficiency in {title} techniques",
        f"Analyze and evaluate {title} solutions",
    ]


def build_template_markdown(syllabus: Dict, selected_modules: List[Dict]) -> str:
    """Build simple markdown from template."""
    info = syllabus["course_info"]
    md = f"# Course: {info['title']}\n\n"
    md += f"**Domain:** {info['domain']}\n"
    md += f"**Level:** {info['level']}\n"
    md += f"**Duration:** {info['duration']}\n\n"

    md += "## Learning Objectives\n"
    for obj in syllabus["learning_objectives"]:
        md += f"- {obj}\n"
    md += "\n"

    md += "## Selected Modules\n"
    for i, mod in enumerate(selected_modules):
        md += f"- {mod.get('title', 'Unknown')}\n"
    md += "\n"

    md += "## Selected Activities\n"
    for act_id in syllabus.get("activities", []):
        md += f"- Activity {act_id}\n"
    md += "\n"

    md += "## Selected Assessments\n"
    for ass_id in syllabus.get("assessments", []):
        md += f"- Assessment {ass_id}\n"

    return md


if __name__ == "__main__":
    # Test fallback generator
    print("Testing fallback generator...\n")

    mock_database = {
        "modules": [
            {
                "id": "mod-1",
                "title": "Python Basics",
                "description": "Introduction to Python",
                "estimated_hours": 40,
                "difficulty": "beginner",
                "key_concepts": ["variables", "functions"],
            },
            {
                "id": "mod-2",
                "title": "Data Structures",
                "description": "Common data structures",
                "estimated_hours": 50,
                "difficulty": "intermediate",
                "key_concepts": ["lists", "dictionaries"],
            },
            {
                "id": "mod-3",
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

    test_course = {
        "title": "Introduction to Python",
        "domain": "computer_science",
        "level": "beginner",
        "duration": "semester",
    }

    result = generate_fallback_syllabus(test_course, mock_database)

    print("=" * 80)
    print("RESULT:")
    print("=" * 80)

    if result["success"]:
        print("✓ Fallback generation successful\n")
        print("Metadata:")
        print(f"  Method: {result['metadata']['generation_method']}")
        print(f"  Selected: {result['metadata']['selected_modules_count']} modules")
        print(f"  Warnings: {result['warnings']}")

        print("\nEnhanced Objectives:")
        for obj in result["json"]["learning_objectives"]:
            print(f"  - {obj}")

        print("\nMarkdown:")
        print("-" * 80)
        print(result["markdown_simple"])
    else:
        print(f"✗ Failed: {result.get('error', 'Unknown error')}")
