#!/usr/bin/env python3
"""
Phase 1: Diagnostic Training (5 epochs, ~30-45 minutes)

GOAL: Validate anti-mode-collapse techniques before committing to full training

SUCCESS CRITERIA:
✅ Output length increases from 70 → 100+ tokens
✅ At least some module calls appear in outputs
✅ No complete gibberish when forcing min_length=200

DECISION POINT:
- If success → Proceed to Phase 2A (Curriculum Learning)
- If partial → Proceed to Phase 2B (Progressive Fine-Tuning)
- If failure → Investigate data/tokenization issues
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
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_training_data(file_path: Path) -> List[Dict[str, str]]:
    """Load training data."""
    with open(file_path, "r") as f:
        data = json.load(f)
    logger.info(f"✅ Loaded {len(data)} training examples")
    return data


def prepare_dataset(
    examples: List[Dict[str, str]], tokenizer, max_input: int, max_output: int
) -> Dataset:
    """Prepare and tokenize dataset."""
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


class AntiModeCollapseTrainer(Trainer):
    """
    Custom Trainer with anti-mode-collapse loss:
    1. Masks EOS tokens for first N positions (prevents early stopping)
    2. Applies position-based weighting (encourages full sequences)
    """

    def __init__(
        self,
        min_length_tokens: int = 150,
        position_weight_start: float = 1.0,
        position_weight_end: float = 2.0,
        eos_token_id: int = 2,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.min_length_tokens = min_length_tokens
        self.position_weight_start = position_weight_start
        self.position_weight_end = position_weight_end
        self.eos_token_id = eos_token_id

        logger.info("\n🛡️  Anti-Mode-Collapse Configuration:")
        logger.info(f"   EOS masking: First {min_length_tokens} tokens")
        logger.info(
            f"   Position weighting: {position_weight_start}x → {position_weight_end}x"
        )

    def compute_loss(
        self, model, inputs, return_outputs=False, num_items_in_batch=None
    ):
        """Custom loss preventing mode collapse."""
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")

        # Per-token cross-entropy loss
        loss_fct = torch.nn.CrossEntropyLoss(reduction="none")
        shift_logits = logits[..., :-1, :].contiguous()
        shift_labels = labels[..., 1:].contiguous()

        loss = loss_fct(
            shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1)
        )
        loss = loss.view(shift_labels.size())

        # FIX 1: Mask EOS tokens in first N positions
        batch_size, seq_len = shift_labels.size()
        for b in range(batch_size):
            for pos in range(min(self.min_length_tokens, seq_len)):
                if shift_labels[b, pos] == self.eos_token_id:
                    loss[b, pos] = 0.0

        # FIX 2: Position-based weighting
        position_weights = (
            torch.linspace(
                self.position_weight_start,
                self.position_weight_end,
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


def run_phase1_diagnostic():
    """Run Phase 1 diagnostic training."""

    logger.info("=" * 80)
    logger.info("🚀 PHASE 1: DIAGNOSTIC TRAINING")
    logger.info("=" * 80)
    logger.info("Duration: 5 epochs (~30-45 minutes)")
    logger.info("Purpose: Validate anti-mode-collapse approach")
    logger.info("=" * 80)

    set_seed(42)

    # Load model
    model_name = "Salesforce/codet5-small"
    logger.info(f"\n📦 Loading {model_name}...")
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

    # Training config - Phase 1
    training_args = TrainingArguments(
        output_dir="./models/phase1-diagnostic",
        num_train_epochs=5,  # Quick validation
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        gradient_accumulation_steps=4,  # Effective batch = 64
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
        logging_steps=5,
        logging_first_step=True,
        report_to="none",
        fp16=False,
        dataloader_num_workers=4,
        seed=42,
    )

    logger.info("\n⚙️  Configuration:")
    logger.info("   Epochs: 5 (diagnostic)")
    logger.info("   Effective batch size: 64")
    logger.info("   Learning rate: 3e-4")

    # Data collator
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        padding=True,
    )

    # Custom trainer with anti-mode-collapse loss
    trainer = AntiModeCollapseTrainer(
        min_length_tokens=150,  # Mild masking
        position_weight_start=1.0,
        position_weight_end=2.0,  # Mild weighting
        eos_token_id=tokenizer.eos_token_id,
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )

    # Train
    logger.info("\n" + "=" * 80)
    logger.info("🏋️  Starting Phase 1 Training (5 epochs)...")
    logger.info("=" * 80 + "\n")

    train_result = trainer.train()

    # Results
    logger.info("\n" + "=" * 80)
    logger.info("📊 Phase 1 Training Complete")
    logger.info("=" * 80)
    logger.info(f"Final train loss: {train_result.training_loss:.4f}")
    logger.info(f"Training time: {train_result.metrics['train_runtime']:.1f}s")

    eval_results = trainer.evaluate()
    logger.info(f"Final eval loss: {eval_results['eval_loss']:.4f}")

    # Save model
    trainer.save_model()
    tokenizer.save_pretrained("./models/phase1-diagnostic")

    logger.info("\n💾 Model saved to: ./models/phase1-diagnostic")

    return model, tokenizer, device


def validate_phase1_results(model, tokenizer, device):
    """
    Validate Phase 1 results against success criteria.

    SUCCESS CRITERIA:
    ✅ Output length: 100-150 tokens (up from 70)
    ✅ Module calls present
    ✅ No gibberish with min_length=200
    """

    logger.info("\n" + "=" * 80)
    logger.info("🧪 PHASE 1 VALIDATION")
    logger.info("=" * 80)

    model.eval()

    test_input = {
        "title": "Introduction to Machine Learning",
        "domain": "computer_science",
        "level": "intermediate",
        "duration": "semester",
        "description": "Fundamentals of supervised and unsupervised learning",
    }

    input_text = f"Generate course syllabus: {json.dumps(test_input)}"
    input_ids = tokenizer(
        input_text, return_tensors="pt", max_length=640, truncation=True
    ).input_ids.to(device)

    # Test 1: Natural generation (beam search)
    logger.info("\n📝 Test 1: Natural Generation (beam search)")
    with torch.no_grad():
        output1 = model.generate(
            input_ids,
            max_length=536,
            num_beams=4,
            early_stopping=False,
            no_repeat_ngram_size=2,
        )
    text1 = tokenizer.decode(output1[0], skip_special_tokens=True)
    tokens1 = len(output1[0])

    logger.info(f"   Tokens generated: {tokens1}")
    logger.info(f"   Character length: {len(text1)}")
    logger.info(f"   Has 'add_module': {'add_module' in text1}")
    logger.info(f"   Has 'add_activity': {'add_activity' in text1}")
    logger.info(f"   Preview: {text1[:200]}...")

    # Test 2: Forced longer generation
    logger.info("\n📝 Test 2: Forced Longer (min_length=200)")
    with torch.no_grad():
        output2 = model.generate(
            input_ids,
            max_length=536,
            min_length=200,
            num_beams=4,
            no_repeat_ngram_size=2,
        )
    text2 = tokenizer.decode(output2[0], skip_special_tokens=True)
    tokens2 = len(output2[0])

    logger.info(f"   Tokens generated: {tokens2}")
    logger.info(f"   Character length: {len(text2)}")

    # Check for gibberish patterns
    has_gibberish = any(
        [
            text2.count('"9"') > 5,  # Repeated "9"
            text2.count("add_%d") > 0,  # Malformed methods
            text2.count('")"') > 3,  # Malformed strings
        ]
    )
    logger.info(f"   Contains gibberish: {has_gibberish}")
    logger.info(f"   Preview: {text2[:200]}...")

    # Evaluate success criteria
    logger.info("\n" + "=" * 80)
    logger.info("📊 PHASE 1 SUCCESS CRITERIA EVALUATION")
    logger.info("=" * 80)

    criteria = {
        "length_increase": tokens1 >= 100,  # Up from 70
        "has_modules": "add_module" in text1,
        "no_gibberish": not has_gibberish,
    }

    logger.info(
        f"\n✅ Token length ≥100: {criteria['length_increase']} (actual: {tokens1})"
    )
    logger.info(f"✅ Module calls present: {criteria['has_modules']}")
    logger.info(f"✅ No gibberish pattern: {criteria['no_gibberish']}")

    success_count = sum(criteria.values())
    total_criteria = len(criteria)

    logger.info(f"\n📊 Overall: {success_count}/{total_criteria} criteria met")

    # Decision
    logger.info("\n" + "=" * 80)
    logger.info("🎯 PHASE 1 DECISION")
    logger.info("=" * 80)

    if success_count >= 3:
        logger.info("✅ STRONG SUCCESS - Proceed to Phase 2A (Curriculum Learning)")
        logger.info("   Anti-mode-collapse techniques are working!")
        decision = "phase2a"
    elif success_count >= 2:
        logger.info("⚠️  PARTIAL SUCCESS - Consider Phase 2B (Progressive Fine-Tuning)")
        logger.info("   Some improvement, but may need more conservative approach")
        decision = "phase2b"
    else:
        logger.info("❌ INSUFFICIENT PROGRESS - Investigate further")
        logger.info("   May have data/tokenization issues to resolve first")
        decision = "investigate"

    # Save results
    results = {
        "phase": "phase1_diagnostic",
        "epochs": 5,
        "test1_tokens": tokens1,
        "test1_chars": len(text1),
        "test1_output": text1,
        "test2_tokens": tokens2,
        "test2_chars": len(text2),
        "test2_gibberish": has_gibberish,
        "criteria": criteria,
        "success_count": success_count,
        "decision": decision,
    }

    with open("phase1_diagnostic_results.json", "w") as f:
        json.dump(results, f, indent=2)

    logger.info("\n💾 Results saved to: phase1_diagnostic_results.json")

    return decision, results


def main():
    """Main Phase 1 pipeline."""
    try:
        # Train
        model, tokenizer, device = run_phase1_diagnostic()

        # Validate
        decision, results = validate_phase1_results(model, tokenizer, device)

        logger.info("\n" + "=" * 80)
        logger.info("🏁 PHASE 1 COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Next step: {decision}")
        logger.info("\nReview phase1_diagnostic_results.json for detailed analysis")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"\n❌ Phase 1 failed: {e}")
        raise


if __name__ == "__main__":
    main()
