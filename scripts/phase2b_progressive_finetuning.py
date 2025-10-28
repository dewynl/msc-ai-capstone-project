#!/usr/bin/env python3
"""
Phase 2B: Progressive Fine-Tuning (Conservative Approach)

Builds capability incrementally by training on progressively more complex outputs:
- Step 1 (10 epochs): Only objectives (simpler target)
- Step 2 (10 epochs): Objectives + modules
- Step 3 (10 epochs): Objectives + modules + activities
- Step 4 (10 epochs): Full sequences (objectives + modules + activities + assessments)

ONLY RUN THIS IF PHASE 1 SHOWS PARTIAL SUCCESS:
⚠️ Output length: 80-100 tokens (marginal improvement)
⚠️ Occasional module calls
⚠️ Some gibberish patterns
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
    return data


def filter_to_complexity_level(
    examples: List[Dict[str, str]], level: int
) -> List[Dict[str, str]]:
    """
    Filter training data to specific complexity level:
    Level 1: set_info + objectives only
    Level 2: set_info + objectives + modules
    Level 3: set_info + objectives + modules + activities
    Level 4: Full (set_info + objectives + modules + activities + assessments)
    """
    filtered = []

    for ex in examples:
        output = ex["output_calls"]
        lines = output.strip().split("\n")

        if level == 1:
            # Only keep set_info + objectives
            new_lines = []
            for line in lines:
                if any(
                    x in line
                    for x in ["SyllabusBuilder()", "set_info", "add_objective"]
                ):
                    new_lines.append(line)
            if new_lines:
                filtered.append(
                    {
                        "input_text": ex["input_text"],
                        "output_calls": "\n".join(new_lines),
                    }
                )

        elif level == 2:
            # Keep set_info + objectives + modules
            new_lines = []
            for line in lines:
                if any(
                    x in line
                    for x in [
                        "SyllabusBuilder()",
                        "set_info",
                        "add_objective",
                        "add_module",
                    ]
                ):
                    new_lines.append(line)
            if new_lines:
                filtered.append(
                    {
                        "input_text": ex["input_text"],
                        "output_calls": "\n".join(new_lines),
                    }
                )

        elif level == 3:
            # Keep set_info + objectives + modules + activities
            new_lines = []
            for line in lines:
                if any(
                    x in line
                    for x in [
                        "SyllabusBuilder()",
                        "set_info",
                        "add_objective",
                        "add_module",
                        "add_activity",
                    ]
                ):
                    new_lines.append(line)
            if new_lines:
                filtered.append(
                    {
                        "input_text": ex["input_text"],
                        "output_calls": "\n".join(new_lines),
                    }
                )

        elif level == 4:
            # Full sequence
            filtered.append(ex)

    logger.info(f"   Level {level}: {len(filtered)} examples")
    return filtered


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


def train_progressive_step(
    model, tokenizer, examples, step_num, step_desc, device, output_dir, epochs=10
):
    """Train one progressive step."""

    logger.info(f"\n{'=' * 80}")
    logger.info(f"STEP {step_num}: {step_desc}")
    logger.info(f"{'=' * 80}")
    logger.info(f"Training on {len(examples)} examples for {epochs} epochs")

    # Prepare dataset
    max_input = 640
    max_output = 536
    tokenized_dataset = prepare_dataset(examples, tokenizer, max_input, max_output)

    # Split
    train_size = int(0.9 * len(tokenized_dataset))
    train_dataset = tokenized_dataset.select(range(train_size))
    eval_dataset = tokenized_dataset.select(range(train_size, len(tokenized_dataset)))

    # Training config
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        gradient_accumulation_steps=4,
        learning_rate=3e-4,
        warmup_steps=10,
        lr_scheduler_type="linear",
        weight_decay=0.01,
        label_smoothing_factor=0.1,
        max_grad_norm=1.0,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        logging_dir="./logs",
        logging_steps=10,
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

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )

    # Train
    logger.info(f"\n🏋️  Training Step {step_num}...")
    train_result = trainer.train()

    logger.info(f"\n✅ Step {step_num} Complete:")
    logger.info(f"   Train loss: {train_result.training_loss:.4f}")
    logger.info(f"   Time: {train_result.metrics['train_runtime']:.1f}s")

    eval_results = trainer.evaluate()
    logger.info(f"   Eval loss: {eval_results['eval_loss']:.4f}")

    # Save
    trainer.save_model()
    tokenizer.save_pretrained(output_dir)

    return model


def run_phase2b_progressive():
    """Run Phase 2B progressive fine-tuning."""

    logger.info("=" * 80)
    logger.info("🚀 PHASE 2B: PROGRESSIVE FINE-TUNING")
    logger.info("=" * 80)
    logger.info("Duration: 40 epochs (4 steps × 10 epochs)")
    logger.info("Purpose: Build capability incrementally")
    logger.info("=" * 80)

    set_seed(42)

    # Load model from Phase 1
    model_path = "./models/phase1-diagnostic"
    logger.info(f"\n📦 Loading model from Phase 1: {model_path}")

    tokenizer = RobertaTokenizer.from_pretrained(model_path)
    model = T5ForConditionalGeneration.from_pretrained(model_path)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    logger.info(f"✅ Model on {device}")

    model.gradient_checkpointing_enable()

    # Load full training data
    base_dir = Path(__file__).parent.parent
    data_file = base_dir / "data" / "training" / "rag_enhanced_t5_training.json"
    full_examples = load_training_data(data_file)

    logger.info("\n📊 Filtering data by complexity level:")

    # Step 1: Objectives only
    level1_examples = filter_to_complexity_level(full_examples, level=1)
    model = train_progressive_step(
        model,
        tokenizer,
        level1_examples,
        step_num=1,
        step_desc="Objectives Only",
        device=device,
        output_dir="./models/phase2b-step1",
    )

    # Step 2: Objectives + Modules
    level2_examples = filter_to_complexity_level(full_examples, level=2)
    model = train_progressive_step(
        model,
        tokenizer,
        level2_examples,
        step_num=2,
        step_desc="Objectives + Modules",
        device=device,
        output_dir="./models/phase2b-step2",
    )

    # Step 3: Objectives + Modules + Activities
    level3_examples = filter_to_complexity_level(full_examples, level=3)
    model = train_progressive_step(
        model,
        tokenizer,
        level3_examples,
        step_num=3,
        step_desc="Objectives + Modules + Activities",
        device=device,
        output_dir="./models/phase2b-step3",
    )

    # Step 4: Full sequences
    level4_examples = filter_to_complexity_level(full_examples, level=4)
    model = train_progressive_step(
        model,
        tokenizer,
        level4_examples,
        step_num=4,
        step_desc="Full Sequences (All Components)",
        device=device,
        output_dir="./models/phase2b-progressive",
    )

    logger.info("\n" + "=" * 80)
    logger.info("🏁 PHASE 2B COMPLETE")
    logger.info("=" * 80)
    logger.info("💾 Final model: ./models/phase2b-progressive")
    logger.info("\n📋 Next step: Run comprehensive evaluation")
    logger.info(
        "   python scripts/evaluate_codet5_model.py --model ./models/phase2b-progressive"
    )

    return model, tokenizer, device


def main():
    """Main Phase 2B pipeline."""
    try:
        # Check Phase 1 exists
        phase1_path = Path("./models/phase1-diagnostic")
        if not phase1_path.exists():
            logger.error(
                "❌ Phase 1 model not found. Run phase1_diagnostic_training.py first."
            )
            return

        # Check Phase 1 results
        results_path = Path("phase1_diagnostic_results.json")
        if results_path.exists():
            with open(results_path) as f:
                results = json.load(f)

            if results.get("decision") == "phase2a":
                logger.warning("⚠️  Phase 1 showed strong success")
                logger.warning(
                    "   Consider running phase2a_curriculum_learning.py instead"
                )
                response = input("Continue with Phase 2B anyway? (yes/no): ")
                if response.lower() != "yes":
                    logger.info(
                        "Exiting. Run phase2a_curriculum_learning.py for better results."
                    )
                    return

        # Run training
        run_phase2b_progressive()

    except Exception as e:
        logger.error(f"\n❌ Phase 2B failed: {e}")
        raise


if __name__ == "__main__":
    main()
