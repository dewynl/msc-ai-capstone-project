#!/usr/bin/env python3
"""
Fine-tune CodeT5 model from user feedback.

This implements the periodic learning layer (Option 1) of the hybrid feedback system.
Requires 50+ high-quality feedback samples to run.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.supabase_client import get_supabase_manager


def export_feedback_training_data(
    min_score: int = 7, min_samples: int = 50, output_path: str = None
):
    """
    Export high-quality syllabi from Supabase for fine-tuning.

    Args:
        min_score: Minimum quality score (1-10 scale)
        min_samples: Minimum number of samples required
        output_path: Where to save training data (default: auto)

    Returns:
        Path to exported training data, or None if insufficient samples
    """
    print("=" * 80)
    print("EXPORTING FEEDBACK DATA FOR FINE-TUNING")
    print("=" * 80)

    # Initialize Supabase
    try:
        db = get_supabase_manager()
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("   Please configure Supabase credentials in .env file")
        return None

    # Get feedback stats
    stats = db.get_feedback_stats()
    print("\n📊 Feedback Statistics:")
    print(f"   Total feedback: {stats['total_feedback']}")
    print(f"   Average score: {stats['avg_score']}/10")
    print(f"   High quality (≥{min_score}/10): {stats['high_quality_count']}")

    if stats["high_quality_count"] < min_samples:
        print("\n⚠️  Insufficient data for fine-tuning")
        print(f"   Required: {min_samples} samples")
        print(f"   Available: {stats['high_quality_count']} samples")
        print(f"   Need {min_samples - stats['high_quality_count']} more ratings!")
        return None

    print(
        f"\n✅ Sufficient data available ({stats['high_quality_count']} ≥ {min_samples})"
    )

    # Fetch high-quality syllabi
    print(f"\n🔍 Fetching syllabi with score ≥ {min_score}/10...")
    high_quality_syllabi = db.get_high_quality_syllabi(min_score=min_score, limit=200)

    print(f"   Retrieved {len(high_quality_syllabi)} syllabi")

    # Format for T5 training
    training_data = []

    for syllabus_record in high_quality_syllabi:
        try:
            # Extract requirements and syllabus
            title = syllabus_record["title"]
            domain = syllabus_record["domain"]
            level = syllabus_record["level"]
            description = syllabus_record["description"]
            syllabus_json = syllabus_record["syllabus_json"]

            # Get feedback score
            feedback = syllabus_record.get("user_feedback", {})
            avg_score = feedback.get("avg_score", 0)

            # Build input text (same format as training)
            input_text = (
                f"Generate syllabus for: {title} | "
                f"{domain} | {level}\n\n"
                f"Description: {description}"
            )

            # Build output text (markdown format)
            # Convert JSON back to markdown format
            modules = syllabus_json.get("modules", [])
            learning_objectives = syllabus_json.get("learning_objectives", [])

            output_text = f"# {title}\n\n"
            output_text += f"**Domain:** {domain}\n"
            output_text += f"**Level:** {level}\n\n"

            if learning_objectives:
                output_text += "## Learning Objectives\n\n"
                for obj in learning_objectives:
                    output_text += f"- {obj}\n"
                output_text += "\n"

            if modules:
                output_text += "## Modules\n\n"
                for i, module in enumerate(modules, 1):
                    mod_title = module.get("title", f"Module {i}")
                    output_text += f"### Module {i}: {mod_title}\n\n"

                    objectives = module.get("learning_objectives", [])
                    if objectives:
                        for obj in objectives:
                            output_text += f"- {obj}\n"
                        output_text += "\n"

            training_entry = {
                "input": input_text,
                "output": output_text,
                "metadata": {
                    "syllabus_id": syllabus_record["id"],
                    "user_score": avg_score,
                    "feedback_count": feedback.get("count", 1),
                    "original_generation_time": syllabus_record.get(
                        "generation_time_seconds", 0
                    ),
                },
            }

            training_data.append(training_entry)

        except Exception as e:
            print(
                f"   ⚠️  Skipped syllabus {syllabus_record.get('id', 'unknown')}: {e}"
            )
            continue

    print(f"\n✅ Formatted {len(training_data)} examples for training")

    # Save to file
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = (
            Path(__file__).parent.parent.parent
            / "data"
            / "training"
            / f"feedback_fine_tune_{timestamp}.json"
        )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(training_data, f, indent=2)

    print(f"\n💾 Saved training data to: {output_path}")
    print(f"   Training examples: {len(training_data)}")
    print(
        f"   Average user score: {sum(t['metadata']['user_score'] for t in training_data) / len(training_data):.2f}/10"
    )

    return str(output_path)


def fine_tune_model(
    training_data_path: str,
    base_model_path: str = "models/codet5-sequenced/checkpoint-196",
    output_model_path: str = None,
    learning_rate: float = 2e-6,
    num_epochs: int = 2,
    batch_size: int = 4,
):
    """
    Fine-tune CodeT5 model on feedback data.

    Args:
        training_data_path: Path to feedback training data JSON
        base_model_path: Path to current model
        output_model_path: Where to save fine-tuned model (default: auto)
        learning_rate: Very small LR to avoid catastrophic forgetting
        num_epochs: Limited epochs (2-3 max)
        batch_size: Small batch size

    Returns:
        Path to fine-tuned model
    """
    print("\n" + "=" * 80)
    print("FINE-TUNING MODEL FROM FEEDBACK")
    print("=" * 80)

    try:
        from datasets import Dataset
        from transformers import (
            DataCollatorForSeq2Seq,
            T5ForConditionalGeneration,
            T5Tokenizer,
            Trainer,
            TrainingArguments,
        )
    except ImportError:
        print("\n❌ Error: transformers and datasets libraries required")
        print("   Install with: pip install transformers datasets")
        return None

    # Load training data
    print(f"\n📂 Loading training data from: {training_data_path}")
    with open(training_data_path) as f:
        training_data = json.load(f)

    print(f"   Loaded {len(training_data)} training examples")

    # Load tokenizer and model
    print(f"\n🔧 Loading model from: {base_model_path}")
    tokenizer = T5Tokenizer.from_pretrained(base_model_path)
    model = T5ForConditionalGeneration.from_pretrained(base_model_path)

    print("   Model loaded successfully")

    # Prepare dataset
    print("\n🔄 Preparing dataset...")

    def tokenize_function(examples):
        """Tokenize input/output pairs."""
        inputs = [ex["input"] for ex in examples]
        outputs = [ex["output"] for ex in examples]

        model_inputs = tokenizer(
            inputs, max_length=512, truncation=True, padding="max_length"
        )

        labels = tokenizer(
            outputs, max_length=512, truncation=True, padding="max_length"
        )

        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    # Create dataset
    dataset_dict = {
        "input": [t["input"] for t in training_data],
        "output": [t["output"] for t in training_data],
    }
    dataset = Dataset.from_dict(dataset_dict)
    tokenized_dataset = dataset.map(
        lambda x: tokenize_function([x]), remove_columns=dataset.column_names
    )

    print(f"   Dataset prepared: {len(tokenized_dataset)} examples")

    # Set up output path
    if output_model_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_model_path = f"models/codet5-sequenced/checkpoint-feedback-{timestamp}"

    # Training arguments (CONSERVATIVE to avoid catastrophic forgetting)
    print("\n⚙️  Training Configuration:")
    print(f"   Learning Rate: {learning_rate} (very small)")
    print(f"   Epochs: {num_epochs}")
    print(f"   Batch Size: {batch_size}")
    print(f"   Output: {output_model_path}")

    training_args = TrainingArguments(
        output_dir=output_model_path,
        learning_rate=learning_rate,  # VERY SMALL to avoid forgetting
        per_device_train_batch_size=batch_size,
        num_train_epochs=num_epochs,  # Just 2-3 epochs
        save_strategy="epoch",
        logging_steps=10,
        save_total_limit=2,
        report_to="none",
        warmup_steps=10,
        weight_decay=0.01,
    )

    # Data collator
    data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )

    # Train
    print("\n🚀 Starting fine-tuning...")
    print("   This may take 10-30 minutes depending on data size")

    trainer.train()

    # Save model
    print(f"\n💾 Saving fine-tuned model to: {output_model_path}")
    trainer.save_model(output_model_path)
    tokenizer.save_pretrained(output_model_path)

    print("\n✅ Fine-tuning complete!")
    print(f"   Model saved to: {output_model_path}")

    return output_model_path


def main():
    """Main entry point for feedback fine-tuning."""
    print("\n" + "=" * 80)
    print("FEEDBACK-BASED MODEL FINE-TUNING PIPELINE")
    print("=" * 80)

    # Step 1: Export feedback data
    training_data_path = export_feedback_training_data(min_score=7, min_samples=50)

    if training_data_path is None:
        print("\n❌ Cannot proceed with fine-tuning - insufficient feedback data")
        print("\n💡 To collect more feedback:")
        print("   1. Generate syllabi using the Streamlit app")
        print("   2. Rate each syllabus (aim for 50+ ratings)")
        print("   3. Run this script again when ready")
        return

    # Step 2: Fine-tune model
    print("\n" + "=" * 80)
    print("PROCEED WITH FINE-TUNING?")
    print("=" * 80)
    print("⚠️  WARNING: Fine-tuning will:")
    print("   - Take 10-30 minutes")
    print("   - Use ~4GB RAM")
    print("   - Create new model checkpoint (~1.5GB)")
    print(f"   - Use data from: {training_data_path}")

    response = input("\nContinue? (yes/no): ")

    if response.lower() not in ["yes", "y"]:
        print("\n❌ Fine-tuning cancelled")
        print(f"   Training data saved to: {training_data_path}")
        print("   You can fine-tune later by running this script again")
        return

    # Proceed with fine-tuning
    model_path = fine_tune_model(
        training_data_path=training_data_path,
        learning_rate=2e-6,
        num_epochs=2,
        batch_size=4,
    )

    if model_path:
        print("\n" + "=" * 80)
        print("FINE-TUNING COMPLETE!")
        print("=" * 80)
        print(f"✅ New model saved to: {model_path}")
        print("\n📋 Next Steps:")
        print("   1. Evaluate the new model vs the old model")
        print("   2. Run comparison tests")
        print("   3. If improved, update model path in generate_syllabus.py")
        print("\n💡 Evaluation command:")
        print(f"   python scripts/evaluation/evaluator.py --model {model_path}")


if __name__ == "__main__":
    main()
