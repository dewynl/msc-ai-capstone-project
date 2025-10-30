#!/usr/bin/env python3
"""
Test script for the trained prerequisite-aware CodeT5 model.

Tests end-to-end syllabus generation with the newly trained model.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from generate_syllabus import generate_complete_syllabus
from model_inference import SyllabusGenerator


def load_rag_database():
    """Load the component database."""
    base_dir = Path(__file__).parent.parent

    with open(base_dir / "data/components/modules.json") as f:
        modules = json.load(f)
    with open(base_dir / "data/components/activities.json") as f:
        activities = json.load(f)
    with open(base_dir / "data/components/assessments.json") as f:
        assessments = json.load(f)

    return {
        "modules": modules,
        "activities": activities,
        "assessments": assessments,
    }


def test_course_generation(
    course_requirements: dict, rag_database: dict, generator: SyllabusGenerator
):
    """
    Test syllabus generation for a single course.

    Args:
        course_requirements: Course specification
        rag_database: Component database
        generator: Pre-loaded model generator
    """
    print("\n" + "=" * 80)
    print(f"🎓 Testing: {course_requirements['title']}")
    print(f"   Domain: {course_requirements.get('domain', 'general')}")
    print(f"   Level: {course_requirements.get('level', 'beginner')}")
    print("=" * 80)

    try:
        result = generate_complete_syllabus(
            course_requirements=course_requirements,
            rag_database=rag_database,
            generator=generator,
            ranker=None,  # Will be created internally
        )

        if result.get("success"):
            print("\n✅ Generation successful!")

            # Display key information
            syllabus = result.get("syllabus", {})
            course_info = syllabus.get("course_info", {})
            modules = syllabus.get("modules", [])

            print(f"\n📋 Course: {course_info.get('title', 'N/A')}")
            print(f"   Duration: {course_info.get('duration', 'N/A')}")
            print(f"   Modules: {len(modules)}")

            print("\n📚 Module Sequence:")
            for i, module in enumerate(modules[:5], 1):  # Show first 5
                title = module.get("title", "Unknown")
                weeks = module.get("week_range", "N/A")
                print(f"   {i}. {title} (Weeks {weeks})")

            if len(modules) > 5:
                print(f"   ... and {len(modules) - 5} more modules")

            # Show quality metrics
            quality_metrics = result.get("quality_metrics", {})
            if quality_metrics:
                print("\n📊 Quality Metrics:")
                prereq_acc = quality_metrics.get("prerequisite_accuracy", 0)
                difficulty_prog = quality_metrics.get("difficulty_progression", 0)
                print(f"   Prerequisite coherence: {prereq_acc:.1%}")
                print(f"   Difficulty progression: {difficulty_prog:.1%}")

            # Show parsing warnings if any
            warnings = result.get("warnings", [])
            if warnings:
                print(f"\n⚠️  Warnings: {len(warnings)}")
                for warning in warnings[:3]:  # Show first 3
                    print(f"   • {warning}")

            return True

        else:
            print(f"\n❌ Generation failed: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"\n❌ Exception during generation: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("=" * 80)
    print("🧪 TESTING TRAINED PREREQUISITE-AWARE MODEL")
    print("=" * 80)
    print()
    print("Model: models/codet5-sequenced/checkpoint-196")
    print("Training: 1,300 prerequisite-aware examples")
    print("Final eval loss: 1.4677")
    print()

    # Load model
    print("Loading trained model...")
    model_path = "models/codet5-sequenced/checkpoint-196"
    generator = SyllabusGenerator(model_path=model_path)

    # Load component database
    print("Loading component database...")
    rag_database = load_rag_database()
    print(f"  Modules: {len(rag_database['modules'])}")
    print(f"  Activities: {len(rag_database['activities'])}")
    print(f"  Assessments: {len(rag_database['assessments'])}")

    # Test courses across different domains and levels
    test_courses = [
        {
            "title": "Advanced Machine Learning",
            "domain": "computer_science",
            "level": "postgraduate",
            "duration": "semester",
            "description": "Advanced topics in machine learning including deep learning, reinforcement learning, and neural architectures.",
        },
        {
            "title": "Introduction to Data Structures",
            "domain": "computer_science",
            "level": "undergraduate",
            "duration": "quarter",
            "description": "Fundamental data structures and their applications in algorithm design.",
        },
        {
            "title": "Calculus and Analysis",
            "domain": "mathematics",
            "level": "undergraduate",
            "duration": "semester",
            "description": "Comprehensive study of differential and integral calculus with applications.",
        },
    ]

    # Track results
    results = []

    # Test each course
    for i, course in enumerate(test_courses, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(test_courses)}")
        success = test_course_generation(course, rag_database, generator)
        results.append({"course": course["title"], "success": success})

    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    successful = sum(1 for r in results if r["success"])
    total = len(results)

    print(f"\nResults: {successful}/{total} successful")
    print("\nDetails:")
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"  {status} {r['course']}")

    print("\n" + "=" * 80)

    if successful == total:
        print("✨ All tests passed! Model is working correctly.")
    elif successful > 0:
        print("⚠️  Some tests passed. Review failures above.")
    else:
        print("❌ All tests failed. Check model and dependencies.")

    return successful == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
