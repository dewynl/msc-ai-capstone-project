from typing import Any

from .component_indexer import build_component_store
from .rag_t5_generator import RAGEnhancedT5Generator
from .retrieval_pipeline import ComponentRetrievalPipeline
from .syllabus_formatter import SyllabusFormatter


def validate_domain_coverage(
    retrieved: dict[str, list], requirements: dict[str, Any]
) -> tuple[bool, str]:
    """Check if retrieved components provide sufficient domain coverage"""

    required_domain = requirements.get("domain", "").lower()
    course_title = requirements.get("title", "").lower()

    # Count domain-relevant components
    relevant_count = 0
    total_count = 0

    for component_type, components in retrieved.items():
        for component in components:
            total_count += 1
            component_domain = component.get("domain", "").lower()
            component_title = component.get("title", "").lower()

            # Check if component matches the required domain AND course topic
            domain_match = (
                required_domain in component_domain
                or component_domain in required_domain
            )
            title_words = [word for word in course_title.split() if len(word) > 3]
            topic_match = any(
                word in component_title or word in component.get("description", "")
                for word in title_words
            )

            # Component must match domain AND have relevant topic content
            if domain_match and topic_match:
                relevant_count += 1

    # Require at least 50% domain relevance and minimum 3 relevant components
    relevance_ratio = relevant_count / total_count if total_count > 0 else 0

    if relevance_ratio < 0.5 or relevant_count < 3:
        return (
            False,
            f"Insufficient domain coverage: only {relevant_count}/{total_count} components match '{required_domain}' domain",
        )

    return True, ""


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

    print("Validating domain coverage...")
    is_valid, error_msg = validate_domain_coverage(retrieved, course_requirements)

    if not is_valid:
        # Return honest "insufficient data" response
        insufficient_data_response = f"""# {course_requirements.get('title', 'Course')}

## Insufficient Domain Data Available

I apologize, but I don't have enough relevant educational components in my knowledge base to generate a quality syllabus for this course.

**Issue**: {error_msg}

**Recommendation**:
- This course would benefit from domain-specific educational content
- Consider consulting with subject matter experts
- The available components are primarily focused on other domains

**Available components found**: {sum(len(comps) for comps in retrieved.values())} total, but most don't match the '{course_requirements.get('domain', '')}' domain.

---
*This honest response prevents generating irrelevant content when domain coverage is insufficient.*
"""

        return {
            "syllabus_content": insufficient_data_response,
            "raw_t5_output": "INSUFFICIENT_DOMAIN_DATA",
            "retrieved_components": retrieved,
            "prompt": "N/A - Domain validation failed",
            "validation_error": error_msg,
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
    }
