from src.rag.rag_system import generate_rag_syllabus


def test_rag_generation():
    """Test the complete RAG system"""

    # Test course requirements
    test_requirements = {
        "title": "Introduction to Machine Learning",
        "domain": "Computer Science",
        "level": "undergraduate",
        "description": "Fundamentals of machine learning algorithms and applications",
    }

    # Generate syllabus using RAG
    result = generate_rag_syllabus(test_requirements)

    print("Generated Syllabus:")
    print("=" * 50)
    print(result["syllabus_content"])

    print("\nRetrieved Components:")
    print("=" * 50)
    for comp_type, components in result["retrieved_components"].items():
        print(f"{comp_type.title()}: {len(components)} components")


if __name__ == "__main__":
    test_rag_generation()
