#!/usr/bin/env python3
"""
Test Improved Fine-tuned T5 Generation
Test the improved prompting and generation parameters
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.rag_system import generate_rag_syllabus
from src.rag.rag_t5_generator import RAGEnhancedT5Generator


def test_improved_generation():
    """Test improved generation with better prompting"""

    print("🧪 Testing Improved Fine-tuned T5 Generation")
    print("=" * 70)

    # Test case that should produce structured output
    test_requirements = {
        "title": "Introduction to Machine Learning",
        "domain": "Computer Science",
        "level": "undergraduate",
        "description": "Comprehensive introduction to machine learning algorithms including supervised learning, unsupervised learning, and neural networks. Students will implement algorithms and work with real datasets.",
    }

    print("📝 Course Requirements:")
    for key, value in test_requirements.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 70)
    print("🎯 Generating Syllabus with Improved RAG System...")

    try:
        # Generate with improved RAG system
        result = generate_rag_syllabus(test_requirements)

        print("\n📄 Generated Syllabus:")
        print("-" * 70)
        print(result["syllabus_content"])
        print("-" * 70)

        # Analysis
        content = result["syllabus_content"]
        print("\n📊 Structure Analysis:")
        print(f"  Length: {len(content)} characters")
        print(f"  Word count: {len(content.split())} words")
        print(f"  Lines: {len(content.split(chr(10)))}")

        # Check for structured elements
        structure_check = {
            "Headers (# ##)": any(line.startswith("#") for line in content.split("\n")),
            "Weekly Schedule": "Week" in content
            and ("Monday" in content or "Topics:" in content),
            "Assessment Plan": "Assessment" in content
            and ("points" in content.lower() or "%" in content),
            "Learning Objectives": "objective" in content.lower() and "•" in content,
            "Course Policies": "policy" in content.lower() or "Policy" in content,
            "Grading Scale": "grading" in content.lower()
            and ("A:" in content or "90" in content),
        }

        print("\n✅ Structure Elements Found:")
        for element, found in structure_check.items():
            status = "✅" if found else "❌"
            print(f"  {status} {element}")

        # Show retrieved components
        print("\n🔍 Retrieved Components:")
        for comp_type, components in result["retrieved_components"].items():
            print(f"  {comp_type}: {len(components)} components")

        # Show the prompt used
        print("\n📋 Input Prompt Used:")
        print("-" * 50)
        print(result["prompt"])
        print("-" * 50)

    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback

        traceback.print_exc()


def test_standalone_with_training_format():
    """Test standalone model with exact training format"""

    print("\n\n🎓 Testing Standalone Model with Training Format")
    print("=" * 70)

    # Create input exactly like training data
    training_format_input = """Generate syllabus for: Data Structures and Algorithms
Domain: Computer Science Level: undergraduate
Duration: semester
Description: Introduction to fundamental data structures and algorithmic problem solving including arrays, linked lists, trees, graphs, and sorting algorithms
Learning Objectives:
- Understand and implement fundamental data structures
- Analyze algorithm complexity using Big O notation
- Design efficient algorithms for common problems
- Apply data structures to solve real-world programming challenges
Target Audience: Undergraduate computer science students with programming experience in Python or Java"""

    print("📝 Training Format Input:")
    print(training_format_input)

    print("\n" + "=" * 70)
    print("🎯 Generating with Fine-tuned Model...")

    try:
        # Use fine-tuned model directly
        generator = RAGEnhancedT5Generator(model_name="./models/t5-syllabus-finetuned")

        # Generate with longer max_length
        generated = generator.generate_syllabus(training_format_input, max_length=3072)

        print("\n📄 Generated Syllabus:")
        print("-" * 70)
        print(generated)
        print("-" * 70)

        # Analysis
        print("\n📊 Analysis:")
        print(f"  Length: {len(generated)} characters")
        print(f"  Word count: {len(generated.split())} words")
        print(f"  Lines: {len(generated.split(chr(10)))}")

        # Check for markdown structure
        lines = generated.split("\n")
        has_headers = any(line.startswith("#") for line in lines)
        has_tables = any("|" in line for line in lines)
        has_bullets = any(
            line.strip().startswith("•") or line.strip().startswith("-")
            for line in lines
        )

        print(f"  Contains markdown headers: {has_headers}")
        print(f"  Contains tables: {has_tables}")
        print(f"  Contains bullet points: {has_bullets}")

        # Look for specific sections
        sections_found = []
        for line in lines:
            if line.startswith("##"):
                sections_found.append(line.strip())

        if sections_found:
            print(f"  Sections found: {len(sections_found)}")
            for section in sections_found[:5]:  # Show first 5
                print(f"    - {section}")

    except Exception as e:
        print(f"❌ Standalone generation failed: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Run improved generation tests"""

    print("🚀 Testing Improved Fine-tuned T5 Syllabus Generation")
    print("=" * 80)

    # Test 1: Improved RAG system
    test_improved_generation()

    # Test 2: Standalone with training format
    test_standalone_with_training_format()

    print("\n✅ All improved generation tests completed!")


if __name__ == "__main__":
    main()
