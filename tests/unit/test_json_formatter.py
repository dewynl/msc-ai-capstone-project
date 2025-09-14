#!/usr/bin/env python3
"""
Test JSON-Structured Syllabus Formatter
Demonstrates the new web-app-ready JSON output format
"""

import json
import sys
from pathlib import Path

# Add src to path (go up two levels from tests/unit/)
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from rag.syllabus_formatter import SyllabusFormatter


def test_json_formatter():
    """Test the new JSON-structured syllabus formatter"""

    print("🧪 Testing JSON Syllabus Formatter for Web Apps...")
    print("=" * 60)

    # Mock course info
    course_info = {
        "title": "Advanced React Development",
        "domain": "Software Development",
        "level": "intermediate",
        "description": "Master advanced React patterns, state management, and performance optimization",
    }

    # Mock retrieved components (simulating what RAG would return)
    mock_components = {
        "modules": [
            {
                "title": "React Hooks and Custom Components",
                "description": "Advanced component patterns using hooks, context, and custom logic",
            },
            {
                "title": "State Management with Redux Toolkit",
                "description": "Modern Redux patterns, RTK Query, and global state architecture",
            },
            {
                "title": "Performance Optimization Techniques",
                "description": "Code splitting, memoization, and React performance best practices",
            },
        ],
        "activities": [
            {"title": "Build Custom Hook Library"},
            {"title": "Implement Redux Store Architecture"},
            {"title": "Performance Audit and Optimization"},
        ],
        "assessments": [
            {
                "title": "Component Architecture Challenge",
                "description": "Design and implement scalable React component patterns",
            },
            {
                "title": "Full-Stack Application Project",
                "description": "Complete React application with state management and optimization",
            },
            {
                "title": "Performance Portfolio Review",
                "description": "Comprehensive review of optimized React applications",
            },
        ],
    }

    # Test the JSON formatter
    formatter = SyllabusFormatter()
    syllabus_json = formatter.format_syllabus(
        course_info,
        "",
        mock_components,  # T5 output not used
    )

    print("✅ JSON Syllabus Generated Successfully!")
    print("\n📊 Structure Analysis:")

    # Analyze the JSON structure
    print(f"📚 Learning Modules: {len(syllabus_json['learning_modules'])}")
    print(f"🎯 Learning Objectives: {len(syllabus_json['learning_objectives'])}")
    print(
        f"📋 Assessment Components: {len(syllabus_json['assessment_strategy']['components'])}"
    )
    print(
        f"🔗 Has Integration Module: {'Yes' if any(m['type'] == 'integration' for m in syllabus_json['learning_modules']) else 'No'}"
    )

    print("\n🎯 Web App Benefits:")
    benefits = [
        "✅ Structured data for easy rendering",
        "✅ Unique IDs for frontend state management",
        "✅ Typed assessment components",
        "✅ Metadata for analytics",
        "✅ Module progression logic",
        "✅ No markdown parsing needed",
    ]
    for benefit in benefits:
        print(f"  {benefit}")

    # Show key structure
    print("\n📝 JSON Structure Preview:")
    print("=" * 50)

    # Pretty print key sections
    key_structure = {
        "title": syllabus_json["title"],
        "domain": syllabus_json["domain"],
        "learning_objectives": syllabus_json["learning_objectives"][:2],  # First 2
        "learning_modules": [
            {
                "id": m["id"],
                "title": m["title"],
                "type": m["type"],
                "activities_count": len(m["learning_activities"]),
            }
            for m in syllabus_json["learning_modules"]
        ],
        "assessment_strategy": {
            "total_components": len(syllabus_json["assessment_strategy"]["components"]),
            "total_weight": syllabus_json["assessment_strategy"]["total_weight"],
            "sample_component": syllabus_json["assessment_strategy"]["components"][0],
        },
    }

    print(json.dumps(key_structure, indent=2))

    # Save the complete JSON to project root
    output_path = Path(__file__).parent.parent.parent / "test_json_syllabus.json"
    with open(output_path, "w") as f:
        json.dump(syllabus_json, f, indent=2)

    print("\n💾 Complete JSON saved to: test_json_syllabus.json")

    # Show how this would be used in a web app
    print("\n🌐 Web App Usage Examples:")
    print("=" * 30)

    print("// React Component Example:")
    print("const SyllabusModule = ({ module }) => (")
    print("  <div key={module.id} className='module'>")
    print("    <h3>{module.title}</h3>")
    print("    <p>{module.description}</p>")
    print("    <ActivityList activities={module.learning_activities} />")
    print("  </div>")
    print(");")

    print("\n// Assessment Rendering:")
    print("assessments.components.map(assessment => (")
    print("  <AssessmentCard")
    print("    key={assessment.id}")
    print("    name={assessment.name}")
    print("    weight={assessment.weight}")
    print("    type={assessment.type}")
    print("  />")
    print("));")


if __name__ == "__main__":
    test_json_formatter()
