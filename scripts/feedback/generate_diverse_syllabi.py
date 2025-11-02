#!/usr/bin/env python3
"""
Generate 50 diverse course syllabi for feedback collection.

This script provides a systematic list of diverse course requirements
to generate through the Streamlit app, ensuring good coverage across
domains, levels, and topics.
"""

import json
from pathlib import Path

# 50 diverse course requirements
# Balanced across domains (CS, Math, Physics) and levels (beginner, intermediate, advanced)
DIVERSE_COURSES = [
    # Computer Science - Beginner (10)
    {
        "title": "Introduction to Python Programming",
        "domain": "computer_science",
        "level": "beginner",
        "description": "Learn Python fundamentals, variables, control structures, and basic data structures",
    },
    {
        "title": "Web Development Basics",
        "domain": "computer_science",
        "level": "beginner",
        "description": "HTML, CSS, JavaScript fundamentals and responsive web design principles",
    },
    {
        "title": "Introduction to Databases",
        "domain": "computer_science",
        "level": "beginner",
        "description": "Database concepts, SQL queries, normalization, and basic database design",
    },
    {
        "title": "Computer Networking Fundamentals",
        "domain": "computer_science",
        "level": "beginner",
        "description": "Network protocols, TCP/IP, routing, and basic network security",
    },
    {
        "title": "Introduction to Algorithms",
        "domain": "computer_science",
        "level": "beginner",
        "description": "Basic algorithms, sorting, searching, and algorithm analysis",
    },
    {
        "title": "Object-Oriented Programming",
        "domain": "computer_science",
        "level": "beginner",
        "description": "OOP principles, classes, inheritance, polymorphism, and encapsulation",
    },
    {
        "title": "Introduction to Data Structures",
        "domain": "computer_science",
        "level": "beginner",
        "description": "Arrays, linked lists, stacks, queues, and basic tree structures",
    },
    {
        "title": "Introduction to Linux",
        "domain": "computer_science",
        "level": "beginner",
        "description": "Linux basics, command line, shell scripting, and system administration",
    },
    {
        "title": "Introduction to Cybersecurity",
        "domain": "computer_science",
        "level": "beginner",
        "description": "Security fundamentals, threats, cryptography basics, and security best practices",
    },
    {
        "title": "Version Control with Git",
        "domain": "computer_science",
        "level": "beginner",
        "description": "Git fundamentals, branching, merging, collaboration, and GitHub workflow",
    },
    # Computer Science - Intermediate (10)
    {
        "title": "Data Structures and Algorithms",
        "domain": "computer_science",
        "level": "intermediate",
        "description": "Advanced data structures, graph algorithms, dynamic programming, and complexity analysis",
    },
    {
        "title": "Software Engineering",
        "domain": "computer_science",
        "level": "intermediate",
        "description": "Software development lifecycle, design patterns, testing, and agile methodologies",
    },
    {
        "title": "Database Systems",
        "domain": "computer_science",
        "level": "intermediate",
        "description": "Advanced SQL, query optimization, transactions, indexing, and distributed databases",
    },
    {
        "title": "Computer Architecture",
        "domain": "computer_science",
        "level": "intermediate",
        "description": "CPU design, memory hierarchy, instruction sets, pipelining, and performance optimization",
    },
    {
        "title": "Operating Systems",
        "domain": "computer_science",
        "level": "intermediate",
        "description": "Process management, memory management, file systems, and concurrent programming",
    },
    {
        "title": "Web Application Development",
        "domain": "computer_science",
        "level": "intermediate",
        "description": "Full-stack development, REST APIs, authentication, and modern web frameworks",
    },
    {
        "title": "Machine Learning Fundamentals",
        "domain": "computer_science",
        "level": "intermediate",
        "description": "Supervised learning, unsupervised learning, model evaluation, and ML algorithms",
    },
    {
        "title": "Mobile App Development",
        "domain": "computer_science",
        "level": "intermediate",
        "description": "iOS/Android development, mobile UI design, and cross-platform frameworks",
    },
    {
        "title": "Cloud Computing",
        "domain": "computer_science",
        "level": "intermediate",
        "description": "Cloud platforms, distributed systems, scalability, and cloud architecture patterns",
    },
    {
        "title": "Computer Graphics",
        "domain": "computer_science",
        "level": "intermediate",
        "description": "3D rendering, graphics pipelines, shaders, and interactive graphics programming",
    },
    # Computer Science - Advanced (7)
    {
        "title": "Advanced Machine Learning",
        "domain": "computer_science",
        "level": "advanced",
        "description": "Deep learning, neural networks, reinforcement learning, and advanced ML techniques",
    },
    {
        "title": "Natural Language Processing",
        "domain": "computer_science",
        "level": "advanced",
        "description": "NLP fundamentals, transformers, language models, and text generation",
    },
    {
        "title": "Computer Vision",
        "domain": "computer_science",
        "level": "advanced",
        "description": "Image processing, object detection, CNNs, and visual recognition systems",
    },
    {
        "title": "Distributed Systems",
        "domain": "computer_science",
        "level": "advanced",
        "description": "Distributed algorithms, consensus protocols, fault tolerance, and scalability",
    },
    {
        "title": "Compiler Design",
        "domain": "computer_science",
        "level": "advanced",
        "description": "Lexical analysis, parsing, semantic analysis, code generation, and optimization",
    },
    {
        "title": "Cryptography",
        "domain": "computer_science",
        "level": "advanced",
        "description": "Cryptographic algorithms, public-key systems, digital signatures, and security protocols",
    },
    {
        "title": "Quantum Computing",
        "domain": "computer_science",
        "level": "advanced",
        "description": "Quantum algorithms, qubits, quantum gates, and quantum programming",
    },
    # Mathematics - Beginner (5)
    {
        "title": "Introduction to Calculus",
        "domain": "mathematics",
        "level": "beginner",
        "description": "Limits, derivatives, integrals, and applications of calculus",
    },
    {
        "title": "Linear Algebra Fundamentals",
        "domain": "mathematics",
        "level": "beginner",
        "description": "Vectors, matrices, linear transformations, and systems of equations",
    },
    {
        "title": "Discrete Mathematics",
        "domain": "mathematics",
        "level": "beginner",
        "description": "Logic, sets, relations, functions, and combinatorics",
    },
    {
        "title": "Probability and Statistics",
        "domain": "mathematics",
        "level": "beginner",
        "description": "Probability theory, distributions, hypothesis testing, and descriptive statistics",
    },
    {
        "title": "Introduction to Abstract Algebra",
        "domain": "mathematics",
        "level": "beginner",
        "description": "Groups, rings, fields, and algebraic structures",
    },
    # Mathematics - Intermediate (5)
    {
        "title": "Multivariable Calculus",
        "domain": "mathematics",
        "level": "intermediate",
        "description": "Partial derivatives, multiple integrals, vector calculus, and applications",
    },
    {
        "title": "Differential Equations",
        "domain": "mathematics",
        "level": "intermediate",
        "description": "ODEs, PDEs, solution methods, and applications in science and engineering",
    },
    {
        "title": "Real Analysis",
        "domain": "mathematics",
        "level": "intermediate",
        "description": "Sequences, series, continuity, differentiation, and Riemann integration",
    },
    {
        "title": "Number Theory",
        "domain": "mathematics",
        "level": "intermediate",
        "description": "Prime numbers, modular arithmetic, cryptographic applications, and Diophantine equations",
    },
    {
        "title": "Mathematical Statistics",
        "domain": "mathematics",
        "level": "intermediate",
        "description": "Statistical inference, estimation theory, hypothesis testing, and regression analysis",
    },
    # Mathematics - Advanced (3)
    {
        "title": "Topology",
        "domain": "mathematics",
        "level": "advanced",
        "description": "Topological spaces, continuity, compactness, connectedness, and homotopy theory",
    },
    {
        "title": "Complex Analysis",
        "domain": "mathematics",
        "level": "advanced",
        "description": "Complex functions, contour integration, residue theory, and conformal mapping",
    },
    {
        "title": "Functional Analysis",
        "domain": "mathematics",
        "level": "advanced",
        "description": "Normed spaces, Banach spaces, Hilbert spaces, and operator theory",
    },
    # Physics - Beginner (3)
    {
        "title": "Introduction to Physics",
        "domain": "physics",
        "level": "beginner",
        "description": "Mechanics, forces, energy, motion, and Newton's laws",
    },
    {
        "title": "Electricity and Magnetism",
        "domain": "physics",
        "level": "beginner",
        "description": "Electric fields, magnetic fields, circuits, and electromagnetic induction",
    },
    {
        "title": "Waves and Optics",
        "domain": "physics",
        "level": "beginner",
        "description": "Wave phenomena, light, reflection, refraction, and optical instruments",
    },
    # Physics - Intermediate (4)
    {
        "title": "Classical Mechanics",
        "domain": "physics",
        "level": "intermediate",
        "description": "Lagrangian mechanics, Hamiltonian mechanics, and rigid body dynamics",
    },
    {
        "title": "Thermodynamics",
        "domain": "physics",
        "level": "intermediate",
        "description": "Laws of thermodynamics, heat engines, entropy, and statistical mechanics",
    },
    {
        "title": "Modern Physics",
        "domain": "physics",
        "level": "intermediate",
        "description": "Quantum mechanics introduction, relativity, atomic structure, and nuclear physics",
    },
    {
        "title": "Electrodynamics",
        "domain": "physics",
        "level": "intermediate",
        "description": "Maxwell's equations, electromagnetic waves, and radiation theory",
    },
    # Physics - Advanced (3)
    {
        "title": "Quantum Mechanics",
        "domain": "physics",
        "level": "advanced",
        "description": "Schrödinger equation, quantum operators, angular momentum, and perturbation theory",
    },
    {
        "title": "General Relativity",
        "domain": "physics",
        "level": "advanced",
        "description": "Einstein field equations, spacetime curvature, black holes, and cosmology",
    },
    {
        "title": "Particle Physics",
        "domain": "physics",
        "level": "advanced",
        "description": "Standard model, particle interactions, quantum field theory, and high-energy physics",
    },
]


def main():
    """Print instructions and course list for systematic generation."""
    print("=" * 80)
    print("SYSTEMATIC SYLLABUS GENERATION FOR FEEDBACK COLLECTION")
    print("=" * 80)
    print(f"\nTotal courses to generate: {len(DIVERSE_COURSES)}")
    print("\nBreakdown by domain and level:")
    print("  Computer Science: 27 (10 beginner, 10 intermediate, 7 advanced)")
    print("  Mathematics: 13 (5 beginner, 5 intermediate, 3 advanced)")
    print("  Physics: 10 (3 beginner, 4 intermediate, 3 advanced)")

    print("\n" + "=" * 80)
    print("INSTRUCTIONS:")
    print("=" * 80)
    print("1. Start the Streamlit app: streamlit run streamlit_app.py")
    print("2. For each course below, enter the details and click 'Generate Syllabus'")
    print("3. Review the generated syllabus and expert examples")
    print("4. Rate the syllabus honestly (1-10) based on:")
    print("   - Pedagogical coherence")
    print("   - Appropriate difficulty progression")
    print("   - Complete coverage of topic")
    print("   - Quality of learning objectives")
    print("5. Add optional comments about what's good/bad")
    print("6. Click 'Save & Submit Feedback'")
    print("7. Track progress: aim for 50+ ratings with varied scores")
    print("\nEstimated time: 25-30 minutes for rating")
    print("Generation time: ~1.5-2 hours total (60-90 sec per syllabus)\n")

    print("=" * 80)
    print("COURSE LIST (Copy-paste into Streamlit):")
    print("=" * 80)

    # Group by domain for easier navigation
    domains = {
        "computer_science": "Computer Science",
        "mathematics": "Mathematics",
        "physics": "Physics",
    }

    for domain_key, domain_name in domains.items():
        courses = [c for c in DIVERSE_COURSES if c["domain"] == domain_key]
        print(f"\n### {domain_name} ({len(courses)} courses)")
        print("-" * 80)

        # Group by level
        for level in ["beginner", "intermediate", "advanced"]:
            level_courses = [c for c in courses if c["level"] == level]
            if level_courses:
                print(f"\n**{level.title()}:**")
                for i, course in enumerate(level_courses, 1):
                    print(f"\n{i}. {course['title']}")
                    print(f"   Level: {course['level']}")
                    print(f"   Description: {course['description']}")

    # Save to JSON for programmatic access
    output_path = (
        Path(__file__).parent.parent.parent
        / "data"
        / "feedback"
        / "diverse_courses.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(DIVERSE_COURSES, f, indent=2)

    print("\n" + "=" * 80)
    print(f"✅ Course list saved to: {output_path}")
    print("\n💡 TIP: Generate in batches of 10-15, then rate them all together")
    print("=" * 80)


if __name__ == "__main__":
    main()
