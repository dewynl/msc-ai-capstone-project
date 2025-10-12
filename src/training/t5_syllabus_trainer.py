#!/usr/bin/env python3
"""
T5 Syllabus Generation Fine-tuning Script
Fine-tune T5 model on structured syllabus generation task using JSON format
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

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
    max_input_length: int = 512  # For JSON course requirements
    max_target_length: int = (
        2048  # Increased for complete JSON syllabus output
    )
    train_batch_size: int = 2  # Smaller batch due to longer sequences
    eval_batch_size: int = 2
    learning_rate: float = 3e-4
    num_epochs: int = 3
    warmup_steps: int = 500
    logging_steps: int = 50
    save_steps: int = 250
    eval_steps: int = 250
    output_dir: str = "./models/t5-syllabus-finetuned"
    gradient_accumulation_steps: int = 8  # Higher accumulation for smaller batches


class SyllabusDataset(Dataset):
    """Dataset for syllabus generation training"""

    def __init__(
        self,
        examples: List[Dict[str, str]],
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

        # Input: JSON course requirements with special prefix
        input_text = f"generate syllabus: {example['input_json']}"

        # Target: JSON syllabus structure
        target_text = example["output_json"]

        # Tokenize input (course requirements JSON)
        input_encoding = self.tokenizer(
            input_text,
            max_length=self.config.max_input_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        # Tokenize target (syllabus JSON)
        target_encoding = self.tokenizer(
            target_text,
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
        special_tokens = ["<course>", "</course>", "<syllabus>", "</syllabus>"]
        self.tokenizer.add_tokens(special_tokens)
        self.model.resize_token_embeddings(len(self.tokenizer))

    def load_json_training_data(self, data_path: str) -> List[Dict[str, Any]]:
        """Load JSON training dataset"""
        logger.info(f"Loading JSON training data from: {data_path}")

        with open(data_path) as f:
            training_examples = json.load(f)

        logger.info(f"Loaded {len(training_examples)} JSON training examples")
        return training_examples

    def prepare_training_examples(
        self, json_examples: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Prepare training examples (already in correct format)"""
        logger.info("Preparing JSON training examples...")

        # Filter out examples that are too long
        filtered_examples = []
        for example in json_examples:
            input_length = len(example["input_json"])
            output_length = len(example["output_json"])

            # Check if they fit within our token limits (rough estimate: 4 chars per token)
            if (
                input_length < self.config.max_input_length * 4
                and output_length < self.config.max_target_length * 4
            ):
                filtered_examples.append(example)
            else:
                logger.debug(
                    f"Skipping example {example.get('original_id', 'unknown')}: too long"
                )

        logger.info(
            f"Filtered to {len(filtered_examples)} examples (removed {len(json_examples) - len(filtered_examples)} too long)"
        )
        return filtered_examples

    def train(self, data_path: str):
        """Train the JSON syllabus generation model"""
        logger.info("🚀 Starting JSON T5 Syllabus Training")

        # Load and prepare data
        json_examples = self.load_json_training_data(data_path)
        training_examples = self.prepare_training_examples(json_examples)

        if len(training_examples) == 0:
            raise ValueError("No training examples available!")

        # Split into train/validation
        train_examples, val_examples = train_test_split(
            training_examples, test_size=0.1, random_state=42
        )

        logger.info(f"Training examples: {len(train_examples)}")
        logger.info(f"Validation examples: {len(val_examples)}")

        # Create datasets
        train_dataset = SyllabusDataset(train_examples, self.tokenizer, self.config)
        val_dataset = SyllabusDataset(val_examples, self.tokenizer, self.config)

        # Create data collator
        data_collator = DataCollatorForSeq2Seq(
            tokenizer=self.tokenizer,
            model=self.model,
            label_pad_token_id=-100,
            pad_to_multiple_of=8,
        )

        # Setup training arguments
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            overwrite_output_dir=True,
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.train_batch_size,
            per_device_eval_batch_size=self.config.eval_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            warmup_steps=self.config.warmup_steps,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_steps=self.config.eval_steps,
            eval_strategy="steps",
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            dataloader_pin_memory=False,
            fp16=torch.cuda.is_available(),  # Use mixed precision if CUDA available
            report_to=[],  # Disable wandb/tensorboard
        )

        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
        )

        # Train the model
        logger.info("Starting training...")
        trainer.train()

        # Save the final model
        logger.info("Saving final model...")
        trainer.save_model()
        self.tokenizer.save_pretrained(self.config.output_dir)

        logger.info("✅ JSON T5 training complete!")
        logger.info(f"📁 Model saved to: {self.config.output_dir}")

    def generate_syllabus(self, course_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a syllabus from course requirements using the trained model"""

        # Convert requirements to JSON string
        input_json = json.dumps(course_requirements, separators=(",", ":"))
        input_text = f"generate syllabus: {input_json}"

        # Tokenize input
        inputs = self.tokenizer(
            input_text,
            max_length=self.config.max_input_length,
            padding=True,
            truncation=True,
            return_tensors="pt",
        )

        # Generate output
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=self.config.max_target_length,
                min_length=100,  # Ensure minimum output length
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=2,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        # Decode output
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        try:
            # Parse JSON output
            syllabus_json = json.loads(generated_text)
            return syllabus_json
        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON parse failed: {e}")
            logger.info("Attempting to repair JSON...")

            # Attempt to repair common JSON issues
            repaired_text = self._repair_json(generated_text)

            try:
                syllabus_json = json.loads(repaired_text)
                logger.info("✅ JSON repair successful!")
                return syllabus_json
            except json.JSONDecodeError as e2:
                logger.error(f"JSON repair failed: {e2}")
                logger.error(f"Original: {generated_text}")
                logger.error(f"Repaired: {repaired_text}")
                return {
                    "error": "Failed to generate valid JSON",
                    "raw_output": generated_text,
                    "repaired_attempt": repaired_text,
                }

    def _repair_json(self, text: str) -> str:
        """Attempt to repair common JSON formatting issues"""
        # Remove any leading/trailing whitespace
        text = text.strip()

        # Add opening brace if missing
        if not text.startswith('{'):
            text = '{' + text

        # Add closing brace if missing
        if not text.endswith('}'):
            text = text + '}'

        # Fix common field issues
        text = text.replace('"prerequisite:"', '"prerequisites":')
        text = text.replace('""target_audience"', '", "target_audience":')

        # Fix missing quotes around values
        import re
        # Fix patterns like: "field":value without quotes around value
        text = re.sub(r'"([^"]+)":\s*([^",}\]]+)(?=[,}])', r'"\1": "\2"', text)

        # Fix double quotes issues
        text = re.sub(r'""([^"]*)"', r'", "\1":', text)

        # Ensure proper comma separation
        text = re.sub(r'}\s*{', '},{', text)

        return text


def test_json_generation():
    """Test the JSON generation with a sample"""

    logger.info("🧪 Testing JSON syllabus generation")

    # Sample course requirements for 3-domain system
    test_requirements = {
        "title": "Introduction to Machine Learning",
        "domain": "computer_science",
        "level": "intermediate",
        "duration": "semester",
        "description": "Fundamentals of machine learning algorithms and applications",
        "learning_objectives": [
            "Understand supervised and unsupervised learning",
            "Implement basic ML algorithms",
            "Evaluate model performance",
        ],
        "prerequisites": "Linear algebra, statistics, programming",
        "target_audience": "Intermediate students in Computer Science",
    }

    # Load trained model
    config = SyllabusTrainingConfig()
    trainer = SyllabusTrainer(config)

    try:
        # Generate syllabus
        result = trainer.generate_syllabus(test_requirements)

        print("📝 Generated Syllabus JSON:")
        print(json.dumps(result, indent=2))

        return result

    except Exception as e:
        logger.error(f"Generation test failed: {e}")
        return None


def main():
    """Main training function"""

    # Setup configuration
    config = SyllabusTrainingConfig()

    # Create trainer
    trainer = SyllabusTrainer(config)

    # Train on clean JSON data
    training_data_path = "data/training/t5_clean_training.json"

    if not Path(training_data_path).exists():
        logger.error(f"Training data not found: {training_data_path}")
        logger.info("Please run create_clean_training_data.py first")
        return

    # Start training
    trainer.train(training_data_path)

    # Test generation
    logger.info("\n" + "=" * 60)
    test_json_generation()


if __name__ == "__main__":
    main()
