#!/usr/bin/env python3
"""
T5 Function Call Trainer - OPTIMIZED

Fine-tune T5-small to generate executable function calls for syllabus construction.
Optimized for small dataset (260 examples) with best practices for academic research.
"""

import json
import logging
import random
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch
from datasets import Dataset
from transformers import (
    DataCollatorForSeq2Seq,
    EarlyStoppingCallback,
    T5ForConditionalGeneration,
    T5Tokenizer,
    Trainer,
    TrainingArguments,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def set_seed(seed: int = 42):
    """Set random seeds for reproducibility (critical for academic work)."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    logger.info(f"🌱 Random seed set to {seed} for reproducibility")


def load_function_call_data(file_path: Path) -> List[Dict[str, str]]:
    """Load function call training data."""
    with open(file_path, "r") as f:
        data = json.load(f)

    logger.info(f"✅ Loaded {len(data)} function call training examples")
    return data


def analyze_dataset_lengths(examples: List[Dict[str, str]], tokenizer):
    """Analyze token lengths to set optimal max_length parameters."""
    input_lengths = []
    output_lengths = []

    for example in examples:
        input_tokens = tokenizer(example["input_text"])["input_ids"]
        output_tokens = tokenizer(example["output_calls"])["input_ids"]
        input_lengths.append(len(input_tokens))
        output_lengths.append(len(output_tokens))

    logger.info("\n📊 Dataset Length Analysis:")
    logger.info(
        f"   Input tokens  - Mean: {np.mean(input_lengths):.0f}, Max: {max(input_lengths)}, 95th percentile: {np.percentile(input_lengths, 95):.0f}"
    )
    logger.info(
        f"   Output tokens - Mean: {np.mean(output_lengths):.0f}, Max: {max(output_lengths)}, 95th percentile: {np.percentile(output_lengths, 95):.0f}"
    )

    return int(np.percentile(input_lengths, 95)), int(np.percentile(output_lengths, 95))


def prepare_training_data(
    examples: List[Dict[str, str]],
    tokenizer,
    max_input_length: int,
    max_output_length: int,
) -> Dataset:
    """Prepare training data with proper length filtering."""

    filtered_examples = []
    for example in examples:
        input_tokens = tokenizer(example["input_text"])["input_ids"]
        output_tokens = tokenizer(example["output_calls"])["input_ids"]

        # Only filter examples that are SIGNIFICANTLY longer than our limits
        if (
            len(input_tokens) <= max_input_length * 1.2  # Allow 20% overflow
            and len(output_tokens) <= max_output_length * 1.2
        ):
            filtered_examples.append(example)

    removed = len(examples) - len(filtered_examples)
    if removed > 0:
        logger.warning(f"⚠️  Removed {removed} examples that were too long")

    logger.info(f"✅ Using {len(filtered_examples)} training examples")

    # Convert to HuggingFace Dataset format
    dataset_dict = {
        "input_text": [ex["input_text"] for ex in filtered_examples],
        "output_calls": [ex["output_calls"] for ex in filtered_examples],
    }

    return Dataset.from_dict(dataset_dict)


def tokenize_function(
    examples, tokenizer, max_input_length: int, max_output_length: int
):
    """Tokenization function for dataset mapping."""
    # Tokenize inputs
    inputs = tokenizer(
        examples["input_text"],
        truncation=True,
        max_length=max_input_length,
        padding="max_length",
    )

    # Tokenize targets (labels)
    targets = tokenizer(
        examples["output_calls"],
        truncation=True,
        max_length=max_output_length,
        padding="max_length",
    )

    inputs["labels"] = targets["input_ids"]

    return inputs


def train_function_call_model():
    """Train T5 model for function call generation with optimized hyperparameters."""

    logger.info("🚀 Starting Optimized T5 Function Call Training")
    logger.info("=" * 80)

    # Set reproducibility seed
    set_seed(42)

    # Load model and tokenizer
    model_name = "t5-small"
    logger.info(f"📦 Loading {model_name} model...")
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)

    # Enable gradient checkpointing for memory efficiency
    model.gradient_checkpointing_enable()
    logger.info("✅ Gradient checkpointing enabled (reduces memory usage)")

    # Load training data
    base_dir = Path(__file__).parent.parent
    data_file = base_dir / "data" / "training" / "rag_enhanced_t5_training.json"

    if not data_file.exists():
        logger.error(f"❌ RAG-enhanced training data not found: {data_file}")
        logger.error("   Run: python scripts/generate_claude_enhanced_training_data.py")
        return

    logger.info(f"📂 Loading training data from: {data_file}")
    examples = load_function_call_data(data_file)

    # Analyze dataset to determine optimal max_length parameters
    max_input_length, max_output_length = analyze_dataset_lengths(examples, tokenizer)

    # Add some buffer for safety, but cap at reasonable limits
    max_input_length = min(max_input_length + 50, 640)  # Cap at 640
    max_output_length = min(max_output_length + 100, 768)  # Cap at 768

    logger.info(
        f"\n⚙️  Using max lengths: Input={max_input_length}, Output={max_output_length}"
    )

    # Prepare training data
    logger.info("\n🔧 Preparing training dataset...")
    dataset = prepare_training_data(
        examples, tokenizer, max_input_length, max_output_length
    )

    # Tokenize dataset
    logger.info("🔤 Tokenizing dataset...")
    tokenized_dataset = dataset.map(
        lambda x: tokenize_function(x, tokenizer, max_input_length, max_output_length),
        batched=True,
        remove_columns=dataset.column_names,
    )

    # Train/validation split (90/10)
    train_size = int(0.9 * len(tokenized_dataset))
    train_dataset = tokenized_dataset.select(range(train_size))
    eval_dataset = tokenized_dataset.select(range(train_size, len(tokenized_dataset)))

    logger.info("\n📊 Dataset Split:")
    logger.info(f"   Training examples: {len(train_dataset)}")
    logger.info(f"   Validation examples: {len(eval_dataset)}")

    # Calculate optimal training steps
    batch_size = 4
    gradient_accumulation_steps = 4  # Effective batch size = 16
    num_epochs = 10  # More epochs with early stopping

    steps_per_epoch = len(train_dataset) // (batch_size * gradient_accumulation_steps)
    total_steps = steps_per_epoch * num_epochs
    warmup_steps = int(0.1 * total_steps)  # 10% warmup

    logger.info("\n📈 Training Configuration:")
    logger.info(f"   Batch size per device: {batch_size}")
    logger.info(f"   Gradient accumulation steps: {gradient_accumulation_steps}")
    logger.info(f"   Effective batch size: {batch_size * gradient_accumulation_steps}")
    logger.info(f"   Number of epochs: {num_epochs}")
    logger.info(f"   Steps per epoch: {steps_per_epoch}")
    logger.info(f"   Total training steps: {total_steps}")
    logger.info(f"   Warmup steps: {warmup_steps}")

    # Optimized training arguments for small dataset fine-tuning
    training_args = TrainingArguments(
        output_dir="./models/t5-function-call-finetuned",
        # Training schedule
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        # Learning rate (higher for small dataset fine-tuning)
        learning_rate=3e-4,  # 0.0003 - optimal for small dataset T5 fine-tuning
        warmup_steps=warmup_steps,
        lr_scheduler_type="linear",  # Linear decay after warmup
        # Regularization (prevent overfitting on small dataset)
        weight_decay=0.01,
        label_smoothing_factor=0.1,  # Helps with overfitting
        max_grad_norm=1.0,  # Gradient clipping
        # Evaluation and saving
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=3,  # Keep only 3 best checkpoints
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        # Logging
        logging_dir="./logs",
        logging_steps=10,
        logging_first_step=True,
        report_to="none",  # Disable wandb
        # Performance optimization
        fp16=torch.cuda.is_available(),  # Use mixed precision if GPU available
        dataloader_num_workers=0,  # CPU training
        # Reproducibility
        seed=42,
        data_seed=42,
    )

    logger.info("\n🎯 Hyperparameters:")
    logger.info(f"   Learning rate: {training_args.learning_rate}")
    logger.info(f"   Weight decay: {training_args.weight_decay}")
    logger.info(f"   Label smoothing: {training_args.label_smoothing_factor}")
    logger.info(f"   Max gradient norm: {training_args.max_grad_norm}")
    logger.info(f"   LR scheduler: {training_args.lr_scheduler_type}")
    logger.info(f"   FP16 training: {training_args.fp16}")

    # Data collator
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        padding=True,
    )

    # Early stopping callback (stop if no improvement for 3 epochs)
    early_stopping = EarlyStoppingCallback(
        early_stopping_patience=3,
        early_stopping_threshold=0.001,  # Minimum improvement threshold
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
        callbacks=[early_stopping],
    )

    # Train the model
    logger.info("\n" + "=" * 80)
    logger.info("🏋️  Starting Training...")
    logger.info("=" * 80 + "\n")

    train_result = trainer.train()

    # Log training results
    logger.info("\n" + "=" * 80)
    logger.info("📊 Training Results:")
    logger.info(f"   Final train loss: {train_result.training_loss:.4f}")
    logger.info(
        f"   Training time: {train_result.metrics['train_runtime']:.2f} seconds"
    )
    logger.info(
        f"   Samples per second: {train_result.metrics['train_samples_per_second']:.2f}"
    )
    logger.info("=" * 80)

    # Evaluate final model
    logger.info("\n🧪 Evaluating final model...")
    eval_results = trainer.evaluate()
    logger.info(f"   Final eval loss: {eval_results['eval_loss']:.4f}")

    # Save model
    logger.info("\n💾 Saving final model...")
    trainer.save_model()
    tokenizer.save_pretrained("./models/t5-function-call-finetuned")

    logger.info("\n" + "=" * 80)
    logger.info("✅ T5 Function Call Training Complete!")
    logger.info("📁 Model saved to: ./models/t5-function-call-finetuned")
    logger.info("=" * 80)

    return model, tokenizer, max_output_length


def test_function_call_generation(model, tokenizer, max_output_length: int):
    """Test the trained function call model with multiple examples."""

    logger.info("\n" + "=" * 80)
    logger.info("🧪 Testing Trained Model")
    logger.info("=" * 80)

    # Test cases covering different domains and levels
    test_cases = [
        {
            "title": "Introduction to Machine Learning",
            "domain": "computer_science",
            "level": "intermediate",
            "description": "Fundamentals of supervised and unsupervised learning",
        },
        {
            "title": "Calculus I",
            "domain": "mathematics",
            "level": "beginner",
            "description": "Limits, derivatives, and basic integration",
        },
        {
            "title": "Quantum Mechanics",
            "domain": "physics",
            "level": "advanced",
            "description": "Wave functions and Schrodinger equation",
        },
    ]

    model.eval()
    success_count = 0

    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n📝 Test {i}/{len(test_cases)}: {test_case['title']}")
        logger.info(f"   Domain: {test_case['domain']}, Level: {test_case['level']}")

        input_data = {
            "title": test_case["title"],
            "domain": test_case["domain"],
            "level": test_case["level"],
            "duration": "semester",
            "description": test_case["description"],
        }

        input_text = f"Generate course syllabus: {json.dumps(input_data)}"

        # Generate with greedy decoding for deterministic output
        input_ids = tokenizer(
            input_text,
            return_tensors="pt",
            max_length=640,
            truncation=True,
            padding=True,
        ).input_ids

        with torch.no_grad():
            generated_tokens = model.generate(
                input_ids,
                max_length=max_output_length,
                num_beams=4,  # Beam search for better quality
                early_stopping=True,
                no_repeat_ngram_size=2,  # Prevent repetition
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

        generated_calls = tokenizer.decode(
            generated_tokens[0], skip_special_tokens=True
        )

        # Validate structure
        has_builder = "SyllabusBuilder()" in generated_calls
        has_module_call = "add_module_by_id" in generated_calls
        has_activity_call = "add_activity_by_id" in generated_calls

        if has_builder and has_module_call and has_activity_call:
            logger.info("   ✅ PASS - Valid function call structure")
            success_count += 1
        else:
            logger.info("   ❌ FAIL - Missing expected structure")

        logger.info(f"   Generated: {generated_calls[:150]}...")

    logger.info(f"\n📊 Test Results: {success_count}/{len(test_cases)} passed")
    return success_count == len(test_cases)


def main():
    """Main training and testing pipeline."""

    try:
        # Train the model
        model, tokenizer, max_output_length = train_function_call_model()

        # Test the model
        success = test_function_call_generation(model, tokenizer, max_output_length)

        if success:
            logger.info("\n🎉 SUCCESS! Model is ready for deployment.")
            logger.info("\n📋 Next Steps:")
            logger.info(
                "   1. Upload to Hugging Face: python scripts/upload_model_to_huggingface.py"
            )
            logger.info("   2. Add HF_MODEL_ID to Streamlit Cloud secrets")
            logger.info("   3. Test in production")
        else:
            logger.warning("\n⚠️  Model needs improvement. Consider:")
            logger.warning("   - Generating more training data")
            logger.warning("   - Adjusting hyperparameters")
            logger.warning("   - Increasing training epochs")

    except Exception as e:
        logger.error(f"\n❌ Training failed: {e}")
        raise


if __name__ == "__main__":
    main()
