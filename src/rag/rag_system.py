from typing import Any

from .component_indexer import build_component_store
from .rag_t5_generator import RAGEnhancedT5Generator
from .retrieval_pipeline import ComponentRetrievalPipeline
from .syllabus_formatter import SyllabusFormatter


def generate_rag_syllabus(
    course_requirements: dict[str, Any], persist_directory: str = "./chroma_db"
) -> dict[str, Any]:
    """Generate syllabus using complete RAG pipeline"""

    print("Loading component store...")
    component_store = build_component_store(persist_directory)

    print("Setting up retrieval pipeline...")
    retrieval_pipeline = ComponentRetrievalPipeline(component_store)

    print("Loading T5 generator...")
    generator = RAGEnhancedT5Generator()

    print("Retrieving relevant components...")
    retrieved = retrieval_pipeline.retrieve_components(course_requirements)

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
    }
