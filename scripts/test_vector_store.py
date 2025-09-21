#!/usr/bin/env python3
"""
Test vector store retrieval performance with simplified schema
"""

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from rag.vector_store import SyllabusComponentStore


def test_retrieval_performance():
    """Test various search queries across domains"""
    print("🧪 Testing Vector Store Retrieval Performance")
    print("=" * 45)

    store = SyllabusComponentStore(persist_directory="./chroma_db")

    test_queries = [
        ("algorithms and data structures", "computer_science"),
        ("calculus and derivatives", "mathematics"),
        ("force and motion", "physics"),
        ("system design", "engineering"),
        ("machine learning", "computer_science"),
        ("probability and statistics", "mathematics"),
        ("beginner programming", "computer_science"),
        ("advanced mathematical concepts", "mathematics")
    ]

    print(f"📈 Collection contains {store.get_collection_stats()['total_components']} components\n")

    for query, expected_domain in test_queries:
        print(f"Query: '{query}'")
        print(f"Expected domain: {expected_domain}")

        start_time = time.time()
        results = store.search(query, k=5)
        search_time = time.time() - start_time

        print(f"Search time: {search_time:.3f}s")
        print(f"Results found: {len(results)}")

        for i, (component, score) in enumerate(results[:3]):
            print(f"  {i+1}. [{component.get('domain', 'unknown')}] {component.get('title', 'No title')[:60]}... (score: {score:.3f})")

        print("-" * 60)

    print("\n🔍 Testing Component Type Filtering:")

    activities_results = store.search("programming exercises", k=3, component_type="activities")
    assessments_results = store.search("programming test", k=3, component_type="assessments")
    modules_results = store.search("programming concepts", k=3, component_type="modules")

    print(f"Activities matching 'programming exercises': {len(activities_results)}")
    print(f"Assessments matching 'programming test': {len(assessments_results)}")
    print(f"Modules matching 'programming concepts': {len(modules_results)}")

    print("\n🌐 Testing Cross-Domain Queries:")
    cross_domain_queries = [
        "mathematical foundations",
        "problem solving methods",
        "data analysis techniques"
    ]

    for query in cross_domain_queries:
        results = store.search(query, k=5)
        domains_found = set(comp.get('domain', 'unknown') for comp, _ in results)
        print(f"'{query}' found in domains: {', '.join(sorted(domains_found))}")

    print("\n✅ Vector store testing completed!")


if __name__ == "__main__":
    test_retrieval_performance()