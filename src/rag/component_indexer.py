import json

from .vector_store import SyllabusComponentStore


def load_all_components() -> list[dict[str, list[dict]]]:
    """ "Load all syllabus components from the dataa/components directory"""

    components = {}

    component_files = {
        "modules": "data/components/modules.json",
        "activities": "data/components/activities.json",
        "assessments": "data/components/assessments.json",
    }

    for component_type, file_path in component_files.items():
        print(f"Loading {component_type} from {file_path}...")
        with open(file_path) as f:
            component_list = json.load(f)
            components[component_type] = component_list
            print(f"✅ Loaded {len(component_list)} {component_type}")

    return components


def build_component_store(
    persist_directory: str = "./chroma_db",
) -> SyllabusComponentStore:
    """Build complete vector store from all components"""
    print("Building syllabus component store...")

    store = SyllabusComponentStore(persist_directory=persist_directory)

    stats = store.get_collection_stats()
    if stats["total_components"] > 0:
        print(
            f"Component store already contains {stats['total_components']} components"
        )
        return store

    components = load_all_components()

    total_added = 0

    for component_type, component_list in components.items():
        store.add_components(component_list, component_type)
        total_added += len(component_list)

    print(f"🎉 Component store built successfully with {total_added} components!")
    return store


def test_component_store():
    """Test the component store with sample queries"""
    print("Testing component store...")

    store = build_component_store()

    test_queries = [
        ("machine learning algorithms", "modules"),
        ("group project activities", "activities"),
        ("final exam assessment", "assessments"),
        ("python programming", None),  # Search all types
    ]

    for query, component_type in test_queries:
        print(f"\n🔍 Query: '{query}' (type: {component_type or 'all'})")
        results = store.search(query, k=3, component_type=component_type)

        for i, (component, score) in enumerate(results, 1):
            print(f"\t{i}. {component.get('title', 'N/A')} (score: {score:.3f})")
            print(f"\t\tDomain: {component.get('domain', 'N/A')}")


if __name__ == "__main__":
    test_component_store()
