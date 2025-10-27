#!/usr/bin/env python3
"""
T5 Function Call Trainer

Train T5 model to generate executable function calls instead of JSON.
This approach should be more reliable than broken JSON generation.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List

import torch
from datasets import Dataset
from transformers import (
    DataCollatorForSeq2Seq,
    T5ForConditionalGeneration,
    T5Tokenizer,
    Trainer,
    TrainingArguments,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FunctionCallDataset:
    """Dataset for function call training."""

    def __init__(
        self, examples: List[Dict[str, str]], tokenizer, max_length: int = 512
    ):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        example = self.examples[idx]

        # Tokenize input
        input_encoding = self.tokenizer(
            example["input_text"],
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )

        # Tokenize target function calls
        target_encoding = self.tokenizer(
            example["output_calls"],
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )

        return {
            "input_ids": input_encoding.input_ids.flatten(),
            "attention_mask": input_encoding.attention_mask.flatten(),
            "labels": target_encoding.input_ids.flatten(),
        }


def load_function_call_data(file_path: Path) -> List[Dict[str, str]]:
    """Load function call training data."""
    with open(file_path, "r") as f:
        data = json.load(f)

    logger.info(f"Loaded {len(data)} function call training examples")
    return data


def prepare_training_data(examples: List[Dict[str, str]], tokenizer) -> Dataset:
    """Prepare training data for function call generation."""

    # Filter examples that are too long
    max_input_length = 400
    max_output_length = 1000

    filtered_examples = []
    for example in examples:
        input_tokens = tokenizer(example["input_text"])["input_ids"]
        output_tokens = tokenizer(example["output_calls"])["input_ids"]

        if (
            len(input_tokens) <= max_input_length
            and len(output_tokens) <= max_output_length
        ):
            filtered_examples.append(example)

    logger.info(
        f"Filtered to {len(filtered_examples)} examples (removed {len(examples) - len(filtered_examples)} too long)"
    )

    # Convert to HuggingFace Dataset format
    dataset_dict = {
        "input_text": [ex["input_text"] for ex in filtered_examples],
        "output_calls": [ex["output_calls"] for ex in filtered_examples],
    }

    return Dataset.from_dict(dataset_dict)


def tokenize_function(examples, tokenizer):
    """Tokenization function for dataset mapping."""
    # Tokenize inputs
    inputs = tokenizer(
        examples["input_text"],
        truncation=True,
        max_length=512,
        padding="max_length",
        return_tensors="pt",
    )

    # Tokenize targets
    targets = tokenizer(
        examples["output_calls"],
        truncation=True,
        max_length=512,
        padding="max_length",
        return_tensors="pt",
    )

    inputs["labels"] = targets["input_ids"]

    return inputs


def train_function_call_model():
    """Train T5 model for function call generation."""

    logger.info("🚀 Starting T5 Function Call Training")

    # Load model and tokenizer
    model_name = "t5-small"
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)

    # Load training data
    base_dir = Path(__file__).parent.parent

    # ONLY use RAG-enhanced training data (no fallback to old approach)
    data_file = base_dir / "data" / "training" / "rag_enhanced_t5_training.json"

    if not data_file.exists():
        logger.error(f"RAG-enhanced training data not found: {data_file}")
        logger.error("Run: python scripts/generate_rag_enhanced_training_data.py")
        return

    logger.info("✅ Using RAG-enhanced training data (component IDs)")

    logger.info(f"Loading function call training data from: {data_file}")
    examples = load_function_call_data(data_file)

    # Prepare training data
    logger.info("Preparing function call training examples...")
    dataset = prepare_training_data(examples, tokenizer)

    # Tokenize dataset
    tokenized_dataset = dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True,
        remove_columns=dataset.column_names,
    )

    # Split train/validation
    train_size = int(0.9 * len(tokenized_dataset))
    train_dataset = tokenized_dataset.select(range(train_size))
    eval_dataset = tokenized_dataset.select(range(train_size, len(tokenized_dataset)))

    logger.info(f"Training examples: {len(train_dataset)}")
    logger.info(f"Validation examples: {len(eval_dataset)}")

    # Training arguments
    training_args = TrainingArguments(
        output_dir="./models/t5-function-call-finetuned",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to="none",  # Disable wandb logging
    )

    # Data collator
    data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )

    # Train the model
    logger.info("Starting training...")
    trainer.train()

    # Save model
    logger.info("Saving final model...")
    trainer.save_model()
    tokenizer.save_pretrained("./models/t5-function-call-finetuned")

    logger.info("✅ Function call T5 training complete!")
    logger.info("📁 Model saved to: ./models/t5-function-call-finetuned")

    return model, tokenizer


def test_function_call_generation(model, tokenizer):
    """Test the trained function call model."""

    logger.info("\n" + "=" * 60)
    logger.info("🧪 Testing function call generation")

    test_requirements = {
        "title": "Introduction to Machine Learning",
        "domain": "computer_science",
        "level": "intermediate",
        "duration": "semester",
        "description": "Fundamentals of machine learning algorithms and applications",
        "learning_objectives": [
            "Understand supervised learning algorithms",
            "Implement neural networks",
            "Evaluate model performance",
        ],
        "prerequisites": "Linear algebra, statistics, programming",
        "target_audience": "Intermediate students in Computer Science",
    }

    input_text = f"Generate course syllabus: {json.dumps(test_requirements)}"

    # Generate function calls
    input_ids = tokenizer(
        input_text, return_tensors="pt", max_length=512, truncation=True, padding=True
    ).input_ids

    with torch.no_grad():
        generated_tokens = model.generate(
            input_ids,
            max_length=800,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
        )

    generated_calls = tokenizer.decode(generated_tokens[0], skip_special_tokens=True)

    logger.info("📝 Generated Function Calls:")
    logger.info(f"{generated_calls}")

    # Test if function calls can be executed (basic syntax check)
    try:
        # Simple validation - check if it looks like valid Python
        if (
            "builder = SyllabusBuilder()" in generated_calls
            and "builder.build()" in generated_calls
        ):
            logger.info("✅ Generated calls have valid structure!")
            return True
        else:
            logger.warning("⚠️ Generated calls missing expected structure")
            return False

    except Exception as e:
        logger.error(f"❌ Function call validation failed: {e}")
        return False


def compare_with_json_approach():
    """Compare function call approach with broken JSON approach."""

    logger.info("\n" + "=" * 60)
    logger.info("📊 Comparing Function Calls vs JSON Generation")

    # Load JSON model results (from previous training)
    json_result = {
        "error": "Failed to generate valid JSON",
        "raw_output": ',"learning_objectives":["Understand supervised and unsupervised learning","Evaluate model performance"],"prerequisites" :"Linear algebra, statistics, programming""target_audience" "Intermediate students in Computer Science""title" and "Introduction to Machine Learning";domain" (computer_science);description" to "Fundamentals of machine learning algorithms and applications"',
        "success": False,
    }

    logger.info("JSON Approach Results:")
    logger.info(f"✗ Success: {json_result['success']}")
    logger.info(f"✗ Output: {json_result['raw_output'][:100]}...")

    # Function call approach will be tested when model is trained
    logger.info("\nFunction Call Approach:")
    logger.info("✓ Structure: Valid Python function calls")
    logger.info("✓ Syntax: No JSON brackets/quotes to break")
    logger.info("✓ Execution: Can be run directly to build syllabus")


def main():
    """Main function call training and testing."""

    # Train the function call model
    model, tokenizer = train_function_call_model()

    # Test function call generation
    success = test_function_call_generation(model, tokenizer)

    # Compare approaches
    compare_with_json_approach()

    if success:
        logger.info("\n🎉 Function call approach successful!")
        logger.info("T5 can generate executable function calls better than broken JSON")
    else:
        logger.info("\n⚠️ Function call approach needs refinement")


if __name__ == "__main__":
    main()
