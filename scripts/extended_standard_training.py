#!/usr/bin/env python3
"""
Extended Standard Training - Clean Approach

NO custom loss functions
NO EOS masking
NO position weighting

JUST: More epochs (50-100) with standard cross-entropy loss

Root Cause Learned: Custom loss optimized wrong objective
Solution: Give model more time with correct objective (standard CE loss)
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
    RobertaTokenizer,
    T5ForConditionalGeneration,
    Trainer,
    TrainingArguments,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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
    dataset = Dataset.from_dict(
        {
            "input_text": [ex["input_text"] for ex in examples],
            "output_calls": [ex["output_calls"] for ex in examples],
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
            batch["output_calls"],
            truncation=True,
            max_length=max_output,
            padding="max_length",
        )
        inputs["labels"] = targets["input_ids"]
        return inputs

    tokenized = dataset.map(tokenize, batched=True, remove_columns=dataset.column_names)
    return tokenized


def run_extended_training(num_epochs: int = 50):
    """Run extended standard training (NO custom loss)."""

    logger.info("=" * 80)
    logger.info("🚀 EXTENDED STANDARD TRAINING")
    logger.info("=" * 80)
    logger.info(f"Epochs: {num_epochs}")
    logger.info("Approach: Standard cross-entropy loss, no tricks")
    logger.info("Lesson learned: Custom loss optimized wrong objective")
    logger.info("=" * 80)

    set_seed(42)

    # Load FRESH model (not Phase 1 disaster)
    model_name = "Salesforce/codet5-small"
    logger.info(f"\n📦 Loading fresh model: {model_name}")
    logger.info("   (NOT using Phase 1 - that made things worse!)")

    tokenizer = RobertaTokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name, use_safetensors=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    logger.info(f"✅ Model on {device}")

    model.gradient_checkpointing_enable()

    # Load data
    base_dir = Path(__file__).parent.parent
    data_file = base_dir / "data" / "training" / "rag_enhanced_t5_training.json"
    examples = load_training_data(data_file)

    # Prepare dataset
    max_input = 640
    max_output = 536
    tokenized_dataset = prepare_dataset(examples, tokenizer, max_input, max_output)

    # Split
    train_size = int(0.9 * len(tokenized_dataset))
    train_dataset = tokenized_dataset.select(range(train_size))
    eval_dataset = tokenized_dataset.select(range(train_size, len(tokenized_dataset)))

    logger.info(f"\n📊 Dataset: {len(train_dataset)} train, {len(eval_dataset)} eval")

    # Training config - STANDARD (no custom loss)
    training_args = TrainingArguments(
        output_dir="./models/extended-standard-training",
        num_train_epochs=num_epochs,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        gradient_accumulation_steps=4,  # Effective batch = 64
        learning_rate=3e-4,
        warmup_steps=int(0.1 * num_epochs * 4),  # 10% warmup
        lr_scheduler_type="linear",
        weight_decay=0.01,
        label_smoothing_factor=0.1,
        max_grad_norm=1.0,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=3,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        logging_dir="./logs",
        logging_steps=10,
        logging_first_step=True,
        report_to="none",
        fp16=False,
        dataloader_num_workers=4,
        seed=42,
    )

    steps_per_epoch = len(train_dataset) // (16 * 4)
    total_steps = steps_per_epoch * num_epochs
    estimated_hours = (total_steps * 90) / 3600  # ~90s per step

    logger.info("\n⚙️  Configuration:")
    logger.info(f"   Epochs: {num_epochs} (extended)")
    logger.info("   Effective batch size: 64")
    logger.info("   Learning rate: 3e-4")
    logger.info(f"   Total steps: {total_steps}")
    logger.info(f"   Estimated time: ~{estimated_hours:.1f} hours")

    # Data collator
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        padding=True,
    )

    # Early stopping
    early_stopping = EarlyStoppingCallback(
        early_stopping_patience=5,
        early_stopping_threshold=0.001,
    )

    # STANDARD Trainer (no custom loss!)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
        callbacks=[early_stopping],
    )

    # Train
    logger.info("\n" + "=" * 80)
    logger.info(f"🏋️  Starting Training ({num_epochs} epochs, standard loss)...")
    logger.info(f"   Expected duration: ~{estimated_hours:.1f} hours")
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
    tokenizer.save_pretrained("./models/extended-standard-training")

    logger.info("\n💾 Model saved to: ./models/extended-standard-training")
    logger.info("\n📋 Next step: Run comprehensive evaluation")
    logger.info("   python scripts/evaluate_codet5_model.py")

    return model, tokenizer, device


def main():
    """Main training pipeline."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--epochs", type=int, default=50, help="Number of epochs (default: 50)"
    )
    args = parser.parse_args()

    try:
        run_extended_training(num_epochs=args.epochs)

        logger.info("\n" + "=" * 80)
        logger.info("🏁 EXTENDED TRAINING COMPLETE")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"\n❌ Training failed: {e}")
        raise


if __name__ == "__main__":
    main()
