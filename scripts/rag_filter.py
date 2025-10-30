#!/usr/bin/env python3
"""
Difficulty-aware RAG filtering for course syllabus generation.

Ensures model only sees pedagogically appropriate components.
"""

from typing import Dict, List


def filter_components_by_difficulty(
    components: List[Dict],
    course_level: str,
    component_type: str = "modules",
    course_domain: str = None,
) -> List[Dict]:
    """
    Filter RAG components by domain and difficulty to match course requirements.

    Filtering rules:
    - Domain: Only components matching course domain (e.g., CS course → CS components only)
    - Difficulty:
      • Beginner courses: Only beginner components
      • Intermediate courses: Beginner + intermediate components
      • Advanced courses: Intermediate + advanced components

    Args:
        components: List of component dicts with 'difficulty' and 'domain' fields
        course_level: 'beginner', 'intermediate', or 'advanced'
        component_type: 'modules', 'activities', or 'assessments' (informational only)
        course_domain: Optional domain filter (e.g., 'computer_science')

    Returns:
        Filtered list of components appropriate for the course level and domain
    """

    if course_domain:
        domain_normalized = course_domain.lower().strip()
        components = [
            c
            for c in components
            if c.get("domain", "").lower().strip() == domain_normalized
        ]

    level = course_level.lower().strip()

    if level == "beginner":
        return [c for c in components if c.get("difficulty", "").lower() == "beginner"]
    elif level == "intermediate":
        allowed = {"beginner", "intermediate"}
        return [c for c in components if c.get("difficulty", "").lower() in allowed]
    else:
        allowed = {"intermediate", "advanced"}
        return [c for c in components if c.get("difficulty", "").lower() in allowed]


def get_filter_stats(
    all_components: List[Dict],
    filtered_components: List[Dict],
    course_level: str,
    course_domain: str = None,
) -> Dict:
    """Get statistics about filtering operation."""
    stats = {
        "total_components": len(all_components),
        "filtered_components": len(filtered_components),
        "filter_rate": len(filtered_components) / len(all_components)
        if all_components
        else 0,
        "course_level": course_level,
        "difficulty_distribution": {
            difficulty: len(
                [c for c in filtered_components if c.get("difficulty") == difficulty]
            )
            for difficulty in ["beginner", "intermediate", "advanced"]
        },
    }

    if course_domain:
        stats["course_domain"] = course_domain
        stats["domain_distribution"] = {
            domain: len([c for c in filtered_components if c.get("domain") == domain])
            for domain in ["computer_science", "mathematics", "physics"]
        }

    return stats


if __name__ == "__main__":
    # Test the filter
    test_modules = [
        {"id": "1", "title": "Python Basics", "difficulty": "beginner"},
        {"id": "2", "title": "Data Structures", "difficulty": "intermediate"},
        {"id": "3", "title": "Advanced ML", "difficulty": "advanced"},
        {"id": "4", "title": "Intro to Programming", "difficulty": "beginner"},
    ]

    print("Testing RAG filter...\n")

    for level in ["beginner", "intermediate", "advanced"]:
        filtered = filter_components_by_difficulty(test_modules, level, "modules")
        stats = get_filter_stats(test_modules, filtered, level)

        print(f"{level.upper()} level:")
        print(f"  Total: {stats['total_components']}")
        print(f"  Filtered: {stats['filtered_components']}")
        print(f"  Titles: {[m['title'] for m in filtered]}")
        print()
