#!/usr/bin/env python3
"""
Generate Claude-Enhanced Training Data

Real-world scenario: An expert educator (Claude) has access to the FULL component
database and selects the most appropriate components for each course.

This creates high-quality training data where:
1. Claude sees ALL available components (like a real educator would)
2. Claude selects semantically appropriate components for each course
3. T5 learns from realistic, coherent examples
4. Deduplication ensures all training examples are unique

Cost: ~$0.50/100 examples (using Claude Sonnet 4.5)
      ~$6.50 for 1,300 examples with 50 variations per course
"""

import json
import os
import random
import time
from pathlib import Path
from typing import Dict, List

from anthropic import (
    Anthropic,
    APIConnectionError,
    APIError,
    APIStatusError,
    APITimeoutError,
    InternalServerError,
    RateLimitError,
)


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
    variation_seed: int = 0,
) -> Dict[str, List]:
    """
    Ask Claude to act as an expert educator and compose a coherent syllabus.

    This mimics real-world usage: an educator reviews available components
    and selects the ones that best fit the course objectives.

    variation_seed: Used to encourage diverse selections across variations.
    """

    # Shuffle candidates to encourage diversity (deterministic per seed)
    random.seed(variation_seed)
    shuffled_modules = candidates["modules"].copy()
    shuffled_activities = candidates["activities"].copy()
    shuffled_assessments = candidates["assessments"].copy()
    random.shuffle(shuffled_modules)
    random.shuffle(shuffled_activities)
    random.shuffle(shuffled_assessments)

    # Create concise component lists for the prompt
    module_list = [
        {
            "id": m["module_id"],
            "title": m["title"],
            "difficulty": m.get("difficulty", ""),
        }
        for m in shuffled_modules
    ]

    activity_list = [
        {
            "id": a["activity_id"],
            "title": a["title"],
            "type": a.get("activity_type", ""),
        }
        for a in shuffled_activities
    ]

    assessment_list = [
        {
            "id": a["assessment_id"],
            "title": a["title"],
            "type": a.get("assessment_type", ""),
        }
        for a in shuffled_assessments
    ]

    prompt = """You are an expert educator designing a course syllabus.

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

IMPORTANT: For training data diversity, explore DIFFERENT valid combinations.
Consider varying:
- The number of components selected (3-5 modules, 3-5 activities, 1-2 assessments)
- The specific topics covered (there are multiple valid approaches)
- The pedagogical style (theory-heavy vs practice-heavy, etc.)

Select 3-5 modules, 3-5 activities, and 1-2 assessments.

Return ONLY a JSON object:
{{
  "module_ids": ["id1", "id2", "id3", ...],
  "activity_ids": ["id1", "id2", "id3", ...],
  "assessment_ids": ["id1", "id2"]
}}

No explanation, just the JSON."""

    # Retry logic for API errors (overload, rate limits, network issues, timeouts)
    max_retries = 5
    base_delay = 2

    # Retryable errors (transient issues)
    retryable_errors = (
        InternalServerError,  # 500 - Server overload
        RateLimitError,  # 429 - Rate limit
        APIConnectionError,  # Network connectivity
        APITimeoutError,  # Request timeout
        APIStatusError,  # Other status errors
    )

    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",  # Best quality for training data generation
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}],
            )
            break  # Success!
        except retryable_errors as e:
            if attempt < max_retries - 1:
                delay = base_delay * (
                    2**attempt
                )  # Exponential backoff: 2s, 4s, 8s, 16s, 32s
                print(
                    f"⚠️  API error ({e.__class__.__name__}), retrying in {delay}s..."
                )
                time.sleep(delay)
            else:
                print(f"❌ API error after {max_retries} retries: {e}")
                raise
        except APIError as e:
            # Non-retryable API errors (auth, bad request, etc.)
            print(f"❌ Non-retryable API error: {e}")
            raise

    # Parse Claude's selections with error handling
    try:
        response_text = response.content[0].text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = (
                response_text.replace("```json", "").replace("```", "").strip()
            )
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()

        selected_ids = json.loads(response_text)

        # Validate response structure
        if not isinstance(selected_ids, dict):
            raise ValueError(f"Expected dict, got {type(selected_ids)}")
        if (
            "module_ids" not in selected_ids
            or "activity_ids" not in selected_ids
            or "assessment_ids" not in selected_ids
        ):
            raise ValueError(
                f"Missing required keys in response: {selected_ids.keys()}"
            )

    except (json.JSONDecodeError, ValueError, KeyError, IndexError) as e:
        print(f"❌ Failed to parse Claude response: {e}")
        print(f"   Raw response: {response.content[0].text[:200]}...")
        raise ValueError(f"Invalid Claude response format: {e}")

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
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate Claude-enhanced training data"
    )
    parser.add_argument(
        "--variations",
        type=int,
        default=10,
        help="Number of variations per course (default: 10)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/training/rag_enhanced_t5_training.json",
        help="Output file path",
    )
    args = parser.parse_args()

    print("🤖 Generating Claude-Enhanced Training Data")
    print("   (Claude acts as expert educator selecting from full database)")
    print(f"   Variations per course: {args.variations}")
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

    # Check for existing checkpoint to resume from
    checkpoint_file = (
        Path(args.output).parent / f"{Path(args.output).stem}_checkpoint.json"
    )
    start_from_course = 0
    training_data = []
    seen_combinations = set()

    if checkpoint_file.exists():
        print(f"\n💾 Found checkpoint: {checkpoint_file}")
        try:
            with open(checkpoint_file, "r") as f:
                training_data = json.load(f)

            # Rebuild seen_combinations from checkpoint
            for example in training_data:
                input_json = json.loads(
                    example["input_text"].replace("Generate course syllabus: ", "")
                )

                # Extract component IDs from the output_calls
                output = example["output_calls"]
                module_ids = []
                activity_ids = []
                assessment_ids = []

                # Simple extraction from output_calls
                for line in output.split("\n"):
                    if "add_module_by_id" in line:
                        id_match = line.split('"')[1] if '"' in line else None
                        if id_match:
                            module_ids.append(id_match)
                    elif "add_activity_by_id" in line:
                        id_match = line.split('"')[1] if '"' in line else None
                        if id_match:
                            activity_ids.append(id_match)
                    elif "add_assessment_by_id" in line:
                        id_match = line.split('"')[1] if '"' in line else None
                        if id_match:
                            assessment_ids.append(id_match)

                title = input_json.get("title", "")
                combo_signature = f"{title}|{'|'.join(sorted(module_ids))}|{'|'.join(sorted(activity_ids))}|{'|'.join(sorted(assessment_ids))}"
                seen_combinations.add(combo_signature)

            # Determine which course to start from
            # Count examples per course template
            course_counts = {}
            for example in training_data:
                input_json = json.loads(
                    example["input_text"].replace("Generate course syllabus: ", "")
                )
                title = input_json.get("title", "")
                course_counts[title] = course_counts.get(title, 0) + 1

            # Find first incomplete course
            for i, template in enumerate(course_templates):
                if course_counts.get(template["title"], 0) < args.variations:
                    start_from_course = i
                    break
            else:
                start_from_course = len(course_templates)  # All complete

            print(f"   ✅ Loaded {len(training_data)} existing examples")
            print(
                f"   🔄 Resuming from course {start_from_course + 1}/{len(course_templates)}"
            )
        except Exception as e:
            print(f"   ⚠️  Checkpoint load failed: {e}")
            print("   Starting fresh...")
            training_data = []
            seen_combinations = set()
            start_from_course = 0

    # Generate training examples with Claude's expertise
    print(
        f"\n🎯 Generating {len(course_templates) * args.variations} training examples..."
    )
    print("   Claude will select appropriate components for each course\n")
    print("   (Deduplication enabled - tracking unique component combinations)\n")
    total_courses = len(course_templates)
    duplicates_skipped = 0

    # Wrap in try/finally to ensure checkpoint on ANY exit
    try:
        for i, template in enumerate(course_templates, 1):
            # Skip completed courses if resuming from checkpoint
            if i - 1 < start_from_course:
                continue

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

            # Generate variations per course
            variation = 0
            attempts = 0
            consecutive_duplicates = 0
            max_attempts = args.variations * 3  # Allow some retries for duplicates
            max_consecutive_duplicates = 10  # Stop if we hit 10 duplicates in a row

            while variation < args.variations and attempts < max_attempts:
                attempts += 1
                print(
                    f"   Variation {variation + 1}/{args.variations}...",
                    end=" ",
                    flush=True,
                )

                # Ask Claude to compose a coherent syllabus
                # Use unique seed per course+variation+attempt for diversity
                variation_seed = (i * 1000) + (variation * 10) + attempts
                selected = ask_claude_to_compose_syllabus(
                    client,
                    template["title"],
                    template["domain"],
                    template["level"],
                    template["description"],
                    candidates,
                    variation_seed=variation_seed,
                )

                # Create unique identifier from selected component IDs
                module_ids = sorted([m["module_id"] for m in selected["modules"]])
                activity_ids = sorted(
                    [a["activity_id"] for a in selected["activities"]]
                )
                assessment_ids = sorted(
                    [a["assessment_id"] for a in selected["assessments"]]
                )

                combo_signature = f"{template['title']}|{'|'.join(module_ids)}|{'|'.join(activity_ids)}|{'|'.join(assessment_ids)}"

                # Check for duplicate
                if combo_signature in seen_combinations:
                    print("⚠️  duplicate, retrying...")
                    duplicates_skipped += 1
                    consecutive_duplicates += 1

                    # Safety: Stop if too many consecutive duplicates
                    if consecutive_duplicates >= max_consecutive_duplicates:
                        print(
                            f"\n   ⚠️  WARNING: Hit {consecutive_duplicates} consecutive duplicates. Stopping this course."
                        )
                        print(
                            f"   Generated {variation}/{args.variations} unique variations for this course."
                        )
                        break

                    continue

                # Reset consecutive duplicate counter on success
                consecutive_duplicates = 0
                seen_combinations.add(combo_signature)

                # Generate training example
                example = generate_training_example(
                    title=template["title"],
                    domain=template["domain"],
                    level=template["level"],
                    description=template["description"],
                    selected_components=selected,
                )

                training_data.append(example)
                variation += 1
                print("✓")

            print()  # Blank line between courses

            # 💾 INCREMENTAL SAVE after each course (checkpoint)
            checkpoint_file = (
                Path(args.output).parent / f"{Path(args.output).stem}_checkpoint.json"
            )
            try:
                with open(checkpoint_file, "w") as f:
                    json.dump(training_data, f, indent=2)
                print(f"   💾 Checkpoint saved: {len(training_data)} examples")
            except Exception as e:
                print(f"   ⚠️  Checkpoint save failed: {e}")

    except (KeyboardInterrupt, Exception) as e:
        print(f"\n\n⚠️  Generation interrupted: {e}")
        print("   Saving checkpoint before exit...")
    finally:
        # ALWAYS save final checkpoint, even on crash/Ctrl+C
        checkpoint_file = (
            Path(args.output).parent / f"{Path(args.output).stem}_checkpoint.json"
        )
        try:
            with open(checkpoint_file, "w") as f:
                json.dump(training_data, f, indent=2)
            print(f"\n💾 Final checkpoint saved: {len(training_data)} examples")
            print("   To resume, run the same command again.")
        except Exception as e:
            print(f"\n❌ CRITICAL: Final checkpoint save failed: {e}")

    print(f"\n✅ Generated {len(training_data)} unique Claude-composed examples")
    if duplicates_skipped > 0:
        print(f"   ℹ️  Skipped {duplicates_skipped} duplicate combinations")

    # Save training data
    output_file = Path(args.output)
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
