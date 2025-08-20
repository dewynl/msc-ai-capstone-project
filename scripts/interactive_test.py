#!/usr/bin/env python3
"""
Interactive RAG System Test
Test your own custom course requirements
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.rag_system import generate_rag_syllabus


def interactive_test():
    """Interactive testing interface"""

    print("🎯 Interactive RAG System Test")
    print("Enter your course details to generate a syllabus")
    print("=" * 50)

    # Get user input
    title = input("Course Title: ").strip()
    if not title:
        title = "Sample Course"

    print(
        "\nDomain options: Computer Science, Data Science, Business, Mathematics, Engineering, Leadership"
    )
    domain = input("Domain: ").strip()
    if not domain:
        domain = "Computer Science"

    print("\nLevel options: undergraduate, graduate, professional")
    level = input("Level: ").strip()
    if not level:
        level = "undergraduate"

    description = input("Course Description: ").strip()
    if not description:
        description = f"Introduction to {title.lower()} covering fundamental concepts and practical applications"

    # Create course requirements
    course = {
        "title": title,
        "domain": domain,
        "level": level,
        "description": description,
    }

    print("\n" + "=" * 50)
    print("🚀 Generating syllabus...")
    print("=" * 50)

    try:
        result = generate_rag_syllabus(course)

        # Display result
        print("\n📄 Generated Syllabus:")
        print("=" * 80)
        print(result["syllabus_content"])
        print("=" * 80)

        # Save option
        save = input("\nSave syllabus to file? (y/n): ").strip().lower()
        if save in ["y", "yes"]:
            filename = f"{title.replace(' ', '_').lower()}_syllabus.md"
            with open(filename, "w") as f:
                f.write(result["syllabus_content"])
            print(f"✅ Saved to: {filename}")

        # Show components
        print("\n🔍 Retrieved Components:")
        for comp_type, components in result["retrieved_components"].items():
            print(f"  {comp_type}: {len(components)} components")
            if components:
                print(f"    Example: {components[0].get('title', 'N/A')}")

    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    interactive_test()
