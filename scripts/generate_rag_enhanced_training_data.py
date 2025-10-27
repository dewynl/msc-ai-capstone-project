#!/usr/bin/env python3
"""
Generate RAG-Enhanced T5 Training Data

This creates training examples where:
1. INPUT includes available components from RAG retrieval
2. OUTPUT uses add_module_by_id(), add_activity_by_id() to reference actual IDs

This trains T5 to actually USE the RAG context instead of generating blindly.
"""

import json
from pathlib import Path
from typing import Dict, List


# Load component database
def load_components():
    """Load all components from JSON files."""
    components_dir = Path("data/components")

    with open(components_dir / "modules.json", "r") as f:
        modules = json.load(f)

    with open(components_dir / "activities.json", "r") as f:
        activities = json.load(f)

    with open(components_dir / "assessments.json", "r") as f:
        assessments = json.load(f)

    return {"modules": modules, "activities": activities, "assessments": assessments}


def retrieve_relevant_components(
    title: str, domain: str, level: str, components: Dict[str, List]
) -> Dict[str, List]:
    """
    Simulate RAG retrieval: filter components by domain and level.

    In real RAG, this would use semantic similarity.
    For training data, we'll filter by matching domain/level.
    """
    # Filter modules
    relevant_modules = [
        m
        for m in components["modules"]
        if m.get("domain") == domain and m.get("difficulty") == level
    ][
        :5
    ]  # Top 5

    # Filter activities
    relevant_activities = [
        a
        for a in components["activities"]
        if a.get("domain") == domain and a.get("difficulty") == level
    ][:5]

    # Filter assessments
    relevant_assessments = [
        a
        for a in components["assessments"]
        if a.get("domain") == domain and a.get("difficulty") == level
    ][:3]

    return {
        "modules": relevant_modules,
        "activities": relevant_activities,
        "assessments": relevant_assessments,
    }


def generate_training_example(
    title: str, domain: str, level: str, description: str, components: Dict[str, List]
) -> Dict[str, str]:
    """Generate a single RAG-enhanced training example."""

    # Step 1: Retrieve relevant components (simulates RAG)
    retrieved = retrieve_relevant_components(title, domain, level, components)

    # Step 2: Build INPUT with available components
    input_data = {
        "title": title,
        "domain": domain,
        "level": level,
        "duration": "semester",
        "description": description,
    }

    # Add available components to INPUT (this is the RAG context!)
    if retrieved["modules"]:
        input_data["available_modules"] = [
            {
                "id": m.get("module_id"),
                "title": m.get("title"),
                "difficulty": m.get("difficulty"),
            }
            for m in retrieved["modules"]
        ]

    if retrieved["activities"]:
        input_data["available_activities"] = [
            {
                "id": a.get("activity_id"),
                "title": a.get("title"),
                "bloom_level": a.get("bloom_level"),
            }
            for a in retrieved["activities"]
        ]

    if retrieved["assessments"]:
        input_data["available_assessments"] = [
            {
                "id": a.get("assessment_id"),
                "title": a.get("title"),
                "assessment_type": a.get("assessment_type"),
            }
            for a in retrieved["assessments"]
        ]

    # Step 3: Build OUTPUT using component IDs
    output_lines = []
    output_lines.append("b = SyllabusBuilder()")
    output_lines.append(
        f'b.set_info("{title}", "{domain}", "{level}", "semester", "{description[:50]}")'
    )

    # Add objectives (generic for now)
    output_lines.append(f'b.add_objective("Understand {title} fundamentals")')
    output_lines.append(f'b.add_objective("Apply {title} techniques")')

    # Add modules BY ID (this is the key change!)
    for module in retrieved["modules"][:2]:
        module_id = module.get("module_id")
        output_lines.append(f'b.add_module_by_id("{module_id}")')

    # Add activities BY ID
    for activity in retrieved["activities"][:2]:
        activity_id = activity.get("activity_id")
        output_lines.append(f'b.add_activity_by_id("{activity_id}")')

    # Add assessments BY ID
    for assessment in retrieved["assessments"][:1]:
        assessment_id = assessment.get("assessment_id")
        output_lines.append(f'b.add_assessment_by_id("{assessment_id}")')

    output_calls = "\n".join(output_lines)

    return {
        "input_text": f"Generate course syllabus: {json.dumps(input_data)}",
        "output_calls": output_calls,
    }


def main():
    """Generate RAG-enhanced training dataset."""
    print("🔧 Generating RAG-Enhanced T5 Training Data")
    print("=" * 80)

    # Load all components
    print("\n📚 Loading component database...")
    components = load_components()
    print(f"   Modules: {len(components['modules'])}")
    print(f"   Activities: {len(components['activities'])}")
    print(f"   Assessments: {len(components['assessments'])}")

    # Define comprehensive course templates across all domains/levels
    course_templates = [
        # Computer Science - Beginner
        {
            "title": "Introduction to Programming",
            "domain": "computer_science",
            "level": "beginner",
            "description": "Fundamental programming concepts and practical coding skills",
        },
        {
            "title": "Web Development Basics",
            "domain": "computer_science",
            "level": "beginner",
            "description": "HTML, CSS, and JavaScript fundamentals",
        },
        {
            "title": "Database Fundamentals",
            "domain": "computer_science",
            "level": "beginner",
            "description": "Introduction to databases and SQL",
        },
        {
            "title": "Computer Networks Basics",
            "domain": "computer_science",
            "level": "beginner",
            "description": "Introduction to networking and protocols",
        },
        # Computer Science - Intermediate
        {
            "title": "Machine Learning Fundamentals",
            "domain": "computer_science",
            "level": "intermediate",
            "description": "Introduction to ML algorithms, neural networks, and applications",
        },
        {
            "title": "Data Structures",
            "domain": "computer_science",
            "level": "intermediate",
            "description": "Arrays, trees, graphs, and algorithmic complexity",
        },
        {
            "title": "Software Engineering",
            "domain": "computer_science",
            "level": "intermediate",
            "description": "Design patterns, testing, and development methodologies",
        },
        {
            "title": "Operating Systems",
            "domain": "computer_science",
            "level": "intermediate",
            "description": "Process management, memory, and file systems",
        },
        # Computer Science - Advanced
        {
            "title": "Advanced Algorithms",
            "domain": "computer_science",
            "level": "advanced",
            "description": "Complex algorithmic techniques and optimization strategies",
        },
        {
            "title": "Distributed Systems",
            "domain": "computer_science",
            "level": "advanced",
            "description": "Scalable systems, consensus algorithms, and fault tolerance",
        },
        {
            "title": "Deep Learning",
            "domain": "computer_science",
            "level": "advanced",
            "description": "Neural network architectures and advanced ML techniques",
        },
        # Mathematics - Beginner
        {
            "title": "Calculus I",
            "domain": "mathematics",
            "level": "beginner",
            "description": "Limits, derivatives, and basic integration",
        },
        {
            "title": "Statistics Fundamentals",
            "domain": "mathematics",
            "level": "beginner",
            "description": "Probability, distributions, and statistical inference",
        },
        {
            "title": "Discrete Mathematics",
            "domain": "mathematics",
            "level": "beginner",
            "description": "Logic, sets, combinatorics, and graph theory",
        },
        # Mathematics - Intermediate
        {
            "title": "Linear Algebra",
            "domain": "mathematics",
            "level": "intermediate",
            "description": "Vector spaces, matrices, eigenvalues and transformations",
        },
        {
            "title": "Multivariable Calculus",
            "domain": "mathematics",
            "level": "intermediate",
            "description": "Partial derivatives, multiple integrals, and vector calculus",
        },
        {
            "title": "Differential Equations",
            "domain": "mathematics",
            "level": "intermediate",
            "description": "ODEs, PDEs, and solution methods",
        },
        # Mathematics - Advanced
        {
            "title": "Real Analysis",
            "domain": "mathematics",
            "level": "advanced",
            "description": "Rigorous calculus, topology, and measure theory",
        },
        {
            "title": "Abstract Algebra",
            "domain": "mathematics",
            "level": "advanced",
            "description": "Groups, rings, fields, and algebraic structures",
        },
        # Physics - Beginner
        {
            "title": "Physics I",
            "domain": "physics",
            "level": "beginner",
            "description": "Mechanics, kinematics, and Newton's laws",
        },
        {
            "title": "Electricity and Magnetism",
            "domain": "physics",
            "level": "beginner",
            "description": "Electric fields, circuits, and magnetic forces",
        },
        # Physics - Intermediate
        {
            "title": "Classical Mechanics",
            "domain": "physics",
            "level": "intermediate",
            "description": "Newton's laws, energy, momentum and rotational dynamics",
        },
        {
            "title": "Thermodynamics",
            "domain": "physics",
            "level": "intermediate",
            "description": "Heat, entropy, and statistical mechanics",
        },
        {
            "title": "Quantum Mechanics I",
            "domain": "physics",
            "level": "intermediate",
            "description": "Wave functions, Schrodinger equation, and quantum states",
        },
        # Physics - Advanced
        {
            "title": "Quantum Field Theory",
            "domain": "physics",
            "level": "advanced",
            "description": "Relativistic quantum mechanics and particle physics",
        },
        {
            "title": "General Relativity",
            "domain": "physics",
            "level": "advanced",
            "description": "Spacetime curvature and gravitational physics",
        },
    ]

    # Generate training examples
    print(f"\n🎯 Generating training examples from {len(course_templates)} templates...")
    training_data = []

    for template in course_templates:
        # Generate multiple variations (10 per template for better coverage)
        for i in range(10):  # 10 variations per template = 260 total examples
            example = generate_training_example(
                title=template["title"],
                domain=template["domain"],
                level=template["level"],
                description=template["description"],
                components=components,
            )
            training_data.append(example)

    print(f"   Generated {len(training_data)} training examples")

    # Save training data
    output_file = Path("data/training/rag_enhanced_t5_training.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(training_data, f, indent=2)

    print(f"\n✅ Saved to: {output_file}")

    # Show example
    print("\n" + "=" * 80)
    print("📋 EXAMPLE TRAINING DATA:")
    print("=" * 80)
    example = training_data[0]

    print("\n📥 INPUT (with RAG context):")
    print("-" * 80)
    input_json = json.loads(
        example["input_text"].replace("Generate course syllabus: ", "")
    )
    print(json.dumps(input_json, indent=2)[:500] + "...")

    print("\n📤 OUTPUT (using component IDs):")
    print("-" * 80)
    print(example["output_calls"][:400] + "...")

    print("\n" + "=" * 80)
    print("💡 KEY DIFFERENCE:")
    print("   OLD: b.add_module('Introduction to ML', 8)")
    print("   NEW: b.add_module_by_id('abc123-def456-...')")
    print("\n   T5 now references ACTUAL database components!")
    print("=" * 80)


if __name__ == "__main__":
    main()
