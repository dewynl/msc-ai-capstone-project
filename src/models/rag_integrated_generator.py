#!/usr/bin/env python3
"""
RAG-Integrated Function Call Generator

This integrates the function call approach with the existing RAG pipeline
to retrieve actual component IDs and create database-ready syllabi.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add parent directories to path to import RAG components
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "rag"))

from .syllabus_builder import SyllabusBuilder

try:
    from rag.retrieval_pipeline import ComponentRetrievalPipeline
    from rag.vector_store import SyllabusComponentStore
except ImportError as e:
    print(f"⚠️  RAG components not available: {e}")
    print("This demo will show the structure with mock data")


class RAGIntegratedSyllabusBuilder(SyllabusBuilder):
    """
    Enhanced SyllabusBuilder that retrieves real components from RAG database
    and includes component IDs in the final syllabus.
    """

    def __init__(self, rag_pipeline=None):
        """Initialize with optional RAG pipeline for component retrieval."""
        super().__init__()
        self.rag_pipeline = rag_pipeline
        self.requirements = {}

    def set_requirements(self, requirements: Dict[str, Any]):
        """Set the course requirements for RAG retrieval."""
        self.requirements = requirements
        return self

    def add_module_by_query(
        self, query: str, estimated_hours: int = 8
    ) -> "RAGIntegratedSyllabusBuilder":
        """
        Add a module by retrieving similar components from RAG database.

        Args:
            query: Search query for module content
            estimated_hours: Estimated hours for the module
        """
        if self.rag_pipeline:
            # Retrieve actual modules from RAG
            retrieved = self.rag_pipeline.retrieve_components(
                self.requirements, k_per_type=3
            )
            modules = retrieved.get("modules", [])

            if modules:
                # Use the best matching module
                best_module = modules[0]
                module_data = {
                    "id": best_module.get("module_id"),  # Component ID from database
                    "title": best_module.get("title", query),
                    "description": best_module.get(
                        "description", f"Module covering {query}"
                    ),
                    "key_concepts": best_module.get("key_concepts", []),
                    "estimated_hours": estimated_hours,
                    "domain": best_module.get("domain"),
                    "difficulty": best_module.get("difficulty"),
                    "source": "rag_retrieved",
                }
            else:
                # Fallback to generated content
                module_data = {
                    "id": None,  # No database ID
                    "title": query,
                    "description": f"Module covering {query}",
                    "key_concepts": [],
                    "estimated_hours": estimated_hours,
                    "source": "generated",
                }
        else:
            # No RAG available - use generated content
            module_data = {
                "id": None,
                "title": query,
                "description": f"Module covering {query}",
                "key_concepts": [],
                "estimated_hours": estimated_hours,
                "source": "generated",
            }

        self.modules.append(module_data)
        return self

    def add_activity_by_query(
        self, query: str, bloom_level: str = "apply", estimated_hours: int = 2
    ) -> "RAGIntegratedSyllabusBuilder":
        """Add activity by retrieving from RAG database."""
        if self.rag_pipeline:
            retrieved = self.rag_pipeline.retrieve_components(
                self.requirements, k_per_type=3
            )
            activities = retrieved.get("activities", [])

            if activities:
                best_activity = activities[0]
                activity_data = {
                    "id": best_activity.get("activity_id"),
                    "title": best_activity.get("title", query),
                    "description": best_activity.get(
                        "description", f"Activity: {query}"
                    ),
                    "bloom_level": bloom_level,
                    "estimated_hours": estimated_hours,
                    "domain": best_activity.get("domain"),
                    "difficulty": best_activity.get("difficulty"),
                    "source": "rag_retrieved",
                }
            else:
                activity_data = {
                    "id": None,
                    "title": query,
                    "description": f"Activity: {query}",
                    "bloom_level": bloom_level,
                    "estimated_hours": estimated_hours,
                    "source": "generated",
                }
        else:
            activity_data = {
                "id": None,
                "title": query,
                "description": f"Activity: {query}",
                "bloom_level": bloom_level,
                "estimated_hours": estimated_hours,
                "source": "generated",
            }

        self.activities.append(activity_data)
        return self

    def add_assessment_by_query(
        self, query: str, assessment_type: str = "exam", estimated_hours: int = 2
    ) -> "RAGIntegratedSyllabusBuilder":
        """Add assessment by retrieving from RAG database."""
        if self.rag_pipeline:
            retrieved = self.rag_pipeline.retrieve_components(
                self.requirements, k_per_type=3
            )
            assessments = retrieved.get("assessments", [])

            if assessments:
                best_assessment = assessments[0]
                assessment_data = {
                    "id": best_assessment.get("assessment_id"),
                    "title": best_assessment.get("title", query),
                    "description": best_assessment.get(
                        "description", f"{assessment_type.title()}: {query}"
                    ),
                    "assessment_type": assessment_type,
                    "estimated_hours": estimated_hours,
                    "domain": best_assessment.get("domain"),
                    "difficulty": best_assessment.get("difficulty"),
                    "source": "rag_retrieved",
                }
            else:
                assessment_data = {
                    "id": None,
                    "title": query,
                    "description": f"{assessment_type.title()}: {query}",
                    "assessment_type": assessment_type,
                    "estimated_hours": estimated_hours,
                    "source": "generated",
                }
        else:
            assessment_data = {
                "id": None,
                "title": query,
                "description": f"{assessment_type.title()}: {query}",
                "assessment_type": assessment_type,
                "estimated_hours": estimated_hours,
                "source": "generated",
            }

        self.assessments.append(assessment_data)
        return self

    def build(self) -> Dict[str, Any]:
        """Build syllabus with component IDs and database references."""
        syllabus = super().build()

        # Add component source information
        component_ids = {
            "module_ids": [m.get("id") for m in self.modules if m.get("id")],
            "activity_ids": [a.get("id") for a in self.activities if a.get("id")],
            "assessment_ids": [a.get("id") for a in self.assessments if a.get("id")],
        }

        # Add database metadata
        syllabus["database_references"] = component_ids
        syllabus["metadata"]["rag_retrieved_components"] = (
            len(component_ids["module_ids"])
            + len(component_ids["activity_ids"])
            + len(component_ids["assessment_ids"])
        )
        syllabus["metadata"]["generated_components"] = (
            syllabus["metadata"]["total_modules"]
            + syllabus["metadata"]["total_activities"]
            + syllabus["metadata"]["total_assessments"]
            - syllabus["metadata"]["rag_retrieved_components"]
        )

        return syllabus


class RAGIntegratedGenerator:
    """Complete generator that combines T5 + Function Calls + RAG retrieval."""

    def __init__(self):
        """Initialize with RAG pipeline if available."""
        self.rag_pipeline = None
        try:
            # Try to initialize RAG components
            component_store = SyllabusComponentStore()
            self.rag_pipeline = ComponentRetrievalPipeline(component_store)
            print("✅ RAG pipeline initialized successfully")
        except Exception as e:
            print(f"⚠️  RAG pipeline not available: {e}")
            print("Will use generated content only")

    def generate_syllabus_with_ids(
        self, requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate syllabus with actual component IDs from database.

        Returns syllabus JSON with:
        - Complete syllabus structure
        - Component IDs for database linking
        - Mix of retrieved and generated content
        """

        # Create RAG-integrated builder
        builder = RAGIntegratedSyllabusBuilder(self.rag_pipeline)
        builder.set_requirements(requirements)

        # Set course info
        title = requirements.get("title", "Generated Course")
        domain = requirements.get("domain", "computer_science")
        level = requirements.get("level", "intermediate")
        description = requirements.get("description", f"Course on {title}")

        builder.set_info(title, domain, level, "semester", description)

        # Add learning objectives (from requirements or generated)
        objectives = requirements.get("learning_objectives", [])
        if not objectives:
            objectives = [
                f"Master {title} concepts",
                f"Apply {title} techniques",
                f"Evaluate {title} solutions",
            ]

        for obj in objectives[:4]:
            builder.add_objective(obj)

        # Add modules using RAG retrieval
        module_queries = [f"Introduction to {title}", f"Advanced {title} Topics"]

        for query in module_queries:
            builder.add_module_by_query(query, 8)

        # Add activities using RAG retrieval
        activity_level = (
            "remember"
            if level == "beginner"
            else "apply"
            if level == "intermediate"
            else "create"
        )
        activity_queries = [f"Hands-on {title} Exercise", f"{title} Workshop"]

        for query in activity_queries:
            builder.add_activity_by_query(query, activity_level, 2)

        # Add assessments using RAG retrieval
        assessment_type = (
            "quiz"
            if level == "beginner"
            else "exam"
            if level == "intermediate"
            else "project"
        )
        builder.add_assessment_by_query(
            f"Final {assessment_type.title()}", assessment_type, 2
        )

        return builder.build()


def demonstrate_with_ids():
    """Demonstrate syllabus generation with component IDs."""

    print("🔗 RAG-Integrated Syllabus Generation")
    print("=" * 60)

    generator = RAGIntegratedGenerator()

    # Test with sample requirements
    requirements = {
        "title": "Machine Learning Fundamentals",
        "domain": "computer_science",
        "level": "intermediate",
        "description": "Introduction to ML algorithms and applications",
        "learning_objectives": [
            "Understand supervised learning",
            "Implement neural networks",
            "Evaluate model performance",
        ],
    }

    print(f"📚 Generating syllabus for: {requirements['title']}")

    syllabus = generator.generate_syllabus_with_ids(requirements)

    print("\n📋 SYLLABUS WITH COMPONENT IDs:")
    print("-" * 50)
    print(json.dumps(syllabus, indent=2))
    print("-" * 50)

    # Show database references
    db_refs = syllabus.get("database_references", {})
    print("\n🔗 DATABASE REFERENCES:")
    print(f"   Module IDs: {db_refs.get('module_ids', [])}")
    print(f"   Activity IDs: {db_refs.get('activity_ids', [])}")
    print(f"   Assessment IDs: {db_refs.get('assessment_ids', [])}")

    metadata = syllabus.get("metadata", {})
    rag_count = metadata.get("rag_retrieved_components", 0)
    gen_count = metadata.get("generated_components", 0)
    print("\n📊 COMPONENT SOURCES:")
    print(f"   RAG Retrieved: {rag_count}")
    print(f"   Generated: {gen_count}")
    print(f"   Total: {rag_count + gen_count}")

    return syllabus


if __name__ == "__main__":
    demonstrate_with_ids()
