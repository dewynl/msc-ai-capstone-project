#!/usr/bin/env python3
"""
Phase 2A: Curriculum Learning (Full Training)

Gradually teaches model to generate longer, more structured outputs through 4 stages:
- Stage 1 (Epochs 1-10): Learn objectives + early modules
- Stage 2 (Epochs 11-25): Learn full module sequences
- Stage 3 (Epochs 26-40): Learn complete sequences (modules → activities → assessments)
- Stage 4 (Epochs 41-50): Refinement

ONLY RUN THIS IF PHASE 1 SHOWS STRONG SUCCESS:
✅ Output length: 100-150+ tokens (up from 70)
✅ Module calls present
✅ No gibberish patterns
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
    TrainerCallback,
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


class CurriculumLearningTrainer(Trainer):
    """
    Curriculum Learning Trainer with progressive difficulty:
    - Stage 1 (Epochs 1-10): Mild constraints
    - Stage 2 (Epochs 11-25): Medium constraints
    - Stage 3 (Epochs 26-40): Strong constraints
    - Stage 4 (Epochs 41-50): Refinement
    """

    def __init__(
        self, curriculum_stages: List[Dict], eos_token_id: int = 2, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.curriculum_stages = curriculum_stages
        self.eos_token_id = eos_token_id
        self.current_stage = self.curriculum_stages[0]

        logger.info("\n📚 Curriculum Learning Stages:")
        for stage in curriculum_stages:
            logger.info(
                f"   Epochs {stage['start']}-{stage['end']}: "
                f"EOS mask={stage['eos_mask']}, "
                f"Weight={stage['weight_start']}x→{stage['weight_end']}x"
            )

    def compute_loss(
        self, model, inputs, return_outputs=False, num_items_in_batch=None
    ):
        """Custom loss with curriculum-based constraints."""

        # Update stage based on current epoch
        current_epoch = self.state.epoch
        for stage in self.curriculum_stages:
            if stage["start"] <= current_epoch <= stage["end"]:
                self.current_stage = stage
                break

        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")

        # Per-token cross-entropy
        loss_fct = torch.nn.CrossEntropyLoss(reduction="none")
        shift_logits = logits[..., :-1, :].contiguous()
        shift_labels = labels[..., 1:].contiguous()

        loss = loss_fct(
            shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1)
        )
        loss = loss.view(shift_labels.size())

        # Curriculum-based EOS masking
        batch_size, seq_len = shift_labels.size()
        eos_mask_length = self.current_stage["eos_mask"]

        for b in range(batch_size):
            for pos in range(min(eos_mask_length, seq_len)):
                if shift_labels[b, pos] == self.eos_token_id:
                    loss[b, pos] = 0.0

        # Curriculum-based position weighting
        position_weights = (
            torch.linspace(
                self.current_stage["weight_start"],
                self.current_stage["weight_end"],
                seq_len,
                device=loss.device,
            )
            .unsqueeze(0)
            .expand(batch_size, -1)
        )

        weighted_loss = loss * position_weights

        # Mask padding
        mask = (shift_labels != -100).float()
        weighted_loss = weighted_loss * mask

        final_loss = weighted_loss.sum() / mask.sum()
        return (final_loss, outputs) if return_outputs else final_loss


class CurriculumCallback(TrainerCallback):
    """Callback to log curriculum stage changes."""

    def __init__(self, stages):
        self.stages = stages
        self.last_stage = None

    def on_epoch_begin(self, args, state, control, **kwargs):
        current_epoch = state.epoch
        for stage in self.stages:
            if stage["start"] <= current_epoch <= stage["end"]:
                if stage != self.last_stage:
                    logger.info(
                        f"\n📚 Curriculum Stage Change: Epochs {stage['start']}-{stage['end']}"
                    )
                    logger.info(f"   EOS masking: {stage['eos_mask']} tokens")
                    logger.info(
                        f"   Position weighting: {stage['weight_start']}x → {stage['weight_end']}x"
                    )
                    self.last_stage = stage
                break


def run_phase2a_curriculum():
    """Run Phase 2A curriculum learning."""

    logger.info("=" * 80)
    logger.info("🚀 PHASE 2A: CURRICULUM LEARNING")
    logger.info("=" * 80)
    logger.info("Duration: 50 epochs (~3-4 hours)")
    logger.info("Purpose: Gradually teach full sequence generation")
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

    # Define curriculum stages
    curriculum_stages = [
        # Stage 1: Learn objectives + early modules
        {
            "start": 0,
            "end": 10,
            "eos_mask": 100,
            "weight_start": 1.0,
            "weight_end": 1.5,
        },
        # Stage 2: Learn full module sequences
        {
            "start": 11,
            "end": 25,
            "eos_mask": 200,
            "weight_start": 1.0,
            "weight_end": 2.5,
        },
        # Stage 3: Learn complete sequences
        {
            "start": 26,
            "end": 40,
            "eos_mask": 250,
            "weight_start": 1.0,
            "weight_end": 3.0,
        },
        # Stage 4: Refinement
        {
            "start": 41,
            "end": 50,
            "eos_mask": 200,
            "weight_start": 1.5,
            "weight_end": 3.0,
        },
    ]

    # Training config
    training_args = TrainingArguments(
        output_dir="./models/phase2a-curriculum",
        num_train_epochs=50,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        gradient_accumulation_steps=4,
        learning_rate=3e-4,
        warmup_steps=50,
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

    logger.info("\n⚙️  Configuration:")
    logger.info("   Epochs: 50 (curriculum learning)")
    logger.info("   Effective batch size: 64")
    logger.info("   Learning rate: 3e-4")

    # Data collator
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        padding=True,
    )

    # Curriculum trainer
    trainer = CurriculumLearningTrainer(
        curriculum_stages=curriculum_stages,
        eos_token_id=tokenizer.eos_token_id,
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
        callbacks=[CurriculumCallback(curriculum_stages)],
    )

    # Train
    logger.info("\n" + "=" * 80)
    logger.info("🏋️  Starting Phase 2A Training (50 epochs)...")
    logger.info("   Expected duration: ~3-4 hours")
    logger.info("=" * 80 + "\n")

    train_result = trainer.train()

    # Results
    logger.info("\n" + "=" * 80)
    logger.info("📊 Phase 2A Training Complete")
    logger.info("=" * 80)
    logger.info(f"Final train loss: {train_result.training_loss:.4f}")
    logger.info(f"Training time: {train_result.metrics['train_runtime']:.1f}s")

    eval_results = trainer.evaluate()
    logger.info(f"Final eval loss: {eval_results['eval_loss']:.4f}")

    # Save model
    trainer.save_model()
    tokenizer.save_pretrained("./models/phase2a-curriculum")

    logger.info("\n💾 Final model saved to: ./models/phase2a-curriculum")
    logger.info("\n📋 Next step: Run comprehensive evaluation")
    logger.info(
        "   python scripts/evaluate_codet5_model.py --model ./models/phase2a-curriculum"
    )

    return model, tokenizer, device


def main():
    """Main Phase 2A pipeline."""
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

            if results.get("decision") != "phase2a":
                logger.warning(f"⚠️  Phase 1 recommended: {results.get('decision')}")
                logger.warning(
                    "   Consider running phase2b_progressive_finetuning.py instead"
                )
                response = input("Continue with Phase 2A anyway? (yes/no): ")
                if response.lower() != "yes":
                    logger.info("Exiting. Run appropriate Phase 2 script.")
                    return

        # Run training
        run_phase2a_curriculum()

        logger.info("\n" + "=" * 80)
        logger.info("🏁 PHASE 2A COMPLETE")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"\n❌ Phase 2A failed: {e}")
        raise


if __name__ == "__main__":
    main()
