#!/usr/bin/env python3
"""
Training Script for Sequenced Syllabus Generation (Tier 1 Implementation)

Trains CodeT5 to:
1. Sequence modules intelligently (prerequisites, difficulty progression)
2. Generate custom learning objectives (context-specific, mentions module content)
3. Allocate weeks based on estimated hours
4. Demonstrate pedagogical reasoning

Training Data: 1,300 examples with intelligent module sequencing
Expected Duration: ~7 hours (increased due to longer output sequences)
"""

import json
import logging
import random
import time
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch
from datasets import Dataset
from transformers import (
    DataCollatorForSeq2Seq,
    EarlyStoppingCallback,
    RobertaTokenizer,
    T5ForConditionalGeneration,
    Trainer,
    TrainerCallback,
    TrainingArguments,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProgressCallback(TrainerCallback):
    """Custom callback to track training progress and estimate time remaining."""

    def __init__(self, total_epochs: int):
        self.total_epochs = total_epochs
        self.start_time = None
        self.epoch_start_time = None

    def on_train_begin(self, args, state, control, **kwargs):
        self.start_time = time.time()
        logger.info("\n⏱️  Training started. Tracking progress...\n")

    def on_epoch_begin(self, args, state, control, **kwargs):
        self.epoch_start_time = time.time()

    def on_epoch_end(self, args, state, control, **kwargs):
        epoch_time = time.time() - self.epoch_start_time
        total_time = time.time() - self.start_time
        current_epoch = state.epoch

        # Estimate remaining time
        avg_time_per_epoch = total_time / current_epoch
        remaining_epochs = self.total_epochs - current_epoch
        estimated_remaining = avg_time_per_epoch * remaining_epochs

        logger.info(f"\n📊 Epoch {current_epoch}/{self.total_epochs} complete")
        logger.info(f"   Epoch time: {epoch_time/60:.1f} min")
        logger.info(f"   Avg time/epoch: {avg_time_per_epoch/60:.1f} min")
        logger.info(f"   Estimated remaining: {estimated_remaining/3600:.1f} hours")
        logger.info(f"   Total elapsed: {total_time/3600:.1f} hours\n")


def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_training_data(file_path: Path) -> List[Dict[str, str]]:
    with open(file_path, "r") as f:
        data = json.load(f)
    logger.info(f"✅ Loaded {len(data)} training examples")
    return data


def prepare_dataset(
    examples: List[Dict[str, str]], tokenizer, max_input: int, max_output: int
) -> Dataset:
    """
    Prepare dataset for sequenced training.

    Note: Uses 'output_markdown' field (not 'output_calls')
    """
    dataset = Dataset.from_dict(
        {
            "input_text": [ex["input_text"] for ex in examples],
            "output_markdown": [ex["output_markdown"] for ex in examples],
        }
    )

    def tokenize(batch):
        inputs = tokenizer(
            batch["input_text"],
            truncation=True,
            max_length=max_input,
            padding="max_length",
        )
        targets = tokenizer(
            batch["output_markdown"],
            truncation=True,
            max_length=max_output,
            padding="max_length",
        )
        inputs["labels"] = targets["input_ids"]
        return inputs

    tokenized = dataset.map(tokenize, batched=True, remove_columns=dataset.column_names)
    return tokenized


def run_sequenced_training(
    data_file: str = "data/training/sequenced_t5_training.json",
    num_epochs: int = 15,
    batch_size: int = 20,
    grad_accum: int = 4,
):
    """
    Run training for sequenced syllabus generation.

    Args:
        data_file: Path to sequenced training data
        num_epochs: Number of training epochs (default: 15)
        batch_size: Per-device batch size (default: 20)
        grad_accum: Gradient accumulation steps (default: 4)
    """

    logger.info("=" * 80)
    logger.info("🚀 TRAINING SEQUENCED SYLLABUS GENERATION (TIER 1)")
    logger.info("=" * 80)
    logger.info(f"Data file: {data_file}")
    logger.info(f"Epochs: {num_epochs}")
    logger.info(f"Effective batch size: {batch_size * grad_accum}")
    logger.info("\nModel will learn to:")
    logger.info("  1. Sequence modules intelligently (prerequisites, difficulty)")
    logger.info("  2. Generate custom learning objectives (specific to modules)")
    logger.info("  3. Allocate weeks based on estimated hours")
    logger.info("  4. Demonstrate pedagogical reasoning")
    logger.info("=" * 80)

    set_seed(42)

    # Load fresh model
    model_name = "Salesforce/codet5-small"
    logger.info(f"\n📦 Loading fresh model: {model_name}")

    tokenizer = RobertaTokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name, use_safetensors=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    logger.info(f"✅ Model on {device}")

    model.gradient_checkpointing_enable()

    # Load data
    base_dir = Path(__file__).parent.parent
    data_path = base_dir / data_file
    examples = load_training_data(data_path)

    # Prepare dataset (LONGER max_output for sequenced format with week ranges)
    max_input = 640
    max_output = 600  # Increased from 536 - sequenced format is longer
    tokenized_dataset = prepare_dataset(examples, tokenizer, max_input, max_output)

    # Split (90/10)
    train_size = int(0.9 * len(tokenized_dataset))
    train_dataset = tokenized_dataset.select(range(train_size))
    eval_dataset = tokenized_dataset.select(range(train_size, len(tokenized_dataset)))

    logger.info(f"\n📊 Dataset: {len(train_dataset)} train, {len(eval_dataset)} eval")

    # Calculate steps
    effective_batch = batch_size * grad_accum
    steps_per_epoch = len(train_dataset) // effective_batch
    total_steps = steps_per_epoch * num_epochs
    warmup_steps = int(0.1 * total_steps)  # 10% warmup

    # Estimate training time (conservative: 120s per step - longer due to increased output)
    estimated_seconds = total_steps * 120
    estimated_hours = estimated_seconds / 3600

    logger.info("\n⚙️  Configuration:")
    logger.info(f"   Epochs: {num_epochs}")
    logger.info(f"   Per-device batch size: {batch_size}")
    logger.info(f"   Gradient accumulation: {grad_accum}")
    logger.info(f"   Effective batch size: {effective_batch}")
    logger.info(f"   Steps per epoch: {steps_per_epoch}")
    logger.info(f"   Total steps: {total_steps}")
    logger.info(f"   Warmup steps: {warmup_steps}")
    logger.info(f"   Max input length: {max_input}")
    logger.info(f"   Max output length: {max_output} (increased for sequenced format)")
    logger.info(f"   Estimated time: ~{estimated_hours:.1f} hours")

    # Training config
    training_args = TrainingArguments(
        output_dir="./models/codet5-sequenced",
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        gradient_accumulation_steps=grad_accum,
        learning_rate=3e-4,
        warmup_steps=warmup_steps,
        lr_scheduler_type="linear",
        weight_decay=0.01,
        label_smoothing_factor=0.1,
        max_grad_norm=1.0,
        # More frequent evaluation (every 0.5 epoch)
        eval_strategy="steps",
        eval_steps=steps_per_epoch // 2,
        # Enhanced checkpointing
        save_strategy="steps",
        save_steps=steps_per_epoch * 2,  # Save every 2 epochs
        save_total_limit=5,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        logging_dir="./logs/codet5-sequenced",
        logging_steps=10,
        logging_first_step=True,
        report_to="none",
        fp16=False,
        dataloader_num_workers=4,
        seed=42,
    )

    # Data collator
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        padding=True,
    )

    # Early stopping
    early_stopping = EarlyStoppingCallback(
        early_stopping_patience=10,
        early_stopping_threshold=0.001,
    )

    # Progress tracking
    progress_callback = ProgressCallback(total_epochs=num_epochs)

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
        callbacks=[early_stopping, progress_callback],
    )

    # Train
    logger.info("\n" + "=" * 80)
    logger.info(f"🏋️  Starting Training ({num_epochs} epochs)...")
    logger.info(f"   Expected duration: ~{estimated_hours:.1f} hours")
    logger.info(f"   Evaluation: Every {steps_per_epoch // 2} steps (~0.5 epoch)")
    logger.info(f"   Checkpoints: Every {steps_per_epoch * 2} steps (~2 epochs)")
    logger.info("=" * 80 + "\n")

    train_result = trainer.train()

    # Results
    logger.info("\n" + "=" * 80)
    logger.info("📊 Training Complete")
    logger.info("=" * 80)
    logger.info(f"Final train loss: {train_result.training_loss:.4f}")
    logger.info(
        f"Training time: {train_result.metrics['train_runtime']:.1f}s ({train_result.metrics['train_runtime']/3600:.2f} hours)"
    )

    eval_results = trainer.evaluate()
    logger.info(f"Final eval loss: {eval_results['eval_loss']:.4f}")

    # Save model
    trainer.save_model()
    tokenizer.save_pretrained("./models/codet5-sequenced")

    logger.info("\n💾 Model saved to: ./models/codet5-sequenced")
    logger.info("\n📋 Next steps:")
    logger.info("   1. Test sequencing quality")
    logger.info("   2. Update generate_syllabus.py to use new model")
    logger.info("   3. Update Streamlit to display weekly schedule")

    return model, tokenizer, device


def main():
    """Main training pipeline."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        type=str,
        default="data/training/sequenced_t5_training.json",
        help="Path to sequenced training data JSON file",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=15,
        help="Number of epochs (default: 15)",
    )
    parser.add_argument(
        "--batch-size", type=int, default=20, help="Per-device batch size (default: 20)"
    )
    parser.add_argument(
        "--grad-accum",
        type=int,
        default=4,
        help="Gradient accumulation steps (default: 4)",
    )
    args = parser.parse_args()

    try:
        run_sequenced_training(
            data_file=args.data,
            num_epochs=args.epochs,
            batch_size=args.batch_size,
            grad_accum=args.grad_accum,
        )

        logger.info("\n" + "=" * 80)
        logger.info("🏁 TRAINING COMPLETE - SEQUENCED SYLLABUS GENERATION")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"\n❌ Training failed: {e}")
        raise


if __name__ == "__main__":
    main()
