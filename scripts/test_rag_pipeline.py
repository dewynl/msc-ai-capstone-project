#!/usr/bin/env python3
"""
Test RAG pipeline with corrected multi-domain data
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from rag.vector_store import SyllabusComponentStore
from rag.retrieval_pipeline import ComponentRetrievalPipeline
from rag.rag_t5_generator import RAGEnhancedT5Generator


def test_rag_pipeline():
    """Test the complete RAG pipeline with various domain scenarios"""
    print("🧪 Testing RAG Pipeline with Multi-Domain Data")
    print("=" * 50)

    store = SyllabusComponentStore(persist_directory="./chroma_db")
    retrieval_pipeline = ComponentRetrievalPipeline(store)
    generator = RAGEnhancedT5Generator()

    test_scenarios = [
        {
            "title": "Introduction to Machine Learning",
            "domain": "computer_science",
            "level": "intermediate",
            "description": "Fundamentals of machine learning algorithms and applications"
        },
        {
            "title": "Calculus and Mathematical Analysis",
            "domain": "mathematics",
            "level": "beginner",
            "description": "Core calculus concepts including derivatives and integrals"
        },
        {
            "title": "Physics for Engineers",
            "domain": "physics",
            "level": "intermediate",
            "description": "Mechanics, thermodynamics, and electromagnetic principles"
        },
        {
            "title": "System Design and Engineering",
            "domain": "engineering",
            "level": "advanced",
            "description": "Complex system architecture and optimization"
        }
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*20} Scenario {i}: {scenario['title']} {'='*20}")
        print(f"Domain: {scenario['domain']} | Level: {scenario['level']}")

        # Test retrieval
        print("\n🔍 Component Retrieval:")
        components = retrieval_pipeline.retrieve_components(scenario, k_per_type=3)

        for comp_type, comp_list in components.items():
            print(f"  {comp_type.title()}: {len(comp_list)} components")
            for j, comp in enumerate(comp_list[:2], 1):
                domain = comp.get('domain', 'unknown')
                title = comp.get('title', 'No title')[:40]
                print(f"    {j}. [{domain}] {title}...")

        # Test filtering
        print("\n🔽 Domain Filtering:")
        filtered = retrieval_pipeline.filter_by_domain_and_level(components, scenario)

        for comp_type, comp_list in filtered.items():
            original_count = len(components.get(comp_type, []))
            filtered_count = len(comp_list)
            print(f"  {comp_type.title()}: {original_count} → {filtered_count} components")

        # Test diversity selection
        print("\n🌈 Diversity Selection:")
        diverse = retrieval_pipeline.get_diverse_components(scenario)

        for comp_type, comp_list in diverse.items():
            domains = set(comp.get('domain', '') for comp in comp_list)
            print(f"  {comp_type.title()}: {len(comp_list)} components across {len(domains)} domains")
            if len(domains) > 1:
                print(f"    Domains: {', '.join(sorted(domains))}")

        # Test prompt generation
        print("\n📝 Prompt Generation:")
        prompt = generator.create_prompt(scenario, diverse)
        print(f"  Prompt length: {len(prompt)} characters")
        print(f"  First 200 chars: {prompt[:200]}...")

        # Optional: Generate syllabus (comment out if model not available)
        try:
            print("\n⚡ Syllabus Generation:")
            syllabus = generator.generate_syllabus(prompt, max_length=500)
            print(f"  Generated length: {len(syllabus)} characters")
            print(f"  Preview: {syllabus[:150]}...")
        except Exception as e:
            print(f"  ⚠️ Generation skipped: {e}")

        print(f"\n{'='*60}")

    print("\n✅ RAG Pipeline testing completed!")


def test_cross_domain_scenarios():
    """Test scenarios that should pull from multiple domains"""
    print("\n🔀 Testing Cross-Domain Scenarios")
    print("=" * 40)

    store = SyllabusComponentStore(persist_directory="./chroma_db")
    retrieval_pipeline = ComponentRetrievalPipeline(store)

    cross_domain_scenarios = [
        {
            "title": "Mathematical Foundations for Computer Science",
            "domain": "computer_science",
            "level": "intermediate",
            "topics": ["discrete mathematics", "algorithms", "logic"]
        },
        {
            "title": "Computational Physics",
            "domain": "physics",
            "level": "advanced",
            "topics": ["numerical methods", "simulation", "modeling"]
        }
    ]

    for scenario in cross_domain_scenarios:
        print(f"\n📋 {scenario['title']}")

        diverse = retrieval_pipeline.get_diverse_components(scenario)

        all_domains = set()
        for comp_type, comp_list in diverse.items():
            domains = set(comp.get('domain', '') for comp in comp_list)
            all_domains.update(domains)
            print(f"  {comp_type}: {domains}")

        print(f"  Total domains accessed: {len(all_domains)} ({', '.join(sorted(all_domains))})")


if __name__ == "__main__":
    test_rag_pipeline()
    test_cross_domain_scenarios()