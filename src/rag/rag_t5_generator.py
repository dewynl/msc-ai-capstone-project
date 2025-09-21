import json
from typing import Any, Dict, List


class RAGEnhancedT5Generator:
    """RAG-enhanced generator using template-based approach for reliable JSON output"""

    def __init__(self, model_name: str = None, device: str = "cpu"):
        print("🔧 Using Template-Based Generation (reliable JSON structure)")
        self.device = device

    def create_prompt(
        self, requirements: dict[str, Any], retrieved_components: dict[str, list]
    ) -> str:
        """Create prompt with retrieved components - match training format exactly"""

        prompt = f"Generate syllabus for: {requirements.get('title', '')}\n"
        prompt += f"Domain: {requirements.get('domain', '')} Level: {requirements.get('level', '')}\n"
        prompt += "Duration: semester\n"
        prompt += f"Description: {requirements.get('description', '')}\n"

        prompt += "Learning Objectives:\n"
        objectives = self._extract_learning_objectives(retrieved_components)
        for obj in objectives[:3]:
            prompt += f"- {obj}\n"

        level = requirements.get("level", "undergraduate").title()
        domain = requirements.get("domain", "")
        domain_display = self._format_domain_display(domain)
        prompt += f"Target Audience: {level} students in {domain_display} with relevant prerequisites\n"

        if retrieved_components:
            prompt += "\nRelevant Educational Components:\n"

            if "modules" in retrieved_components and retrieved_components["modules"]:
                modules = retrieved_components["modules"][:3]
                domains_covered = set(mod.get("domain", "") for mod in modules)

                prompt += f"Modules: {len(modules)} available covering "
                module_topics = [mod.get("title", "")[:25] for mod in modules[:2]]
                prompt += ", ".join(module_topics)

                if len(domains_covered) > 1:
                    prompt += f" (spanning {len(domains_covered)} domains)"
                prompt += "\n"

            activities = retrieved_components.get("activities", [])
            assessments = retrieved_components.get("assessments", [])

            activity_domains = set(act.get("domain", "") for act in activities)
            assessment_domains = set(ass.get("domain", "") for ass in assessments)

            prompt += f"Activities: {len(activities)} hands-on exercises"
            if len(activity_domains) > 1:
                prompt += f" across {len(activity_domains)} domains"
            prompt += "\n"

            prompt += f"Assessments: {len(assessments)} evaluation methods"
            if len(assessment_domains) > 1:
                prompt += f" across {len(assessment_domains)} domains"
            prompt += "\n"

        return prompt

    def _format_domain_display(self, domain: str) -> str:
        """Format domain name for display"""
        domain_names = {
            "computer_science": "Computer Science",
            "mathematics": "Mathematics",
            "physics": "Physics",
            "engineering": "Engineering",
            "biology": "Biology",
            "chemistry": "Chemistry"
        }
        return domain_names.get(domain.lower(), domain.title())

    def _extract_learning_objectives(self, components: dict[str, list]) -> list[str]:
        """Extract learning objectives from retrieved components"""
        objectives = []

        for module in components.get("modules", [])[:2]:
            module_objectives = module.get("learning_objectives", [])
            objectives.extend(module_objectives[:2])

        if not objectives:
            objectives = [
                "Understand fundamental concepts and principles in the subject area",
                "Apply theoretical knowledge to practical problem-solving scenarios",
                "Analyze and evaluate information critically within the domain",
            ]

        return objectives[:4]

    def generate_syllabus(self, prompt: str = None, max_length: int = None) -> str:
        """Generate syllabus using template-based approach - prompt parameter kept for compatibility"""
        return "Template-based generation complete"

    def generate_syllabus_json(self, requirements: Dict[str, Any], retrieved_components: Dict[str, List]) -> Dict[str, Any]:
        """Generate structured JSON syllabus using template approach"""

        learning_objectives = []
        for module in retrieved_components.get("modules", [])[:2]:
            module_objectives = module.get("learning_objectives", [])
            learning_objectives.extend(module_objectives[:2])

        if not learning_objectives:
            learning_objectives = [
                "Understand fundamental concepts and principles in the subject area",
                "Apply theoretical knowledge to practical problem-solving scenarios",
                "Analyze and evaluate information critically within the domain"
            ]
        syllabus = {
            "course_info": {
                "title": requirements.get("title", ""),
                "domain": requirements.get("domain", ""),
                "level": requirements.get("level", ""),
                "duration": requirements.get("duration", "semester"),
                "description": requirements.get("description", "")
            },
            "learning_objectives": learning_objectives[:4],
            "modules": [
                {
                    "title": module.get("title", ""),
                    "description": self._truncate_text(module.get("description", ""), 150),
                    "key_concepts": module.get("key_concepts", [])[:3],
                    "estimated_hours": module.get("estimated_hours", 4)
                }
                for module in retrieved_components.get("modules", [])[:3]
            ],
            "activities": [
                {
                    "title": activity.get("title", ""),
                    "description": self._truncate_text(activity.get("description", ""), 100),
                    "bloom_level": activity.get("bloom_level", "apply"),
                    "estimated_hours": activity.get("estimated_hours", 1)
                }
                for activity in retrieved_components.get("activities", [])[:4]
            ],
            "assessments": [
                {
                    "title": assessment.get("title", ""),
                    "assessment_type": assessment.get("assessment_type", "exam"),
                    "estimated_hours": assessment.get("estimated_hours", 2)
                }
                for assessment in retrieved_components.get("assessments", [])[:2]
            ]
        }

        return syllabus

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to specified length with ellipsis"""
        if len(text) <= max_length:
            return text
        return text[:max_length].rsplit(' ', 1)[0] + "..."
