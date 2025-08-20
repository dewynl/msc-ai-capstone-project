#!/usr/bin/env python3
"""
Quick RAG System Test
Simple test for one course generation
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.rag_system import generate_rag_syllabus


def quick_test():
    """Quick test of RAG system"""

    # Test course
    course = {
        "title": "Web Development Fundamentals",
        "domain": "Computer Science",
        "level": "undergraduate",
        "description": "Introduction to web development including HTML, CSS, JavaScript, and modern frameworks",
    }

    print("🧪 Quick RAG Test")
    print(f"Course: {course['title']}")
    print(f"Domain: {course['domain']}")
    print("-" * 50)

    try:
        result = generate_rag_syllabus(course)

        # Save to file
        with open("generated_syllabus.md", "w") as f:
            f.write(result["syllabus_content"])

        print("✅ Success! Generated syllabus saved to: generated_syllabus.md")
        print("📊 Stats:")
        print(f"  - Length: {len(result['syllabus_content'])} characters")
        print(f"  - Words: {len(result['syllabus_content'].split())} words")
        print(
            f"  - Retrieved: {sum(len(comps) for comps in result['retrieved_components'].values())} components"
        )

        # Quick structure check
        content = result["syllabus_content"]
        checks = {
            "Headers": content.count("#"),
            "Weekly Schedule": "Week 1:" in content,
            "Assessment Table": "|" in content and "points" in content.lower(),
            "Learning Objectives": "objectives" in content.lower(),
            "Course Policies": "policy" in content.lower(),
        }

        print("📋 Structure Check:")
        for check, result in checks.items():
            print(f"  - {check}: {'✅' if result else '❌'}")

    except Exception as e:
        print(f"❌ Failed: {e}")


if __name__ == "__main__":
    quick_test()
