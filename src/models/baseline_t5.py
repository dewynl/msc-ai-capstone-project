from typing import Any

import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer


class BaselineT5:
    """
    Standard T5 model for syllabus generation
    """

    def __init__(self, model_name: str = "t5-base"):
        self.model_name = model_name
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)

        self.device = torch.device("cpu")
        self.model.to(self.device)

    def prepare_input(self, context: dict[str, Any]) -> str:
        """Convert course context to T5 input format"""
        prompt = f"Generate syllabus: Title: {context['course_title']} "
        prompt += f"Domain: {context['domain']} Level: {context['level']} "
        prompt += f"Description: {context['course_description']}"
        return prompt

    def generate_syllabus(self, context: dict[str, Any], max_length: int = 1024) -> str:
        """Generate syllabus from course context"""
        input_text = self.prepare_input(context)

        # Tokenize input
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            padding=True,
            max_length=512,
            truncation=True,
        ).to(self.device)

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_return_sequences=1,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        # Decode output
        generated_text: str = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text
