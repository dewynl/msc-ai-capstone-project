#!/usr/bin/env python3
"""
STEM-Focused Educational Components Generation System

This system generates synthetic educational components using the simplified
STEM-focused data model for Computer Science, Mathematics, Physics, and Engineering.
"""

import hashlib
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import anthropic

# Import our new simplified models
from .models import (
    STEM_DOMAIN_GUIDELINES,
    AssessmentType,
    BloomLevel,
    DifficultyLevel,
    Domain,
    validate_assessment_component,
    validate_course_module,
    validate_learning_activity,
)

ANTHROPIC_MODEL = "claude-sonnet-4-20250514"


class STEMComponentsGenerator:
    """Generate high-quality STEM educational components with simplified schema"""

    def __init__(self, api_key: str, output_dir: str = "data/components/stem"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.rate_limit_delay = 2.0
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Component files for STEM focus
        self.activities_file = self.output_dir / "stem_learning_activities.json"
        self.assessments_file = self.output_dir / "stem_assessments.json"
        self.modules_file = self.output_dir / "stem_modules.json"

        # Load existing components
        self.existing_activities = self._load_existing_components(self.activities_file)
        self.existing_assessments = self._load_existing_components(
            self.assessments_file
        )
        self.existing_modules = self._load_existing_components(self.modules_file)

        # STEM domains (simplified from 12 to 4)
        self.stem_domains = [
            Domain.CS,  # Computer Science
            Domain.MATH,  # Mathematics
            Domain.PHYSICS,  # Physics
            Domain.ENGINEERING,  # Engineering
        ]

        # Bloom's taxonomy levels
        self.bloom_levels = [
            BloomLevel.REMEMBER,
            BloomLevel.UNDERSTAND,
            BloomLevel.APPLY,
            BloomLevel.ANALYZE,
            BloomLevel.EVALUATE,
            BloomLevel.CREATE,
        ]

        # Difficulty levels
        self.difficulty_levels = [
            DifficultyLevel.BEGINNER,
            DifficultyLevel.INTERMEDIATE,
            DifficultyLevel.ADVANCED,
        ]

        # Assessment types
        self.assessment_types = [
            AssessmentType.EXAM,
            AssessmentType.PROJECT,
            AssessmentType.ASSIGNMENT,
            AssessmentType.QUIZ,
            AssessmentType.LAB,
        ]

        print("🔬 STEM Components Generator initialized")
        print(f"   Domains: {len(self.stem_domains)} STEM areas")
        print(
            f"   Existing: {len(self.existing_activities)} activities, "
            f"{len(self.existing_assessments)} assessments, "
            f"{len(self.existing_modules)} modules"
        )

    def _load_existing_components(self, file_path: Path) -> List[Dict]:
        """Load existing components from file"""
        if not file_path.exists():
            return []

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
            print(f"📂 Loaded {len(data)} existing components from {file_path.name}")
            return data
        except Exception as e:
            print(f"⚠️ Error loading components from {file_path}: {e}")
            return []

    def _get_component_hash(self, title: str, description: str) -> str:
        """Generate hash for duplicate detection"""
        content = f"{title.lower().strip()}{description.lower().strip()}"
        return hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()

    def _is_duplicate(
        self, new_component: Dict, existing_components: List[Dict]
    ) -> bool:
        """Check if component already exists (improved duplicate detection)"""
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
        self, component: Dict, file_path: Path, existing_components: List[Dict]
    ) -> None:
        """Save component immediately to prevent data loss"""
        existing_components.append(component)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_components, f, indent=2, ensure_ascii=False)

    def _create_stem_activity_prompt(
        self, domain: Domain, bloom_level: BloomLevel, difficulty: DifficultyLevel
    ) -> str:
        """Create focused prompt for STEM learning activities"""

        domain_info = STEM_DOMAIN_GUIDELINES[domain]

        prompt = f"""Generate a high-quality learning activity for {domain_info['name']} education.

REQUIREMENTS:
- Domain: {domain_info['name']} ({', '.join(domain_info['areas'])})
- Bloom Level: {bloom_level.value}
- Difficulty: {difficulty.value}
- Time: 1-8 hours (be realistic for the activity scope)

FOCUS AREAS for {domain_info['name']}:
- Core concepts: {', '.join(domain_info['typical_concepts'])}
- Mathematical foundation: {', '.join(domain_info.get('math_foundation', ['Logic', 'Problem solving']))}

FORMAT (return as valid JSON):
{{
    "title": "Specific, actionable title (max 80 chars)",
    "description": "Clear description of what students will learn and do (2-3 sentences)",
    "stem_domain": "{domain.value}",
    "bloom_level": "{bloom_level.value}",
    "difficulty": "{difficulty.value}",
    "estimated_hours": <integer 1-8>,
    "learning_objectives": [
        "Specific, measurable objective 1 (start with action verb)",
        "Specific, measurable objective 2 (start with action verb)"
    ],
    "instructions": "Step-by-step instructions for students (detailed, practical)",
    "materials_needed": [
        "Material 1",
        "Material 2"
    ],
    "assessment_method": "How student learning will be assessed (1 sentence)"
}}

QUALITY CRITERIA:
- Activities should build on typical {domain_info['name']} knowledge progression
- Instructions should be implementable in real classroom/lab setting
- Learning objectives should be measurable and appropriate for {bloom_level.value} level
- Avoid generic activities - make them specific to {domain_info['name']}
- Time estimate should match activity complexity"""

        return prompt

    def _create_stem_assessment_prompt(
        self,
        domain: Domain,
        assessment_type: AssessmentType,
        difficulty: DifficultyLevel,
    ) -> str:
        """Create focused prompt for STEM assessments"""

        domain_info = STEM_DOMAIN_GUIDELINES[domain]

        prompt = f"""Generate a high-quality assessment component for {domain_info['name']} education.

REQUIREMENTS:
- Domain: {domain_info['name']} ({', '.join(domain_info['areas'])})
- Assessment Type: {assessment_type.value}
- Difficulty: {difficulty.value}
- Time: 1-40 hours (realistic for {assessment_type.value})

FOCUS AREAS for {domain_info['name']}:
- Core concepts: {', '.join(domain_info['typical_concepts'])}
- Mathematical foundation: {', '.join(domain_info.get('math_foundation', ['Problem solving']))}

FORMAT (return as valid JSON):
{{
    "title": "Specific assessment title (max 80 chars)",
    "description": "Clear description of what students will be assessed on (2-3 sentences)",
    "stem_domain": "{domain.value}",
    "assessment_type": "{assessment_type.value}",
    "difficulty": "{difficulty.value}",
    "estimated_hours": <integer 1-40>,
    "learning_objectives": [
        "Specific learning objective 1 being assessed",
        "Specific learning objective 2 being assessed"
    ],
    "criteria": [
        "Assessment criteria 1 (how quality will be judged)",
        "Assessment criteria 2 (how quality will be judged)",
        "Assessment criteria 3 (how quality will be judged)"
    ],
    "materials_needed": [
        "Required material/tool 1",
        "Required material/tool 2"
    ]
}}

QUALITY CRITERIA:
- Assessment should authentically measure {domain_info['name']} understanding
- Criteria should be specific, measurable, and appropriate for {difficulty.value} level
- For {assessment_type.value}: make requirements realistic for that format
- Time estimate should reflect actual student work time
- Avoid generic assessments - make them domain-specific"""

        return prompt

    def _create_stem_module_prompt(
        self, domain: Domain, difficulty: DifficultyLevel
    ) -> str:
        """Create focused prompt for STEM course modules"""

        domain_info = STEM_DOMAIN_GUIDELINES[domain]

        prompt = f"""Generate a coherent course module for {domain_info['name']} education.

REQUIREMENTS:
- Domain: {domain_info['name']} ({', '.join(domain_info['areas'])})
- Difficulty: {difficulty.value}
- Time: 3-30 hours total (lectures + student work)

FOCUS AREAS for {domain_info['name']}:
- Core concepts: {', '.join(domain_info['typical_concepts'])}
- Mathematical foundation: {', '.join(domain_info.get('math_foundation', ['Problem solving']))}

FORMAT (return as valid JSON):
{{
    "title": "Module title (max 80 chars)",
    "description": "Module overview and what students will master (2-3 sentences)",
    "stem_domain": "{domain.value}",
    "difficulty": "{difficulty.value}",
    "estimated_hours": <integer 3-30>,
    "key_concepts": [
        "Core concept 1 covered in this module",
        "Core concept 2 covered in this module",
        "Core concept 3 covered in this module"
    ],
    "learning_objectives": [
        "Specific learning objective 1 (measurable)",
        "Specific learning objective 2 (measurable)"
    ],
    "suggested_readings": [
        "Textbook chapter or paper 1",
        "Textbook chapter or paper 2"
    ]
}}

QUALITY CRITERIA:
- Module should cover cohesive topic cluster in {domain_info['name']}
- Key concepts should build on each other logically
- Learning objectives should be appropriate for {difficulty.value} level
- Readings should be realistic and domain-appropriate
- Time estimate should include both instruction and student work time
- Module should fit naturally in {domain_info['name']} curriculum sequence"""

        return prompt

    def _call_anthropic_api(self, prompt: str, max_retries: int = 3) -> Optional[Dict]:
        """Make API call to Anthropic with retry logic and validation"""

        for attempt in range(max_retries):
            try:
                time.sleep(self.rate_limit_delay)

                response = self.client.messages.create(
                    model=ANTHROPIC_MODEL,
                    max_tokens=1500,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}],
                )

                content = response.content[0].text.strip()

                # Extract JSON from response
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    json_content = content[json_start:json_end].strip()
                else:
                    json_content = content

                # Parse and validate JSON
                component_data = json.loads(json_content)
                return component_data

            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    print(f"❌ Failed to parse JSON after {max_retries} attempts")
                    return None

            except Exception as e:
                print(f"⚠️ API call error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    print(f"❌ API call failed after {max_retries} attempts")
                    return None
                time.sleep(self.rate_limit_delay * (attempt + 1))

        return None

    def generate_stem_learning_activities(
        self, count_per_domain: int = 40
    ) -> List[Dict]:
        """Generate STEM-focused learning activities"""

        print(
            f"\n🎯 Generating STEM Learning Activities ({count_per_domain} per domain)"
        )
        total_target = count_per_domain * len(self.stem_domains)
        current_total = len(self.existing_activities)
        needed = total_target - current_total

        if needed <= 0:
            print(f"✅ Already have {current_total} activities (target: {total_target})")
            return self.existing_activities[:total_target]

        print(f"   Target: {total_target} total ({count_per_domain} per domain)")
        print(f"   Existing: {current_total}")
        print(f"   Need to generate: {needed}")

        activities = self.existing_activities.copy()
        generated_count = 0

        # Generate activities across all STEM domains and difficulty levels
        for i in range(needed):
            domain = self.stem_domains[i % len(self.stem_domains)]
            bloom_level = self.bloom_levels[i % len(self.bloom_levels)]
            difficulty = self.difficulty_levels[i % len(self.difficulty_levels)]

            print(
                f"📝 Generating activity {i+1}/{needed}: {domain.value} - {bloom_level.value} - {difficulty.value}"
            )

            prompt = self._create_stem_activity_prompt(domain, bloom_level, difficulty)
            component_data = self._call_anthropic_api(prompt)

            if not component_data:
                print(f"⚠️ Skipping activity {i+1} due to generation failure")
                continue

            # Validate against our schema
            if not validate_learning_activity(component_data):
                print(
                    f"⚠️ Skipping invalid activity: {component_data.get('title', 'Unknown')}"
                )
                continue

            # Check for duplicates
            if self._is_duplicate(component_data, activities):
                print(f"⚠️ Skipping duplicate activity: {component_data['title']}")
                continue

            # Save immediately
            self._save_component_immediately(
                component_data, self.activities_file, activities
            )
            generated_count += 1

            print(
                f"✅ Generated: {component_data['title']} ({component_data['estimated_hours']}h)"
            )

        print(f"🎉 Generated {generated_count} new STEM learning activities")
        return activities

    def generate_stem_assessments(self, count_per_domain: int = 15) -> List[Dict]:
        """Generate STEM-focused assessments"""

        print(
            f"\n📋 Generating STEM Assessment Components ({count_per_domain} per domain)"
        )
        total_target = count_per_domain * len(self.stem_domains)
        current_total = len(self.existing_assessments)
        needed = total_target - current_total

        if needed <= 0:
            print(
                f"✅ Already have {current_total} assessments (target: {total_target})"
            )
            return self.existing_assessments[:total_target]

        print(f"   Target: {total_target} total ({count_per_domain} per domain)")
        print(f"   Existing: {current_total}")
        print(f"   Need to generate: {needed}")

        assessments = self.existing_assessments.copy()
        generated_count = 0

        for i in range(needed):
            domain = self.stem_domains[i % len(self.stem_domains)]
            assessment_type = self.assessment_types[i % len(self.assessment_types)]
            difficulty = self.difficulty_levels[i % len(self.difficulty_levels)]

            print(
                f"📋 Generating assessment {i+1}/{needed}: {domain.value} - {assessment_type.value} - {difficulty.value}"
            )

            prompt = self._create_stem_assessment_prompt(
                domain, assessment_type, difficulty
            )
            component_data = self._call_anthropic_api(prompt)

            if not component_data:
                print(f"⚠️ Skipping assessment {i+1} due to generation failure")
                continue

            # Validate against our schema
            if not validate_assessment_component(component_data):
                print(
                    f"⚠️ Skipping invalid assessment: {component_data.get('title', 'Unknown')}"
                )
                continue

            # Check for duplicates
            if self._is_duplicate(component_data, assessments):
                print(f"⚠️ Skipping duplicate assessment: {component_data['title']}")
                continue

            # Save immediately
            self._save_component_immediately(
                component_data, self.assessments_file, assessments
            )
            generated_count += 1

            print(
                f"✅ Generated: {component_data['title']} ({component_data['estimated_hours']}h)"
            )

        print(f"🎉 Generated {generated_count} new STEM assessment components")
        return assessments

    def generate_stem_modules(self, count_per_domain: int = 10) -> List[Dict]:
        """Generate STEM-focused course modules"""

        print(f"\n📚 Generating STEM Course Modules ({count_per_domain} per domain)")
        total_target = count_per_domain * len(self.stem_domains)
        current_total = len(self.existing_modules)
        needed = total_target - current_total

        if needed <= 0:
            print(f"✅ Already have {current_total} modules (target: {total_target})")
            return self.existing_modules[:total_target]

        print(f"   Target: {total_target} total ({count_per_domain} per domain)")
        print(f"   Existing: {current_total}")
        print(f"   Need to generate: {needed}")

        modules = self.existing_modules.copy()
        generated_count = 0

        for i in range(needed):
            domain = self.stem_domains[i % len(self.stem_domains)]
            difficulty = self.difficulty_levels[i % len(self.difficulty_levels)]

            print(
                f"📚 Generating module {i+1}/{needed}: {domain.value} - {difficulty.value}"
            )

            prompt = self._create_stem_module_prompt(domain, difficulty)
            component_data = self._call_anthropic_api(prompt)

            if not component_data:
                print(f"⚠️ Skipping module {i+1} due to generation failure")
                continue

            # Validate against our schema
            if not validate_course_module(component_data):
                print(
                    f"⚠️ Skipping invalid module: {component_data.get('title', 'Unknown')}"
                )
                continue

            # Check for duplicates
            if self._is_duplicate(component_data, modules):
                print(f"⚠️ Skipping duplicate module: {component_data['title']}")
                continue

            # Save immediately
            self._save_component_immediately(component_data, self.modules_file, modules)
            generated_count += 1

            print(
                f"✅ Generated: {component_data['title']} ({component_data['estimated_hours']}h)"
            )

        print(f"🎉 Generated {generated_count} new STEM course modules")
        return modules

    def generate_all_stem_components(
        self,
        activities_per_domain: int = 40,
        assessments_per_domain: int = 15,
        modules_per_domain: int = 10,
    ):
        """Generate complete STEM component library"""

        print("🚀 Starting Complete STEM Components Generation")
        print("=" * 70)

        start_time = datetime.now()

        try:
            # Generate all component types
            activities = self.generate_stem_learning_activities(activities_per_domain)
            assessments = self.generate_stem_assessments(assessments_per_domain)
            modules = self.generate_stem_modules(modules_per_domain)

            end_time = datetime.now()
            duration = end_time - start_time

            # Summary report
            print("\n🎉 STEM Components Generation Complete!")
            print("=" * 70)
            print("📊 Total Components Generated:")
            print(
                f"   🎯 Activities: {len(activities)} ({activities_per_domain} per domain)"
            )
            print(
                f"   📋 Assessments: {len(assessments)} ({assessments_per_domain} per domain)"
            )
            print(f"   📚 Modules: {len(modules)} ({modules_per_domain} per domain)")
            print(f"   ⏱️ Generation time: {duration}")
            print(f"   🎓 STEM domains covered: {len(self.stem_domains)}")

            total_components = len(activities) + len(assessments) + len(modules)
            print(f"\n🔢 Grand Total: {total_components} STEM educational components")

            # Estimate total educational content hours
            total_hours = sum(a.get("estimated_hours", 0) for a in activities)
            total_hours += sum(a.get("estimated_hours", 0) for a in assessments)
            total_hours += sum(m.get("estimated_hours", 0) for m in modules)
            print(f"⏰ Total educational content: ~{total_hours} hours")

            return {
                "activities": activities,
                "assessments": assessments,
                "modules": modules,
                "generation_time": duration,
                "total_components": total_components,
                "total_hours": total_hours,
            }

        except KeyboardInterrupt:
            print("\n⚠️ Generation interrupted by user")
            return None
        except Exception as e:
            print(f"\n❌ Generation failed: {e}")
            return None


def main():
    """Main execution function for STEM components generation"""

    import os
    import sys

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your Anthropic API key:")
        print("export ANTHROPIC_API_KEY='your-api-key-here'")
        sys.exit(1)

    # Create generator
    generator = STEMComponentsGenerator(api_key)

    # Start generation with reasonable targets for MSc project
    results = generator.generate_all_stem_components(
        activities_per_domain=40,  # 160 total activities
        assessments_per_domain=15,  # 60 total assessments
        modules_per_domain=10,  # 40 total modules
    )

    if results:
        print("\n✅ STEM components generation completed successfully!")
        print(f"📁 Files saved in: {generator.output_dir}")
    else:
        print("\n❌ STEM components generation failed or was interrupted")
        sys.exit(1)


if __name__ == "__main__":
    main()
