#!/usr/bin/env python3
"""
Difficulty-aware RAG filtering for course syllabus generation.

This is a CRITICAL component that ensures model only sees pedagogically
appropriate components, matching the training data distribution.
"""

from typing import Dict, List


def filter_components_by_difficulty(
    components: List[Dict], course_level: str, component_type: str = "modules"
) -> List[Dict]:
    """
    Filter RAG components by difficulty to match course level.

    CRITICAL: This ensures model only sees appropriate components,
    matching the training data distribution.

    Training data analysis showed:
    - Beginner courses: 0% had advanced modules
    - Intermediate courses: Had beginner + intermediate
    - Advanced courses: Had intermediate + advanced

    Args:
        components: List of component dicts with 'difficulty' field
        course_level: 'beginner', 'intermediate', or 'advanced'
        component_type: 'modules', 'activities', or 'assessments'

    Returns:
        Filtered list of components appropriate for the course level
    """

    # Activities and assessments don't need difficulty filtering
    if component_type != "modules":
        return components

    # Normalize level
    level = course_level.lower().strip()

    # Filter by difficulty
    if level == "beginner":
        # Beginner courses: only beginner modules
        return [c for c in components if c.get("difficulty", "").lower() == "beginner"]

    elif level == "intermediate":
        # Intermediate courses: beginner + intermediate modules
        allowed = {"beginner", "intermediate"}
        return [c for c in components if c.get("difficulty", "").lower() in allowed]

    else:  # advanced
        # Advanced courses: intermediate + advanced modules
        allowed = {"intermediate", "advanced"}
        return [c for c in components if c.get("difficulty", "").lower() in allowed]


def get_filter_stats(
    all_components: List[Dict], filtered_components: List[Dict], course_level: str
) -> Dict:
    """
    Get statistics about filtering operation.

    Useful for debugging and monitoring.

    Returns:
        Dict with filter statistics
    """
    return {
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
