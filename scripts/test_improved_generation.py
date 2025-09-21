#!/usr/bin/env python3
"""
Test improved syllabus generation with template-based approach
"""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from rag.vector_store import SyllabusComponentStore
from rag.retrieval_pipeline import ComponentRetrievalPipeline
from rag.rag_t5_generator import RAGEnhancedT5Generator


def generate_with_rag_pipeline():
    """Test syllabus generation using RAG pipeline instead of raw T5"""
    print("🧪 Testing RAG-Enhanced Generation")
    print("=" * 40)

    # Initialize RAG components
    store = SyllabusComponentStore(persist_directory="./chroma_db")
    retrieval_pipeline = ComponentRetrievalPipeline(store)
    generator = RAGEnhancedT5Generator()

    # Test scenarios
    test_scenarios = [
        {
            "title": "Introduction to Machine Learning",
            "domain": "computer_science",
            "level": "intermediate",
            "description": "Fundamentals of machine learning algorithms and applications"
        },
        {
            "title": "Linear Algebra Fundamentals",
            "domain": "mathematics",
            "level": "beginner",
            "description": "Core concepts in linear algebra including vectors, matrices, and transformations"
        },
        {
            "title": "Classical Mechanics",
            "domain": "physics",
            "level": "intermediate",
            "description": "Newtonian mechanics covering forces, motion, and energy"
        }
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*20} Test {i}: {scenario['title']} {'='*20}")

        # Retrieve components
        components = retrieval_pipeline.get_diverse_components(scenario)

        print(f"📦 Retrieved components:")
        for comp_type, comp_list in components.items():
            domains = set(comp.get('domain', '') for comp in comp_list)
            print(f"  {comp_type}: {len(comp_list)} components from {domains}")

        # Create prompt
        prompt = generator.create_prompt(scenario, components)
        print(f"\n📝 Prompt length: {len(prompt)} characters")

        # Generate syllabus
        try:
            syllabus = generator.generate_syllabus(prompt, max_length=1000)
            print(f"\n📄 Generated syllabus ({len(syllabus)} chars):")
            print(syllabus[:300] + "..." if len(syllabus) > 300 else syllabus)

        except Exception as e:
            print(f"\n❌ Generation failed: {e}")

        print(f"\n{'='*60}")


def create_simple_template_generator():
    """Create a simple template-based generator as fallback"""
    print("\n🔧 Creating Template-Based Generator")
    print("=" * 35)

    def template_generate(requirements, components):
        """Generate syllabus using templates"""

        # Extract learning objectives from modules
        objectives = []
        for module in components.get("modules", [])[:2]:
            module_objectives = module.get("learning_objectives", [])
            objectives.extend(module_objectives[:2])

        # Create structured syllabus
        syllabus = {
            "course_info": {
                "title": requirements["title"],
                "domain": requirements["domain"],
                "level": requirements["level"],
                "description": requirements["description"]
            },
            "learning_objectives": objectives[:4],
            "modules": [
                {
                    "title": module.get("title", ""),
                    "description": module.get("description", "")[:150] + "...",
                    "estimated_hours": module.get("estimated_hours", 4)
                }
                for module in components.get("modules", [])[:3]
            ],
            "activities": [
                {
                    "title": activity.get("title", ""),
                    "bloom_level": activity.get("bloom_level", "apply"),
                    "estimated_hours": activity.get("estimated_hours", 1)
                }
                for activity in components.get("activities", [])[:3]
            ],
            "assessments": [
                {
                    "title": assessment.get("title", ""),
                    "assessment_type": assessment.get("assessment_type", "exam"),
                    "estimated_hours": assessment.get("estimated_hours", 2)
                }
                for assessment in components.get("assessments", [])[:2]
            ]
        }

        return syllabus

    # Test template approach
    store = SyllabusComponentStore(persist_directory="./chroma_db")
    retrieval_pipeline = ComponentRetrievalPipeline(store)

    test_req = {
        "title": "Introduction to Machine Learning",
        "domain": "computer_science",
        "level": "intermediate",
        "description": "Fundamentals of machine learning algorithms and applications"
    }

    components = retrieval_pipeline.get_diverse_components(test_req)
    result = template_generate(test_req, components)

    print("\n📄 Template-Generated Syllabus:")
    print(json.dumps(result, indent=2)[:500] + "...")

    return template_generate


if __name__ == "__main__":
    # Test both approaches
    generate_with_rag_pipeline()
    create_simple_template_generator()

    print("\n💡 Recommendations:")
    print("1. Use template-based generation for reliable JSON structure")
    print("2. Consider retraining T5 with more data and better prompts")
    print("3. Focus on RAG component quality over T5 generation complexity")