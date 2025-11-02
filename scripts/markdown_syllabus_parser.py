#!/usr/bin/env python3
"""
Markdown Syllabus Parser

Converts model-generated markdown (with indices) to structured JSON (with UUIDs).
Parser receives the same rag_context that model saw to ensure indices map correctly.
"""

import json
import re
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ParseResult:
    """Result of parsing markdown to JSON."""

    success: bool
    syllabus: Optional[Dict]
    errors: List[str]
    warnings: List[str]


class MarkdownSyllabusParser:
    """
    Parse markdown syllabus with indices to JSON with UUIDs.

    Handles:
    - Multiple markdown formatting variations
    - Missing sections (graceful degradation)
    - Invalid indices (skip and warn)
    - Fuzzy index extraction (multiple patterns)
    """

    def parse(self, markdown: str, rag_context: Dict) -> ParseResult:
        """
        Main parsing method.

        Args:
            markdown: Model output with [index] tags
            rag_context: Same context model saw (available_modules, etc.)

        Returns:
            ParseResult with success status, syllabus JSON, and any errors/warnings
        """
        errors = []
        warnings = []

        try:
            # Extract course info
            course_info = self._extract_course_info(markdown)
            if not course_info.get("title"):
                warnings.append("Missing course title")

            # Extract learning objectives
            objectives = self._extract_objectives(markdown)
            if not objectives:
                warnings.append("No learning objectives found")

            # Extract component indices
            # Try new format first (## Module Sequence), fallback to old format
            module_indices = self._extract_module_sequence(markdown)
            if not module_indices:
                module_indices = self._extract_section_indices(
                    markdown, "## Selected Modules"
                )

            activity_indices = self._extract_section_indices(
                markdown, "## Selected Activities"
            )
            assessment_indices = self._extract_section_indices(
                markdown, "## Selected Assessments"
            )

            # Convert indices to UUIDs
            modules = self._indices_to_uuids(
                module_indices,
                rag_context.get("available_modules", []),
                "modules",
                warnings,
            )

            activities = self._indices_to_uuids(
                activity_indices,
                rag_context.get("available_activities", []),
                "activities",
                warnings,
            )

            assessments = self._indices_to_uuids(
                assessment_indices,
                rag_context.get("available_assessments", []),
                "assessments",
                warnings,
            )

            # Build final JSON
            syllabus = {
                "course_info": course_info,
                "learning_objectives": objectives,
                "modules": modules,  # List of UUIDs
                "activities": activities,  # List of UUIDs
                "assessments": assessments,  # List of UUIDs
            }

            # Validate minimum requirements
            if not modules and not activities:
                warnings.append("No modules or activities selected")

            success = len(errors) == 0

            return ParseResult(
                success=success, syllabus=syllabus, errors=errors, warnings=warnings
            )

        except Exception as e:
            errors.append(f"Parsing failed: {str(e)}")
            return ParseResult(
                success=False, syllabus=None, errors=errors, warnings=warnings
            )

    def _extract_course_info(self, markdown: str) -> Dict:
        """Extract course info from markdown header."""
        info = {}

        # Title: # Course: Title
        title_match = re.search(r"# Course:\s*(.+)$", markdown, re.MULTILINE)
        if title_match:
            info["title"] = title_match.group(1).strip()

        # Domain: **Domain:** value
        domain_match = re.search(r"\*\*Domain:\*\*\s*(.+)$", markdown, re.MULTILINE)
        if domain_match:
            info["domain"] = domain_match.group(1).strip()

        # Level: **Level:** value
        level_match = re.search(r"\*\*Level:\*\*\s*(.+)$", markdown, re.MULTILINE)
        if level_match:
            info["level"] = level_match.group(1).strip()

        # Duration: **Duration:** value
        duration_match = re.search(r"\*\*Duration:\*\*\s*(.+)$", markdown, re.MULTILINE)
        if duration_match:
            info["duration"] = duration_match.group(1).strip()

        return info

    def _extract_objectives(self, markdown: str) -> List[str]:
        """Extract learning objectives from markdown."""
        objectives = []

        # Find ## Learning Objectives section
        section_match = re.search(
            r"## Learning Objectives\s*\n(.*?)(?=\n##|\Z)", markdown, re.DOTALL
        )

        if section_match:
            section_text = section_match.group(1)

            # Extract bullet points: - Objective
            bullets = re.findall(r"^\s*[-*]\s+(.+)$", section_text, re.MULTILINE)
            objectives.extend(bullets)

        return objectives

    def _extract_module_sequence(self, markdown: str) -> List[int]:
        """
        Extract module indices from sequenced format.

        Expected format:
            ## Module Sequence

            ### Weeks 1-2: Python Basics (8 hours)
            [0] This module explores...

        Returns:
            List of module indices in sequence order
        """
        section_match = re.search(
            r"## Module Sequence\n+(.*?)(?=\n## |\Z)", markdown, re.DOTALL
        )

        if section_match:
            section_text = section_match.group(1)
        else:
            section_text = markdown

        indices = []
        subsection_pattern = r"###\s+Week[^\n]+\n\s*\[(\d+)\]"
        matches = re.findall(subsection_pattern, section_text)

        for idx_str in matches:
            indices.append(int(idx_str))

        return indices

    def _extract_section_indices(self, markdown: str, section_header: str) -> List[int]:
        """
        Extract indices from a section like '## Selected Modules'.

        Supports multiple formats:
        - [0], [1], [2]
        - [0] [1] [2]
        - [0]\n[1]\n[2]

        Uses fuzzy matching for robustness.
        """
        # Find section
        section_pattern = rf"{re.escape(section_header)}\s*\n(.*?)(?=\n##|\Z)"
        section_match = re.search(section_pattern, markdown, re.DOTALL)

        if not section_match:
            return []

        section_text = section_match.group(1)

        # Extract all [digit] patterns
        indices_str = re.findall(r"\[(\d+)\]", section_text)

        # Convert to integers
        indices = [int(i) for i in indices_str]

        return indices

    def _indices_to_uuids(
        self,
        indices: List[int],
        available_components: List[Dict],
        component_type: str,
        warnings: List[str],
    ) -> List[str]:
        """
        Convert indices to UUIDs with validation and deduplication.

        Args:
            indices: List of indices from model output (may contain duplicates)
            available_components: Array model saw (same rag_context)
            component_type: 'modules', 'activities', or 'assessments'
            warnings: List to append warnings to

        Returns:
            List of UUIDs (deduplicated, order preserved)
        """
        uuids = []
        seen_uuids = set()  # Track duplicates
        duplicate_count = 0

        for idx in indices:
            if 0 <= idx < len(available_components):
                # Valid index - get UUID using type-specific field
                component = available_components[idx]

                # Use deterministic type-specific field
                if component_type == "modules":
                    uuid = component["module_id"]
                elif component_type == "activities":
                    uuid = component["activity_id"]
                elif component_type == "assessments":
                    uuid = component["assessment_id"]
                else:
                    raise ValueError(f"Unknown component_type: {component_type}")

                # Skip if we've already seen this UUID
                if uuid in seen_uuids:
                    duplicate_count += 1
                    continue

                seen_uuids.add(uuid)
                uuids.append(uuid)
            else:
                # Invalid index - warn and skip
                warnings.append(
                    f"Invalid {component_type} index [{idx}] "
                    f"(max: {len(available_components) - 1})"
                )

        # Warn if duplicates were found
        if duplicate_count > 0:
            warnings.append(
                f"Removed {duplicate_count} duplicate {component_type} "
                f"(model generated same index multiple times)"
            )

        return uuids


def expand_with_database_details(syllabus: Dict, rag_context: Dict) -> str:
    """
    Expand simplified syllabus JSON to rich markdown with database details.

    This is the TEMPLATE that adds descriptions, hours, etc.
    Model only provides indices, this function provides rich content.
    """
    lines = []

    # Course header
    info = syllabus["course_info"]
    lines.append(f"# {info.get('title', 'Untitled Course')}")
    lines.append("")
    lines.append(f"**Domain:** {info.get('domain', 'N/A')}")
    lines.append(f"**Level:** {info.get('level', 'N/A')}")
    lines.append(f"**Duration:** {info.get('duration', 'N/A')}")
    lines.append("")

    # Learning objectives
    if syllabus["learning_objectives"]:
        lines.append("## Learning Objectives")
        for obj in syllabus["learning_objectives"]:
            lines.append(f"- {obj}")
        lines.append("")

    # Modules (EXPANDED with database details)
    if syllabus["modules"]:
        lines.append("## Modules")
        lines.append("")

        # Build lookup: UUID → component (using type-specific field)
        uuid_to_module = {
            m["module_id"]: m for m in rag_context.get("available_modules", [])
        }

        for module_uuid in syllabus["modules"]:
            module = uuid_to_module.get(module_uuid)
            if module:
                lines.append(f"### {module['title']}")
                lines.append(f"{module.get('description', 'No description available')}")
                lines.append("")
                lines.append(
                    f"- **Duration:** {module.get('estimated_hours', 0)} hours"
                )
                lines.append(f"- **Difficulty:** {module.get('difficulty', 'N/A')}")

                key_concepts = module.get("key_concepts", [])
                if key_concepts:
                    lines.append(f"- **Key Concepts:** {', '.join(key_concepts[:5])}")

                lines.append("")

    # Activities (EXPANDED)
    if syllabus["activities"]:
        lines.append("## Activities")
        lines.append("")

        uuid_to_activity = {
            a["activity_id"]: a for a in rag_context.get("available_activities", [])
        }

        for activity_uuid in syllabus["activities"]:
            activity = uuid_to_activity.get(activity_uuid)
            if activity:
                lines.append(f"### {activity['title']}")
                lines.append(
                    f"{activity.get('description', 'No description available')}"
                )
                lines.append("")
                lines.append(
                    f"- **Duration:** {activity.get('estimated_hours', 0)} hours"
                )
                lines.append(f"- **Bloom Level:** {activity.get('bloom_level', 'N/A')}")
                lines.append("")

    # Assessments (EXPANDED)
    if syllabus["assessments"]:
        lines.append("## Assessments")
        lines.append("")

        uuid_to_assessment = {
            a["assessment_id"]: a for a in rag_context.get("available_assessments", [])
        }

        for assessment_uuid in syllabus["assessments"]:
            assessment = uuid_to_assessment.get(assessment_uuid)
            if assessment:
                lines.append(f"### {assessment['title']}")
                lines.append(
                    f"{assessment.get('description', 'No description available')}"
                )
                lines.append("")
                lines.append(f"- **Type:** {assessment.get('assessment_type', 'N/A')}")
                lines.append(
                    f"- **Duration:** {assessment.get('estimated_hours', 0)} hours"
                )
                lines.append("")

    return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    # Test with sample markdown
    sample_markdown = """# Course: Introduction to Programming

**Domain:** computer_science
**Level:** beginner
**Duration:** semester

## Learning Objectives
- Understand programming fundamentals
- Write simple Python programs

## Selected Modules
[0], [1]

## Selected Activities
[0]

## Selected Assessments
[0]
"""

    # Mock RAG context (using deterministic type-specific fields)
    mock_context = {
        "available_modules": [
            {
                "module_id": "uuid-mod-0",
                "title": "Python Basics",
                "description": "Learn Python",
                "estimated_hours": 40,
                "difficulty": "beginner",
                "key_concepts": ["variables", "functions"],
            },
            {
                "module_id": "uuid-mod-1",
                "title": "Data Structures",
                "description": "Master data structures",
                "estimated_hours": 50,
                "difficulty": "beginner",
                "key_concepts": ["arrays", "lists"],
            },
        ],
        "available_activities": [
            {
                "activity_id": "uuid-act-0",
                "title": "Coding Exercise 1",
                "description": "Practice basics",
                "estimated_hours": 5,
                "bloom_level": "Apply",
            },
        ],
        "available_assessments": [
            {
                "assessment_id": "uuid-ass-0",
                "title": "Midterm Exam",
                "description": "Test knowledge",
                "estimated_hours": 2,
                "assessment_type": "exam",
            },
        ],
    }

    # Parse
    parser = MarkdownSyllabusParser()
    result = parser.parse(sample_markdown, mock_context)

    print("=" * 80)
    print("PARSER TEST")
    print("=" * 80)
    print()
    print(f"Success: {result.success}")
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")
    print()
    print("Parsed JSON:")
    print(json.dumps(result.syllabus, indent=2))
    print()
    print("=" * 80)
    print("EXPANDED MARKDOWN")
    print("=" * 80)
    print()
    expanded = expand_with_database_details(result.syllabus, mock_context)
    print(expanded)
