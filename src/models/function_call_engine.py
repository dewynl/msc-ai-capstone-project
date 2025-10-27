#!/usr/bin/env python3
"""
Function Call Execution Engine

This module bridges T5's generated text output with the SyllabusBuilder execution.
It handles parsing T5's output (which may not be perfect function calls) and
converting it into executable function calls.
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

from .syllabus_builder import execute_function_calls

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class T5FunctionCallGenerator:
    """
    T5-based function call generator for syllabus creation.

    This class loads the trained T5 model and generates function calls
    that can be executed by the SyllabusBuilder.
    """

    def __init__(self, model_path: str = "./models/t5-function-call-finetuned"):
        """
        Initialize the T5 function call generator.

        Args:
            model_path: Path to the trained T5 model
        """
        self.model_path = Path(model_path)
        self.tokenizer = None
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the trained T5 model and tokenizer.

        Priority order:
        1. Hugging Face Hub (via HF_MODEL_ID env var or Streamlit secret)
        2. Local fine-tuned model
        3. Base t5-small (fallback)
        """
        try:
            # Check for Hugging Face model ID (for production deployment)
            hf_model_id = os.getenv("HF_MODEL_ID")

            # Check Streamlit secrets if available (for Streamlit Cloud)
            try:
                import streamlit as st

                if hasattr(st, "secrets") and "HF_MODEL_ID" in st.secrets:
                    hf_model_id = st.secrets["HF_MODEL_ID"]
            except Exception:
                pass  # Not running in Streamlit or secrets not configured

            if hf_model_id:
                # Load from Hugging Face Hub
                logger.info(
                    f"🤗 Loading fine-tuned model from Hugging Face: {hf_model_id}"
                )
                self.tokenizer = T5Tokenizer.from_pretrained(hf_model_id)
                self.model = T5ForConditionalGeneration.from_pretrained(hf_model_id)
                logger.info("✅ Fine-tuned model loaded from Hugging Face Hub")

            elif self.model_path.exists():
                # Load from local path
                logger.info(
                    f"📁 Loading trained model from local path: {self.model_path}"
                )
                self.tokenizer = T5Tokenizer.from_pretrained(self.model_path)
                self.model = T5ForConditionalGeneration.from_pretrained(self.model_path)
                logger.info("✅ Fine-tuned model loaded from local path")

            else:
                # Fallback to base model
                logger.warning(
                    "⚠️  No fine-tuned model found. Using base T5.\n"
                    "   - Set HF_MODEL_ID env var to use Hugging Face model\n"
                    "   - Or train locally: python scripts/t5_function_call_trainer.py"
                )
                self.tokenizer = T5Tokenizer.from_pretrained("t5-small")
                self.model = T5ForConditionalGeneration.from_pretrained("t5-small")

            # Set to evaluation mode
            self.model.eval()
            logger.info("✅ T5 model loaded successfully")

        except Exception as e:
            logger.error(f"❌ Failed to load T5 model: {e}")
            raise

    def generate_function_calls(self, requirements: Dict[str, Any]) -> str:
        """
        Generate function calls for the given course requirements.

        Args:
            requirements: Course requirements dictionary

        Returns:
            Generated function calls as string
        """
        # Format input for T5
        input_text = f"Generate course syllabus: {json.dumps(requirements)}"

        # Tokenize input
        input_ids = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=640,  # Match training config
            truncation=True,
            padding=True,
        ).input_ids

        # Generate function calls with beam search (deterministic, higher quality)
        with torch.no_grad():
            generated_tokens = self.model.generate(
                input_ids,
                max_length=571,  # Match training output length
                num_beams=4,  # Beam search for better quality
                early_stopping=True,
                no_repeat_ngram_size=2,  # Prevent repetition
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        # Decode generated tokens
        generated_calls = self.tokenizer.decode(
            generated_tokens[0], skip_special_tokens=True
        )

        # Fix common T5 issues before execution
        import re

        # Issue 1: Missing newlines between statements
        # T5 sometimes generates "b = SyllabusBuilder() b.set_info(...)" on one line
        # Handle both 'b.' and 'c.' (c is corrected to b in next step)
        generated_calls = re.sub(r"(\S)\s+([bc]\.)", r"\1\n\2", generated_calls)

        # Issue 2: Wrong variable name (T5 sometimes generates 'c.' instead of 'b.')
        # This is a known T5 error - correct it before execution
        # Replace any 'c.' calls with 'b.' for all builder methods
        generated_calls = re.sub(
            r"\bc\.(set_info|add_objective|add_module_by_id|add_activity_by_id|add_assessment_by_id|add_module|add_activity|add_assessment|build)",
            r"b.\1",
            generated_calls,
        )

        # Issue 3: Check for minimum expected length (should have multiple function calls)
        if len(generated_calls) < 200:
            logger.warning(
                f"⚠️  Generated output too short ({len(generated_calls)} chars), may be incomplete"
            )

        logger.info(f"📝 Generated function calls: {generated_calls[:200]}...")
        return generated_calls


class FunctionCallParser:
    """
    Parser for converting T5's output into executable function calls.

    T5 might not generate perfect function call syntax, so this parser
    handles common issues and converts the output into valid function calls.
    """

    @staticmethod
    def parse_t5_output(t5_output: str) -> str:
        """
        Parse T5's output and convert it to executable function calls.

        Args:
            t5_output: Raw output from T5 model

        Returns:
            Cleaned, executable function calls
        """
        # Remove common T5 artifacts and clean up
        cleaned = t5_output.strip()

        # Handle common T5 patterns that aren't perfect function calls
        if not cleaned.startswith("b = SyllabusBuilder()"):
            cleaned = FunctionCallParser._convert_to_function_calls(cleaned)

        return cleaned

    @staticmethod
    def _convert_to_function_calls(t5_output: str) -> str:
        """
        Enhanced conversion of T5's structured output to function calls.

        Handles multiple T5 output patterns with robust parsing.
        """
        calls = ["b = SyllabusBuilder()"]

        try:
            # Enhanced pattern matching for T5 output

            # 1. Extract course information with multiple patterns
            title = FunctionCallParser._extract_field(t5_output, "title")
            domain = FunctionCallParser._extract_field(t5_output, "domain")
            level = FunctionCallParser._extract_field(t5_output, "level")
            duration = (
                FunctionCallParser._extract_field(t5_output, "duration") or "semester"
            )
            description = (
                FunctionCallParser._extract_field(t5_output, "description")
                or f'Course on {title or "various topics"}'
            )

            # Build course info call
            if title or domain or level:
                title = title or "Generated Course"
                domain = domain or "computer_science"
                level = level or "intermediate"
                calls.append(
                    f'b.set_info("{title}", "{domain}", "{level}", "{duration}", "{description[:100]}")'
                )

            # 2. Extract learning objectives with enhanced patterns
            objectives = FunctionCallParser._extract_objectives(t5_output)
            for obj in objectives[:4]:  # Limit to 4 objectives
                cleaned_obj = obj.replace('"', '\\"').strip()[
                    :100
                ]  # Clean and truncate
                if cleaned_obj:
                    calls.append(f'b.add_objective("{cleaned_obj}")')

            # 3. Extract or generate modules
            modules = FunctionCallParser._extract_modules(t5_output)
            if not modules:  # Generate default modules if none found
                if title:
                    modules = [
                        (
                            f"Introduction to {title.split()[0] if title.split() else 'Subject'}",
                            8,
                        ),
                        (
                            f"Advanced {title.split()[-1] if title.split() else 'Topics'}",
                            12,
                        ),
                    ]
                else:
                    modules = [("Fundamentals", 8), ("Advanced Topics", 12)]

            for module_title, hours in modules[:3]:  # Limit to 3 modules
                calls.append(f'b.add_module("{module_title}", {hours})')

            # 4. Generate activities based on level
            activity_level = (
                "remember"
                if level == "beginner"
                else "apply"
                if level == "intermediate"
                else "create"
            )
            activities = [
                (
                    f"Hands-on {title.split()[0] if title and title.split() else 'Practice'} Exercise",
                    activity_level,
                    2,
                ),
                (
                    f"{title.split()[-1] if title and title.split() else 'Concept'} Workshop",
                    activity_level,
                    3,
                ),
            ]

            for activity_title, bloom_level, hours in activities:
                calls.append(
                    f'b.add_activity("{activity_title}", "{bloom_level}", {hours})'
                )

            # 5. Generate assessments
            assessment_type = (
                "quiz"
                if level == "beginner"
                else "exam"
                if level == "intermediate"
                else "project"
            )
            calls.append(
                f'b.add_assessment("Final {assessment_type.title()}", "{assessment_type}", 2)'
            )

            calls.append("result = b.build()")
            return "\n".join(calls)

        except Exception as e:
            logger.warning(f"Enhanced parsing failed, using fallback: {e}")
            return FunctionCallParser._create_fallback_calls(t5_output)

    @staticmethod
    def _extract_field(text: str, field_name: str) -> str:
        """Extract a field value from T5 output using multiple patterns."""
        patterns = [
            rf'"{field_name}":\s*"([^"]+)"',  # JSON-like: "field": "value"
            rf'{field_name}:\s*"([^"]+)"',  # No quotes: field: "value"
            rf'{field_name}["\']:\s*["\']([^"\']+)["\']',  # Various quote styles
            rf"{field_name}[=:]\s*([^,\s}}]+)",  # Simple assignment: field=value or field: value
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    @staticmethod
    def _extract_objectives(text: str) -> List[str]:
        """Extract learning objectives from T5 output."""
        objectives = []

        # Multiple patterns for objectives
        patterns = [
            r'"learning_objectives":\s*\[([^\]]+)\]',  # JSON array
            r"learning_objectives[:\[]([^\]]+)[\]]?",  # Various formats
            r"objectives?[:\[]([^\]]+)[\]]?",  # Short form
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                objectives_text = match.group(1)
                # Extract individual objectives
                objective_matches = re.findall(r'"([^"]+)"', objectives_text)
                if objective_matches:
                    objectives.extend(objective_matches)
                    break

        # If no structured objectives found, look for any educational terms
        if not objectives:
            educational_terms = re.findall(
                r"((?:understand|learn|implement|master|analyze|evaluate|create|apply)[^.]{10,80})",
                text,
                re.IGNORECASE,
            )
            objectives.extend(educational_terms[:3])

        return objectives

    @staticmethod
    def _extract_modules(text: str) -> List[tuple]:
        """Extract course modules from T5 output."""
        modules = []

        # Look for module patterns
        module_patterns = [
            r'"modules":\s*\[([^\]]+)\]',
            r"modules?[:\[]([^\]]+)[\]]?",
        ]

        for pattern in module_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                modules_text = match.group(1)
                # Try to extract module titles
                module_titles = re.findall(r'"title":\s*"([^"]+)"', modules_text)
                for title in module_titles:
                    modules.append((title, 8))  # Default 8 hours
                break

        return modules

    @staticmethod
    def _create_fallback_calls(t5_output: str) -> str:
        """
        Create fallback function calls when parsing fails.

        Args:
            t5_output: Original T5 output

        Returns:
            Basic function calls
        """
        return """
b = SyllabusBuilder()
b.set_info("Generated Course", "computer_science", "intermediate", "semester", "Generated course description")
b.add_objective("Learn fundamental concepts")
b.add_objective("Apply theoretical knowledge")
b.add_module("Introduction", 8)
b.add_activity("Hands-on Exercise", "apply", 2)
b.add_assessment("Final Assessment", "exam", 2)
syllabus = b.build()
""".strip()


class FunctionCallSyllabusGenerator:
    """
    Complete pipeline for generating syllabi using the function call approach.

    This combines T5 generation, parsing, and execution into a single interface.
    """

    def __init__(self, model_path: str = "./models/t5-function-call-finetuned"):
        """
        Initialize the complete function call pipeline.

        Args:
            model_path: Path to trained T5 model
        """
        self.t5_generator = T5FunctionCallGenerator(model_path)
        self.parser = FunctionCallParser()

    def generate_syllabus(
        self, requirements: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], str]:
        """
        Generate a complete syllabus using the function call approach.

        Args:
            requirements: Course requirements dictionary

        Returns:
            Tuple of (syllabus_dict, generated_function_calls)
        """
        logger.info("🚀 Starting function call syllabus generation")

        try:
            # Step 1: Generate function calls using T5
            raw_output = self.t5_generator.generate_function_calls(requirements)

            # Step 2: Parse and clean the function calls
            function_calls = self.parser.parse_t5_output(raw_output)

            # Step 3: Execute function calls to build syllabus
            syllabus = execute_function_calls(function_calls)

            logger.info("✅ Function call syllabus generation successful!")
            return syllabus, function_calls

        except Exception as e:
            logger.error(f"❌ Function call generation failed: {e}")
            # Fallback to basic syllabus
            fallback_calls = self.parser._create_fallback_calls(str(requirements))
            syllabus = execute_function_calls(fallback_calls)
            return syllabus, fallback_calls

    def test_generation(self) -> Dict[str, Any]:
        """
        Test the complete function call pipeline.

        Returns:
            Test results dictionary
        """
        logger.info("🧪 Testing function call pipeline...")

        test_requirements = {
            "title": "Machine Learning Fundamentals",
            "domain": "computer_science",
            "level": "intermediate",
            "duration": "semester",
            "description": "Introduction to machine learning algorithms and applications",
            "learning_objectives": [
                "Understand supervised learning algorithms",
                "Implement neural networks",
                "Evaluate model performance",
            ],
            "prerequisites": "Linear algebra, statistics, programming",
            "target_audience": "Intermediate students in Computer Science",
        }

        try:
            syllabus, function_calls = self.generate_syllabus(test_requirements)

            results = {
                "success": True,
                "generated_syllabus": syllabus,
                "function_calls": function_calls,
                "metadata": {
                    "total_components": (
                        len(syllabus.get("modules", []))
                        + len(syllabus.get("activities", []))
                        + len(syllabus.get("assessments", []))
                    ),
                    "has_course_info": bool(syllabus.get("course_info")),
                    "has_objectives": bool(syllabus.get("learning_objectives")),
                    "function_calls_length": len(function_calls),
                },
            }

            logger.info("✅ Pipeline test successful!")
            return results

        except Exception as e:
            logger.error(f"❌ Pipeline test failed: {e}")
            return {"success": False, "error": str(e)}


def main():
    """Test the complete function call pipeline."""
    print("🚀 Testing Function Call Execution Engine")

    try:
        # Initialize the complete pipeline
        generator = FunctionCallSyllabusGenerator()

        # Test generation
        results = generator.test_generation()

        if results["success"]:
            print("✅ Function call pipeline test successful!")
            print(
                f"Generated syllabus: '{results['generated_syllabus']['course_info']['title']}'"
            )
            print(f"Total components: {results['metadata']['total_components']}")
            print(
                f"Function calls: {results['metadata']['function_calls_length']} characters"
            )
            print("\n📋 Sample function calls:")
            print(results["function_calls"][:300] + "...")
        else:
            print(f"❌ Pipeline test failed: {results['error']}")

    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {e}")

    print("\n🎉 Function call execution engine complete!")


if __name__ == "__main__":
    main()
