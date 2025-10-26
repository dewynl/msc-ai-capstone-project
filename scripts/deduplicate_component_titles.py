#!/usr/bin/env python3
"""
Deduplicate component titles in the dataset by appending domain/difficulty.

This script finds components with duplicate titles and makes them unique by
appending descriptive suffixes like "(Computer Science - Beginner)".
"""

import json
from collections import defaultdict
from pathlib import Path


def deduplicate_titles(components, title_key, id_key):
    """Deduplicate titles by appending domain, difficulty, and number if needed."""
    # Group components by title
    title_groups = defaultdict(list)
    for component in components:
        title = component.get(title_key, "")
        title_groups[title].append(component)

    # Track changes
    changed_count = 0
    all_used_titles = set()

    # Process duplicates
    for title, group in title_groups.items():
        if len(group) > 1:  # Duplicate found
            for i, component in enumerate(group, 1):
                domain = component.get("domain", "").replace("_", " ").title()
                difficulty = component.get("difficulty", "").title()

                # Create base unique title with suffix
                base_title = f"{title} ({domain} - {difficulty})"

                # If this title is still a duplicate, add number
                if base_title in all_used_titles:
                    # Find next available number
                    counter = 2
                    while f"{base_title} #{counter}" in all_used_titles:
                        counter += 1
                    new_title = f"{base_title} #{counter}"
                else:
                    new_title = base_title

                component[title_key] = new_title
                all_used_titles.add(new_title)
                changed_count += 1

    return changed_count


def main():
    print("🔧 Deduplicating Component Titles in Dataset")
    print("=" * 70)

    base_path = Path("data/components")
    total_changes = 0

    # Process modules
    print("\n📚 Processing modules.json...")
    modules_path = base_path / "modules.json"
    with open(modules_path, "r") as f:
        modules = json.load(f)

    original_count = len(modules)
    changes = deduplicate_titles(modules, "title", "module_id")
    total_changes += changes

    with open(modules_path, "w") as f:
        json.dump(modules, f, indent=2)

    print(f"   ✅ Updated {changes} of {original_count} modules")

    # Process activities
    print("\n🎯 Processing activities.json...")
    activities_path = base_path / "activities.json"
    with open(activities_path, "r") as f:
        activities = json.load(f)

    original_count = len(activities)
    changes = deduplicate_titles(activities, "title", "activity_id")
    total_changes += changes

    with open(activities_path, "w") as f:
        json.dump(activities, f, indent=2)

    print(f"   ✅ Updated {changes} of {original_count} activities")

    # Process assessments
    print("\n📝 Processing assessments.json...")
    assessments_path = base_path / "assessments.json"
    with open(assessments_path, "r") as f:
        assessments = json.load(f)

    original_count = len(assessments)
    changes = deduplicate_titles(assessments, "title", "assessment_id")
    total_changes += changes

    with open(assessments_path, "w") as f:
        json.dump(assessments, f, indent=2)

    print(f"   ✅ Updated {changes} of {original_count} assessments")

    print("\n" + "=" * 70)
    print(f"✅ Total components updated: {total_changes}")
    print("\n⚠️  IMPORTANT: You need to rebuild ChromaDB for changes to take effect:")
    print("   rm -rf chroma_db")
    print("   python -m src.rag.component_indexer")
    print("\n   Or just let Streamlit rebuild it automatically on next deployment.")


if __name__ == "__main__":
    main()
