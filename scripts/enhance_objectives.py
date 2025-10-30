#!/usr/bin/env python3
"""
Enhance generic model-generated objectives with domain-specific templates.

Uses Bloom's Taxonomy and domain knowledge to create better objectives.
"""

import re
from typing import Dict, List

# Bloom's Taxonomy verbs by level
BLOOMS_TAXONOMY = {
    "beginner": {
        "remember": [
            "define",
            "identify",
            "list",
            "name",
            "recall",
            "recognize",
            "state",
        ],
        "understand": [
            "explain",
            "describe",
            "summarize",
            "interpret",
            "classify",
            "compare",
        ],
        "apply": ["demonstrate", "implement", "use", "execute", "solve", "practice"],
    },
    "intermediate": {
        "apply": ["apply", "construct", "develop", "organize", "utilize"],
        "analyze": [
            "analyze",
            "differentiate",
            "distinguish",
            "examine",
            "investigate",
            "test",
        ],
        "evaluate": ["assess", "critique", "judge", "justify", "validate", "defend"],
    },
    "advanced": {
        "evaluate": ["evaluate", "critique", "assess", "appraise", "argue", "defend"],
        "create": [
            "design",
            "construct",
            "develop",
            "formulate",
            "devise",
            "synthesize",
        ],
    },
}

# Domain-specific objective patterns
DOMAIN_PATTERNS = {
    "computer_science": {
        "beginner": [
            "Understand fundamental {concept} principles and their applications",
            "Implement basic {concept} solutions to solve common problems",
            "Debug and test {concept} implementations systematically",
            "Apply best practices in {concept} development",
        ],
        "intermediate": [
            "Analyze {concept} trade-offs and design optimal solutions",
            "Develop efficient {concept} algorithms and data structures",
            "Evaluate {concept} performance and optimize implementations",
            "Apply {concept} patterns to real-world applications",
        ],
        "advanced": [
            "Design and architect scalable {concept} systems",
            "Evaluate advanced {concept} techniques and research literature",
            "Synthesize novel {concept} approaches to complex problems",
            "Critique {concept} methodologies and propose improvements",
        ],
    },
    "mathematics": {
        "beginner": [
            "Understand core {concept} definitions and theorems",
            "Apply {concept} techniques to solve standard problems",
            "Prove basic {concept} statements using direct methods",
            "Recognize {concept} patterns in mathematical structures",
        ],
        "intermediate": [
            "Analyze {concept} problems using multiple approaches",
            "Construct mathematical proofs involving {concept}",
            "Apply {concept} to model real-world phenomena",
            "Connect {concept} to other mathematical domains",
        ],
        "advanced": [
            "Formulate original {concept} conjectures and proofs",
            "Evaluate {concept} research and extend existing results",
            "Synthesize {concept} theory with other advanced topics",
            "Develop novel {concept} techniques and methodologies",
        ],
    },
    "science": {
        "beginner": [
            "Describe fundamental {concept} principles and mechanisms",
            "Identify key {concept} phenomena in natural systems",
            "Conduct basic {concept} experiments and observations",
            "Explain {concept} using appropriate scientific terminology",
        ],
        "intermediate": [
            "Analyze {concept} using quantitative methods",
            "Design {concept} experiments to test hypotheses",
            "Interpret {concept} data and draw evidence-based conclusions",
            "Apply {concept} principles to complex scenarios",
        ],
        "advanced": [
            "Evaluate current {concept} research and methodologies",
            "Design original {concept} research studies",
            "Synthesize {concept} findings across multiple studies",
            "Develop novel {concept} theories or models",
        ],
    },
    "business": {
        "beginner": [
            "Understand fundamental {concept} frameworks and models",
            "Identify key {concept} factors in business contexts",
            "Apply basic {concept} tools to business scenarios",
            "Explain {concept} impact on organizational performance",
        ],
        "intermediate": [
            "Analyze {concept} challenges using business frameworks",
            "Develop {concept} strategies for organizational goals",
            "Evaluate {concept} decisions using financial metrics",
            "Apply {concept} principles to case studies",
        ],
        "advanced": [
            "Design comprehensive {concept} strategies for complex organizations",
            "Evaluate {concept} approaches in dynamic markets",
            "Synthesize {concept} insights from multiple business disciplines",
            "Formulate innovative {concept} solutions to industry challenges",
        ],
    },
}

# Fallback for unknown domains
DEFAULT_PATTERNS = {
    "beginner": [
        "Understand fundamental {concept} concepts and principles",
        "Apply basic {concept} techniques to standard problems",
        "Identify key {concept} components and relationships",
        "Demonstrate proficiency in core {concept} skills",
    ],
    "intermediate": [
        "Analyze {concept} problems and develop solutions",
        "Apply {concept} knowledge to complex scenarios",
        "Evaluate {concept} approaches and outcomes",
        "Integrate {concept} with other related areas",
    ],
    "advanced": [
        "Design advanced {concept} systems and solutions",
        "Evaluate {concept} research and best practices",
        "Synthesize {concept} knowledge to create innovations",
        "Lead {concept} projects and mentor others",
    ],
}


def extract_concepts_from_modules(selected_modules: List[Dict]) -> List[str]:
    """Extract key concepts from selected module titles."""
    concepts = []

    for module in selected_modules[:5]:  # Use first 5 modules
        title = module.get("title", "")

        # Extract title-cased phrases (e.g., "Machine Learning", "Python Programming")
        words = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", title)

        # Also extract from descriptions if available
        if "key_concepts" in module:
            concepts.extend(module["key_concepts"][:3])
        elif words:
            concepts.append(" ".join(words[:3]))  # First few words

    return concepts[:4]  # Max 4 concepts


def enhance_objectives(
    generic_objectives: List[str], course_info: Dict, selected_modules: List[Dict]
) -> List[str]:
    """
    Replace generic objectives with domain-specific, Bloom's-based objectives.

    Args:
        generic_objectives: Model-generated generic objectives
        course_info: dict with domain, level, title
        selected_modules: List of selected module dicts

    Returns:
        List of enhanced objectives
    """

    domain = course_info.get("domain", "general")
    level = course_info.get("level", "beginner")
    title = course_info.get("title", "")

    # Get domain patterns
    patterns = DOMAIN_PATTERNS.get(domain, DEFAULT_PATTERNS)
    level_patterns = patterns.get(level, patterns["beginner"])

    # Extract concepts from modules
    concepts = extract_concepts_from_modules(selected_modules)

    if not concepts:
        # Fallback: extract from title
        concepts = [title.replace("Introduction to ", "").replace("Advanced ", "")]

    # Generate enhanced objectives
    enhanced = []

    for i, pattern in enumerate(level_patterns):
        if i < len(concepts):
            concept = concepts[i]
        else:
            concept = concepts[0] if concepts else title

        objective = pattern.format(concept=concept)
        enhanced.append(objective)

    return enhanced


def detect_generic_objectives(objectives: List[str]) -> bool:
    """Check if objectives are generic template-based."""

    generic_patterns = [
        r"Master .+ fundamentals and concepts",
        r"Apply .+ knowledge to practical problems",
        r"Understand .+ basics",
    ]

    for obj in objectives:
        for pattern in generic_patterns:
            if re.search(pattern, obj):
                return True

    return False


# Example usage
if __name__ == "__main__":
    # Simulate model output
    generic_objectives = [
        "Master Introduction to Programming fundamentals and concepts",
        "Apply Introduction to Programming knowledge to practical problems",
    ]

    course_info = {
        "title": "Introduction to Programming",
        "domain": "computer_science",
        "level": "beginner",
    }

    selected_modules = [
        {"title": "Python Basics", "key_concepts": ["variables", "functions", "loops"]},
        {
            "title": "Data Structures",
            "key_concepts": ["arrays", "lists", "dictionaries"],
        },
        {"title": "Algorithms", "key_concepts": ["sorting", "searching", "complexity"]},
    ]

    print("BEFORE (Generic):")
    for obj in generic_objectives:
        print(f"  - {obj}")

    print("\nAFTER (Enhanced):")
    enhanced = enhance_objectives(generic_objectives, course_info, selected_modules)
    for obj in enhanced:
        print(f"  - {obj}")

    print("\n" + "=" * 80)
    print("COMPARISON:")
    print("=" * 80)

    # Test different levels
    for level in ["beginner", "intermediate", "advanced"]:
        course_info["level"] = level
        enhanced = enhance_objectives(generic_objectives, course_info, selected_modules)

        print(f"\n{level.upper()}:")
        for obj in enhanced:
            print(f"  - {obj}")
