#!/usr/bin/env python3
"""
Model inference wrapper for CodeT5 syllabus generation.

Provides a simple interface for loading the trained model and generating syllabi.
"""

import os

import torch
from transformers import RobertaTokenizer, T5ForConditionalGeneration


class SyllabusGenerator:
    """
    Wrapper for CodeT5 model inference.

    Loads the trained model and provides a simple generate() method.
    """

    def __init__(self, model_path: str = "models/codet5-markdown-FULL"):
        """
        Initialize the generator with trained model.

        Args:
            model_path: Path to trained model directory
        """
        # Check if model exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                f"Please train the model first using phase4_full_training.py"
            )

        print(f"Loading model from {model_path}...")

        # Load tokenizer and model
        self.tokenizer = RobertaTokenizer.from_pretrained(model_path)
        self.model = T5ForConditionalGeneration.from_pretrained(model_path)

        # Move to GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        self.model.eval()  # Set to evaluation mode

        print(f"Model loaded successfully on {self.device}")

    def generate(
        self,
        prompt: str,
        max_length: int = 400,
        num_beams: int = 2,
        temperature: float = 1.0,
        early_stopping: bool = False,
    ) -> str:
        """
        Generate markdown syllabus from prompt.

        Args:
            prompt: Input prompt with course requirements and available components
            max_length: Maximum output length in tokens
            num_beams: Number of beams for beam search
            temperature: Sampling temperature (1.0 = no change)
            early_stopping: Whether to stop when all beams finish

        Returns:
            Generated markdown syllabus
        """
        # Tokenize input
        input_ids = self.tokenizer(
            prompt, return_tensors="pt", max_length=512, truncation=True
        ).input_ids

        # Move to device
        input_ids = input_ids.to(self.device)

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids,
                max_length=max_length,
                num_beams=num_beams,
                temperature=temperature,
                early_stopping=early_stopping,
                do_sample=False,  # Deterministic for consistency
            )

        # Decode output
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return generated_text

    def generate_batch(self, prompts: list, **kwargs) -> list:
        """
        Generate syllabi for multiple prompts (batch inference).

        Args:
            prompts: List of input prompts
            **kwargs: Additional arguments passed to generate()

        Returns:
            List of generated markdown syllabi
        """
        results = []
        for prompt in prompts:
            result = self.generate(prompt, **kwargs)
            results.append(result)
        return results


if __name__ == "__main__":
    # Test the generator
    print("Testing SyllabusGenerator...\n")

    # Test prompt
    test_prompt = """Generate syllabus for: Introduction to Python | computer_science | beginner

Available modules:
[0] Python Basics (40h, beginner)
[1] Data Types (20h, beginner)
[2] Control Flow (30h, beginner)

Available activities:
[0] Coding Exercises (5h)

Available assessments:
[0] Final Exam (exam)

Select relevant components and generate markdown syllabus."""

    try:
        # Initialize generator
        generator = SyllabusGenerator()

        # Generate
        print("Generating syllabus...")
        result = generator.generate(test_prompt)

        print("\nGenerated Syllabus:")
        print("=" * 80)
        print(result)
        print("=" * 80)

        print("\nSuccess! Model is working correctly.")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(
            "\nPlease ensure the model is trained and located at models/codet5-markdown-FULL/"
        )
    except Exception as e:
        print(f"Error during generation: {e}")
        import traceback

        traceback.print_exc()
