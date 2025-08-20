#!/usr/bin/env python3
"""
Syllabus Formatter
Post-process T5 output to create structured syllabus format
"""

import re
from typing import Any


class SyllabusFormatter:
    """Format T5 output into structured syllabus template"""

    def format_syllabus(
        self,
        course_info: dict[str, Any],
        t5_output: str,
        retrieved_components: dict[str, list],
    ) -> str:
        """Convert T5 output into structured syllabus template"""

        title = course_info.get("title", "Course Title")
        domain = course_info.get("domain", "Computer Science")
        level = course_info.get("level", "undergraduate")
        description = course_info.get("description", "Course description")

        # Extract learning objectives from components
        objectives = self._extract_objectives(retrieved_components)

        # Create structured syllabus
        syllabus = f"""# {title}
**[Semester]**

## Course Description

{description}

{self._clean_t5_content(t5_output)}

## Learning Objectives

Upon successful completion of this course, students will be able to:

{self._format_objectives(objectives)}

## Target Audience

{level.title()} students in {domain} with appropriate prerequisites and foundational knowledge.

## Weekly Schedule

{self._generate_weekly_schedule(retrieved_components, title)}

## Assessment Plan

{self._generate_assessment_plan(retrieved_components, course_info)}

### Grading Scale
- A: 90-100% (Excellent work demonstrating mastery)
- B: 80-89% (Good work meeting expectations)
- C: 70-79% (Satisfactory work meeting minimum requirements)
- D: 60-69% (Below expectations, minimal competency)
- F: Below 60% (Failing to meet course requirements)

## Required Materials

### Textbooks
- Primary textbook covering {domain.lower()} fundamentals
- Supplementary readings and online resources
- Access to required software and development tools

### Software Requirements
- Development environment appropriate for {domain.lower()}
- Access to course learning management system
- Reliable internet connection for online activities

## Course Policies

### Attendance Policy
Regular attendance is expected and contributes to learning success. Students are responsible for material covered during any absences.

### Late Work Policy
- Assignments: 10% penalty per day late, up to 5 days
- Major projects: Must be arranged in advance with instructor
- Exams: Must be taken at scheduled times unless emergency arrangements made

### Academic Integrity
All work must be original and properly cited. Collaboration policies will be specified for each assignment. Use of AI tools must be disclosed when permitted.

### Communication Policy
- Check course management system regularly for announcements
- Email instructor for questions outside of class
- Use appropriate academic communication standards
"""

        return syllabus

    def _clean_t5_content(self, t5_output: str) -> str:
        """Clean and extract useful content from T5 output"""
        # Remove repetitive text and formatting issues
        lines = t5_output.split("\n")
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            if line and len(line) > 10:  # Skip very short lines
                # Remove obvious repetition
                if not any(line.lower() in prev.lower() for prev in cleaned_lines[-2:]):
                    cleaned_lines.append(line)

        # Join and clean up
        content = " ".join(cleaned_lines)

        # Remove obvious artifacts
        content = re.sub(
            r"Generate syllabus for:.*?Target Audience:", "", content, flags=re.DOTALL
        )
        content = re.sub(
            r"Relevant Educational Components:.*", "", content, flags=re.DOTALL
        )
        content = re.sub(r"\s+", " ", content)  # Normalize whitespace

        if len(content.strip()) > 50:
            return f"## Additional Course Information\n\n{content.strip()}\n"
        else:
            return ""

    def _extract_objectives(self, components: dict[str, list]) -> list[str]:
        """Extract learning objectives from retrieved components"""
        objectives = []

        # Get objectives from modules
        for module in components.get("modules", [])[:3]:
            module_objectives = module.get("learning_objectives", [])
            objectives.extend(module_objectives[:2])

        # Default objectives if none found
        if not objectives:
            objectives = [
                "Understand fundamental concepts and principles in the subject area",
                "Apply theoretical knowledge to practical problem-solving scenarios",
                "Analyze and evaluate information critically within the domain",
                "Demonstrate proficiency through hands-on activities and assessments",
            ]

        return objectives[:4]  # Limit to 4 objectives

    def _format_objectives(self, objectives: list[str]) -> str:
        """Format learning objectives as bullet points"""
        formatted = []
        for obj in objectives:
            # Clean up objective text
            obj = obj.strip()
            if not obj.startswith("•"):
                obj = f"• {obj}"
            formatted.append(obj)

        return "\n".join(formatted)

    def _generate_weekly_schedule(self, components: dict[str, list], title: str) -> str:
        """Generate weekly schedule from components"""

        modules = components.get("modules", [])
        activities = components.get("activities", [])

        # Create 10-week schedule
        weeks = []
        week_num = 1

        # Distribute modules across weeks
        for i, module in enumerate(modules[:8]):  # Use up to 8 modules
            week_title = module.get("title", f"Topic {i+1}")[:50]
            week_description = module.get("description", "")[:100]

            # Add related activity if available
            activity = None
            if i < len(activities):
                activity = activities[i]

            week_content = f"""### Week {week_num}: {week_title}
**Topics:** {week_description}
- **Monday:** Introduction and theoretical foundations
- **Wednesday:** {activity.get('title', 'Practical exercise') if activity else 'Hands-on practice'}
- **Friday:** Application and review"""

            # Add assessment if it's a milestone week
            if week_num % 3 == 0 and week_num <= 9:
                assessments = components.get("assessments", [])
                if assessments:
                    assess_idx = (week_num // 3) - 1
                    if assess_idx < len(assessments):
                        assessment = assessments[assess_idx]
                        week_content += f"\n- **Assessment:** {assessment.get('title', 'Evaluation')} - Due Friday"

            weeks.append(week_content)
            week_num += 1

            if week_num > 10:  # Limit to 10 weeks
                break

        # Add final weeks if needed
        while week_num <= 10:
            if week_num == 10:
                weeks.append(
                    f"""### Week {week_num}: Final Projects and Review
**Topics:** Project presentations, course review, final preparation
- **Monday:** Final project presentations
- **Wednesday:** Course review and synthesis
- **Friday:** Final exam or project submission"""
                )
            else:
                weeks.append(
                    f"""### Week {week_num}: Advanced Topics
**Topics:** Extended applications and advanced concepts
- **Monday:** Advanced concepts introduction
- **Wednesday:** Practical applications
- **Friday:** Review and discussion"""
                )
            week_num += 1

        return "\n\n".join(weeks)

    def _generate_assessment_plan(
        self, components: dict[str, list], course_info: dict[str, Any] = None
    ) -> str:
        """Generate assessment plan from components"""

        assessments = components.get("assessments", [])
        domain = (
            course_info.get("domain", "Computer Science")
            if course_info
            else "Computer Science"
        )

        # Create assessment table
        plan = """| Assessment Type | Percentage | Description |
|----------------|------------|-------------|"""

        if len(assessments) >= 3:
            # Use actual assessments with full titles and descriptions
            assess_1 = assessments[0].get("title", "Quizzes and Assignments")
            assess_2 = assessments[1].get("title", "Practical Projects")
            assess_3 = assessments[2].get("title", "Final Examination")

            # Use actual descriptions if available, otherwise create domain-specific ones
            desc_1 = assessments[0].get("description", "")
            desc_2 = assessments[1].get("description", "")
            desc_3 = assessments[2].get("description", "")

            # Fallback to meaningful descriptions if not provided
            if not desc_1:
                desc_1 = (
                    f"Regular knowledge checks and {domain.lower()} concept assessments"
                )
            if not desc_2:
                desc_2 = (
                    f"Hands-on {domain.lower()} projects and practical applications"
                )
            if not desc_3:
                desc_3 = f"Comprehensive evaluation of {domain.lower()} mastery"

            plan += f"""
| {assess_1} | 25% | {desc_1} |
| {assess_2} | 40% | {desc_2} |
| {assess_3} | 25% | {desc_3} |
| Participation & Engagement | 10% | Class engagement, discussion, and attendance |
| **Total** | **100%** | |"""
        else:
            # Default assessment plan with domain context
            plan += f"""
| Quizzes & Assignments | 25% | Regular {domain.lower()} knowledge checks and homework |
| Projects & Applications | 40% | Practical {domain.lower()} projects and assignments |
| Final Examination | 25% | Comprehensive {domain.lower()} evaluation |
| Participation & Engagement | 10% | Class engagement and attendance |
| **Total** | **100%** | |"""

        return plan
