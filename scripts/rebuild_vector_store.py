#!/usr/bin/env python3
"""
Rebuild vector store with simplified component schema
Loads extracted components and reindexes them in ChromaDB
"""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from rag.vector_store import SyllabusComponentStore


def load_components(file_path: Path) -> list:
    """Load components from JSON file"""
    if not file_path.exists():
        print(f"Warning: {file_path} does not exist")
        return []

    with open(file_path, 'r') as f:
        components = json.load(f)

    print(f"Loaded {len(components)} components from {file_path.name}")
    return components


def main():
    """Rebuild vector store with extracted components"""
    print("🔄 Rebuilding Vector Store")
    print("=" * 30)

    store = SyllabusComponentStore(persist_directory="./chroma_db")
    data_dir = Path("data/components")

    activities = load_components(data_dir / "activities.json")
    assessments = load_components(data_dir / "assessments.json")
    modules = load_components(data_dir / "modules.json")

    total_components = len(activities) + len(assessments) + len(modules)
    print(f"\n📊 Components to index: {total_components}")

    if activities:
        store.add_components(activities, "activities")

    if assessments:
        store.add_components(assessments, "assessments")

    if modules:
        store.add_components(modules, "modules")
    stats = store.get_collection_stats()
    print(f"\n✅ Vector store rebuilt with {stats['total_components']} components")

    return store


if __name__ == "__main__":
    store = main()