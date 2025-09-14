from typing import Any

from .component_indexer import build_component_store
from .domain_validator import (
    DomainValidator,
    create_enhanced_insufficient_data_response,
)
from .rag_t5_generator import RAGEnhancedT5Generator
from .retrieval_pipeline import ComponentRetrievalPipeline
from .syllabus_formatter import SyllabusFormatter


def generate_rag_syllabus(
    course_requirements: dict[str, Any], persist_directory: str = "./chroma_db"
) -> dict[str, Any]:
    """Generate syllabus using complete RAG pipeline with enhanced domain validation"""

    print("Loading component store...")
    component_store = build_component_store(persist_directory)

    print("Setting up retrieval pipeline...")
    retrieval_pipeline = ComponentRetrievalPipeline(component_store)

    print("Loading T5 generator...")
    generator = RAGEnhancedT5Generator()

    print("Retrieving relevant components...")
    retrieved = retrieval_pipeline.retrieve_components(course_requirements)

    print("Validating domain coverage with enhanced validation...")
    validator = DomainValidator()
    is_valid, error_msg, confidence_score = validator.validate_domain_coverage(
        retrieved, course_requirements
    )

    if not is_valid:
        # Return enhanced "insufficient data" response with suggestions
        insufficient_data_response = create_enhanced_insufficient_data_response(
            course_requirements, error_msg, confidence_score, retrieved, validator
        )

        return {
            "syllabus_content": insufficient_data_response,
            "raw_t5_output": "INSUFFICIENT_DOMAIN_DATA",
            "retrieved_components": retrieved,
            "prompt": "N/A - Domain validation failed",
            "validation_error": error_msg,
            "confidence_score": confidence_score,
        }

    print("Creating prompt with retrieved components...")
    prompt = generator.create_prompt(course_requirements, retrieved)

    print("Generating syllabus with T5...")
    t5_output = generator.generate_syllabus(prompt)

    print("Formatting into structured syllabus...")
    formatter = SyllabusFormatter()
    structured_syllabus = formatter.format_syllabus(
        course_requirements, t5_output, retrieved
    )

    return {
        "syllabus_content": structured_syllabus,
        "raw_t5_output": t5_output,
        "retrieved_components": retrieved,
        "prompt": prompt,
        "confidence_score": confidence_score,
        "domain_validation": "passed",
    }
