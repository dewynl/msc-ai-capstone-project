#!/usr/bin/env python3
"""
Test Fine-tuned T5 Syllabus Generation
Test the fine-tuned model's ability to generate structured syllabi
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.rag_system import generate_rag_syllabus
from src.training.t5_syllabus_trainer import SyllabusTrainer, SyllabusTrainingConfig


def test_fine_tuned_standalone():
    """Test fine-tuned model standalone (without RAG)"""

    print("🧪 Testing Fine-tuned T5 Model (Standalone)")
    print("=" * 60)

    # Initialize trainer with fine-tuned model
    config = SyllabusTrainingConfig()
    trainer = SyllabusTrainer(config)

    # Test course requirements (same format as training data)
    test_input = """Generate syllabus for: Introduction to Machine Learning
Domain: Computer Science Level: undergraduate
Duration: semester
Description: Fundamentals of machine learning algorithms and applications including supervised learning, unsupervised learning, and neural networks. Students will implement algorithms and work on real-world datasets.
Learning Objectives:
- Understand supervised and unsupervised learning algorithms
- Implement basic ML algorithms from scratch
- Evaluate model performance using appropriate metrics
Target Audience: Undergraduate computer science students with programming experience"""

    print("📝 Input:")
    print(test_input)
    print("\n" + "=" * 60)

    # Generate with fine-tuned model
    try:
        generated = trainer.generate_syllabus(
            test_input, "./models/t5-syllabus-finetuned"
        )
        print("🎯 Generated Syllabus:")
        print(generated)

        # Analyze output
        print("\n" + "=" * 60)
        print("📊 Analysis:")
        print(f"Length: {len(generated)} characters")
        print(f"Word count: {len(generated.split())} words")
        print(f"Contains '##': {'##' in generated}")
        print(f"Contains 'Week': {'Week' in generated}")
        print(f"Contains 'Assessment': {'Assessment' in generated}")

    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback

        traceback.print_exc()


def test_fine_tuned_with_rag():
    """Test fine-tuned model with RAG enhancement"""

    print("\n\n🔬 Testing Fine-tuned T5 Model with RAG")
    print("=" * 60)

    # Test course requirements
    test_requirements = {
        "title": "Advanced Database Systems",
        "domain": "Computer Science",
        "level": "graduate",
        "description": "Advanced topics in database systems including distributed databases, NoSQL systems, and database performance optimization",
    }

    print("📝 Course Requirements:")
    for key, value in test_requirements.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)

    try:
        # Generate with RAG + fine-tuned model
        result = generate_rag_syllabus(test_requirements)

        print("🎯 Generated Syllabus:")
        print(result["syllabus_content"])

        print("\n📋 Retrieved Components:")
        for comp_type, components in result["retrieved_components"].items():
            print(f"  {comp_type}: {len(components)} components")
            for i, comp in enumerate(components[:2], 1):
                print(f"    {i}. {comp.get('title', 'N/A')}")

        # Analysis
        content = result["syllabus_content"]
        print("\n" + "=" * 60)
        print("📊 Analysis:")
        print(f"Length: {len(content)} characters")
        print(f"Word count: {len(content.split())} words")
        print("Contains structured elements:")
        print(f"  - Headers (##): {'##' in content}")
        print(f"  - Weekly schedule: {'Week' in content}")
        print(f"  - Assessment plan: {'Assessment' in content}")
        print(f"  - Learning objectives: {'objective' in content.lower()}")
        print(
            f"  - Course policies: {'policy' in content.lower() or 'Policy' in content}"
        )

    except Exception as e:
        print(f"❌ RAG generation failed: {e}")
        import traceback

        traceback.print_exc()


def compare_base_vs_finetuned():
    """Compare base T5 vs fine-tuned model output"""

    print("\n\n⚖️  Comparing Base vs Fine-tuned Models")
    print("=" * 60)

    from src.rag.rag_t5_generator import RAGEnhancedT5Generator

    test_prompt = """Generate syllabus for: Data Structures and Algorithms
Domain: Computer Science Level: undergraduate
Duration: semester
Description: Introduction to fundamental data structures and algorithmic problem solving
Available Educational Components:
Relevant Modules:
1. Graph Algorithms: BFS and DFS traversal methods
2. Hash Tables: Implementation and collision resolution
Relevant Activities:
1. Binary search tree implementation lab
2. Algorithm complexity analysis workshop
Relevant Assessments:
1. Data structures practical exam
2. Algorithm analysis quiz"""

    # Test with base model
    print("🏃 Base T5 Model:")
    try:
        base_generator = RAGEnhancedT5Generator(model_name="t5-small")
        base_output = base_generator.generate_syllabus(test_prompt, max_length=512)
        print(base_output)
        print(f"Length: {len(base_output)} chars, Words: {len(base_output.split())}")
    except Exception as e:
        print(f"Base model failed: {e}")

    print("\n" + "-" * 40)

    # Test with fine-tuned model
    print("🎓 Fine-tuned Model:")
    try:
        finetuned_generator = RAGEnhancedT5Generator(
            model_name="./models/t5-syllabus-finetuned"
        )
        finetuned_output = finetuned_generator.generate_syllabus(
            test_prompt, max_length=512
        )
        print(finetuned_output)
        print(
            f"Length: {len(finetuned_output)} chars, Words: {len(finetuned_output.split())}"
        )
    except Exception as e:
        print(f"Fine-tuned model failed: {e}")


def main():
    """Run all tests"""

    print("🚀 Testing Fine-tuned T5 Syllabus Generation")
    print("=" * 80)

    # Test 1: Standalone fine-tuned model
    test_fine_tuned_standalone()

    # Test 2: Fine-tuned model with RAG
    test_fine_tuned_with_rag()

    # Test 3: Comparison
    compare_base_vs_finetuned()

    print("\n✅ All tests completed!")


if __name__ == "__main__":
    main()
