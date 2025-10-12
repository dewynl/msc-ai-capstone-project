#!/usr/bin/env python3
"""
Custom Input JSON Demo with Component IDs
Modify the requirements below and run to get JSON output with component IDs!
"""

import json
import sys
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent))

from src.models.rag_integrated_generator import RAGIntegratedGenerator


def main():
    # 🔧 MODIFY THESE INPUTS TO TEST DIFFERENT COURSES:
    requirements = {
        "title": "Deep Learning with PyTorch",
        "domain": "computer_science",
        "level": "advanced",
        "description": "Advanced neural networks and deep learning with PyTorch framework",
    }

    print("🚀 Loading RAG-Integrated Generator...")
    generator = RAGIntegratedGenerator()

    print(f"📚 Generating syllabus with component IDs for: {requirements['title']}")
    syllabus = generator.generate_syllabus_with_ids(requirements)

    print("\n" + "=" * 60)
    print("📄 FINAL JSON OUTPUT:")
    print("=" * 60)
    print(json.dumps(syllabus, indent=2))
    print("=" * 60)

    # Save to file
    safe_title = requirements["title"].replace(" ", "_").lower()
    filename = f"syllabus_{safe_title}.json"
    with open(filename, "w") as f:
        json.dump(syllabus, f, indent=2)

    print(f"\n✅ Saved to: {filename}")
    print(
        f"📊 Generated: {len(syllabus.get('modules', []))} modules, {len(syllabus.get('activities', []))} activities, {len(syllabus.get('assessments', []))} assessments"
    )

    # Show component IDs
    db_refs = syllabus.get("database_references", {})
    print("\n🔗 COMPONENT IDs:")
    print(f"   Module IDs: {db_refs.get('module_ids', [])}")
    print(f"   Activity IDs: {db_refs.get('activity_ids', [])}")
    print(f"   Assessment IDs: {db_refs.get('assessment_ids', [])}")

    metadata = syllabus.get("metadata", {})
    rag_count = metadata.get("rag_retrieved_components", 0)
    gen_count = metadata.get("generated_components", 0)
    print("\n📊 COMPONENT SOURCES:")
    print(f"   RAG Retrieved (with IDs): {rag_count}")
    print(f"   Generated (no IDs): {gen_count}")


if __name__ == "__main__":
    main()
