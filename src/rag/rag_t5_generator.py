from typing import Any

import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer


class RAGEnhancedT5Generator:
    """RAG-enhanced T5 model for generating syllabus components"""

    def __init__(
        self, model_name: str = "./models/t5-syllabus-finetuned", device: str = "cpu"
    ):
        print(f"Loading fine-tuned model from: {model_name}")
        try:
            self.model = T5ForConditionalGeneration.from_pretrained(model_name)
            self.tokenizer = T5Tokenizer.from_pretrained(model_name)
            print("✅ Fine-tuned model loaded successfully")
        except Exception as e:
            print(f"⚠️ Could not load fine-tuned model: {e}")
            print("Falling back to base t5-small model")
            self.model = T5ForConditionalGeneration.from_pretrained("t5-small")
            self.tokenizer = T5Tokenizer.from_pretrained("t5-small")

        self.device = device

    def create_prompt(
        self, requirements: dict[str, Any], retrieved_components: dict[str, list]
    ) -> str:
        """Create prompt with retrieved components - match training format exactly"""

        # Format exactly like training data input
        prompt = f"Generate syllabus for: {requirements.get('title', '')}\n"
        prompt += f"Domain: {requirements.get('domain', '')} Level: {requirements.get('level', '')}\n"
        prompt += "Duration: semester\n"  # Default duration
        prompt += f"Description: {requirements.get('description', '')}\n"

        # Add learning objectives (inferred from components)
        prompt += "Learning Objectives:\n"
        objectives = self._extract_learning_objectives(retrieved_components)
        for obj in objectives[:3]:  # Limit to 3 for input length
            prompt += f"- {obj}\n"

        # Add target audience with domain formatting
        level = requirements.get("level", "undergraduate").title()
        domain = requirements.get("domain", "")
        domain_display = self._format_domain_display(domain)
        prompt += f"Target Audience: {level} students in {domain_display} with relevant prerequisites\n"

        # Add component context with domain diversity
        if retrieved_components:
            prompt += "\nRelevant Educational Components:\n"

            # Add top modules with domain information
            if "modules" in retrieved_components and retrieved_components["modules"]:
                modules = retrieved_components["modules"][:3]
                domains_covered = set(mod.get("domain", "") for mod in modules)

                prompt += f"Modules: {len(modules)} available covering "
                module_topics = [mod.get("title", "")[:25] for mod in modules[:2]]
                prompt += ", ".join(module_topics)

                if len(domains_covered) > 1:
                    prompt += f" (spanning {len(domains_covered)} domains)"
                prompt += "\n"

            # Add activities and assessments summary with domain context
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

        # Get objectives from modules
        # RATIONALE: Limit to first 2 objectives per module to manage T5 input token budget (512 tokens max).
        # Learning objectives are often 20-40 tokens each, and we need space for course description,
        # component summaries, and other prompt sections. Taking top 2 from most relevant modules
        # (already ranked by similarity) provides highest quality context while staying within limits.
        # This mirrors training data format which typically had 3-4 objectives per syllabus.
        for module in components.get("modules", [])[
            :2
        ]:  # Only top 2 most relevant modules
            module_objectives = module.get("learning_objectives", [])
            objectives.extend(module_objectives[:2])  # Take first 2 from each module

        # If no objectives found, create generic ones
        if not objectives:
            objectives = [
                "Understand fundamental concepts and principles in the subject area",
                "Apply theoretical knowledge to practical problem-solving scenarios",
                "Analyze and evaluate information critically within the domain",
            ]

        return objectives[:4]  # Return max 4 objectives

    def generate_syllabus(self, prompt: str, max_length: int = 2048) -> str:
        """Generate syllabus using prompt with retrieved components"""
        inputs = self.tokenizer(
            prompt,
            max_length=512,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=max_length,
                min_length=200,
                num_beams=4,
                early_stopping=False,
                do_sample=True,
                temperature=0.7,
                repetition_penalty=1.3,
                length_penalty=1.1,
                no_repeat_ngram_size=4,
            )

        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return generated_text
