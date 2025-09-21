#!/usr/bin/env python3
"""
Create T5 training data for multi-domain system (CS, Math, Physics)
Generate syllabi from cleaned components with simplified schema
"""

import json
import random
import sys
from pathlib import Path
from typing import Dict, List, Any

sys.path.append(str(Path(__file__).parent.parent / "src"))

from rag.vector_store import SyllabusComponentStore
from rag.retrieval_pipeline import ComponentRetrievalPipeline

random.seed(42)


class CleanTrainingDataGenerator:
    def __init__(self):
        self.store = SyllabusComponentStore(persist_directory="./chroma_db")
        self.retrieval_pipeline = ComponentRetrievalPipeline(self.store)

        self.domains = ["computer_science", "mathematics", "physics"]
        self.levels = ["beginner", "intermediate", "advanced"]

        # Course templates for each domain
        self.course_templates = {
            "computer_science": [
                "Introduction to Programming",
                "Data Structures and Algorithms",
                "Machine Learning Fundamentals",
                "Software Engineering Principles",
                "Database Systems",
                "Computer Networks",
                "Operating Systems",
                "Web Development",
                "Artificial Intelligence",
                "Cybersecurity Basics"
            ],
            "mathematics": [
                "Calculus and Analysis",
                "Linear Algebra",
                "Statistics and Probability",
                "Discrete Mathematics",
                "Mathematical Modeling",
                "Numerical Methods",
                "Real Analysis",
                "Abstract Algebra",
                "Differential Equations",
                "Mathematical Logic"
            ],
            "physics": [
                "Classical Mechanics",
                "Electromagnetism",
                "Thermodynamics",
                "Quantum Physics Introduction",
                "Waves and Optics",
                "Modern Physics",
                "Mechanics and Dynamics",
                "Physics Laboratory Methods",
                "Computational Physics",
                "Statistical Mechanics"
            ]
        }

    def generate_course_requirements(self, domain: str, level: str, title: str) -> Dict[str, Any]:
        """Generate course requirements for training"""
        descriptions = {
            "computer_science": {
                "beginner": f"Introduction to {title.lower()} covering fundamental concepts and practical applications.",
                "intermediate": f"Comprehensive study of {title.lower()} with hands-on projects and problem-solving.",
                "advanced": f"Advanced topics in {title.lower()} with research components and complex applications."
            },
            "mathematics": {
                "beginner": f"Foundation course in {title.lower()} emphasizing core concepts and computational skills.",
                "intermediate": f"Rigorous treatment of {title.lower()} with proofs and theoretical applications.",
                "advanced": f"Graduate-level {title.lower()} with research topics and advanced theory."
            },
            "physics": {
                "beginner": f"Introductory {title.lower()} covering fundamental principles and experimental methods.",
                "intermediate": f"Comprehensive {title.lower()} with mathematical formalism and laboratory work.",
                "advanced": f"Advanced {title.lower()} with modern research topics and theoretical frameworks."
            }
        }

        return {
            "title": title,
            "domain": domain,
            "level": level,
            "duration": "semester",
            "description": descriptions[domain][level],
            "learning_objectives": [],
            "prerequisites": "",
            "target_audience": f"{level.title()} students in {domain.replace('_', ' ').title()}"
        }

    def retrieve_and_assemble_components(self, requirements: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Retrieve components for a course using the pipeline"""
        # Get diverse components across domains if applicable
        components = self.retrieval_pipeline.get_diverse_components(
            requirements,
            target_counts={"modules": 3, "activities": 4, "assessments": 2}
        )

        # Ensure we have some components
        for comp_type in ["modules", "activities", "assessments"]:
            if len(components.get(comp_type, [])) == 0:
                # Fallback: retrieve any components of this type
                fallback = self.store.search(f"{comp_type} {requirements['domain']}", k=2, component_type=comp_type)
                components[comp_type] = [result[0] for result in fallback]

        return components

    def create_training_example(self, domain: str, level: str, title: str) -> Dict[str, str]:
        """Create a single training example"""
        # Generate course requirements
        requirements = self.generate_course_requirements(domain, level, title)

        # Retrieve components
        components = self.retrieve_and_assemble_components(requirements)

        # Extract learning objectives from modules
        learning_objectives = []
        for module in components.get("modules", [])[:2]:
            objectives = module.get("learning_objectives", [])
            learning_objectives.extend(objectives[:2])  # Take 2 from each module

        requirements["learning_objectives"] = learning_objectives[:4]  # Max 4 total

        # Create simplified syllabus output
        syllabus = {
            "course_info": {
                "title": requirements["title"],
                "domain": requirements["domain"],
                "level": requirements["level"],
                "duration": requirements["duration"],
                "description": requirements["description"]
            },
            "learning_objectives": requirements["learning_objectives"],
            "modules": [
                {
                    "title": module.get("title", ""),
                    "description": module.get("description", "")[:200] + "...",  # Truncate for training
                    "key_concepts": module.get("key_concepts", [])[:3],
                    "estimated_hours": module.get("estimated_hours", 4)
                }
                for module in components.get("modules", [])[:3]
            ],
            "activities": [
                {
                    "title": activity.get("title", ""),
                    "description": activity.get("description", "")[:150] + "...",
                    "bloom_level": activity.get("bloom_level", ""),
                    "estimated_hours": activity.get("estimated_hours", 1)
                }
                for activity in components.get("activities", [])[:4]
            ],
            "assessments": [
                {
                    "title": assessment.get("title", ""),
                    "assessment_type": assessment.get("assessment_type", "exam"),
                    "estimated_hours": assessment.get("estimated_hours", 2)
                }
                for assessment in components.get("assessments", [])[:2]
            ]
        }

        # Convert to JSON strings for T5 training format
        input_json = json.dumps(requirements, separators=(",", ":"))
        output_json = json.dumps(syllabus, separators=(",", ":"))

        return {
            "input_json": input_json,
            "output_json": output_json
        }

    def generate_training_dataset(self, examples_per_domain: int = 30) -> List[Dict[str, str]]:
        """Generate complete training dataset"""
        training_examples = []

        print("🏗️ Generating multi-domain training dataset...")

        for domain in self.domains:
            print(f"\n📚 Generating {examples_per_domain} examples for {domain}")

            domain_templates = self.course_templates[domain]

            for i in range(examples_per_domain):
                # Cycle through levels and titles
                level = self.levels[i % len(self.levels)]
                title = domain_templates[i % len(domain_templates)]

                try:
                    example = self.create_training_example(domain, level, title)
                    training_examples.append(example)

                    if (i + 1) % 10 == 0:
                        print(f"  Generated {i + 1}/{examples_per_domain} examples")

                except Exception as e:
                    print(f"  ⚠️ Failed to generate example {i+1}: {e}")
                    continue

        print(f"\n✅ Generated {len(training_examples)} total training examples")
        return training_examples


def main():
    """Generate multi-domain training data"""
    print("🚀 Creating Clean Multi-Domain T5 Training Data")
    print("=" * 40)

    generator = CleanTrainingDataGenerator()

    # Generate training examples (30 per domain = 90 total)
    training_data = generator.generate_training_dataset(examples_per_domain=30)

    # Save training data
    output_file = Path("data/training/t5_clean_training.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(training_data, f, indent=2)

    print(f"\n💾 Saved training data to: {output_file}")
    print(f"📊 Dataset statistics:")
    print(f"  Total examples: {len(training_data)}")

    # Count by domain
    domains_count = {}
    for example in training_data:
        try:
            requirements = json.loads(example["input_json"])
            domain = requirements.get("domain", "unknown")
            domains_count[domain] = domains_count.get(domain, 0) + 1
        except:
            continue

    for domain, count in domains_count.items():
        print(f"  {domain}: {count} examples")

    print(f"\n🎯 Ready for T5 training!")


if __name__ == "__main__":
    main()