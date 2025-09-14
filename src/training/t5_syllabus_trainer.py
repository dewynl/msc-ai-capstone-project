#!/usr/bin/env python3
"""
T5 Syllabus Generation Fine-tuning Script
Fine-tune T5 model on syllabus generation task using our structured dataset
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset
from transformers import (
    DataCollatorForSeq2Seq,
    T5ForConditionalGeneration,
    T5Tokenizer,
    Trainer,
    TrainingArguments,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SyllabusTrainingConfig:
    """Configuration for syllabus training"""

    model_name: str = "t5-small"
    max_input_length: int = 512
    max_target_length: int = 1024
    train_batch_size: int = 4
    eval_batch_size: int = 4
    learning_rate: float = 3e-4
    num_epochs: int = 3
    warmup_steps: int = 500
    logging_steps: int = 100
    save_steps: int = 500
    eval_steps: int = 500
    output_dir: str = "./models/t5-syllabus-finetuned"
    gradient_accumulation_steps: int = 4


class SyllabusDataset(Dataset):
    """Dataset for syllabus generation training"""

    def __init__(
        self,
        examples: list[dict[str, str]],
        tokenizer: T5Tokenizer,
        config: SyllabusTrainingConfig,
    ):
        self.examples = examples
        self.tokenizer = tokenizer
        self.config = config

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        example = self.examples[idx]

        # Tokenize input (course requirements)
        input_encoding = self.tokenizer(
            example["input_text"],
            max_length=self.config.max_input_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        # Tokenize target (syllabus template)
        target_encoding = self.tokenizer(
            example["target_text"],
            max_length=self.config.max_target_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        return {
            "input_ids": input_encoding.input_ids.flatten(),
            "attention_mask": input_encoding.attention_mask.flatten(),
            "labels": target_encoding.input_ids.flatten(),
        }


class SyllabusTrainer:
    """Fine-tune T5 for syllabus generation"""

    def __init__(self, config: SyllabusTrainingConfig):
        self.config = config
        self.tokenizer = T5Tokenizer.from_pretrained(config.model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(config.model_name)

        # Add special tokens if needed
        special_tokens = {
            "additional_special_tokens": [
                "[WEEK]",
                "[ASSESSMENT]",
                "[OBJECTIVE]",
                "[POLICY]",
            ]
        }
        self.tokenizer.add_special_tokens(special_tokens)
        self.model.resize_token_embeddings(len(self.tokenizer))

        logger.info(f"Initialized T5 model: {config.model_name}")
        logger.info(f"Vocabulary size: {len(self.tokenizer)}")

    def load_syllabus_data(self, data_path: str) -> list[dict[str, Any]]:
        """Load syllabus dataset"""
        logger.info(f"Loading syllabus data from: {data_path}")

        with open(data_path) as f:
            syllabi = json.load(f)

        logger.info(f"Loaded {len(syllabi)} syllabi")
        return syllabi

    def prepare_training_examples(
        self, syllabi: list[dict[str, Any]]
    ) -> list[dict[str, str]]:
        """Convert syllabus data into training examples"""
        logger.info("Preparing training examples...")

        examples = []

        for syllabus in syllabi:
            course_info = syllabus["course_info"]
            syllabus_template = syllabus["syllabus_template"]

            # Create input text (course requirements)
            input_text = self.format_course_input(course_info)

            # Target text is the syllabus template
            target_text = syllabus_template

            examples.append(
                {
                    "input_text": input_text,
                    "target_text": target_text,
                    "course_id": syllabus.get("course_template_id", "unknown"),
                }
            )

        logger.info(f"Created {len(examples)} training examples")
        return examples

    def format_course_input(self, course_info: dict[str, Any]) -> str:
        """Format course information as input prompt"""

        input_parts = [
            f"Generate syllabus for: {course_info.get('title', '')}",
            f"Domain: {course_info.get('department', '')} Level: {course_info.get('level', '')}",
            f"Duration: {course_info.get('duration', 'semester')}",
            f"Description: {course_info.get('description', '')}",
        ]

        # Add learning objectives
        objectives = course_info.get("learning_objectives", [])
        if objectives:
            input_parts.append("Learning Objectives:")
            for obj in objectives[:3]:  # Limit to 3 for input length
                input_parts.append(f"- {obj}")

        # Add target audience
        if course_info.get("target_audience"):
            input_parts.append(f"Target Audience: {course_info['target_audience']}")

        return "\n".join(input_parts)

    def split_data(
        self, examples: list[dict[str, str]], test_size: float = 0.2
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        """Split data into train/validation sets"""

        train_examples, val_examples = train_test_split(
            examples, test_size=test_size, random_state=42, shuffle=True
        )

        logger.info(
            f"Split data: {len(train_examples)} train, {len(val_examples)} validation"
        )
        return train_examples, val_examples

    def train(self, data_path: str):
        """Fine-tune T5 model on syllabus generation"""

        # Load and prepare data
        syllabi = self.load_syllabus_data(data_path)
        examples = self.prepare_training_examples(syllabi)
        train_examples, val_examples = self.split_data(examples)

        # Create datasets
        train_dataset = SyllabusDataset(train_examples, self.tokenizer, self.config)
        val_dataset = SyllabusDataset(val_examples, self.tokenizer, self.config)

        # Data collator
        data_collator = DataCollatorForSeq2Seq(
            tokenizer=self.tokenizer, model=self.model, padding=True
        )

        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.train_batch_size,
            per_device_eval_batch_size=self.config.eval_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            warmup_steps=self.config.warmup_steps,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_steps=self.config.eval_steps,
            eval_strategy="steps",  # Updated parameter name
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            remove_unused_columns=False,
            dataloader_pin_memory=False,
            fp16=torch.cuda.is_available(),
            report_to=[],  # Disable wandb logging
        )

        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            data_collator=data_collator,
            tokenizer=self.tokenizer,
        )

        # Train the model
        logger.info("Starting training...")
        trainer.train()

        # Save the final model
        logger.info(f"Saving final model to: {self.config.output_dir}")
        trainer.save_model()
        self.tokenizer.save_pretrained(self.config.output_dir)

        return trainer

    def generate_syllabus(
        self, course_requirements: str, model_path: str = None
    ) -> str:
        """Generate syllabus using fine-tuned model"""

        # Load fine-tuned model if path provided
        if model_path:
            self.model = T5ForConditionalGeneration.from_pretrained(model_path)
            self.tokenizer = T5Tokenizer.from_pretrained(model_path)

        # Tokenize input
        inputs = self.tokenizer(
            course_requirements,
            max_length=self.config.max_input_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_length=self.config.max_target_length,
                num_beams=4,
                early_stopping=True,
                do_sample=False,
                temperature=0.7,
                repetition_penalty=1.1,
            )

        # Decode output
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text


def main():
    """Main training function"""

    # Configuration
    config = SyllabusTrainingConfig(
        model_name="t5-small",
        num_epochs=3,
        train_batch_size=2,  # Smaller for memory
        eval_batch_size=2,
        learning_rate=3e-4,
        output_dir="./models/t5-syllabus-finetuned",
    )

    # Initialize trainer
    trainer = SyllabusTrainer(config)

    # Path to syllabus dataset
    data_path = "data/assembled_syllabi/syllabi_dataset.json"

    if not Path(data_path).exists():
        logger.error(f"Dataset not found: {data_path}")
        return

    # Train the model
    try:
        trainer.train(data_path)
        logger.info("✅ Training completed successfully!")

        # Test generation
        test_input = """Generate syllabus for: Introduction to Machine Learning
Domain: Computer Science Level: undergraduate
Duration: semester
Description: Fundamentals of machine learning algorithms and applications
Learning Objectives:
- Understand supervised and unsupervised learning
- Implement basic ML algorithms
- Evaluate model performance"""

        logger.info("Testing generation with fine-tuned model...")
        generated = trainer.generate_syllabus(test_input, config.output_dir)
        logger.info("Generated syllabus preview:")
        logger.info(generated[:500] + "..." if len(generated) > 500 else generated)

    except Exception as e:
        logger.error(f"Training failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
