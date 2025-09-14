#!/usr/bin/env python3
"""
Rebuild ChromaDB Vector Store
"""

import sys
from pathlib import Path

from rag.component_indexer import build_component_store

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))


def main():
    print("Rebuilding ChromaDB vector store...")
    print("This will take a few minutes to process ~98k components")
    print("-" * 50)

    try:
        # Build the component store (this will create new ChromaDB)
        store = build_component_store(persist_directory="./chroma_db")

        # Get stats
        stats = store.get_collection_stats()
        print("Vector store rebuilt successfully!")
        print(f"Total components indexed: {stats['total_components']}")

        # Quick test search
        print("\nTesting search functionality...")
        results = store.search("machine learning algorithms", k=3)
        print(f"Test search returned {len(results)} results")
        for i, (component, score) in enumerate(results, 1):
            print(f"  {i}. {component.get('title', 'N/A')[:50]} (score: {score:.3f})")

        print("\nVector store is ready for use!")

    except Exception as e:
        print(f"Error rebuilding vector store: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
