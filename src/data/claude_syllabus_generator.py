"""
Claude API Synthetic Data Generation for MSc AI Project
======================================================

Automated course syllabus generation using Claude's API following the established
data model diagrams and dissertation methodology from docs/.
"""

import hashlib
import json
import os
import random
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, TypedDict

import anthropic

ANTHROPIC_MODEL = "claude-sonnet-4-20250514"


class BloomLevel(TypedDict):
    verbs: list[str]
    complexity: int


@dataclass
class CourseContext:
    """Matches the input data model from data-model-diagram.md"""

    course_title: str
    course_description: str
    learning_objectives: list[str]
    domain: str
    level: str
    duration: str
    prerequisites: str | None = None
    target_audience: str | None = None


@dataclass
class GeneratedSyllabus:
    """Complete generated syllabus following IEEE LOM compliance"""

    context: CourseContext
    syllabus_content: str
    structure_metadata: dict[str, Any]
    quality_score: float
    generation_timestamp: str


class ClaudeSyllabusGenerator:
    """
    Generates synthetic syllabus data using Claude API following the template-based
    approach defined in the data model diagrams and dissertation methodology.
    """

    def __init__(self, api_key: str, output_dir: str = "data/synthetic"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.rate_limit_delay = 2.0
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.generated_titles: set[str] = set()
        self.content_hashes: set[str] = set()

        self.educational_templates = {
            "university_courses": {
                "domains": [
                    "Computer Science",
                    "Data Science",
                    "Mathematics",
                    "Statistics",
                    "Physics",
                    "Engineering",
                    "Biology",
                    "Chemistry",
                ],
                "levels": ["undergraduate", "graduate"],
                "typical_features": [
                    "Academic rigor",
                    "Research components",
                    "Theoretical foundations",
                    "Peer review",
                    "Academic writing",
                    "Critical analysis",
                ],
                "assessment_types": [
                    "Examinations",
                    "Research papers",
                    "Lab reports",
                    "Group projects",
                    "Presentations",
                    "Problem sets",
                    "Term papers",
                    "Thesis defense",
                    "Peer review",
                    "Literature review",
                    "Data analysis projects",
                    "Academic poster sessions",
                ],
            },
            "corporate_training": {
                "domains": [
                    "Business Strategy",
                    "Data Analysis",
                    "Project Management",
                    "Leadership",
                    "Communication",
                    "Digital Marketing",
                    "Sales",
                    "Operations Management",
                    "Financial Planning",
                    "Human Resources",
                    "Supply Chain Management",
                    "Quality Management",
                    "Risk Management",
                    "Change Management",
                ],
                "levels": ["entry", "intermediate", "advanced", "executive"],
                "typical_features": [
                    "Practical application",
                    "ROI focus",
                    "Industry relevance",
                    "Case studies",
                    "Skills development",
                    "Performance metrics",
                ],
                "assessment_types": [
                    "Skills assessments",
                    "Case study analysis",
                    "Simulations",
                    "Portfolio development",
                    "Peer feedback",
                    "Manager evaluation",
                    "360-degree reviews",
                    "ROI analysis",
                    "Action learning projects",
                    "Business impact assessments",
                    "Capstone presentations",
                    "Competency evaluations",
                ],
            },
            "professional_development": {
                "domains": [
                    "Software Development",
                    "Design Thinking",
                    "Agile Methods",
                    "Technical Writing",
                    "Public Speaking",
                    "Networking",
                    "Data Visualization",
                    "Product Management",
                    "User Experience Design",
                    "Digital Transformation",
                    "Innovation Management",
                ],
                "levels": ["beginner", "intermediate", "expert"],
                "typical_features": [
                    "Hands-on practice",
                    "Portfolio building",
                    "Industry standards",
                    "Peer collaboration",
                    "Mentorship",
                    "Real projects",
                ],
                "assessment_types": [
                    "Portfolio reviews",
                    "Practical demonstrations",
                    "Peer assessments",
                    "Industry certifications",
                    "Project presentations",
                    "Code reviews",
                    "Design critiques",
                    "Sprint retrospectives",
                    "Client feedback",
                    "Professional showcases",
                    "Skill badges",
                    "Mentorship evaluations",
                ],
            },
            "certification_prep": {
                "domains": [
                    "AWS Cloud",
                    "PMP",
                    "Google Analytics",
                    "Salesforce",
                    "Cisco Networking",
                    "Microsoft Azure",
                    "CompTIA Security+",
                    "Oracle Database",
                    "VMware Virtualization",
                    "ITIL Service Management",
                ],
                "levels": ["associate", "professional", "expert"],
                "typical_features": [
                    "Exam focus",
                    "Practice tests",
                    "Industry alignment",
                    "Structured learning",
                    "Time management",
                    "Success metrics",
                ],
                "assessment_types": [
                    "Practice examinations",
                    "Mock tests",
                    "Diagnostic assessments",
                    "Timed exercises",
                    "Certification simulations",
                    "Adaptive testing",
                    "Performance analytics",
                    "Knowledge gap analysis",
                    "Readiness assessments",
                    "Final certification exam",
                    "Practical labs",
                    "Scenario-based testing",
                ],
            },
        }

        self.blooms_taxonomy: dict[str, BloomLevel] = {
            "remember": {
                "verbs": [
                    "identify",
                    "list",
                    "recognize",
                    "recall",
                    "define",
                    "describe",
                ],
                "complexity": 1,
            },
            "understand": {
                "verbs": ["explain", "summarize", "interpret", "classify", "compare"],
                "complexity": 2,
            },
            "apply": {
                "verbs": ["solve", "demonstrate", "calculate", "implement", "use"],
                "complexity": 3,
            },
            "analyze": {
                "verbs": [
                    "examine",
                    "breakdown",
                    "differentiate",
                    "investigate",
                    "categorize",
                ],
                "complexity": 4,
            },
            "evaluate": {
                "verbs": ["assess", "critique", "judge", "validate", "defend"],
                "complexity": 5,
            },
            "create": {
                "verbs": ["design", "develop", "construct", "formulate", "compose"],
                "complexity": 6,
            },
        }

        self.credential_context = {
            "university_courses": "PhD credentials and academic titles (Dr./Prof.)",
            "corporate_training": "MBA, CPA, PMP, Six Sigma, or industry certifications",
            "professional_development": "Industry expertise, senior roles, or specialized certifications",
            "certification_prep": "Relevant certification expertise and training credentials",
        }

        self.institution_context = {
            "university_courses": "realistic university or college names",
            "corporate_training": "corporate training institutes or business academies",
            "professional_development": "professional development centers or skills academies",
            "certification_prep": "certification training centers or exam preparation institutes",
        }

        self.prompt_variations = [
            "Create a comprehensive, professional course syllabus following educational standards.",
            "Develop a detailed academic syllabus that meets institutional requirements.",
            "Design a complete course outline with professional educational components.",
            "Construct a thorough syllabus document following best practices.",
            "Generate a well-structured course syllabus with academic rigor.",
        ]

    def generate_course_context(
        self, template_type: str, domain: str, seed: int
    ) -> CourseContext:
        """Generate course context using template-based approach"""

        template_info = self.educational_templates[template_type]

        random.seed(seed)

        level = random.choice(template_info["levels"])
        features = random.sample(template_info["typical_features"], 3)
        assessment_types = random.sample(template_info["assessment_types"], 2)

        prompt = f"""Generate a comprehensive course context for {template_type.replace('_', ' ')} in {domain} domain at {level} level.

EDUCATIONAL FRAMEWORK REQUIREMENTS:
- Template Type: {template_type.replace('_', ' ').title()}
- Domain: {domain}
- Level: {level}
- Key Features: {', '.join(features)}
- Assessment Style: {', '.join(assessment_types)}

BLOOM'S TAXONOMY PROGRESSION (CRITICAL FOR TRAINING DATA):
Create exactly 4 learning objectives that demonstrate clear cognitive progression:
1. Remember/Understand level: "Students will identify/explain/describe..."
2. Apply level: "Students will demonstrate/implement/solve..."
3. Analyze/Evaluate level: "Students will analyze/assess/critique..."
4. Create/Synthesize level: "Students will design/develop/construct..."

EDUCATIONAL STANDARDS COMPLIANCE:
- Follow IEEE Learning Object Metadata (LOM) structure
- Ensure pedagogical coherence between objectives and content
- Include realistic prerequisites that build proper knowledge scaffolding
- Target audience must reflect appropriate entry-level competencies

CONTENT DEPTH REQUIREMENTS:
- Course description: 300-400 words with specific domain terminology
- Include concrete learning activities and assessment methods
- Reference real-world applications and industry relevance
- Mention specific tools, technologies, or methodologies

OUTPUT FORMAT (JSON only):
{{
    "course_title": "Specific, realistic course title reflecting domain and level",
    "course_description": "Comprehensive 300-400 word description with domain-specific terminology, learning methods, assessment approaches, and real-world applications",
    "learning_objectives": [
        "Students will [Remember/Understand verb] [specific domain knowledge] [context/application]",
        "Students will [Apply verb] [domain skills/methods] to [specific scenarios/problems]",
        "Students will [Analyze/Evaluate verb] [complex domain concepts] using [analytical methods/frameworks]",
        "Students will [Create/Synthesize verb] [advanced outcomes/solutions] by [integration/innovation methods]"
    ],
    "prerequisites": "Detailed prerequisites with specific course names, competencies, or experience requirements",
    "target_audience": "Specific description of intended learners including background, career stage, and learning goals"
}}

QUALITY VALIDATION:
- Ensure domain terminology accuracy and professional authenticity
- Verify logical progression from prerequisites through objectives
- Confirm assessment alignment with learning outcomes
- Validate realistic institutional and professional context"""

        try:
            response = self.client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text.strip()

            json_start = content.find("{")
            json_end = content.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in Claude response")

            json_content = content[json_start:json_end]
            context_data = json.loads(json_content)

            return CourseContext(
                course_title=context_data["course_title"],
                course_description=context_data["course_description"],
                learning_objectives=context_data["learning_objectives"],
                domain=domain,
                level=level,
                duration=random.choice(["semester", "quarter", "6-week", "intensive"]),
                prerequisites=context_data.get("prerequisites"),
                target_audience=context_data.get("target_audience"),
            )

        except Exception as e:
            print(f"Error generating context for {domain}: {e}")
            raise e

    def generate_syllabus_content(
        self, context: CourseContext, template_type: str, seed: int
    ) -> str:
        """Generate complete syllabus content from course context with enhanced diversity"""

        template_info = self.educational_templates[template_type]

        random.seed(seed + 1000)
        assessment_plan = random.choice(template_info["assessment_types"])

        credential_hint = self.credential_context[template_type]
        institution_hint = self.institution_context[template_type]

        base_prompt = random.choice(self.prompt_variations)

        prompt = f"""{base_prompt} Ensure consistent structure and educational authenticity for neural network training data.

COURSE CONTEXT:
Title: {context.course_title}
Domain: {context.domain}
Level: {context.level}
Duration: {context.duration}
Template: {template_type.replace('_', ' ').title()}

COURSE DESCRIPTION:
{context.course_description}

LEARNING OBJECTIVES (Bloom's Taxonomy Aligned):
{chr(10).join('• ' + obj for obj in context.learning_objectives)}

PREREQUISITES: {context.prerequisites}
TARGET AUDIENCE: {context.target_audience}

INSTRUCTOR & INSTITUTION GENERATION:
- Create realistic instructor name with appropriate {credential_hint}
- Generate fitting institution name ({institution_hint})
- Design logical course code for {context.domain} at {context.level} level
- Include professional email, office hours, and contact information
- Add realistic office location and meeting times

MANDATORY SYLLABUS STRUCTURE (for neural training consistency):
1. **Course Information Section**
   - Course code, title, credits (appropriate for level)
   - Meeting times, location, format specification
   - Instructor details (name, credentials, contact, office hours)
   - Prerequisites and learning outcomes alignment

2. **Detailed Weekly Schedule Section**
   - Adapt to {context.duration} format with logical progression
   - Week-by-week topics showing pedagogical sequencing
   - Include readings, assignments, and milestone dates
   - Show clear connection between weeks and learning objectives
   - End-of-week deliverables or assessments

3. **Assessment and Grading Section**
   - Comprehensive grading breakdown (must total exactly 100%)
   - Primary assessment: {assessment_plan}
   - Include rubrics or evaluation criteria
   - Clear due dates and submission guidelines
   - Grade distribution policy and scale

4. **Learning Resources Section**
   - Required textbooks with specific editions and authors
   - Technology requirements (software, hardware, platforms)
   - Supplementary materials and online resources
   - Library and research database access

5. **Course Policies Section**
   - Attendance and participation requirements
   - Late work and makeup examination policies
   - Academic integrity and plagiarism guidelines
   - Accessibility accommodations and support services
   - Communication protocols and response times

EDUCATIONAL QUALITY REQUIREMENTS:
- Demonstrate clear pedagogical progression in weekly topics
- Align assessments with specific learning objectives
- Include domain-specific terminology and industry relevance
- Reference current tools, methodologies, and best practices
- Maintain professional academic tone throughout
- Ensure realistic workload and time management

STRUCTURAL CONSISTENCY REQUIREMENTS:
- Use identical markdown formatting across all sections
- Maintain consistent heading hierarchy (##, ###, etc.)
- Apply uniform bullet point styles and numbering
- Keep section ordering exactly as specified above
- Include all mandatory subsections within each main section

FORMAT SPECIFICATIONS:
- Professional markdown with clear section headers
- Target length: 1200-1800 words for comprehensive coverage
- Include realistic details: specific dates, times, room numbers
- Use appropriate academic calendar references (Fall 2024, Spring 2025)
- Maintain consistency with {template_type.replace('_', ' ')} context and institutional standards"""

        try:
            response = self.client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
            )

            return str(response.content[0].text.strip())

        except Exception as e:
            print(f"Error generating syllabus for {context.course_title}: {e}")
            raise e

    def _is_duplicate_content(self, title: str, content: str) -> bool:
        """Check if content is a duplicate based on title and content hash"""
        # Check title uniqueness
        if title.lower() in self.generated_titles:
            return True

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

    def assess_syllabus_quality(
        self, syllabus_content: str, context: CourseContext
    ) -> float:
        """Rule-based quality assessment using educational standards"""

        score = 0.0
        content_lower = syllabus_content.lower()

        # IEEE LOM structure compliance (0.3)
        if "course information" in content_lower:
            score += 0.05
        if "learning objective" in content_lower or "learning outcome" in content_lower:
            score += 0.1
        if "schedule" in content_lower and (
            "week" in content_lower or "session" in content_lower
        ):
            score += 0.1
        if "assessment" in content_lower or "grading" in content_lower:
            score += 0.05

        # Bloom's taxonomy progression (0.2)
        bloom_verbs_found = 0
        for level_data in self.blooms_taxonomy.values():
            for verb in level_data["verbs"]:
                if verb in content_lower:
                    bloom_verbs_found += 1
                    break
        if bloom_verbs_found >= 3:
            score += 0.2
        elif bloom_verbs_found >= 2:
            score += 0.1

        # Content comprehensiveness (0.2)
        word_count = len(syllabus_content.split())
        if 1000 <= word_count <= 2000:
            score += 0.2
        elif 800 <= word_count < 1000:
            score += 0.1

        # Educational policies and standards (0.15)
        if any(
            policy in content_lower
            for policy in ["policy", "academic integrity", "attendance"]
        ):
            score += 0.05
        if "accessibility" in content_lower or "accommodation" in content_lower:
            score += 0.05
        if "resource" in content_lower or "material" in content_lower:
            score += 0.05

        # Domain relevance (0.15)
        domain_terms = context.domain.lower().split()
        domain_mentions = sum(1 for term in domain_terms if term in content_lower)
        if domain_mentions >= 2:
            score += 0.15
        elif domain_mentions >= 1:
            score += 0.1

        return min(score, 1.0)

    def extract_structure_metadata(self, syllabus_content: str) -> dict[str, Any]:
        """Extract structural metadata following IEEE LOM compliance"""

        lines = syllabus_content.split("\n")

        return {
            "word_count": len(syllabus_content.split()),
            "line_count": len(lines),
            "section_count": len([line for line in lines if line.startswith("#")]),
            "has_schedule": any(
                "week" in line.lower() or "session" in line.lower() for line in lines
            ),
            "has_assessment_plan": any(
                "assessment" in line.lower() or "grading" in line.lower()
                for line in lines
            ),
            "has_learning_objectives": any(
                "objective" in line.lower() or "outcome" in line.lower()
                for line in lines
            ),
            "has_policies": any("policy" in line.lower() for line in lines),
            "has_resources": any(
                "resource" in line.lower() or "material" in line.lower()
                for line in lines
            ),
            "bloom_taxonomy_coverage": self._analyze_bloom_coverage(syllabus_content),
        }

    def _analyze_bloom_coverage(self, content: str) -> dict[str, bool]:
        """Analyze Bloom's taxonomy coverage in the syllabus"""

        content_lower = content.lower()
        coverage = {}

        for level, data in self.blooms_taxonomy.items():
            coverage[level] = any(verb in content_lower for verb in data["verbs"])

        return coverage

    def generate_dataset_batch(
        self, template_type: str, count: int, start_seed: int = 0, max_retries: int = 5
    ) -> list[GeneratedSyllabus]:
        """Generate batch of syllabi for specific template type with duplicate detection"""

        template_info = self.educational_templates[template_type]
        domains = template_info["domains"]

        print(f"Generating {count} syllabi for {template_type}...")

        syllabi: list[GeneratedSyllabus] = []
        i = 0
        attempts = 0
        max_attempts = count * 3  # Prevent infinite loops

        while len(syllabi) < count and attempts < max_attempts:
            current_seed = start_seed + i
            domain = domains[i % len(domains)]
            attempts += 1

            for retry in range(max_retries):
                try:
                    print(
                        f"\t[{len(syllabi)+1}/{count}] Generating context for {domain}... (attempt {retry+1})"
                    )

                    # Add retry variation to seed to get different content
                    retry_seed = current_seed + (retry * 1000)
                    context = self.generate_course_context(
                        template_type, domain, retry_seed
                    )

                    # Check for duplicate title
                    if self._is_duplicate_content(
                        context.course_title, context.course_description
                    ):
                        print(
                            f"\t[{len(syllabi)+1}/{count}] Duplicate title detected, retrying..."
                        )
                        continue

                    time.sleep(self.rate_limit_delay)

                    print(
                        f"\t[{len(syllabi)+1}/{count}] Generating syllabus content..."
                    )

                    syllabus_content = self.generate_syllabus_content(
                        context, template_type, retry_seed
                    )

                    # Check for duplicate content
                    if self._is_duplicate_content(
                        context.course_title, syllabus_content
                    ):
                        print(
                            f"\t[{len(syllabi)+1}/{count}] Duplicate content detected, retrying..."
                        )
                        continue

                    quality_score = self.assess_syllabus_quality(
                        syllabus_content, context
                    )
                    metadata = self.extract_structure_metadata(syllabus_content)

                    syllabus = GeneratedSyllabus(
                        context=context,
                        syllabus_content=syllabus_content,
                        structure_metadata=metadata,
                        quality_score=quality_score,
                        generation_timestamp=datetime.now().isoformat(),
                    )

                    # Mark as generated to prevent future duplicates
                    self._mark_content_generated(context.course_title, syllabus_content)
                    syllabi.append(syllabus)

                    print(
                        f"\t[{len(syllabi)}/{count}] Generated (Quality: {quality_score:.3f})"
                    )

                    time.sleep(self.rate_limit_delay)
                    break  # Success, exit retry loop

                except Exception as e:
                    print(
                        f"\t[{len(syllabi)+1}/{count}] Error (attempt {retry+1}): {e}"
                    )
                    if retry == max_retries - 1:
                        print(
                            f"\t[{len(syllabi)+1}/{count}] Max retries reached, skipping..."
                        )
                    else:
                        time.sleep(
                            self.rate_limit_delay * (retry + 1)
                        )  # Exponential backoff

            i += 1

        print(
            f"Completed {template_type}: {len(syllabi)}/{count} syllabi generated ({attempts} total attempts)"
        )
        return syllabi

    def generate_dataset_batch_with_domains(
        self,
        template_type: str,
        count: int,
        start_seed: int = 0,
        domain_subset: list[str] | None = None,
        max_retries: int = 3,
    ) -> list[GeneratedSyllabus]:
        """Generate batch with specific domain subset for tiered approach"""

        template_info = self.educational_templates[template_type]
        domains = domain_subset if domain_subset else template_info["domains"]

        print(
            f"Generating {count} syllabi for {template_type} (using {len(domains)} domains)..."
        )
        print(f"Target domains: {', '.join(domains)}")

        syllabi: list[GeneratedSyllabus] = []
        i = 0
        attempts = 0
        max_attempts = count * 3  # Prevent infinite loops

        while len(syllabi) < count and attempts < max_attempts:
            current_seed = start_seed + i
            domain = domains[i % len(domains)]
            attempts += 1

            for retry in range(max_retries):
                try:
                    print(
                        f"\t[{len(syllabi)+1}/{count}] Generating context for {domain}... (attempt {retry+1})"
                    )

                    # Add retry variation to seed to get different content
                    retry_seed = current_seed + (retry * 1000)
                    context = self.generate_course_context(
                        template_type, domain, retry_seed
                    )

                    # Check for duplicate title
                    if self._is_duplicate_content(
                        context.course_title, context.course_description
                    ):
                        print(
                            f"\t[{len(syllabi)+1}/{count}] Duplicate title detected, retrying..."
                        )
                        continue

                    time.sleep(self.rate_limit_delay)

                    print(
                        f"\t[{len(syllabi)+1}/{count}] Generating syllabus content..."
                    )

                    syllabus_content = self.generate_syllabus_content(
                        context, template_type, retry_seed
                    )

                    # Check for duplicate content
                    if self._is_duplicate_content(
                        context.course_title, syllabus_content
                    ):
                        print(
                            f"\t[{len(syllabi)+1}/{count}] Duplicate content detected, retrying..."
                        )
                        continue

                    quality_score = self.assess_syllabus_quality(
                        syllabus_content, context
                    )
                    metadata = self.extract_structure_metadata(syllabus_content)

                    syllabus = GeneratedSyllabus(
                        context=context,
                        syllabus_content=syllabus_content,
                        structure_metadata=metadata,
                        quality_score=quality_score,
                        generation_timestamp=datetime.now().isoformat(),
                    )

                    # Mark as generated to prevent future duplicates
                    self._mark_content_generated(context.course_title, syllabus_content)
                    syllabi.append(syllabus)

                    print(
                        f"\t[{len(syllabi)}/{count}] Generated (Quality: {quality_score:.3f})"
                    )

                    time.sleep(self.rate_limit_delay)
                    break  # Success, exit retry loop

                except Exception as e:
                    print(
                        f"\t[{len(syllabi)+1}/{count}] Error (attempt {retry+1}): {e}"
                    )
                    if retry == max_retries - 1:
                        print(
                            f"\t[{len(syllabi)+1}/{count}] Max retries reached, skipping..."
                        )
                    else:
                        time.sleep(
                            self.rate_limit_delay * (retry + 1)
                        )  # Exponential backoff

            i += 1

        print(
            f"Completed {template_type}: {len(syllabi)}/{count} syllabi generated ({attempts} total attempts)"
        )
        return syllabi

    def generate_complete_dataset(
        self, total_syllabi: int = 4000
    ) -> list[GeneratedSyllabus]:
        """
        Generate complete training dataset following the methodology from
        Section 4.4.2: Training Data Generation Methodology
        """

        print("=" * 70)
        print("CLAUDE API SYNTHETIC DATA GENERATION")
        print("Following MSc AI Project Methodology")
        print("=" * 70)

        start_time = time.time()

        template_distribution = {
            "university_courses": 800,
            "corporate_training": 1400,
            "professional_development": 1100,
            "certification_prep": 700,
        }

        total_expected = sum(template_distribution.values())
        print(f"Target: {total_expected:,} syllabi across 4 template types")
        print(f"Estimated time: {(total_expected * 5) / 60:.1f} minutes")
        print(f"Estimated cost: ${total_expected * 0.024:.2f}")
        print("=" * 70)

        all_syllabi = []
        current_seed = 42

        total_generated = 0

        for i, (template_type, count) in enumerate(template_distribution.items(), 1):
            if count == 0:
                continue

            print(f"\n[{i}/4] {template_type.upper().replace('_', ' ')}")
            print(f"Target: {count:,} samples (~100 per domain)")

            batch_start = time.time()

            batch_syllabi = self.generate_dataset_batch(
                template_type=template_type, count=count, start_seed=current_seed
            )

            batch_time = time.time() - batch_start
            total_generated += len(batch_syllabi)
            progress_pct = (total_generated / total_expected) * 100
            elapsed_total = time.time() - start_time
            eta_seconds = (
                (elapsed_total / total_generated * (total_expected - total_generated))
                if total_generated > 0
                else 0
            )

            print(
                f"Completed: {len(batch_syllabi):,}/{count:,} in {batch_time/60:.1f} minutes"
            )
            print(
                f"Overall Progress: {total_generated:,}/{total_expected:,} ({progress_pct:.1f}%)"
            )
            print(f"ETA: {eta_seconds/60:.1f} minutes remaining")

            all_syllabi.extend(batch_syllabi)
            current_seed += count

            self._save_batch_results(template_type, batch_syllabi)

        end_time = time.time()
        duration_minutes = (end_time - start_time) / 60

        print("\n" + "=" * 70)
        print("GENERATION COMPLETE")
        print("=" * 70)
        print(f"Total syllabi generated: {len(all_syllabi):,}")
        print(f"Total duration: {duration_minutes:.1f} minutes")
        print(f"Data saved to: {self.output_dir}")
        print(f"Estimated actual cost: ${len(all_syllabi) * 0.024:.2f}")

        if all_syllabi:
            avg_quality = sum(s.quality_score for s in all_syllabi) / len(all_syllabi)
            high_quality = sum(1 for s in all_syllabi if s.quality_score >= 0.8)
            print(f"Average quality score: {avg_quality:.3f}")
            print(
                f"High quality samples: {high_quality:,} ({high_quality/len(all_syllabi)*100:.1f}%)"
            )

        print("=" * 70)
        return all_syllabi

    def _save_batch_results(
        self, template_type: str, syllabi: list[GeneratedSyllabus]
    ) -> None:
        """Save intermediate batch results with timestamp"""

        timestamp = datetime.now().strftime("%d-%m-%y_%H%M")
        batch_data = [asdict(syllabus) for syllabus in syllabi]
        batch_file = self.output_dir / f"{template_type}_batch_{timestamp}.json"

        with open(batch_file, "w", encoding="utf-8") as f:
            json.dump(batch_data, f, indent=2, ensure_ascii=False)

        print(f"\tBatch saved: {batch_file}")

    def save_complete_dataset(self, syllabi: list[GeneratedSyllabus]) -> None:
        """Save complete dataset with train/validation/test splits with timestamps"""

        print("\nSaving complete dataset...")

        timestamp = datetime.now().strftime("%d-%m-%y_%H%M")
        dataset = [asdict(syllabus) for syllabus in syllabi]
        random.shuffle(dataset)
        train_size = int(0.7 * len(dataset))
        val_size = int(0.15 * len(dataset))

        splits = {
            "train": dataset[:train_size],
            "validation": dataset[train_size : train_size + val_size],
            "test": dataset[train_size + val_size :],
        }

        # Save complete dataset with timestamp
        complete_file = (
            self.output_dir / f"claude_generated_syllabi_complete_{timestamp}.json"
        )
        with open(complete_file, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)

        # Save splits with timestamps
        for split_name, split_data in splits.items():
            split_file = self.output_dir / f"{split_name}_data_{timestamp}.json"
            with open(split_file, "w", encoding="utf-8") as f:
                json.dump(split_data, f, indent=2, ensure_ascii=False)

        self._save_dataset_statistics(syllabi, timestamp)

        print("Dataset saved successfully!")
        print(f"\tTotal: {len(dataset)} syllabi")
        print(f"\tTrain: {len(splits['train'])}")
        print(f"\tValidation: {len(splits['validation'])}")
        print(f"\tTest: {len(splits['test'])}")
        print(f"\tTimestamp: {timestamp}")

    def _save_dataset_statistics(
        self, syllabi: list[GeneratedSyllabus], timestamp: str
    ) -> None:
        """Generate comprehensive dataset statistics with timestamp"""

        stats: dict[str, Any] = {
            "generation_info": {
                "total_syllabi": len(syllabi),
                "generation_date": datetime.now().isoformat(),
                "model_used": ANTHROPIC_MODEL,
                "methodology": "Template-based generation following MSc AI project data model",
            },
            "template_distribution": {},
            "domain_distribution": {},
            "quality_metrics": {
                "average_quality_score": 0,
                "quality_distribution": {"high": 0, "medium": 0, "low": 0},
            },
            "content_analysis": {
                "average_word_count": 0,
                "bloom_taxonomy_coverage": {},
                "standards_compliance_rate": 0,
            },
        }

        quality_scores = []
        word_counts = []

        for syllabus in syllabi:
            template_type = self._infer_template_type(syllabus.context)
            stats["template_distribution"][template_type] = (
                stats["template_distribution"].get(template_type, 0) + 1
            )

            domain = syllabus.context.domain
            stats["domain_distribution"][domain] = (
                stats["domain_distribution"].get(domain, 0) + 1
            )

            quality_scores.append(syllabus.quality_score)
            if syllabus.quality_score >= 0.8:
                stats["quality_metrics"]["quality_distribution"]["high"] += 1
            elif syllabus.quality_score >= 0.6:
                stats["quality_metrics"]["quality_distribution"]["medium"] += 1
            else:
                stats["quality_metrics"]["quality_distribution"]["low"] += 1

            word_counts.append(syllabus.structure_metadata["word_count"])

        stats["quality_metrics"]["average_quality_score"] = sum(quality_scores) / len(
            quality_scores
        )
        stats["content_analysis"]["average_word_count"] = sum(word_counts) / len(
            word_counts
        )
        stats["content_analysis"]["standards_compliance_rate"] = len(
            [s for s in syllabi if s.quality_score >= 0.7]
        ) / len(syllabi)

        # Save statistics with timestamp
        stats_file = self.output_dir / f"dataset_statistics_{timestamp}.json"
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)

        print("\nDataset Statistics:")
        print(
            f"\tQuality Score: {stats['quality_metrics']['average_quality_score']:.3f}"
        )
        print(f"\tWord Count: {stats['content_analysis']['average_word_count']:.0f}")
        print(
            f"\tCompliance Rate: {stats['content_analysis']['standards_compliance_rate']:.1%}"
        )
        print(f"\tStatistics: {stats_file}")

    def _infer_template_type(self, context: CourseContext) -> str:
        """Infer template type from context characteristics"""

        domain_lower = context.domain.lower()
        description_lower = context.course_description.lower()

        if any(
            term in domain_lower
            for term in ["computer science", "mathematics", "physics", "engineering"]
        ):
            return "university_courses"
        elif any(
            term in description_lower
            for term in ["business", "corporate", "management", "leadership"]
        ):
            return "corporate_training"
        elif any(
            term in description_lower
            for term in ["certification", "exam", "aws", "google", "microsoft"]
        ):
            return "certification_prep"
        else:
            return "professional_development"


def main() -> None:
    """Main execution function"""

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not found!")
        return

    print("Starting Claude-powered synthetic data generation...")
    print("Following MSc AI project methodology and data model")

    generator = ClaudeSyllabusGenerator(api_key=api_key)
    total_syllabi = 4000

    try:
        syllabi = generator.generate_complete_dataset(total_syllabi)
        generator.save_complete_dataset(syllabi)

        print("\nSUCCESS: Synthetic dataset generation complete!")
        print(
            f"Ready for neural network training with {len(syllabi)} realistic syllabi"
        )

    except KeyboardInterrupt:
        print("\nGeneration interrupted by user")
    except Exception as e:
        print(f"\nError in generation pipeline: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
