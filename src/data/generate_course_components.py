# Educational Components Generation System

import hashlib
import json
import time
import uuid
from datetime import datetime
from pathlib import Path

import anthropic

ANTHROPIC_MODEL = "claude-sonnet-4-20250514"


# Component creation functions return dictionaries


def create_learning_activity(**kwargs):
    return {
        "activity_id": kwargs.get("activity_id", str(uuid.uuid4())),
        "title": kwargs["title"],
        "description": kwargs["description"],
        "bloom_level": kwargs["bloom_level"],
        "domain": kwargs["domain"],
        "difficulty_level": kwargs["difficulty_level"],
        "estimated_duration": kwargs["estimated_duration"],
        "learning_objectives": kwargs["learning_objectives"],
        "instructions": kwargs["instructions"],
        "materials_needed": kwargs["materials_needed"],
        "assessment_method": kwargs["assessment_method"],
        "scaffolding_notes": kwargs["scaffolding_notes"],
        "module_id": kwargs["module_id"],
    }


def create_assessment_component(**kwargs):
    return {
        "assessment_id": kwargs.get("assessment_id", str(uuid.uuid4())),
        "title": kwargs["title"],
        "type": kwargs["type"],
        "description": kwargs["description"],
        "domain": kwargs["domain"],
        "difficulty_level": kwargs["difficulty_level"],
        "estimated_time": kwargs["estimated_time"],
        "total_points": kwargs["total_points"],
        "learning_objectives_assessed": kwargs["learning_objectives_assessed"],
        "rubric_criteria": kwargs["rubric_criteria"],
        "instructions": kwargs["instructions"],
        "grading_notes": kwargs["grading_notes"],
        "module_id": kwargs["module_id"],
    }


def create_module_component(**kwargs):
    return {
        "module_id": kwargs.get("module_id", str(uuid.uuid4())),
        "title": kwargs["title"],
        "description": kwargs["description"],
        "domain": kwargs["domain"],
        "week_number": kwargs["week_number"],
        "learning_objectives": kwargs["learning_objectives"],
        "key_concepts": kwargs["key_concepts"],
        "prerequisite_concepts": kwargs["prerequisite_concepts"],
        "readings": kwargs["readings"],
        "estimated_workload": kwargs["estimated_workload"],
        "summary": kwargs["summary"],
    }


class EducationalComponentGenerator:
    def __init__(self, api_key: str, output_dir: str = "data/components"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.rate_limit_delay = 2.0
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Component files for incremental saving
        self.activities_file = self.output_dir / "learning_activities.json"
        self.assessments_file = self.output_dir / "assessments.json"
        self.modules_file = self.output_dir / "modules.json"

        # Load existing components
        self.existing_activities = self._load_existing_components(
            self.activities_file, "LearningActivity"
        )
        self.existing_assessments = self._load_existing_components(
            self.assessments_file, "AssessmentComponent"
        )
        self.existing_modules = self._load_existing_components(
            self.modules_file, "ModuleComponent"
        )

        # Educational domains aligned with training templates
        self.domains = [
            # University courses (testing with core domains first)
            "Computer Science",
            "Data Science",
            "Mathematics",
            "Physics",
            # Professional development
            "Software Development",
            "Data Analysis",
            "Project Management",
            "Leadership",
            # Certification prep
            "AWS Cloud",
            "PMP",
            "Google Analytics",
            "Cisco Networking",
        ]

        # Bloom's taxonomy levels
        self.bloom_levels = [
            "remember",
            "understand",
            "apply",
            "analyze",
            "evaluate",
            "create",
        ]

        # Difficulty levels
        self.difficulty_levels = ["beginner", "intermediate", "advanced", "expert"]

    def _load_existing_components(self, file_path: Path, component_class) -> list:
        """Load existing components from file"""
        if not file_path.exists():
            return []

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            components = []
            for item in data:
                if component_class == "LearningActivity":
                    components.append(item)
                elif component_class == "AssessmentComponent":
                    components.append(item)
                elif component_class == "ModuleComponent":
                    components.append(item)

            print(f"Loaded {len(components)} existing {component_class}s")
            return components
        except Exception as e:
            print(f"Error loading existing components from {file_path}: {e}")
            return []

    def _get_component_hash(self, title: str, description: str) -> str:
        """Generate hash for duplicate detection"""
        content = f"{title.lower().strip()}{description.lower().strip()}"
        return hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()

    def _is_duplicate(self, new_component, existing_components) -> bool:
        """Check if component already exists"""
        new_hash = self._get_component_hash(
            new_component["title"], new_component["description"]
        )

        for existing in existing_components:
            existing_hash = self._get_component_hash(
                existing["title"], existing["description"]
            )
            if new_hash == existing_hash:
                return True
        return False

    def _save_component_immediately(
        self, component, file_path: Path, existing_components: list
    ) -> None:
        """Save component immediately to prevent data loss"""
        existing_components.append(component)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                list(existing_components),
                f,
                indent=2,
                ensure_ascii=False,
            )

    def generate_learning_activities(
        self, count: int = 50, domain: str = None
    ) -> list[dict]:
        """Generate detailed learning activities"""

        print(f"Generating {count} learning activities...")
        print(f"Starting with {len(self.existing_activities)} existing activities")

        activities = self.existing_activities.copy()
        needed = count - len(activities)

        if needed <= 0:
            print(f"Already have {len(activities)} activities (target: {count})")
            return activities[:count]

        target_domains = [domain] if domain else self.domains

        for i in range(needed):
            current_domain = target_domains[i % len(target_domains)]
            bloom_level = self.bloom_levels[i % len(self.bloom_levels)]
            difficulty = self.difficulty_levels[i % len(self.difficulty_levels)]

            prompt = f"""Create a detailed, specific learning activity for {current_domain} at {bloom_level} level.

REQUIREMENTS:
- Domain: {current_domain}
- Bloom's Level: {bloom_level}
- Difficulty: {difficulty}
- Must be highly specific and actionable
- Include step-by-step instructions
- Provide clear success criteria

Generate a comprehensive learning activity that instructors can immediately implement.

OUTPUT FORMAT (JSON only):
{{
    "title": "Specific, actionable activity title",
    "description": "2-3 sentence overview of what students will do and learn",
    "learning_objectives": [
        "Students will [specific bloom verb] [specific content] by [method/context]",
        "Students will [specific bloom verb] [specific content] through [activity type]"
    ],
    "instructions": "Detailed step-by-step instructions (300-400 words) that teachers can follow exactly. Include timing, groupings, materials setup, and student actions.",
    "materials_needed": [
        "Specific item 1",
        "Specific item 2",
        "Specific software/tool if applicable"
    ],
    "assessment_method": "How to evaluate student success (rubric points, deliverables, observations)",
    "scaffolding_notes": "Tips for supporting struggling students and extending for advanced learners",
    "estimated_duration": "X minutes/hours"
}}

Focus on practical implementation details that make this activity immediately usable."""

            try:
                response = self.client.messages.create(
                    model=ANTHROPIC_MODEL,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}],
                )

                content = response.content[0].text.strip()
                json_start = content.find("{")
                json_end = content.rfind("}") + 1

                if json_start != -1 and json_end > json_start:
                    json_content = content[json_start:json_end]
                    data = json.loads(json_content)

                    activity = create_learning_activity(
                        activity_id=str(uuid.uuid4()),
                        title=data["title"],
                        description=data["description"],
                        bloom_level=bloom_level,
                        domain=current_domain,
                        difficulty_level=difficulty,
                        estimated_duration=data["estimated_duration"],
                        learning_objectives=data["learning_objectives"],
                        instructions=data["instructions"],
                        materials_needed=data["materials_needed"],
                        assessment_method=data["assessment_method"],
                        scaffolding_notes=data["scaffolding_notes"],
                        module_id="",  # Will be set later when linking to modules
                    )

                    # Check for duplicates
                    if not self._is_duplicate(activity, activities):
                        self._save_component_immediately(
                            activity, self.activities_file, activities
                        )
                        activity_title = activity["title"]
                        print(
                            f"\t[{len(activities)}/{count}] Generated: {activity_title}"
                        )
                    else:
                        activity_title = activity["title"]
                        print(f"\t[{i+1}/{needed}] Skipped duplicate: {activity_title}")

                time.sleep(self.rate_limit_delay)

            except Exception as e:
                print(f"\t[{i+1}/{needed}] Error generating activity: {e}")
                continue

        return activities

    def generate_assessments(self, count: int = 30, domain: str = None) -> list[dict]:
        """Generate detailed assessment components"""

        print(f"Generating {count} assessment components...")
        print(f"Starting with {len(self.existing_assessments)} existing assessments")

        assessments = self.existing_assessments.copy()
        needed = count - len(assessments)

        if needed <= 0:
            print(f"Already have {len(assessments)} assessments (target: {count})")
            return assessments[:count]

        target_domains = [domain] if domain else self.domains
        assessment_types = [
            "quiz",
            "project",
            "exam",
            "discussion",
            "presentation",
            "portfolio",
            "lab_report",
        ]

        for i in range(needed):
            current_domain = target_domains[i % len(target_domains)]
            assessment_type = assessment_types[i % len(assessment_types)]
            difficulty = self.difficulty_levels[i % len(self.difficulty_levels)]

            prompt = f"""Create a detailed assessment component for {current_domain}.

REQUIREMENTS:
- Domain: {current_domain}
- Type: {assessment_type}
- Difficulty: {difficulty}
- Must be specific and implementable
- Include clear grading criteria
- Provide detailed instructions

OUTPUT FORMAT (JSON only):
{{
    "title": "Specific assessment title",
    "description": "Clear overview of what students will be assessed on",
    "estimated_time": "Time needed for completion",
    "total_points": 100,
    "learning_objectives_assessed": [
        "Specific objective 1",
        "Specific objective 2"
    ],
    "rubric_criteria": [
        "Criterion 1 (25 points): Specific evaluation standard",
        "Criterion 2 (25 points): Specific evaluation standard",
        "Criterion 3 (25 points): Specific evaluation standard",
        "Criterion 4 (25 points): Specific evaluation standard"
    ],
    "instructions": "Detailed instructions for students (300-400 words) including requirements, format, submission guidelines",
    "grading_notes": "Guidelines for instructors on evaluation, common issues to watch for, grade distribution expectations"
}}

Make this assessment immediately usable by instructors."""

            try:
                response = self.client.messages.create(
                    model=ANTHROPIC_MODEL,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}],
                )

                content = response.content[0].text.strip()
                json_start = content.find("{")
                json_end = content.rfind("}") + 1

                if json_start != -1 and json_end > json_start:
                    json_content = content[json_start:json_end]
                    data = json.loads(json_content)

                    assessment = create_assessment_component(
                        assessment_id=str(uuid.uuid4()),
                        title=data["title"],
                        type=assessment_type,
                        description=data["description"],
                        domain=current_domain,
                        difficulty_level=difficulty,
                        estimated_time=data["estimated_time"],
                        total_points=data["total_points"],
                        learning_objectives_assessed=data[
                            "learning_objectives_assessed"
                        ],
                        rubric_criteria=data["rubric_criteria"],
                        instructions=data["instructions"],
                        grading_notes=data["grading_notes"],
                        module_id="",  # Will be set later when linking to modules
                    )

                    # Check for duplicates
                    if not self._is_duplicate(assessment, assessments):
                        self._save_component_immediately(
                            assessment, self.assessments_file, assessments
                        )
                        assessment_title = assessment["title"]
                        print(
                            f"\t[{len(assessments)}/{count}] Generated: {assessment_title}"
                        )
                    else:
                        assessment_title = assessment["title"]
                        print(
                            f"\t[{i+1}/{needed}] Skipped duplicate: {assessment_title}"
                        )

                time.sleep(self.rate_limit_delay)

            except Exception as e:
                print(f"\t[{i+1}/{needed}] Error generating assessment: {e}")
                continue

        return assessments

    def generate_modules(self, count: int = 20, domain: str = None) -> list[dict]:
        """Generate course module/unit components"""

        print(f"Generating {count} module components...")
        print(f"Starting with {len(self.existing_modules)} existing modules")

        modules = self.existing_modules.copy()
        needed = count - len(modules)

        if needed <= 0:
            print(f"Already have {len(modules)} modules (target: {count})")
            return modules[:count]

        target_domains = [domain] if domain else self.domains

        for i in range(needed):
            current_domain = target_domains[i % len(target_domains)]

            prompt = f"""Create a detailed course module for {current_domain}.

REQUIREMENTS:
- Domain: {current_domain}
- Include specific, actionable content
- Focus on a distinct topic/concept within the domain
- Provide clear learning objectives

OUTPUT FORMAT (JSON only):
{{
    "title": "Specific Module Title",
    "description": "Comprehensive overview of this module's focus and why it matters (200-300 words)",
    "learning_objectives": [
        "Students will [specific verb] [specific content] by [method]",
        "Students will [specific verb] [specific content] through [activity]",
        "Students will [specific verb] [specific content] using [tool/framework]"
    ],
    "key_concepts": [
        "Specific concept 1 with brief definition",
        "Specific concept 2 with brief definition",
        "Specific concept 3 with brief definition"
    ],
    "prerequisite_concepts": [
        "Foundation concepts needed",
        "Background knowledge required"
    ],
    "readings": [
        "Specific textbook chapter: Title (Author, Year) pp. X-Y",
        "Journal article: Title (Author, Year) - specific focus",
        "Online resource: Platform/Site - specific content"
    ],
    "estimated_workload": "X hours total (Y hours reading, Z hours activities, W hours assignments)",
    "summary": "Key takeaways and how this module connects to overall course goals (150-200 words)"
}}

Create a module that instructors can immediately implement."""

            try:
                response = self.client.messages.create(
                    model=ANTHROPIC_MODEL,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}],
                )

                content = response.content[0].text.strip()
                json_start = content.find("{")
                json_end = content.rfind("}") + 1

                if json_start != -1 and json_end > json_start:
                    json_content = content[json_start:json_end]
                    data = json.loads(json_content)

                    module = create_module_component(
                        module_id=str(uuid.uuid4()),
                        title=data["title"],
                        description=data["description"],
                        domain=current_domain,
                        week_number=0,  # Will be assigned by syllabus assembler
                        learning_objectives=data["learning_objectives"],
                        key_concepts=data["key_concepts"],
                        prerequisite_concepts=data["prerequisite_concepts"],
                        readings=data["readings"],
                        estimated_workload=data["estimated_workload"],
                        summary=data["summary"],
                    )

                    # Check for duplicates
                    if not self._is_duplicate(module, modules):
                        self._save_component_immediately(
                            module, self.modules_file, modules
                        )
                        module_title = module["title"]
                        print(f"\t[{len(modules)}/{count}] Generated: {module_title}")
                    else:
                        module_title = module["title"]
                        print(f"\t[{i+1}/{needed}] Skipped duplicate: {module_title}")

                time.sleep(self.rate_limit_delay)

            except Exception as e:
                print(f"\t[{i+1}/{needed}] Error generating module: {e}")
                continue

        return modules

    def link_components_to_modules(
        self,
        activities: list[dict],
        assessments: list[dict],
        modules: list[dict],
    ) -> None:
        """Simple random linking of components to modules by domain"""

        # Group modules by domain
        modules_by_domain = {}
        for module in modules:
            if module["domain"] not in modules_by_domain:
                modules_by_domain[module["domain"]] = []
            modules_by_domain[module["domain"]].append(module)

        # Simple random linking
        import random

        for activity in activities:
            if activity["domain"] in modules_by_domain:
                chosen_module = random.choice(modules_by_domain[activity["domain"]])
                activity["module_id"] = chosen_module["module_id"]

        for assessment in assessments:
            if assessment["domain"] in modules_by_domain:
                chosen_module = random.choice(modules_by_domain[assessment["domain"]])
                assessment["module_id"] = chosen_module["module_id"]

    def save_components(
        self,
        activities: list[dict],
        assessments: list[dict],
        modules: list[dict],
    ) -> None:
        """Final save with timestamped backup"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")

        # Create timestamped backup files
        backup_activities = self.output_dir / f"learning_activities_{timestamp}.json"
        backup_assessments = self.output_dir / f"assessments_{timestamp}.json"
        backup_modules = self.output_dir / f"modules_{timestamp}.json"

        with open(backup_activities, "w", encoding="utf-8") as f:
            json.dump(
                list(activities),
                f,
                indent=2,
                ensure_ascii=False,
            )

        with open(backup_assessments, "w", encoding="utf-8") as f:
            json.dump(
                list(assessments),
                f,
                indent=2,
                ensure_ascii=False,
            )

        with open(backup_modules, "w", encoding="utf-8") as f:
            json.dump(list(modules), f, indent=2, ensure_ascii=False)

        print("\nTimestamped backups created:")
        print(f"\tActivities: {backup_activities}")
        print(f"\tAssessments: {backup_assessments}")
        print(f"\tModules: {backup_modules}")


def main() -> None:
    """Generate educational components using Claude API"""

    import os

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not found!")
        return

    generator = EducationalComponentGenerator(api_key=api_key)

    print("Starting educational component generation...")
    print("=" * 60)

    # Generate quick test component library (3 domains: CS, Data Science, Math)
    # modules = generator.generate_modules(count=60)         # ~20 per domain
    # activities = generator.generate_learning_activities(count=120)   # ~40 per domain
    # assessments = generator.generate_assessments(count=30)           # ~10 per domain

    # Production scale (uncomment when ready for full generation):
    modules = generator.generate_modules(count=600)  # ~50 per domain (3+ semesters)
    activities = generator.generate_learning_activities(
        count=1200
    )  # ~100 per domain (~2 per module)
    assessments = generator.generate_assessments(
        count=300
    )  # ~25 per domain (~1 per 2 modules)

    # Link activities and assessments to modules
    generator.link_components_to_modules(activities, assessments, modules)

    # Create timestamped backup
    generator.save_components(activities, assessments, modules)

    print("=" * 60)
    print("Component generation complete!")
    print(
        f"Final counts: {len(activities)} activities, {len(assessments)} assessments, {len(modules)} modules"
    )
    print("Components saved to main files and timestamped backups")


if __name__ == "__main__":
    main()
