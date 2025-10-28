#!/usr/bin/env python3
"""
Phase 4: Full Training (7 hours)

Based on Phase 3B success:
- Model learned both structure AND selection
- Loss dropped from 3.10 → 0.01 in 100 steps
- Ready for full training on all 1,117 examples

Training Plan:
- All 1,117 examples
- ~15 epochs (~4,185 steps)
- Expected time: 7 hours on GPU
- Save checkpoints every epoch
- Monitor loss progression

Expected Outcome:
- 80-90% Tier 1 success (perfect markdown + indices)
- 10-15% Tier 2 success (readable markdown, parser issues)
- Total: 90-95% success rate
"""

import json
import time
from pathlib import Path

import torch
from datasets import Dataset
from transformers import (
    DataCollatorForSeq2Seq,
    RobertaTokenizer,
    T5ForConditionalGeneration,
    Trainer,
    TrainingArguments,
)


def load_training_data(data_path: str, train_split: float = 0.95):
    """Load all training data and split into train/eval."""
    print(f"📂 Loading training data: {data_path}")

    with open(data_path) as f:
        data = json.load(f)

    print(f"   ✅ Loaded {len(data)} examples\\n")

    # Split into train/eval
    split_idx = int(len(data) * train_split)
    train_data = data[:split_idx]
    eval_data = data[split_idx:]

    print(f"   Train: {len(train_data)} examples")
    print(f"   Eval:  {len(eval_data)} examples\\n")

    return train_data, eval_data


def prepare_inputs(examples, tokenizer, max_input_length=512, max_output_length=400):
    """Tokenize inputs and outputs."""
    inputs = []
    outputs = []

    for ex in examples:
        input_text = ex["input_text"]
        json_str = input_text.replace("Generate course syllabus: ", "")
        input_data = json.loads(json_str)

        # Build compact prompt (same as Phase 3B)
        prompt = f"Generate syllabus for: {input_data['title']} | {input_data['domain']} | {input_data['level']}\\n\\n"
        prompt += "Available modules:\\n"
        for i, mod in enumerate(input_data.get("available_modules", [])[:20]):
            prompt += f"[{i}] {mod['title']} ({mod.get('estimated_hours', 0)}h, {mod.get('difficulty', 'N/A')})\\n"

        prompt += "\\nAvailable activities:\\n"
        for i, act in enumerate(input_data.get("available_activities", [])[:15]):
            prompt += f"[{i}] {act['title']} ({act.get('estimated_hours', 0)}h)\\n"

        prompt += "\\nAvailable assessments:\\n"
        for i, ass in enumerate(input_data.get("available_assessments", [])[:5]):
            prompt += f"[{i}] {ass['title']} ({ass.get('assessment_type', 'N/A')})\\n"

        prompt += "\\nSelect relevant components and generate markdown syllabus."

        inputs.append(prompt)
        outputs.append(ex["output_markdown"])

    # Tokenize
    model_inputs = tokenizer(
        inputs, max_length=max_input_length, truncation=True, padding=False
    )

    labels = tokenizer(
        outputs, max_length=max_output_length, truncation=True, padding=False
    )

    model_inputs["labels"] = labels["input_ids"]

    return model_inputs


def full_train(output_dir: str = "models/codet5-markdown-FULL"):
    """Full training on all 1,117 examples for ~15 epochs."""
    print("=" * 80)
    print("PHASE 4: FULL TRAINING")
    print("=" * 80)
    print("\\n🎯 Goal: Train production model to 90-95% success rate")
    print("⏱️  Expected time: 7 hours\\n")
    print("💡 Based on Phase 3B success:")
    print("   ✅ Model learned both structure AND selection")
    print("   ✅ Loss dropped 99.7% in 100 steps")
    print("   ✅ Ready for full dataset\\n")

    # Load model and tokenizer
    print("📦 Loading CodeT5-small...")
    tokenizer = RobertaTokenizer.from_pretrained("Salesforce/codet5-small")
    model = T5ForConditionalGeneration.from_pretrained("Salesforce/codet5-small")
    print("   ✅ Loaded\\n")

    # Load data
    train_data, eval_data = load_training_data(
        "data/training/markdown_training_1300.json"
    )

    # Prepare datasets
    print("🔄 Tokenizing data...")
    train_tokenized = prepare_inputs(train_data, tokenizer)
    eval_tokenized = prepare_inputs(eval_data, tokenizer)

    train_dataset = Dataset.from_dict(train_tokenized)
    eval_dataset = Dataset.from_dict(eval_tokenized)
    print("   ✅ Tokenized\\n")

    # Calculate training metrics
    steps_per_epoch = len(train_data) // 4  # batch size = 4
    target_epochs = 15
    total_steps = steps_per_epoch * target_epochs

    print("⚙️  Training configuration:")
    print(f"   Examples: {len(train_data)} train, {len(eval_data)} eval")
    print("   Batch size: 4")
    print(f"   Steps per epoch: {steps_per_epoch}")
    print(f"   Target epochs: {target_epochs}")
    print(f"   Total steps: {total_steps}")
    print("   Learning rate: 3e-4")
    print(f"   Warmup steps: {steps_per_epoch // 2} (half epoch)")
    print(f"   Save every: {steps_per_epoch} steps (1 epoch)")
    print(f"   Eval every: {steps_per_epoch} steps (1 epoch)")
    print("   Logging: Every 50 steps\\n")

    # Training args
    training_args = TrainingArguments(
        output_dir=output_dir,
        max_steps=total_steps,
        per_device_train_batch_size=4,
        learning_rate=3e-4,
        warmup_steps=steps_per_epoch // 2,  # Half epoch warmup
        save_steps=steps_per_epoch,  # Save every epoch
        eval_steps=steps_per_epoch,  # Eval every epoch
        logging_steps=50,  # Log frequently
        save_total_limit=5,  # Keep last 5 checkpoints
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        fp16=torch.cuda.is_available(),
        dataloader_num_workers=2,
        report_to="none",
        remove_unused_columns=False,
        eval_strategy="steps",  # Enable evaluation
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
    )

    # Train
    start_time = time.time()
    print("🚀 Starting full training (~7 hours)...")
    print("─" * 80)
    trainer.train()
    print("─" * 80)

    elapsed = time.time() - start_time
    elapsed_hours = elapsed / 3600
    print(f"✅ Full training complete! ({elapsed_hours:.1f} hours)\\n")

    # Save final model
    print(f"💾 Saving final model to: {output_dir}")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("   ✅ Saved\\n")

    # Save training stats
    stats = {
        "total_steps": total_steps,
        "epochs": target_epochs,
        "train_examples": len(train_data),
        "eval_examples": len(eval_data),
        "training_time_hours": elapsed_hours,
        "final_train_loss": trainer.state.log_history[-1].get("loss"),
        "final_eval_loss": trainer.state.log_history[-1].get("eval_loss"),
    }

    stats_path = Path(output_dir) / "training_stats.json"
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)

    print("📊 Training statistics:")
    print(f"   Total steps: {stats['total_steps']}")
    print(f"   Epochs: {stats['epochs']}")
    print(f"   Training time: {stats['training_time_hours']:.1f} hours")
    print(f"   Final train loss: {stats['final_train_loss']:.4f}")
    print(f"   Final eval loss: {stats['final_eval_loss']:.4f}")
    print()

    return output_dir


if __name__ == "__main__":
    print("Phase 4 - Full Training (7 hours)")
    print("Based on Phase 3B GO decision: Structure + Selection learned")
    print()

    # Full training
    model_path = full_train()

    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("✅ Phase 4 Complete - Model trained on all 1,117 examples")
    print()
    print("➡️  Phase 5: Run evaluation script")
    print("   python scripts/phase5_comprehensive_evaluation.py")
    print()
    print("Expected results:")
    print("  - 80-90% Tier 1 success (perfect markdown + indices)")
    print("  - 10-15% Tier 2 success (readable markdown)")
    print("  - 90-95% total success rate")
    print()
