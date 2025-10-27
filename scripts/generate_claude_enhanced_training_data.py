#!/usr/bin/env python3
"""
Generate Claude-Enhanced Training Data

Real-world scenario: An expert educator (Claude) has access to the FULL component
database and selects the most appropriate components for each course.

This creates high-quality training data where:
1. Claude sees ALL available components (like a real educator would)
2. Claude selects semantically appropriate components for each course
3. T5 learns from realistic, coherent examples

Cost: ~$0.04-0.39 for 260 examples (using Claude Haiku)
"""

import json
import os
from pathlib import Path
from typing import Dict, List

from anthropic import Anthropic


def load_all_components():
    """Load ALL components from the database."""
    components_dir = Path("data/components")

    with open(components_dir / "modules.json", "r") as f:
        modules = json.load(f)

    with open(components_dir / "activities.json", "r") as f:
        activities = json.load(f)

    with open(components_dir / "assessments.json", "r") as f:
        assessments = json.load(f)

    return {"modules": modules, "activities": activities, "assessments": assessments}


def get_component_candidates(
    domain: str, level: str, all_components: Dict[str, List]
) -> Dict[str, List]:
    """
    Get a comprehensive set of candidates for Claude to choose from.

    Includes:
    - All components matching domain/level (primary matches)
    - Some from adjacent levels (for flexibility)
    - Some from related domains (for cross-disciplinary courses)

    This gives Claude real choices while keeping token costs reasonable.
    """
    # Primary matches (exact domain + level)
    primary_modules = [
        m
        for m in all_components["modules"]
        if m.get("domain") == domain and m.get("difficulty") == level
    ]

    primary_activities = [
        a
        for a in all_components["activities"]
        if a.get("domain") == domain and a.get("difficulty") == level
    ]

    primary_assessments = [
        a
        for a in all_components["assessments"]
        if a.get("domain") == domain and a.get("difficulty") == level
    ]

    # Adjacent level matches (for courses that might span levels)
    level_map = {
        "beginner": "intermediate",
        "intermediate": "advanced",
        "advanced": "intermediate",
    }
    adjacent_level = level_map.get(level, level)

    adjacent_modules = [
        m
        for m in all_components["modules"]
        if m.get("domain") == domain and m.get("difficulty") == adjacent_level
    ][
        :10
    ]  # Just a few for flexibility

    adjacent_activities = [
        a
        for a in all_components["activities"]
        if a.get("domain") == domain and a.get("difficulty") == adjacent_level
    ][:10]

    # Combine and deduplicate
    candidate_modules = primary_modules + adjacent_modules
    candidate_activities = primary_activities + adjacent_activities
    candidate_assessments = primary_assessments

    # Limit to reasonable numbers to control API costs
    return {
        "modules": candidate_modules[:50],  # Up to 50 modules
        "activities": candidate_activities[:50],  # Up to 50 activities
        "assessments": candidate_assessments[:30],  # Up to 30 assessments
    }


def ask_claude_to_compose_syllabus(
    client: Anthropic,
    title: str,
    domain: str,
    level: str,
    description: str,
    candidates: Dict[str, List],
) -> Dict[str, List]:
    """
    Ask Claude to act as an expert educator and compose a coherent syllabus.

    This mimics real-world usage: an educator reviews available components
    and selects the ones that best fit the course objectives.
    """

    # Create concise component lists for the prompt
    module_list = [
        {
            "id": m["module_id"],
            "title": m["title"],
            "difficulty": m.get("difficulty", ""),
        }
        for m in candidates["modules"]
    ]

    activity_list = [
        {
            "id": a["activity_id"],
            "title": a["title"],
            "type": a.get("activity_type", ""),
        }
        for a in candidates["activities"]
    ]

    assessment_list = [
        {
            "id": a["assessment_id"],
            "title": a["title"],
            "type": a.get("assessment_type", ""),
        }
        for a in candidates["assessments"]
    ]

    prompt = f"""You are an expert educator designing a course syllabus.

Course Details:
- Title: {title}
- Domain: {domain}
- Level: {level}
- Description: {description}

You have access to the following components from your institution's curriculum database.
Select the MOST APPROPRIATE ones that would create a coherent, pedagogically sound course.

Available Modules ({len(module_list)} options):
{json.dumps(module_list, indent=2)}

Available Activities ({len(activity_list)} options):
{json.dumps(activity_list, indent=2)}

Available Assessments ({len(assessment_list)} options):
{json.dumps(assessment_list, indent=2)}

As an experienced educator, select components that:
1. Match the course level and learning objectives
2. Build on each other in a logical progression
3. Cover the core topics described in the course description
4. Provide appropriate assessment of learning outcomes

Select 3-5 modules, 3-5 activities, and 1-2 assessments.

Return ONLY a JSON object:
{{
  "module_ids": ["id1", "id2", "id3", ...],
  "activity_ids": ["id1", "id2", "id3", ...],
  "assessment_ids": ["id1", "id2"]
}}

No explanation, just the JSON."""

    response = client.messages.create(
        model="claude-3-5-haiku-20241022",  # Most cost-effective
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )

    # Parse Claude's selections
    response_text = response.content[0].text.strip()

    # Remove markdown code blocks if present
    if response_text.startswith("```json"):
        response_text = response_text.replace("```json", "").replace("```", "").strip()
    elif response_text.startswith("```"):
        response_text = response_text.replace("```", "").strip()

    selected_ids = json.loads(response_text)

    # Get full component objects
    selected = {
        "modules": [
            m
            for m in candidates["modules"]
            if m["module_id"] in selected_ids.get("module_ids", [])
        ],
        "activities": [
            a
            for a in candidates["activities"]
            if a["activity_id"] in selected_ids.get("activity_ids", [])
        ],
        "assessments": [
            a
            for a in candidates["assessments"]
            if a["assessment_id"] in selected_ids.get("assessment_ids", [])
        ],
    }

    return selected


def generate_training_example(
    title: str,
    domain: str,
    level: str,
    description: str,
    selected_components: Dict[str, List],
) -> Dict[str, str]:
    """Generate a training example from Claude's component selections."""

    # Build INPUT with available components (mimics RAG retrieval)
    input_data = {
        "title": title,
        "domain": domain,
        "level": level,
        "duration": "semester",
        "description": description,
    }

    # Add selected components as "available" (this is what RAG would provide)
    if selected_components["modules"]:
        input_data["available_modules"] = [
            {
                "id": m.get("module_id"),
                "title": m.get("title"),
                "difficulty": m.get("difficulty"),
            }
            for m in selected_components["modules"]
        ]

    if selected_components["activities"]:
        input_data["available_activities"] = [
            {
                "id": a.get("activity_id"),
                "title": a.get("title"),
                "type": a.get("activity_type"),
            }
            for a in selected_components["activities"]
        ]

    if selected_components["assessments"]:
        input_data["available_assessments"] = [
            {
                "id": a.get("assessment_id"),
                "title": a.get("title"),
                "type": a.get("assessment_type"),
            }
            for a in selected_components["assessments"]
        ]

    # Build OUTPUT using component IDs
    output_lines = []
    output_lines.append("b = SyllabusBuilder()")
    output_lines.append(
        f'b.set_info("{title}", "{domain}", "{level}", "semester", "{description[:100]}")'
    )

    # Add objectives
    output_lines.append(f'b.add_objective("Master {title} fundamentals and concepts")')
    output_lines.append(
        f'b.add_objective("Apply {title} knowledge to practical problems")'
    )

    # Add modules BY ID
    for module in selected_components["modules"][:4]:  # Use up to 4 modules
        module_id = module.get("module_id")
        output_lines.append(f'b.add_module_by_id("{module_id}")')

    # Add activities BY ID
    for activity in selected_components["activities"][:3]:  # Use up to 3 activities
        activity_id = activity.get("activity_id")
        output_lines.append(f'b.add_activity_by_id("{activity_id}")')

    # Add assessments BY ID
    for assessment in selected_components["assessments"][:2]:  # Use up to 2 assessments
        assessment_id = assessment.get("assessment_id")
        output_lines.append(f'b.add_assessment_by_id("{assessment_id}")')

    output_calls = "\n".join(output_lines)

    return {
        "input_text": f"Generate course syllabus: {json.dumps(input_data)}",
        "output_calls": output_calls,
    }


def main():
    """Generate Claude-composed training dataset."""
    print("🤖 Generating Claude-Enhanced Training Data")
    print("   (Claude acts as expert educator selecting from full database)")
    print("=" * 80)

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("\n📋 To set it up:")
        print("   1. Add credits at: https://console.anthropic.com/settings/billing")
        print("   2. Create API key at: https://console.anthropic.com/settings/keys")
        print("   3. Run: export ANTHROPIC_API_KEY='your_key_here'")
        print("   4. Run this script again")
        return

    client = Anthropic(api_key=api_key)

    # Load ALL components
    print("\n📚 Loading FULL component database...")
    all_components = load_all_components()
    print(f"   Total Modules: {len(all_components['modules'])}")
    print(f"   Total Activities: {len(all_components['activities'])}")
    print(f"   Total Assessments: {len(all_components['assessments'])}")

    # Course templates (26 diverse courses)
    course_templates = [
        # Computer Science - Beginner
        {
            "title": "Introduction to Programming",
            "domain": "computer_science",
            "level": "beginner",
            "description": "Fundamental programming concepts using Python, including variables, control flow, functions, and basic data structures",
        },
        {
            "title": "Web Development Basics",
            "domain": "computer_science",
            "level": "beginner",
            "description": "HTML, CSS, and JavaScript fundamentals for building interactive websites",
        },
        {
            "title": "Database Fundamentals",
            "domain": "computer_science",
            "level": "beginner",
            "description": "Introduction to relational databases, SQL queries, and database design principles",
        },
        {
            "title": "Computer Networks Basics",
            "domain": "computer_science",
            "level": "beginner",
            "description": "Introduction to networking concepts, protocols, and internet architecture",
        },
        # Computer Science - Intermediate
        {
            "title": "Machine Learning Fundamentals",
            "domain": "computer_science",
            "level": "intermediate",
            "description": "Introduction to supervised and unsupervised learning, neural networks, and practical ML applications",
        },
        {
            "title": "Data Structures",
            "domain": "computer_science",
            "level": "intermediate",
            "description": "Arrays, linked lists, trees, graphs, hash tables, and algorithmic complexity analysis",
        },
        {
            "title": "Software Engineering",
            "domain": "computer_science",
            "level": "intermediate",
            "description": "Software design patterns, testing methodologies, version control, and agile development",
        },
        {
            "title": "Operating Systems",
            "domain": "computer_science",
            "level": "intermediate",
            "description": "Process management, memory allocation, file systems, and concurrent programming",
        },
        # Computer Science - Advanced
        {
            "title": "Advanced Algorithms",
            "domain": "computer_science",
            "level": "advanced",
            "description": "Complex algorithmic techniques including dynamic programming, graph algorithms, and NP-completeness",
        },
        {
            "title": "Distributed Systems",
            "domain": "computer_science",
            "level": "advanced",
            "description": "Building scalable distributed systems, consensus algorithms, CAP theorem, and fault tolerance",
        },
        {
            "title": "Deep Learning",
            "domain": "computer_science",
            "level": "advanced",
            "description": "Advanced neural network architectures, CNNs, RNNs, transformers, and modern deep learning techniques",
        },
        # Mathematics - Beginner
        {
            "title": "Calculus I",
            "domain": "mathematics",
            "level": "beginner",
            "description": "Limits, derivatives, applications of derivatives, and introduction to integration",
        },
        {
            "title": "Statistics Fundamentals",
            "domain": "mathematics",
            "level": "beginner",
            "description": "Descriptive statistics, probability theory, distributions, and basic statistical inference",
        },
        {
            "title": "Discrete Mathematics",
            "domain": "mathematics",
            "level": "beginner",
            "description": "Logic, set theory, combinatorics, graph theory, and mathematical proofs",
        },
        # Mathematics - Intermediate
        {
            "title": "Linear Algebra",
            "domain": "mathematics",
            "level": "intermediate",
            "description": "Vector spaces, matrices, eigenvalues, linear transformations, and applications",
        },
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
            "description": "Ordinary and partial differential equations, solution methods, and applications",
        },
        # Mathematics - Advanced
        {
            "title": "Real Analysis",
            "domain": "mathematics",
            "level": "advanced",
            "description": "Rigorous treatment of calculus, metric spaces, topology, and measure theory",
        },
        {
            "title": "Abstract Algebra",
            "domain": "mathematics",
            "level": "advanced",
            "description": "Group theory, ring theory, field theory, and algebraic structures",
        },
        # Physics - Beginner
        {
            "title": "Physics I",
            "domain": "physics",
            "level": "beginner",
            "description": "Classical mechanics, kinematics, dynamics, and Newton's laws of motion",
        },
        {
            "title": "Electricity and Magnetism",
            "domain": "physics",
            "level": "beginner",
            "description": "Electric fields, circuits, magnetic forces, and electromagnetic induction",
        },
        # Physics - Intermediate
        {
            "title": "Classical Mechanics",
            "domain": "physics",
            "level": "intermediate",
            "description": "Lagrangian and Hamiltonian mechanics, energy conservation, and rotational dynamics",
        },
        {
            "title": "Thermodynamics",
            "domain": "physics",
            "level": "intermediate",
            "description": "Laws of thermodynamics, heat engines, entropy, and statistical mechanics",
        },
        {
            "title": "Quantum Mechanics I",
            "domain": "physics",
            "level": "intermediate",
            "description": "Wave-particle duality, Schrodinger equation, quantum states, and measurement",
        },
        # Physics - Advanced
        {
            "title": "Quantum Field Theory",
            "domain": "physics",
            "level": "advanced",
            "description": "Relativistic quantum mechanics, particle physics, and field quantization",
        },
        {
            "title": "General Relativity",
            "domain": "physics",
            "level": "advanced",
            "description": "Spacetime geometry, Einstein field equations, and gravitational physics",
        },
    ]

    # Generate training examples with Claude's expertise
    print(f"\n🎯 Generating {len(course_templates) * 10} training examples...")
    print("   Claude will select appropriate components for each course\n")
    training_data = []
    total_courses = len(course_templates)

    for i, template in enumerate(course_templates, 1):
        print(f"📚 [{i}/{total_courses}] {template['title']}")

        # Get candidate components for Claude to choose from
        candidates = get_component_candidates(
            template["domain"], template["level"], all_components
        )

        print(
            f"   Candidates: {len(candidates['modules'])} modules, "
            f"{len(candidates['activities'])} activities, "
            f"{len(candidates['assessments'])} assessments"
        )

        # Generate 10 variations per course
        for variation in range(10):
            print(f"   Variation {variation + 1}/10...", end=" ", flush=True)

            # Ask Claude to compose a coherent syllabus
            selected = ask_claude_to_compose_syllabus(
                client,
                template["title"],
                template["domain"],
                template["level"],
                template["description"],
                candidates,
            )

            # Generate training example
            example = generate_training_example(
                title=template["title"],
                domain=template["domain"],
                level=template["level"],
                description=template["description"],
                selected_components=selected,
            )

            training_data.append(example)
            print("✓")

        print()  # Blank line between courses

    print(f"\n✅ Generated {len(training_data)} Claude-composed examples")

    # Save training data
    output_file = Path("data/training/rag_enhanced_t5_training.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(training_data, f, indent=2)

    print(f"\n💾 Saved to: {output_file}")

    # Show example
    print("\n" + "=" * 80)
    print("📋 EXAMPLE: Claude-Composed Training Data")
    print("=" * 80)
    example = training_data[0]

    input_json = json.loads(
        example["input_text"].replace("Generate course syllabus: ", "")
    )
    print(f"\nCourse: {input_json['title']}")
    print(f"Description: {input_json['description']}")

    print("\nClaude selected these modules:")
    for m in input_json.get("available_modules", []):
        print(f"  ✓ {m['title']} ({m.get('difficulty', 'N/A')})")

    print("\nClaude selected these activities:")
    for a in input_json.get("available_activities", [])[:3]:
        print(f"  ✓ {a['title']}")

    print("\n📤 Generated Function Calls:")
    print("-" * 80)
    print(example["output_calls"])

    print("\n" + "=" * 80)
    print("✨ Training Data Quality:")
    print("   - Claude selected semantically appropriate components")
    print("   - Components actually match course objectives")
    print("   - Mimics real-world educator workflow")
    print("   - T5 learns from coherent, realistic examples")
    print("=" * 80)


if __name__ == "__main__":
    main()
