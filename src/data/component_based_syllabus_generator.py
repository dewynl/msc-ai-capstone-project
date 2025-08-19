# Component-Based Syllabus Generator

import hashlib
import json
import random
import time
from datetime import datetime
from pathlib import Path

import anthropic

ANTHROPIC_MODEL = "claude-sonnet-4-20250514"


# Simple dictionary structures instead of dataclasses


class ComponentBasedSyllabusGenerator:
    """
    Generates complete syllabi by intelligently selecting and assembling
    pre-generated educational components.
    """

    def __init__(
        self,
        api_key: str,
        components_dir: str = "data/components",
        output_dir: str = "data/assembled_syllabi",
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.rate_limit_delay = 2.0
        self.components_dir = Path(components_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Component libraries (loaded from files)
        self.activities: list[dict] = []
        self.assessments: list[dict] = []
        self.modules: list[dict] = []

        # Duplication tracking
        self.generated_titles: set[str] = set()
        self.content_hashes: set[str] = set()
        self.component_usage_counts: dict[
            str, int
        ] = {}  # Track how often each component is used
        self.component_combination_hashes: set[
            str
        ] = set()  # Track component combinations

        # Simplified course templates
        self.course_templates = {
            "academic": {
                "domains": [
                    "Computer Science",
                    "Data Science",
                    "Mathematics",
                    "Physics",
                ],
                "levels": ["undergraduate", "graduate"],
                "durations": ["semester", "quarter"],
            },
            "professional": {
                "domains": [
                    "Software Development",
                    "Data Analysis",
                    "Project Management",
                    "Leadership",
                ],
                "levels": ["beginner", "intermediate", "advanced"],
                "durations": ["6-week", "intensive", "semester"],
            },
            "certification": {
                "domains": ["AWS Cloud", "PMP", "Google Analytics", "Cisco Networking"],
                "levels": ["associate", "professional", "expert"],
                "durations": ["intensive", "6-week"],
            },
        }

    def load_components(
        self, activities_file: str, assessments_file: str, modules_file: str
    ) -> None:
        """Load generated components from JSON files"""

        print(f"Loading components from {self.components_dir}")

        # Load activities
        activities_path = self.components_dir / activities_file
        with open(activities_path, encoding="utf-8") as f:
            self.activities = json.load(f)

        # Load assessments
        assessments_path = self.components_dir / assessments_file
        with open(assessments_path, encoding="utf-8") as f:
            self.assessments = json.load(f)

        # Load modules
        modules_path = self.components_dir / modules_file
        with open(modules_path, encoding="utf-8") as f:
            self.modules = json.load(f)

        print(
            f"Loaded: {len(self.activities)} activities, {len(self.assessments)} assessments, {len(self.modules)} modules"
        )

        # Initialize component usage tracking
        for activity in self.activities:
            self.component_usage_counts[activity["activity_id"]] = 0
        for assessment in self.assessments:
            self.component_usage_counts[assessment["assessment_id"]] = 0
        for module in self.modules:
            self.component_usage_counts[module["module_id"]] = 0

    def generate_course_requirements(
        self, template_type: str, domain: str, seed: int
    ) -> dict:
        """Generate realistic course requirements"""

        random.seed(seed)

        template = self.course_templates[template_type]
        level = random.choice(template["levels"])
        duration = random.choice(template["durations"])

        prompt = f"""Generate realistic course requirements for a {template_type.replace('_', ' ')} course.

REQUIREMENTS:
- Domain: {domain}
- Level: {level}
- Duration: {duration}
- Template: {template_type}

Create a detailed course specification that a real educational institution would use.

OUTPUT FORMAT (JSON only):
{{
    "course_title": "Specific, realistic course title for {domain} at {level} level",
    "course_description": "Comprehensive 200-300 word description explaining what students will learn, why it matters, and how it fits into their educational/career path",
    "learning_objectives": [
        "Students will [specific action verb] [specific knowledge/skill] to [real-world application]",
        "Students will [specific action verb] [specific knowledge/skill] through [specific method/tool]",
        "Students will [specific action verb] [specific knowledge/skill] by [specific process/approach]",
        "Students will [specific action verb] [specific knowledge/skill] using [specific technology/framework]"
    ],
    "target_audience": "Specific description of intended learners including background, experience level, and career goals",
    "prerequisites": "Detailed prerequisites including specific courses, skills, or experience requirements"
}}

Make this course specification realistic and immediately implementable."""

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

                return {
                    "course_title": data["course_title"],
                    "domain": domain,
                    "level": level,
                    "duration": duration,
                    "learning_objectives": data["learning_objectives"],
                    "target_audience": data["target_audience"],
                    "prerequisites": data["prerequisites"],
                    "course_description": data["course_description"],
                }

        except Exception as e:
            print(f"Error generating course requirements: {e}")
            raise e

    def _is_duplicate_content(self, title: str, content: str) -> bool:
        """Check if content is a duplicate based on content hash (not title)"""

        # Skip title uniqueness check - too restrictive after many samples
        # if title.lower() in self.generated_titles:
        #     return True

        # Check content similarity using hash
        content_hash = hashlib.md5(
            content.encode("utf-8"), usedforsecurity=False
        ).hexdigest()
        if content_hash in self.content_hashes:
            return True

        return False

    def _mark_content_generated(self, title: str, content: str) -> None:
        """Mark content as generated to prevent future duplicates"""
        self.generated_titles.add(title.lower())
        content_hash = hashlib.md5(
            content.encode("utf-8"), usedforsecurity=False
        ).hexdigest()
        self.content_hashes.add(content_hash)

    def _is_component_combination_overused(self, components: dict[str, list]) -> bool:
        """Check if this specific combination of components has been used too much"""

        # Create a hash of the component combination
        component_ids = []
        for module in components["modules"]:
            component_ids.append(module["module_id"])
        for activity in components["activities"]:
            component_ids.append(activity["activity_id"])
        for assessment in components["assessments"]:
            component_ids.append(assessment["assessment_id"])

        # Sort for consistent hashing
        component_ids.sort()
        combination_str = "|".join(component_ids)
        combination_hash = hashlib.md5(
            combination_str.encode("utf-8"), usedforsecurity=False
        ).hexdigest()

        return combination_hash in self.component_combination_hashes

    def _mark_component_combination_used(self, components: dict[str, list]) -> None:
        """Mark this component combination as used"""

        # Create a hash of the component combination
        component_ids = []
        for module in components["modules"]:
            component_ids.append(module["module_id"])
            self.component_usage_counts[module["module_id"]] += 1
        for activity in components["activities"]:
            component_ids.append(activity["activity_id"])
            self.component_usage_counts[activity["activity_id"]] += 1
        for assessment in components["assessments"]:
            component_ids.append(assessment["assessment_id"])
            self.component_usage_counts[assessment["assessment_id"]] += 1

        # Sort for consistent hashing
        component_ids.sort()
        combination_str = "|".join(component_ids)
        combination_hash = hashlib.md5(
            combination_str.encode("utf-8"), usedforsecurity=False
        ).hexdigest()

        self.component_combination_hashes.add(combination_hash)

    def _check_component_exhaustion(self, requirements: dict) -> bool:
        """
        Check if we're running out of viable components for this domain.
        Returns True if we should stop generating to prevent low-quality repetition.
        """

        # Get domain-specific components
        domain_modules = [
            m for m in self.modules if m["domain"] == requirements["domain"]
        ]
        domain_activities = [
            a for a in self.activities if a["domain"] == requirements["domain"]
        ]
        domain_assessments = [
            a for a in self.assessments if a["domain"] == requirements["domain"]
        ]

        # Check if we have enough unused components
        # Calculate reasonable max usage based on total syllabi we want to generate
        # If we want 200 syllabi with 50 components per domain, each component can be used ~8 times
        MAX_USAGE_PER_COMPONENT = max(3, self._calculate_max_usage_per_component())

        available_modules = sum(
            1
            for m in domain_modules
            if self.component_usage_counts.get(m["module_id"], 0)
            < MAX_USAGE_PER_COMPONENT
        )
        available_activities = sum(
            1
            for a in domain_activities
            if self.component_usage_counts.get(a["activity_id"], 0)
            < MAX_USAGE_PER_COMPONENT
        )
        available_assessments = sum(
            1
            for a in domain_assessments
            if self.component_usage_counts.get(a["assessment_id"], 0)
            < MAX_USAGE_PER_COMPONENT
        )

        # Determine minimum needed for a viable course
        weeks_map = {"semester": 16, "quarter": 12, "6-week": 6, "intensive": 4}
        weeks_needed = weeks_map.get(requirements["duration"], 16)

        min_modules_needed = weeks_needed
        min_activities_needed = weeks_needed * 2  # 2 activities per module
        min_assessments_needed = max(1, weeks_needed // 3)  # 1 assessment per 3 modules

        # Check if we have enough components left
        if (
            available_modules < min_modules_needed
            or available_activities < min_activities_needed
            or available_assessments < min_assessments_needed
        ):
            return True

        # Check overall exhaustion rate
        total_components = (
            len(domain_modules) + len(domain_activities) + len(domain_assessments)
        )
        heavily_used_components = sum(
            1
            for count in self.component_usage_counts.values()
            if count >= MAX_USAGE_PER_COMPONENT
        )

        exhaustion_rate = (
            heavily_used_components / total_components if total_components > 0 else 1
        )

        # If more than 70% of components are heavily used, we're exhausting the library
        if exhaustion_rate > 0.7:
            return True

        return False

    def _get_component_diversity_score(self, components: dict[str, list]) -> float:
        """
        Calculate a diversity score for the selected components.
        Higher score = more diverse (less repetitive) combination.
        """

        score = 1.0

        # Penalize overused components
        for module in components["modules"]:
            usage = self.component_usage_counts.get(module["module_id"], 0)
            if usage > 0:
                score -= 0.1 * usage  # Penalty increases with usage

        for activity in components["activities"]:
            usage = self.component_usage_counts.get(activity["activity_id"], 0)
            if usage > 0:
                score -= 0.05 * usage

        for assessment in components["assessments"]:
            usage = self.component_usage_counts.get(assessment["assessment_id"], 0)
            if usage > 0:
                score -= 0.05 * usage

        return max(0.0, score)  # Don't go below 0

    def _calculate_max_usage_per_component(self) -> int:
        """
        Calculate reasonable max usage per component based on:
        - Total syllabi we want to generate
        - Number of components available per domain
        """

        # Estimate total syllabi across all templates and domains
        total_syllabi_target = 0
        for template_info in self.course_templates.values():
            total_syllabi_target += (
                len(template_info["domains"]) * 15
            )  # ~15 syllabi per domain

        # Average components per domain
        avg_modules_per_domain = (
            len(self.modules) // len(self.course_templates) // 4
        )  # 4 domains per template avg

        # Calculate max usage needed for modules (most constraining)
        # Each syllabus needs ~12 modules on average
        modules_needed_per_syllabus = 12
        total_module_uses_needed = total_syllabi_target * modules_needed_per_syllabus

        if avg_modules_per_domain > 0:
            max_usage_needed = total_module_uses_needed // (
                avg_modules_per_domain * len(self.course_templates) * 4
            )
            return max(3, min(max_usage_needed, 15))  # Between 3 and 15 uses max

        return 5  # Default fallback

    def select_components_for_course(
        self, requirements: dict, max_attempts: int = 5
    ) -> dict[str, list]:
        """Select appropriate components for the course requirements with diversity optimization"""

        # Check for component exhaustion first
        if self._check_component_exhaustion(requirements):
            raise RuntimeError(
                f"Component library exhausted for domain: {requirements['domain']}"
            )

        # Filter components by domain and availability
        MAX_USAGE_PER_COMPONENT = self._calculate_max_usage_per_component()

        available_modules = [
            m
            for m in self.modules
            if m["domain"] == requirements["domain"]
            and self.component_usage_counts.get(m["module_id"], 0)
            < MAX_USAGE_PER_COMPONENT
        ]
        available_activities = [
            a
            for a in self.activities
            if a["domain"] == requirements["domain"]
            and self.component_usage_counts.get(a["activity_id"], 0)
            < MAX_USAGE_PER_COMPONENT
        ]
        available_assessments = [
            a
            for a in self.assessments
            if a["domain"] == requirements["domain"]
            and self.component_usage_counts.get(a["assessment_id"], 0)
            < MAX_USAGE_PER_COMPONENT
        ]

        # Determine course length in weeks
        weeks_map = {"semester": 16, "quarter": 12, "6-week": 6, "intensive": 4}
        weeks_needed = weeks_map.get(requirements["duration"], 16)

        # Try multiple selections to find the most diverse combination
        best_components = None
        best_diversity_score = -1

        for _ in range(max_attempts):
            try:
                # Select modules for the course duration
                selected_modules = []
                if available_modules:
                    # Sort by week number and usage (prefer less used)
                    sorted_modules = sorted(
                        available_modules,
                        key=lambda x: (
                            x["week_number"],
                            self.component_usage_counts.get(x["module_id"], 0),
                        ),
                    )
                    selected_modules = sorted_modules[
                        : min(weeks_needed, len(sorted_modules))
                    ]

                # Select activities (2-3 per module)
                selected_activities = []
                if available_activities and selected_modules:
                    activities_per_module = 3
                    target_activity_count = (
                        len(selected_modules) * activities_per_module
                    )

                    # Prefer less used activities
                    sorted_activities = sorted(
                        available_activities,
                        key=lambda x: self.component_usage_counts.get(
                            x["activity_id"], 0
                        ),
                    )
                    selected_activities = sorted_activities[
                        : min(target_activity_count, len(sorted_activities))
                    ]

                # Select assessments (1 per 2-3 modules)
                selected_assessments = []
                if available_assessments and selected_modules:
                    assessment_count = max(1, len(selected_modules) // 3)

                    # Prefer less used assessments
                    sorted_assessments = sorted(
                        available_assessments,
                        key=lambda x: self.component_usage_counts.get(
                            x["assessment_id"], 0
                        ),
                    )
                    selected_assessments = sorted_assessments[
                        : min(assessment_count, len(sorted_assessments))
                    ]

                components = {
                    "modules": selected_modules,
                    "activities": selected_activities,
                    "assessments": selected_assessments,
                }

                # Check if this combination has been used before
                if self._is_component_combination_overused(components):
                    continue

                # Calculate diversity score
                diversity_score = self._get_component_diversity_score(components)

                if diversity_score > best_diversity_score:
                    best_diversity_score = diversity_score
                    best_components = components

                # If we found a very diverse combination, use it
                if diversity_score > 0.8:
                    break

            except Exception:
                continue

        if best_components is None:
            raise RuntimeError(
                f"Could not find viable component combination for {requirements['domain']}"
            )

        return best_components

    def assemble_complete_syllabus(
        self, requirements: dict, components: dict[str, list]
    ) -> str:
        """Use Claude to assemble components into a complete, realistic syllabus"""

        modules = components["modules"]
        activities = components["activities"]
        assessments = components["assessments"]

        # Create summaries for Claude
        modules_summary = []
        for module in modules[:10]:  # Limit to avoid token limits
            modules_summary.append(
                {
                    "week": module["week_number"],
                    "title": module["title"],
                    "description": module["description"][:200] + "...",
                    "key_concepts": module["key_concepts"][:3],
                    "learning_objectives": module["learning_objectives"][:2],
                }
            )

        activities_summary = []
        for activity in activities[:15]:  # Limit to avoid token limits
            activities_summary.append(
                {
                    "title": activity["title"],
                    "description": activity["description"],
                    "bloom_level": activity["bloom_level"],
                    "duration": activity["estimated_duration"],
                    "objectives": activity["learning_objectives"][:2],
                }
            )

        assessments_summary = []
        for assessment in assessments[:10]:  # Limit to avoid token limits
            assessments_summary.append(
                {
                    "title": assessment["title"],
                    "type": assessment["type"],
                    "description": assessment["description"],
                    "points": assessment["total_points"],
                    "objectives": assessment["learning_objectives_assessed"][:2],
                }
            )

        prompt = f"""Create a structured course syllabus focusing on educational content only, using the provided components.

COURSE REQUIREMENTS:
Title: {requirements["course_title"]}
Domain: {requirements["domain"]}
Level: {requirements["level"]}
Duration: {requirements["duration"]}

Course Description:
{requirements["course_description"]}

Learning Objectives:
{chr(10).join('• ' + obj for obj in requirements["learning_objectives"])}

Target Audience: {requirements["target_audience"]}
Prerequisites: {requirements["prerequisites"]}

AVAILABLE COMPONENTS TO USE:

WEEKLY MODULES:
{json.dumps(modules_summary, indent=2)}

LEARNING ACTIVITIES:
{json.dumps(activities_summary, indent=2)}

ASSESSMENTS:
{json.dumps(assessments_summary, indent=2)}

TASK: Create educational syllabus content that focuses on the academic structure and learning design.

REQUIRED SYLLABUS SECTIONS:
1. **Course Title and Description** (use provided requirements)
2. **Learning Objectives** (use provided objectives)
3. **Prerequisites and Target Audience** (use provided details)
4. **Weekly Schedule** (integrate modules with activities in logical sequence)
5. **Assessment Plan** (integrate provided assessments with grading breakdown)
6. **Required Materials** (textbooks, software, resources needed)
7. **Course Policies** (general academic policies like attendance, late work, academic integrity)

IMPORTANT RESTRICTIONS - DO NOT INCLUDE:
- Instructor names, emails, or contact information
- Specific classroom locations, room numbers, or meeting times
- University-specific details, dates, or semester information
- Office hours, phone numbers, or administrative details
- Specific institutional policies or procedures

Focus on creating reusable educational content that any institution could adapt. Use clean academic formatting and maintain professional tone."""

        try:
            response = self.client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
            )

            return response.content[0].text.strip()

        except Exception as e:
            print(f"Error assembling syllabus: {e}")
            raise e

    def assess_syllabus_quality(
        self, syllabus_content: str, requirements: dict
    ) -> float:
        """Simple quality check for generated syllabi"""
        word_count = len(syllabus_content.split())
        content_lower = syllabus_content.lower()

        # Essential elements check
        essential_keywords = ["learning objective", "assessment", "schedule"]
        found_keywords = sum(
            1 for keyword in essential_keywords if keyword in content_lower
        )

        if word_count >= 1000 and found_keywords >= 3:
            return 0.9
        elif word_count >= 600 and found_keywords >= 2:
            return 0.7
        else:
            return 0.4

    def generate_syllabus_dataset(
        self,
        samples_per_template: int = 50,
        filename: str = "syllabi_dataset.json",
        max_retries: int = 5,
    ) -> list[dict]:
        """Generate complete dataset of assembled syllabi"""

        print("Generating component-based syllabus dataset...")
        print("=" * 60)

        # Load existing syllabi if any
        existing_syllabi = self.load_existing_dataset(filename)
        self._load_tracking_from_existing_syllabi(existing_syllabi)

        # Track progress by domain and template
        generated_counts = {}
        for syllabus in existing_syllabi:
            key = f"{syllabus['course_requirements']['domain']}_{self._get_template_from_requirements(syllabus['course_requirements'])}"
            generated_counts[key] = generated_counts.get(key, 0) + 1

        all_syllabi = existing_syllabi.copy()
        seed = 42 + len(existing_syllabi)  # Continue from where we left off

        for template_type, template_info in self.course_templates.items():
            print(f"\nProcessing template: {template_type}")

            for domain in template_info["domains"]:
                key = f"{domain}_{template_type}"
                samples_for_domain = samples_per_template // len(
                    template_info["domains"]
                )
                already_generated = generated_counts.get(key, 0)
                remaining_needed = max(0, samples_for_domain - already_generated)

                if remaining_needed == 0:
                    print(
                        f"\t{domain}: Already complete ({already_generated}/{samples_for_domain})"
                    )
                    continue

                print(
                    f"\t{domain}: Need {remaining_needed} more (have {already_generated}/{samples_for_domain})"
                )

                domain_attempts = 0
                domain_successes = 0
                max_domain_attempts = remaining_needed * 3
                domain_exhausted = False

                while (
                    domain_successes < remaining_needed
                    and domain_attempts < max_domain_attempts
                    and not domain_exhausted
                ):
                    domain_attempts += 1

                    for retry in range(max_retries):
                        try:
                            total_generated = len(all_syllabi)
                            print(
                                f"\t\t[{total_generated + 1}] Generating: {domain} - {template_type} (attempt {retry+1})"
                            )

                            # Add retry variation to seed
                            retry_seed = seed + (retry * 1000) + domain_attempts

                            # Generate course requirements
                            requirements = self.generate_course_requirements(
                                template_type, domain, retry_seed
                            )

                            # Check for duplicate title
                            if self._is_duplicate_content(
                                requirements["course_title"],
                                requirements["course_description"],
                            ):
                                print(
                                    f"\t\t[{total_generated + 1}] Duplicate title detected, retrying..."
                                )
                                continue

                            time.sleep(self.rate_limit_delay)

                            # Select components
                            components = self.select_components_for_course(requirements)

                            # Check component combination diversity
                            diversity_score = self._get_component_diversity_score(
                                components
                            )
                            if (
                                diversity_score < 0.01
                            ):  # Skip low-diversity combinations
                                print(
                                    f"\t\t[{total_generated + 1}] Low diversity combination, retrying..."
                                )
                                continue

                            # Assemble syllabus
                            syllabus_content = self.assemble_complete_syllabus(
                                requirements, components
                            )

                            # Check for duplicate content
                            if self._is_duplicate_content(
                                requirements["course_title"], syllabus_content
                            ):
                                print(
                                    f"\t\t[{total_generated + 1}] Duplicate content detected, retrying..."
                                )
                                continue

                            # Assess quality
                            quality = self.assess_syllabus_quality(
                                syllabus_content, requirements
                            )

                            # Reject very low quality syllabi
                            if quality < 0.4:
                                print(
                                    f"\t\t[{total_generated + 1}] Low quality syllabus ({quality:.3f}), retrying..."
                                )
                                continue

                            # Success! Create the syllabus
                            assembled_syllabus = {
                                "course_requirements": requirements,
                                "selected_modules": components["modules"],
                                "selected_activities": components["activities"],
                                "selected_assessments": components["assessments"],
                                "syllabus_content": syllabus_content,
                                "quality_score": quality,
                                "generation_timestamp": datetime.now().isoformat(),
                            }

                            # Mark components as used and content as generated
                            self._mark_component_combination_used(components)
                            self._mark_content_generated(
                                requirements["course_title"], syllabus_content
                            )

                            # IMMEDIATELY save to file
                            self.append_syllabus_to_file(assembled_syllabus, filename)

                            all_syllabi.append(assembled_syllabus)
                            domain_successes += 1

                            print(
                                f"\t\t[{len(all_syllabi)}] ✅ SAVED: {requirements['course_title']} (Quality: {quality:.3f}, Diversity: {diversity_score:.3f})"
                            )

                            time.sleep(self.rate_limit_delay)
                            break  # Success, exit retry loop

                        except RuntimeError as e:
                            if "exhausted" in str(e):
                                print(
                                    f"\t\t[{len(all_syllabi)+1}] Component library exhausted for {domain} - stopping domain"
                                )
                                domain_exhausted = True
                                break
                            else:
                                print(
                                    f"\t\t[{len(all_syllabi)+1}] Error (attempt {retry+1}): {e}"
                                )
                                if retry == max_retries - 1:
                                    print(
                                        f"\t\t[{len(all_syllabi)+1}] Max retries reached for {domain}"
                                    )
                                else:
                                    time.sleep(self.rate_limit_delay * (retry + 1))
                        except Exception as e:
                            print(
                                f"\t\t[{len(all_syllabi)+1}] Error (attempt {retry+1}): {e}"
                            )
                            if retry == max_retries - 1:
                                print(
                                    f"\t\t[{len(all_syllabi)+1}] Max retries reached for {domain}"
                                )
                            else:
                                time.sleep(self.rate_limit_delay * (retry + 1))

                    seed += 1

                # Update counts
                final_count = already_generated + domain_successes
                completion_rate = (
                    final_count / samples_for_domain if samples_for_domain > 0 else 0
                )
                status = " (EXHAUSTED)" if domain_exhausted else ""
                print(
                    f"\t{domain} status: {final_count}/{samples_for_domain} ({completion_rate:.1%}){status}"
                )

        print("=" * 60)
        print(f"Generated {len(all_syllabi)} total syllabi (saved incrementally)")
        print(f"Dataset file: {self.output_dir / filename}")

        return all_syllabi

    def _deserialize_syllabus(self, data: dict) -> dict:
        """Convert JSON data back to syllabus dict object"""
        course_info = data["course_info"]
        requirements = {
            "course_title": course_info["title"],
            "domain": course_info["department"],
            "level": course_info["level"],
            "duration": course_info["duration"],
            "learning_objectives": course_info["learning_objectives"],
            "target_audience": course_info["target_audience"],
            "prerequisites": course_info["prerequisites"],
            "course_description": course_info["description"],
        }

        return {
            "course_requirements": requirements,
            "selected_modules": [],  # We don't need to reconstruct these for tracking
            "selected_activities": [],
            "selected_assessments": [],
            "syllabus_content": data["syllabus_template"],
            "quality_score": data["template_metadata"]["quality_score"],
            "generation_timestamp": data["template_metadata"]["last_updated"],
        }

    def load_existing_dataset(self, filename: str) -> list[dict]:
        """Load existing syllabi from file if it exists"""
        output_file = self.output_dir / filename
        if output_file.exists() and output_file.stat().st_size > 0:
            try:
                with open(output_file, encoding="utf-8") as f:
                    data = json.load(f)
                    if data:  # Check if data is not empty
                        syllabi = [self._deserialize_syllabus(item) for item in data]
                        print(f"Loaded {len(syllabi)} existing syllabi from {filename}")
                        return syllabi
            except Exception as e:
                print(f"Error loading existing dataset: {e}")
                return []
        return []

    def _load_tracking_from_existing_syllabi(self, syllabi: list[dict]):
        """Initialize tracking data from existing syllabi"""
        for syllabus in syllabi:
            # Mark titles and content as generated
            self._mark_content_generated(
                syllabus["course_requirements"]["course_title"],
                syllabus["syllabus_content"],
            )

    def append_syllabus_to_file(self, syllabus: dict, filename: str):
        """Append new syllabus to file immediately"""
        output_file = self.output_dir / filename

        # Load existing JSON data directly (don't deserialize)
        existing_data = []
        if output_file.exists() and output_file.stat().st_size > 0:
            try:
                with open(output_file, encoding="utf-8") as f:
                    existing_data = json.load(f)
            except Exception as e:
                print(f"Error loading existing data: {e}")
                existing_data = []

        # Convert new syllabus to JSON format
        course_title = syllabus["course_requirements"]["course_title"]
        template_id = f"TMPL_{hash(str(course_title)) % 10000:04d}"
        new_syllabus_data = {
            "course_template_id": template_id,
            "course_info": {
                "title": syllabus["course_requirements"]["course_title"],
                "department": syllabus["course_requirements"]["domain"],
                "level": syllabus["course_requirements"]["level"],
                "duration": syllabus["course_requirements"]["duration"],
                "description": syllabus["course_requirements"]["course_description"],
                "learning_objectives": syllabus["course_requirements"][
                    "learning_objectives"
                ],
                "prerequisites": syllabus["course_requirements"]["prerequisites"],
                "target_audience": syllabus["course_requirements"]["target_audience"],
            },
            "syllabus_template": syllabus["syllabus_content"],
            "component_refs": {
                "module_ids": [
                    module["module_id"] for module in syllabus["selected_modules"]
                ],
                "activity_ids": [
                    activity["activity_id"]
                    for activity in syllabus["selected_activities"]
                ],
                "assessment_ids": [
                    assessment["assessment_id"]
                    for assessment in syllabus["selected_assessments"]
                ],
            },
            "template_metadata": {
                "created_date": "2024-01-15",
                "last_updated": syllabus["generation_timestamp"].split("T")[0],
                "approval_status": "approved",
                "version": "1.0",
                "quality_score": syllabus["quality_score"],
                "component_counts": {
                    "modules": len(syllabus["selected_modules"]),
                    "activities": len(syllabus["selected_activities"]),
                    "assessments": len(syllabus["selected_assessments"]),
                },
            },
        }

        # Add to existing data
        existing_data.append(new_syllabus_data)

        # Save updated dataset
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)

    def save_syllabus_dataset(self, syllabi: list[dict], filename: str = None) -> None:
        """Save assembled syllabi dataset in realistic institutional format"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")

        if filename is None:
            filename = f"assembled_syllabi_dataset_{timestamp}.json"

        # Convert to realistic institutional database format
        dataset = []
        for syllabus in syllabi:
            # Create course template record
            course_title = syllabus["course_requirements"]["course_title"]
            template_id = f"TMPL_{hash(str(course_title)) % 10000:04d}"
            course_template = {
                "course_template_id": template_id,
                "course_info": {
                    "title": syllabus["course_requirements"]["course_title"],
                    "department": syllabus["course_requirements"]["domain"],
                    "level": syllabus["course_requirements"]["level"],
                    "duration": syllabus["course_requirements"]["duration"],
                    "description": syllabus["course_requirements"][
                        "course_description"
                    ],
                    "learning_objectives": syllabus["course_requirements"][
                        "learning_objectives"
                    ],
                    "prerequisites": syllabus["course_requirements"]["prerequisites"],
                    "target_audience": syllabus["course_requirements"][
                        "target_audience"
                    ],
                },
                "syllabus_template": syllabus["syllabus_content"],
                "component_refs": {
                    "module_ids": [
                        module["module_id"] for module in syllabus["selected_modules"]
                    ],
                    "activity_ids": [
                        activity["activity_id"]
                        for activity in syllabus["selected_activities"]
                    ],
                    "assessment_ids": [
                        assessment["assessment_id"]
                        for assessment in syllabus["selected_assessments"]
                    ],
                },
                "template_metadata": {
                    "created_date": "2024-01-15",
                    "last_updated": syllabus["generation_timestamp"].split("T")[0],
                    "approval_status": "approved",
                    "version": "1.0",
                    "quality_score": syllabus["quality_score"],
                    "component_counts": {
                        "modules": len(syllabus["selected_modules"]),
                        "activities": len(syllabus["selected_activities"]),
                        "assessments": len(syllabus["selected_assessments"]),
                    },
                },
            }

            dataset.append(course_template)

        # Save dataset
        output_file = self.output_dir / filename
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)

        print(f"\nDataset saved: {output_file}")
        print("Format: Institutional course templates with component references")
        print(f"Total course templates: {len(dataset)}")
        print(
            "Component data available in: data/components/ (activities, assessments, modules)"
        )

    def _get_template_from_requirements(self, requirements: dict) -> str:
        """Determine template type from requirements (for resume tracking)"""
        # Simple heuristic based on level and duration
        if requirements["level"] in ["undergraduate", "graduate"]:
            return "academic"
        elif requirements["level"] in ["associate", "professional", "expert"]:
            return "certification"
        else:
            return "professional"


def main() -> None:
    """Generate syllabi from pre-generated components"""

    import os

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not found!")
        return

    # Initialize generator
    generator = ComponentBasedSyllabusGenerator(api_key=api_key)

    # Load existing components (update filenames as needed)
    try:
        generator.load_components(
            activities_file="learning_activities_20250816_1408.json",  # Update with actual filename
            assessments_file="assessments_20250816_1408.json",  # Update with actual filename
            modules_file="modules_20250816_1408.json",  # Update with actual filename
        )
    except FileNotFoundError as e:
        print(f"Component files not found: {e}")
        print(
            "Please run generate_course_components.py first to generate component library"
        )
        return

    # Generate syllabus dataset
    generator.generate_syllabus_dataset(samples_per_template=60)

    print("\nComponent-based syllabus generation complete!")
    print("Ready for T5 training with realistic, component-assembled syllabi")


if __name__ == "__main__":
    main()
