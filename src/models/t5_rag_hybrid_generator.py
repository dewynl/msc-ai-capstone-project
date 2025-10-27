#!/usr/bin/env python3
"""
T5 + RAG Hybrid Syllabus Generator

This is the PROPER implementation that combines:
1. T5 model for generating function calls from user requirements (ML/AI)
2. RAG for retrieving actual components from the database
3. SyllabusBuilder for programmatic construction

This is what should be deployed in the Streamlit app for the MSc AI project.
"""

import logging
from typing import Any, Dict

from .function_call_engine import FunctionCallParser, T5FunctionCallGenerator

try:
    from src.rag.component_indexer import build_component_store
    from src.rag.retrieval_pipeline import ComponentRetrievalPipeline
except ImportError as e:
    print(f"⚠️  RAG components not available: {e}")
    ComponentRetrievalPipeline = None
    build_component_store = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class T5RAGHybridGenerator:
    """
    Hybrid generator combining T5 function call generation with RAG component retrieval.

    Architecture:
    1. User Input → T5 Model generates function calls
    2. Parser extracts structured function calls
    3. For each component request, RAG retrieves actual database components
    4. SyllabusBuilder executes and constructs valid JSON syllabus

    This ensures:
    - T5 provides the ML/AI component (understanding user intent)
    - RAG provides actual educational components
    - 100% JSON validity through programmatic builder
    """

    def __init__(
        self,
        model_path: str = "./models/t5-function-call-finetuned",
        use_rag: bool = True,
    ):
        """
        Initialize hybrid generator with T5 and optional RAG.

        Args:
            model_path: Path to trained T5 model
            use_rag: Whether to use RAG for component retrieval
        """
        # Initialize T5 generator (ML component)
        logger.info("🤖 Loading T5 model for function call generation...")
        self.t5_generator = T5FunctionCallGenerator(model_path)
        self.parser = FunctionCallParser()

        # Initialize RAG pipeline (database component)
        self.rag_pipeline = None
        if use_rag and ComponentRetrievalPipeline is not None:
            try:
                logger.info("🔧 Initializing RAG vector store...")
                component_store = build_component_store()
                self.rag_pipeline = ComponentRetrievalPipeline(component_store)
                logger.info("✅ RAG pipeline initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️  RAG pipeline not available: {e}")
                logger.warning("Will use T5-generated content only")

    def generate_syllabus(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate syllabus using RAG-ENHANCED T5 approach (CORRECT ORDER).

        Process:
        1. RAG retrieves relevant components from database FIRST
        2. Feed retrieved components to T5 as CONTEXT
        3. T5 generates function calls that reference actual component IDs
        4. Execute function calls to build syllabus with real content
        5. Return valid JSON structure

        Args:
            requirements: Dictionary with title, domain, level, description, etc.

        Returns:
            Complete syllabus dictionary with metadata showing T5 vs RAG contribution
        """
        logger.info("🚀 Starting RAG→T5→Execute hybrid syllabus generation")

        try:
            # Step 1: RAG retrieves relevant components FIRST (if available)
            retrieved_components = {}
            if self.rag_pipeline:
                logger.info("🔍 RAG retrieving relevant components from database...")
                retrieved_components = self.rag_pipeline.retrieve_components(
                    requirements, k_per_type=5
                )
                logger.info(
                    f"✅ RAG found {len(retrieved_components.get('modules', []))} modules, "
                    f"{len(retrieved_components.get('activities', []))} activities, "
                    f"{len(retrieved_components.get('assessments', []))} assessments"
                )
            else:
                logger.info("⚠️  No RAG available, T5 will generate without context")

            # Step 2: Create enhanced prompt with retrieved components as context
            enhanced_requirements = requirements.copy()
            if retrieved_components:
                # Add component information to T5's context
                enhanced_requirements["available_modules"] = [
                    {
                        "id": m.get("module_id"),
                        "title": m.get("title"),
                        "difficulty": m.get("difficulty"),
                    }
                    for m in retrieved_components.get("modules", [])[:5]
                ]
                enhanced_requirements["available_activities"] = [
                    {
                        "id": a.get("activity_id"),
                        "title": a.get("title"),
                        "bloom_level": a.get("bloom_level"),
                    }
                    for a in retrieved_components.get("activities", [])[:5]
                ]
                enhanced_requirements["available_assessments"] = [
                    {
                        "id": a.get("assessment_id"),
                        "title": a.get("title"),
                        "assessment_type": a.get("assessment_type"),
                    }
                    for a in retrieved_components.get("assessments", [])[:3]
                ]

            # Step 3: Generate function calls using T5 with RAG context (ML COMPONENT)
            logger.info(
                "📝 T5 generating function calls from requirements + RAG context..."
            )
            raw_output = self.t5_generator.generate_function_calls(
                enhanced_requirements
            )
            logger.info(
                f"✅ T5 generated {len(raw_output)} characters of function calls"
            )

            # Step 2: Parse T5 output into structured function calls
            logger.info("🔍 Parsing T5 output...")
            function_calls = self.parser.parse_t5_output(raw_output)
            logger.info(f"✅ Parsed {len(function_calls)} function calls")

            # Step 3: Execute function calls with optional RAG enhancement
            from .syllabus_builder import execute_function_calls

            syllabus = execute_function_calls(function_calls)

            # Step 4: Add generation metadata
            if "metadata" not in syllabus:
                syllabus["metadata"] = {}

            syllabus["metadata"]["generation_method"] = "rag_enhanced_t5"
            syllabus["metadata"]["t5_generated"] = True
            syllabus["metadata"]["function_calls_count"] = len(function_calls)

            # RAG statistics (what was available for T5 to reference)
            if retrieved_components:
                syllabus["metadata"]["rag_components_retrieved"] = (
                    len(retrieved_components.get("modules", []))
                    + len(retrieved_components.get("activities", []))
                    + len(retrieved_components.get("assessments", []))
                )
                syllabus["metadata"]["rag_modules_available"] = len(
                    retrieved_components.get("modules", [])
                )
                syllabus["metadata"]["rag_activities_available"] = len(
                    retrieved_components.get("activities", [])
                )
                syllabus["metadata"]["rag_assessments_available"] = len(
                    retrieved_components.get("assessments", [])
                )
            else:
                syllabus["metadata"]["rag_components_retrieved"] = 0

            logger.info("✅ RAG→T5→Execute hybrid generation successful!")
            return syllabus

        except Exception as e:
            logger.error(f"❌ T5+RAG generation failed: {e}")
            logger.info("🔄 Falling back to basic generation...")

            # Fallback: Create basic syllabus structure
            from .syllabus_builder import SyllabusBuilder

            builder = SyllabusBuilder()
            title = requirements.get("title", "Generated Course")
            domain = requirements.get("domain", "computer_science")
            level = requirements.get("level", "intermediate")
            description = requirements.get("description", f"Course on {title}")

            builder.set_info(title, domain, level, "semester", description)
            builder.add_objective(f"Understand {title} concepts")
            builder.add_objective(f"Apply {title} techniques")

            syllabus = builder.build()
            syllabus["metadata"]["generation_method"] = "fallback"
            syllabus["metadata"]["t5_generated"] = False
            syllabus["metadata"]["error"] = str(e)

            return syllabus


def demonstrate_hybrid_generation():
    """Demonstrate the T5+RAG hybrid generator."""
    print("🎓 T5+RAG Hybrid Syllabus Generator Demo")
    print("=" * 60)

    generator = T5RAGHybridGenerator()

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

    print(f"\n📚 Generating syllabus for: {requirements['title']}")
    print(f"   Domain: {requirements['domain']}, Level: {requirements['level']}")

    syllabus = generator.generate_syllabus(requirements)

    print("\n✅ GENERATED SYLLABUS:")
    print("-" * 60)
    print(f"Title: {syllabus.get('course_info', {}).get('title', 'N/A')}")
    print(f"Modules: {len(syllabus.get('modules', []))}")
    print(f"Activities: {len(syllabus.get('activities', []))}")
    print(f"Assessments: {len(syllabus.get('assessments', []))}")
    print(
        f"Generation Method: {syllabus.get('metadata', {}).get('generation_method', 'N/A')}"
    )
    print(f"T5 Generated: {syllabus.get('metadata', {}).get('t5_generated', False)}")
    print("-" * 60)

    return syllabus


if __name__ == "__main__":
    demonstrate_hybrid_generation()
