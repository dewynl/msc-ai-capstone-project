#!/usr/bin/env python3
"""
Phase 1: Convert Training Data to Markdown Format

Transform 1,117 function call examples into simplified markdown format.

KEY SIMPLIFICATION:
- Model outputs INDICES ONLY (not full descriptions)
- Model outputs learning objectives (creative generation)
- Template expands indices with database details later

This makes the task much simpler for the model.
"""

import json
import re
from pathlib import Path
from typing import Dict, List


def extract_course_info(output_calls: str) -> Dict:
    """Extract course info from set_info() call."""
    # Pattern: set_info("title", "domain", "level", "duration", "description")
    pattern = (
        r'set_info\("([^"]+)",\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)"\)'
    )
    match = re.search(pattern, output_calls)

    if match:
        return {
            "title": match.group(1),
            "domain": match.group(2),
            "level": match.group(3),
            "duration": match.group(4),
            "description": match.group(5),
        }
    return {}


def extract_objectives(output_calls: str) -> List[str]:
    """Extract learning objectives from add_objective() calls."""
    pattern = r'add_objective\("([^"]+)"\)'
    return re.findall(pattern, output_calls)


def extract_component_uuids(output_calls: str, function_name: str) -> List[str]:
    """Extract UUIDs from add_*_by_id() calls."""
    pattern = rf'{function_name}\("([^"]+)"\)'
    return re.findall(pattern, output_calls)


def map_uuids_to_indices(
    uuids: List[str], available_components: List[Dict]
) -> List[int]:
    """
    Map UUIDs to indices in the available components array.

    This is the KEY transformation: UUID → index
    Model will output indices, not UUIDs!
    """
    uuid_to_index = {comp["id"]: i for i, comp in enumerate(available_components)}

    indices = []
    for uuid in uuids:
        if uuid in uuid_to_index:
            indices.append(uuid_to_index[uuid])
        else:
            # UUID not in available list (shouldn't happen in good data)
            print(f"⚠️  Warning: UUID {uuid[:8]}... not found in available components")

    return indices


def convert_to_simplified_markdown(example: Dict) -> str:
    """
    Convert one example to SIMPLIFIED markdown.

    Key principle: Model outputs structure + indices + objectives.
    Model does NOT output full descriptions (template adds those later).
    """
    # Parse input
    input_text = example["input_text"]
    json_str = input_text.replace("Generate course syllabus: ", "")
    input_data = json.loads(json_str)

    # Parse output
    output_calls = example["output_calls"]

    # Extract components
    course_info = extract_course_info(output_calls)
    objectives = extract_objectives(output_calls)

    # Extract UUIDs and map to indices
    module_uuids = extract_component_uuids(output_calls, "add_module_by_id")
    activity_uuids = extract_component_uuids(output_calls, "add_activity_by_id")
    assessment_uuids = extract_component_uuids(output_calls, "add_assessment_by_id")

    available_modules = input_data.get("available_modules", [])
    available_activities = input_data.get("available_activities", [])
    available_assessments = input_data.get("available_assessments", [])

    module_indices = map_uuids_to_indices(module_uuids, available_modules)
    activity_indices = map_uuids_to_indices(activity_uuids, available_activities)
    assessment_indices = map_uuids_to_indices(assessment_uuids, available_assessments)

    # Build SIMPLIFIED markdown
    # Model outputs THIS, not full descriptions!

    markdown_lines = []

    # Course info section
    markdown_lines.append("# Course: " + course_info.get("title", "Untitled"))
    markdown_lines.append("")
    markdown_lines.append(f"**Domain:** {course_info.get('domain', 'N/A')}")
    markdown_lines.append(f"**Level:** {course_info.get('level', 'N/A')}")
    markdown_lines.append(f"**Duration:** {course_info.get('duration', 'N/A')}")
    markdown_lines.append("")

    # Learning objectives (model generates these - creative part)
    if objectives:
        markdown_lines.append("## Learning Objectives")
        for obj in objectives:
            markdown_lines.append(f"- {obj}")
        markdown_lines.append("")

    # Selected modules (JUST INDICES!)
    if module_indices:
        markdown_lines.append("## Selected Modules")
        markdown_lines.append(", ".join(f"[{i}]" for i in module_indices))
        markdown_lines.append("")

    # Selected activities
    if activity_indices:
        markdown_lines.append("## Selected Activities")
        markdown_lines.append(", ".join(f"[{i}]" for i in activity_indices))
        markdown_lines.append("")

    # Selected assessments
    if assessment_indices:
        markdown_lines.append("## Selected Assessments")
        markdown_lines.append(", ".join(f"[{i}]" for i in assessment_indices))
        markdown_lines.append("")

    return "\n".join(markdown_lines)


def validate_conversion(original: Dict, markdown: str, input_data: Dict) -> Dict:
    """Validate that conversion preserves essential information."""

    validation = {
        "has_title": "# Course:" in markdown,
        "has_objectives": "## Learning Objectives" in markdown,
        "has_modules": "## Selected Modules" in markdown
        or len(input_data.get("available_modules", [])) == 0,
        "has_activities": "## Selected Activities" in markdown
        or len(input_data.get("available_activities", [])) == 0,
        "has_structure": markdown.count("##") >= 1,
        "length_ok": 100 <= len(markdown) <= 1000,
    }

    validation["passed"] = all(validation.values())

    return validation


def main():
    print("=" * 80)
    print("PHASE 1: CONVERT TRAINING DATA TO MARKDOWN")
    print("=" * 80)
    print("\n🎯 Goal: Transform 1,117 function call examples → simplified markdown")
    print("📝 Key: Model outputs INDICES only, not full descriptions\n")

    # Load original training data
    input_path = Path("data/training/rag_enhanced_t5_training_1300_FIXED.json")
    output_path = Path("data/training/markdown_training_1300.json")

    print(f"📂 Loading: {input_path}")
    with open(input_path) as f:
        data = json.load(f)

    print(f"   ✅ Loaded {len(data)} examples\n")

    # Convert each example
    print("🔄 Converting examples...")

    converted = []
    validation_stats = {"success": 0, "warnings": 0, "errors": 0}

    for i, example in enumerate(data):
        try:
            # Convert to markdown
            markdown = convert_to_simplified_markdown(example)

            # Validate
            input_text = example["input_text"]
            json_str = input_text.replace("Generate course syllabus: ", "")
            input_data = json.loads(json_str)

            validation = validate_conversion(example, markdown, input_data)

            if validation["passed"]:
                validation_stats["success"] += 1
            else:
                validation_stats["warnings"] += 1
                if i < 5:  # Show first few warnings
                    print(
                        f"   ⚠️  Example {i}: {[k for k, v in validation.items() if not v and k != 'passed']}"
                    )

            # Store converted example
            # Keep input_text format consistent with original
            converted.append(
                {
                    "input_text": example["input_text"],  # Keep same input format
                    "output_markdown": markdown,
                }
            )

            # Progress indicator
            if (i + 1) % 200 == 0:
                print(f"   Processed {i + 1}/{len(data)}...")

        except Exception as e:
            validation_stats["errors"] += 1
            print(f"   ❌ Error in example {i}: {str(e)[:100]}")

    print("\n✅ Conversion complete!")
    print(f"   Success: {validation_stats['success']}/{len(data)}")
    print(f"   Warnings: {validation_stats['warnings']}")
    print(f"   Errors: {validation_stats['errors']}\n")

    # Check output statistics
    lengths = [len(ex["output_markdown"]) for ex in converted]
    avg_length = sum(lengths) / len(lengths)

    print("📊 Output Statistics:")
    print(f"   Average length: {avg_length:.0f} chars")
    print(f"   Min length: {min(lengths)} chars")
    print(f"   Max length: {max(lengths)} chars")
    print("   Expected: 200-400 chars (simplified format)")
    print()

    if avg_length < 100:
        print("   ⚠️  WARNING: Average length seems too short")
        print("   Check if conversion is losing information")
    elif avg_length > 500:
        print("   ⚠️  WARNING: Average length higher than expected")
        print("   Model might struggle with long outputs")
    else:
        print("   ✅ Length distribution looks good")

    print()

    # Save converted data
    print(f"💾 Saving to: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(converted, f, indent=2)

    print(f"   ✅ Saved {len(converted)} examples\n")

    # Show sample
    print("📝 Sample Output (first example):")
    print("─" * 80)
    print(converted[0]["output_markdown"])
    print("─" * 80)
    print()

    print("📝 Sample Output (example with no modules - edge case):")
    # Find example with no modules
    no_modules = next(
        (ex for ex in converted if "## Selected Modules" not in ex["output_markdown"]),
        None,
    )
    if no_modules:
        print("─" * 80)
        print(no_modules["output_markdown"])
        print("─" * 80)
    else:
        print("   (No examples found with zero modules)")
    print()

    # Final summary
    print("=" * 80)
    print("✅ PHASE 1 COMPLETE")
    print("=" * 80)
    print()
    print(f"✅ Converted {len(converted)} examples to simplified markdown")
    print(f"✅ Average output length: {avg_length:.0f} chars")
    print(f"✅ Validation passed: {validation_stats['success']}/{len(data)}")
    print()
    print("🚀 Next step: Phase 2 - Build markdown parser")
    print()

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
