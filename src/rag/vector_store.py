import json
import uuid
from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer


class SyllabusComponentStore:
    """Storage and retrieval system for syllabus components using ChromaDB"""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        persist_directory: str = "./chroma_db",
    ):
        self.encoder = SentenceTransformer(model_name)
        self.client = chromadb.PersistentClient(path=persist_directory)

        self.collection = self.client.get_or_create_collection(
            name="syllabus_components",
            metadata={"description": "Syllabus modules, activities, and assessments"},
        )

    def encode_component(self, component: dict[str, Any]) -> str:
        """Convert syllabus component to searchable text"""

        text_parts = [
            component.get("title", ""),
            component.get("description", ""),
            component.get("domain", ""),  # Updated for simplified schema
            " ".join(component.get("learning_objectives", [])),
        ]

        # Add component-specific fields for better encoding
        if "bloom_level" in component:
            text_parts.append(component.get("bloom_level", ""))
        if "assessment_type" in component:
            text_parts.append(component.get("assessment_type", ""))
        if "key_concepts" in component:
            text_parts.extend(component.get("key_concepts", []))

        return " ".join(filter(None, text_parts))

    def add_components(self, components: list[dict[str, Any]], component_type: str):
        """Add syllabus components to ChromaDB collection"""
        print(f"Adding {len(components)} {component_type} to vector store...")

        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []

        for component in components:
            # Create searchable text
            doc_text = self.encode_component(component)
            documents.append(doc_text)

            # Add metadata (ChromaDB will store this alongside vectors)
            metadata = {
                "component_type": component_type,
                "title": component.get("title", ""),
                "domain": component.get("domain", ""),  # Updated for simplified schema
                "difficulty": component.get("difficulty", ""),
                "estimated_hours": str(component.get("estimated_hours", 0)),
                "original_data": json.dumps(component),  # Store full component data
            }
            metadatas.append(metadata)

            # Use existing ID or generate new one
            component_id = component.get(f"{component_type[:-1]}_id", str(uuid.uuid4()))
            ids.append(f"{component_type}_{component_id}")

        # Add to ChromaDB (it handles embedding generation automatically)
        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

        print(f"✅ Added {len(components)} {component_type} successfully")

    def search(
        self, query: str, k: int = 5, component_type: str = None
    ) -> list[tuple[dict[str, Any], float]]:
        """Search for syllabus components based on a query"""

        where_filters = {}

        if component_type:
            where_filters = {"component_type": component_type}

        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            where=where_filters if where_filters else None,
        )

        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for _, metadata, distance in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
                strict=False,
            ):
                original_data = json.loads(metadata["original_data"])
                similarity_score = 1 - distance
                formatted_results.append((original_data, similarity_score))

        return formatted_results

    def get_collection_stats(self) -> dict[str, Any]:
        """Get statistics about the stored components"""
        count = self.collection.count()
        return {"total_components": count}
