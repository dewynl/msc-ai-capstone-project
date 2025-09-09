#!/usr/bin/env python3
"""
Syllabus Formatter
Post-process T5 output to create structured syllabus format
"""

from typing import Any


class SyllabusFormatter:
    """Format T5 output into structured syllabus template"""

    def format_syllabus(
        self,
        course_info: dict[str, Any],
        t5_output: str,
        retrieved_components: dict[str, list],
    ) -> dict[str, Any]:
        """Convert T5 output into structured JSON for web app rendering"""

        title = course_info.get("title", "Course Title")
        domain = course_info.get("domain", "Computer Science")
        level = course_info.get("level", "undergraduate")
        description = course_info.get("description", "Course description")

        # Extract learning objectives from components
        objectives = self._extract_objectives(retrieved_components)

        # Create structured JSON syllabus
        syllabus_data = {
            "title": title,
            "description": description,
            "domain": domain,
            "level": level,
            "target_audience": f"{level.title()} students in {domain} with appropriate prerequisites and foundational knowledge",
            "learning_objectives": objectives,
            "learning_modules": self._generate_modules_as_data(retrieved_components),
            "assessment_strategy": self._generate_assessment_data(
                retrieved_components, course_info
            ),
            "metadata": {
                "generated_from": "rag_system",
                "components_used": {
                    "modules": len(retrieved_components.get("modules", [])),
                    "activities": len(retrieved_components.get("activities", [])),
                    "assessments": len(retrieved_components.get("assessments", [])),
                },
            },
        }

        return syllabus_data

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

    def _generate_modules_as_data(
        self, components: dict[str, list]
    ) -> list[dict[str, Any]]:
        """Generate structured learning modules data for web app"""

        modules = components.get("modules", [])
        activities = components.get("activities", [])

        learning_modules = []

        # Create modules from retrieved components
        for i, module in enumerate(modules):
            module_title = module.get("title", f"Learning Module {i+1}")
            module_description = module.get(
                "description", "Core concepts and applications"
            )

            # Get related activities
            module_activities = []
            if i < len(activities):
                activity = activities[i]
                module_activities.append(activity.get("title", "Practical exercises"))

            # Add complementary activities based on module content
            if (
                "fundamental" in module_title.lower()
                or "introduction" in module_title.lower()
            ):
                module_activities.extend(["Conceptual overview", "Guided practice"])
            elif (
                "advanced" in module_title.lower()
                or "application" in module_title.lower()
            ):
                module_activities.extend(
                    ["Case study analysis", "Project implementation"]
                )
            else:
                module_activities.extend(
                    ["Interactive exercises", "Problem-solving activities"]
                )

            module_data = {
                "id": f"module_{i+1}",
                "number": i + 1,
                "title": module_title,
                "description": module_description,
                "learning_activities": module_activities[:4],  # Limit to 4 activities
                "key_outcomes": "Students will demonstrate understanding through practical application and assessment",
                "type": "content",
            }

            learning_modules.append(module_data)

        # Add synthesis module if we have multiple modules
        if len(learning_modules) > 1:
            synthesis_module = {
                "id": "integration_module",
                "number": len(learning_modules) + 1,
                "title": "Integration and Synthesis",
                "description": "Connecting concepts across all learning modules and applying knowledge to complex scenarios",
                "learning_activities": [
                    "Capstone project development",
                    "Cross-module concept integration",
                    "Peer collaboration and presentation",
                    "Reflective analysis and synthesis",
                ],
                "key_outcomes": "Students will synthesize learning from all modules and demonstrate mastery through comprehensive application",
                "type": "integration",
            }
            learning_modules.append(synthesis_module)

        return learning_modules

    def _generate_assessment_data(
        self, components: dict[str, list], course_info: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Generate structured assessment data for web app"""

        assessments = components.get("assessments", [])
        modules = components.get("modules", [])
        domain = (
            course_info.get("domain", "Computer Science")
            if course_info
            else "Computer Science"
        )

        assessment_components = []

        if len(assessments) >= 3:
            # Use actual assessments with module-based descriptions
            assessment_components = [
                {
                    "id": "assessment_1",
                    "name": assessments[0].get("title", "Module Assessments"),
                    "weight": 30,
                    "description": assessments[0].get("description", "")
                    or f"Progressive assessments aligned with learning modules in {domain.lower()}",
                    "type": "formative",
                },
                {
                    "id": "assessment_2",
                    "name": assessments[1].get("title", "Applied Projects"),
                    "weight": 40,
                    "description": assessments[1].get("description", "")
                    or f"Practical {domain.lower()} projects demonstrating applied knowledge",
                    "type": "project",
                },
                {
                    "id": "assessment_3",
                    "name": assessments[2].get("title", "Comprehensive Evaluation"),
                    "weight": 25,
                    "description": assessments[2].get("description", "")
                    or "Integrated assessment of all learning modules and synthesis capabilities",
                    "type": "summative",
                },
            ]
        else:
            # Default module-based assessment strategy
            assessment_components = [
                {
                    "id": "module_assessments",
                    "name": "Module Assessments",
                    "weight": 30,
                    "description": "Progressive evaluations aligned with each learning module",
                    "type": "formative",
                },
                {
                    "id": "applied_projects",
                    "name": "Applied Projects",
                    "weight": 40,
                    "description": f"Hands-on {domain.lower()} projects demonstrating practical mastery",
                    "type": "project",
                },
                {
                    "id": "synthesis_assessment",
                    "name": "Synthesis Assessment",
                    "weight": 25,
                    "description": "Comprehensive evaluation integrating all learning modules",
                    "type": "summative",
                },
            ]

        # Add engagement component
        assessment_components.append(
            {
                "id": "learning_engagement",
                "name": "Learning Engagement",
                "weight": 5,
                "description": "Active participation in learning activities and peer collaboration",
                "type": "participation",
            }
        )

        return {
            "components": assessment_components,
            "total_weight": 100,
            "grading_philosophy": "Module-based progressive assessment with integrated synthesis evaluation",
        }
