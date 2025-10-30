#!/usr/bin/env python3
"""
Generate Training Data with Intelligent Module Sequencing + Custom Objectives

This creates training data where T5 learns to:
1. Sequence modules logically (prerequisites, difficulty, topics)
2. Generate custom learning objectives (specific to selected modules)

Output format includes:
- Custom learning objectives mentioning module content
- Weekly schedule with module descriptions
- Logical ordering (not just [0], [1], [2], [3])
"""

import json
import random
from math import ceil
from pathlib import Path
from typing import Dict, List

# Bloom's taxonomy verbs by course level
BLOOM_VERBS = {
    "beginner": [
        "Understand",
        "Explain",
        "Implement",
        "Apply",
        "Describe",
        "Use",
        "Practice",
    ],
    "intermediate": [
        "Analyze",
        "Design",
        "Develop",
        "Compare",
        "Evaluate",
        "Optimize",
        "Debug",
    ],
    "advanced": [
        "Architect",
        "Synthesize",
        "Create",
        "Innovate",
        "Research",
        "Critique",
        "Engineer",
    ],
}

# Topic ordering (for breaking ties when prerequisites are equal)
TOPIC_ORDER = {
    "basics": 0,
    "fundamentals": 0,
    "introduction": 0,
    "python": 1,
    "programming": 1,
    "syntax": 1,
    "control": 2,
    "functions": 3,
    "data structures": 4,
    "algorithms": 5,
    "advanced": 6,
    "optimization": 6,
    "system": 7,
    "architecture": 7,
}


def difficulty_to_score(difficulty: str) -> int:
    """Convert difficulty to numeric score for sorting."""
    mapping = {"beginner": 0, "intermediate": 1, "advanced": 2}
    return mapping.get(difficulty.lower(), 1)


def get_topic_order(title: str) -> int:
    """Determine topic order based on title keywords."""
    title_lower = title.lower()
    for keyword, order in TOPIC_ORDER.items():
        if keyword in title_lower:
            return order
    return 5  # Default middle position


def has_prerequisite_relationship(mod1: Dict, mod2: Dict) -> bool:
    """
    Check if mod2 requires mod1 as prerequisite.

    Simple heuristic:
    - "Advanced X" requires "X Basics" or "Introduction to X"
    - "Intermediate X" requires "X Fundamentals"
    - Check explicit prerequisites field
    """
    # Check explicit prerequisites
    prereqs = mod2.get("prerequisites", [])
    if mod1.get("title") in prereqs or mod1.get("id") in prereqs:
        return True

    # Check title patterns
    title1_lower = mod1.get("title", "").lower()
    title2_lower = mod2.get("title", "").lower()

    # "Python Basics" should come before "Python Advanced"
    if "basics" in title1_lower or "fundamentals" in title1_lower:
        if "advanced" in title2_lower or "intermediate" in title2_lower:
            # Check if same topic
            title1_words = set(title1_lower.split())
            title2_words = set(title2_lower.split())
            common_words = title1_words & title2_words
            if len(common_words) > 1:  # Share significant words
                return True

    return False


def sequence_modules_intelligently(
    modules: List[Dict], course_level: str
) -> List[Dict]:
    """
    Order modules by:
    1. Prerequisites (basics before advanced)
    2. Difficulty progression (easier first)
    3. Topic ordering (foundational → specialized)

    Returns ordered list with week allocations.
    """
    if not modules:
        return []

    # Create copy to avoid modifying original
    modules = modules.copy()

    # Step 1: Build prerequisite awareness
    # Count how many modules each one is a prerequisite for
    prereq_counts = {mod["id"]: 0 for mod in modules}

    for i, mod1 in enumerate(modules):
        for mod2 in modules[i + 1 :]:
            if has_prerequisite_relationship(mod1, mod2):
                prereq_counts[mod1["id"]] += 1

    # Step 2: Sort by multiple criteria
    def sort_key(module):
        return (
            -prereq_counts[module["id"]],  # Prereqs first (negative = descending)
            difficulty_to_score(module.get("difficulty", "intermediate")),
            get_topic_order(module.get("title", "")),
            module.get("title", ""),  # Alphabetical as final tiebreaker
        )

    modules.sort(key=sort_key)

    # Step 3: Allocate weeks
    current_week = 1
    for module in modules:
        hours = module.get("estimated_hours", 8)
        weeks_needed = max(1, ceil(hours / 4))  # 4 hours/week
        week_end = current_week + weeks_needed - 1

        if weeks_needed == 1:
            module["week_range"] = f"Week {current_week}"
        else:
            module["week_range"] = f"Weeks {current_week}-{week_end}"

        module["weeks_allocated"] = weeks_needed
        current_week = week_end + 1

    return modules


def extract_key_technology(module: Dict) -> str:
    """Extract main technology/tool from module."""
    title = module.get("title", "")

    # Common technologies
    techs = ["Python", "Java", "C++", "JavaScript", "SQL", "TensorFlow", "PyTorch"]
    for tech in techs:
        if tech.lower() in title.lower():
            return tech

    # Check key concepts
    concepts = module.get("key_concepts", [])
    if concepts and len(concepts[0]) < 30:  # Not too long
        return concepts[0].split()[0]  # First word

    return "appropriate tools"


def generate_custom_objectives(modules: List[Dict], course_info: Dict) -> List[str]:
    """
    Generate context-specific learning objectives.

    - Uses actual module titles and concepts
    - Applies Bloom's taxonomy appropriate for level
    - Covers diverse aspects (implementation, analysis, application)
    """
    level = course_info.get("level", "beginner").lower()
    verbs = BLOOM_VERBS.get(level, BLOOM_VERBS["intermediate"])

    objectives = []

    # Generate 1 objective per module (up to 4-5)
    for i, module in enumerate(modules[:5]):
        verb = verbs[i % len(verbs)]

        # Extract content
        title = module.get("title", "programming concepts")
        concepts = module.get("key_concepts", [])
        tech = extract_key_technology(module)

        # Generate objective
        if concepts:
            # Use first key concept
            concept = concepts[0]
            if len(concept) > 50:  # Too long, use title instead
                objective = f"{verb} {title.lower()} using {tech}"
            else:
                objective = f"{verb} {concept.lower()} using {tech}"
        else:
            # Fallback to title
            objective = f"{verb} {title.lower()} effectively"

        # Ensure it's a proper sentence
        if not objective[0].isupper():
            objective = objective.capitalize()

        if not objective.endswith((".", "!", "?")):
            objective += ""

        objectives.append(objective)

    return objectives


def generate_module_description(module: Dict) -> str:
    """Generate brief description for module in schedule."""
    title = module.get("title", "Module")

    # Try to extract essence from description
    desc = module.get("description", "")
    if desc:
        # Get first sentence or first 60 chars
        first_sentence = desc.split(".")[0]
        if len(first_sentence) <= 60:
            return first_sentence
        else:
            return desc[:57] + "..."

    # Fallback: use first key concept
    concepts = module.get("key_concepts", [])
    if concepts:
        return concepts[0][:60]

    return "Core concepts and applications"


def generate_training_example(
    course_info: Dict,
    selected_modules: List[Dict],
    selected_activities: List[Dict],
    selected_assessments: List[Dict],
) -> Dict:
    """Generate single training example with sequencing."""

    # Sequence modules intelligently
    sequenced_modules = sequence_modules_intelligently(
        selected_modules, course_info.get("level", "beginner")
    )

    # Generate custom objectives
    objectives = generate_custom_objectives(sequenced_modules, course_info)

    # Build output markdown
    output_lines = []

    # Course header
    title = course_info.get("title", "Course")
    domain = course_info.get("domain", "general")
    level = course_info.get("level", "beginner")
    duration = course_info.get("duration", "semester")

    output_lines.append(f"# Course: {title}\n")
    output_lines.append(f"**Domain:** {domain}")
    output_lines.append(f"**Level:** {level}")
    output_lines.append(f"**Duration:** {duration}\n")

    # Learning objectives
    output_lines.append("## Learning Objectives")
    for obj in objectives:
        output_lines.append(f"- {obj}")
    output_lines.append("")

    # Module sequence with weeks
    output_lines.append("## Module Sequence\n")

    for i, module in enumerate(sequenced_modules):
        week_range = module.get("week_range", "Week 1")
        hours = module.get("estimated_hours", 8)
        desc = generate_module_description(module)

        output_lines.append(f"### {week_range}: {module['title']} ({hours} hours)")
        output_lines.append(f"[{i}] {desc}\n")

    # Activities (keep simple)
    output_lines.append("## Selected Activities")
    activity_indices = ", ".join([f"[{i}]" for i in range(len(selected_activities))])
    output_lines.append(activity_indices + "\n")

    # Assessments (keep simple)
    output_lines.append("## Selected Assessments")
    assessment_indices = ", ".join([f"[{i}]" for i in range(len(selected_assessments))])
    output_lines.append(assessment_indices)

    output_markdown = "\n".join(output_lines)

    # Build input prompt (same as before, but modules are ranked)
    prompt_lines = []
    prompt_lines.append(f"Generate syllabus for: {title} | {domain} | {level}\n")

    prompt_lines.append("Available modules:")
    for i, mod in enumerate(selected_modules):
        mod_title = mod.get("title", "Unknown")
        mod_hours = mod.get("estimated_hours", 8)
        mod_diff = mod.get("difficulty", "N/A")
        prompt_lines.append(f"[{i}] {mod_title} ({mod_hours}h, {mod_diff})")

    prompt_lines.append("\nAvailable activities:")
    for i, act in enumerate(selected_activities):
        act_title = act.get("title", "Unknown")
        prompt_lines.append(f"[{i}] {act_title}")

    prompt_lines.append("\nAvailable assessments:")
    for i, assess in enumerate(selected_assessments):
        assess_title = assess.get("title", "Unknown")
        prompt_lines.append(f"[{i}] {assess_title}")

    prompt_lines.append("\nSelect and sequence modules, generate objectives.")

    input_text = "\n".join(prompt_lines)

    return {"input_text": input_text, "output_markdown": output_markdown}


def load_rag_database() -> Dict:
    """Load RAG database components."""
    base_dir = Path(__file__).parent.parent
    components_dir = base_dir / "data" / "components"

    # Load modules
    with open(components_dir / "modules.json") as f:
        modules = json.load(f)

    # Normalize
    for module in modules:
        if "module_id" in module:
            module["id"] = module.pop("module_id")

    # Load activities
    with open(components_dir / "activities.json") as f:
        activities = json.load(f)

    for activity in activities:
        if "activity_id" in activity:
            activity["id"] = activity.pop("activity_id")

    # Load assessments
    with open(components_dir / "assessments.json") as f:
        assessments = json.load(f)

    for assessment in assessments:
        if "assessment_id" in assessment:
            assessment["id"] = assessment.pop("assessment_id")

    return {"modules": modules, "activities": activities, "assessments": assessments}


def generate_sequenced_training_data(num_examples: int = 1300, output_file: str = None):
    """
    Generate training data with intelligent sequencing.

    Creates varied examples with different:
    - Module orderings (based on prerequisites, difficulty)
    - Number of modules (2-5 per course)
    - Custom objectives (specific to modules)
    - Week allocations (based on hours)
    """
    print("=" * 80)
    print("GENERATING SEQUENCED TRAINING DATA")
    print("=" * 80)
    print(f"Target: {num_examples} examples\n")

    # Load RAG database
    print("Loading RAG database...")
    database = load_rag_database()
    print(f"  ✓ {len(database['modules'])} modules")
    print(f"  ✓ {len(database['activities'])} activities")
    print(f"  ✓ {len(database['assessments'])} assessments\n")

    # Course templates
    domains = ["computer_science", "mathematics", "physics"]
    levels = ["beginner", "intermediate", "advanced"]
    durations = ["semester", "quarter", "summer"]

    titles_by_domain = {
        "computer_science": [
            "Introduction to Programming",
            "Data Structures and Algorithms",
            "Machine Learning Fundamentals",
            "Web Development",
            "Database Systems",
            "Software Engineering",
            "Computer Networks",
            "Operating Systems",
        ],
        "mathematics": [
            "Calculus I",
            "Linear Algebra",
            "Probability and Statistics",
            "Discrete Mathematics",
            "Differential Equations",
            "Number Theory",
        ],
        "physics": [
            "Classical Mechanics",
            "Electromagnetism",
            "Quantum Mechanics",
            "Thermodynamics",
            "Optics",
        ],
    }

    examples = []
    random.seed(42)

    print("Generating examples...")
    for i in range(num_examples):
        # Random course
        domain = random.choice(domains)
        level = random.choice(levels)
        duration = random.choice(durations)
        title = random.choice(titles_by_domain[domain])

        # Add level to title
        level_prefix = ""
        if level == "beginner":
            level_prefix = random.choice(
                ["Introduction to", "Fundamentals of", "Basics of"]
            )
        elif level == "advanced":
            level_prefix = "Advanced"

        if level_prefix:
            title = f"{level_prefix} {title}"

        course_info = {
            "title": title,
            "domain": domain,
            "level": level,
            "duration": duration,
        }

        # Filter modules by domain + difficulty
        filtered_modules = [
            m
            for m in database["modules"]
            if m.get("domain") == domain and m.get("difficulty") == level
        ]

        if len(filtered_modules) < 2:
            # Fallback: use any modules from domain
            filtered_modules = [
                m for m in database["modules"] if m.get("domain") == domain
            ]

        if len(filtered_modules) < 2:
            continue  # Skip if not enough modules

        # Select 2-5 modules randomly
        num_modules = random.randint(2, min(5, len(filtered_modules)))
        selected_modules = random.sample(filtered_modules, num_modules)

        # Select activities and assessments
        filtered_activities = [
            a for a in database["activities"] if a.get("domain") == domain
        ]
        filtered_assessments = [
            a for a in database["assessments"] if a.get("domain") == domain
        ]

        num_activities = random.randint(2, min(4, len(filtered_activities)))
        num_assessments = random.randint(1, min(3, len(filtered_assessments)))

        selected_activities = random.sample(filtered_activities, num_activities)
        selected_assessments = random.sample(filtered_assessments, num_assessments)

        # Generate example with sequencing
        example = generate_training_example(
            course_info, selected_modules, selected_activities, selected_assessments
        )

        examples.append(example)

        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{num_examples} examples...")

    print(f"\n✓ Generated {len(examples)} examples")

    # Save
    if output_file is None:
        output_file = (
            Path(__file__).parent.parent
            / "data"
            / "training"
            / "sequenced_t5_training.json"
        )

    print(f"\nSaving to: {output_file}")
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(examples, f, indent=2)

    print(f"✓ Saved {len(examples)} examples\n")

    # Show sample
    print("=" * 80)
    print("SAMPLE EXAMPLE")
    print("=" * 80)
    print("\nInput:")
    print(examples[0]["input_text"][:500] + "...")
    print("\nOutput:")
    print(examples[0]["output_markdown"][:800] + "...")

    return examples


if __name__ == "__main__":
    generate_sequenced_training_data(num_examples=1300)
