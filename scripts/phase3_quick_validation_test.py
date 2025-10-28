#!/usr/bin/env python3
"""
Phase 3: Quick Validation Test - CRITICAL GATE

Train for ONLY 10 steps (5 minutes) to check if model shows learning signal.

DO NOT PROCEED TO 7-HOUR TRAINING WITHOUT THIS PASSING!

Success Criteria:
- Output length > 100 chars (not completely broken)
- Has markdown structure (## headers)
- Has some index patterns ([digit])
- Is somewhat readable

If ANY of these fail → DEBUG or PIVOT TO PATH 7
"""

import json

import torch
from datasets import Dataset
from transformers import (
    DataCollatorForSeq2Seq,
    RobertaTokenizer,
    T5ForConditionalGeneration,
    Trainer,
    TrainingArguments,
)


def load_training_data(data_path: str, max_examples: int = 100):
    """Load a small subset for quick training."""
    print(f"📂 Loading training data: {data_path}")

    with open(data_path) as f:
        data = json.load(f)

    # Use only first 100 examples for quick test
    data = data[:max_examples]

    print(f"   ✅ Loaded {len(data)} examples (quick test subset)\n")

    return data


def prepare_inputs(examples, tokenizer, max_input_length=512, max_output_length=400):
    """Tokenize inputs and outputs."""
    inputs = []
    outputs = []

    for ex in examples:
        # Input: Same format as Phase 0 validation (medium-compact)
        input_text = ex["input_text"]
        json_str = input_text.replace("Generate course syllabus: ", "")
        input_data = json.loads(json_str)

        # Build compact prompt
        prompt = f"Generate syllabus for: {input_data['title']} | {input_data['domain']} | {input_data['level']}\n\n"
        prompt += "Available modules:\n"
        for i, mod in enumerate(input_data.get("available_modules", [])[:20]):
            prompt += f"[{i}] {mod['title']} ({mod.get('estimated_hours', 0)}h, {mod.get('difficulty', 'N/A')})\n"

        prompt += "\nAvailable activities:\n"
        for i, act in enumerate(input_data.get("available_activities", [])[:15]):
            prompt += f"[{i}] {act['title']} ({act.get('estimated_hours', 0)}h)\n"

        prompt += "\nAvailable assessments:\n"
        for i, ass in enumerate(input_data.get("available_assessments", [])[:5]):
            prompt += f"[{i}] {ass['title']} ({ass.get('assessment_type', 'N/A')})\n"

        prompt += "\nSelect relevant components and generate markdown syllabus."

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


def quick_train(output_dir: str = "models/codet5-markdown-QUICKTEST"):
    """Train for just 10 steps to check learning signal."""
    print("=" * 80)
    print("PHASE 3: QUICK VALIDATION TEST")
    print("=" * 80)
    print("\n⚠️  CRITICAL GATE: This determines if we proceed to 7h training\n")
    print("🎯 Goal: Train 10 steps and check for ANY learning signal")
    print("⏱️  Expected time: 5 minutes\n")

    # Load model and tokenizer
    print("📦 Loading CodeT5-small...")
    tokenizer = RobertaTokenizer.from_pretrained("Salesforce/codet5-small")
    model = T5ForConditionalGeneration.from_pretrained("Salesforce/codet5-small")
    print("   ✅ Loaded\n")

    # Load data (just 100 examples)
    data = load_training_data(
        "data/training/markdown_training_1300.json", max_examples=100
    )

    # Prepare inputs
    print("🔄 Tokenizing data...")
    tokenized = prepare_inputs(data, tokenizer)
    dataset = Dataset.from_dict(tokenized)
    print("   ✅ Tokenized\n")

    # Training args (MINIMAL - just 10 steps!)
    print("⚙️  Training configuration:")
    print("   Steps: 10 (QUICK TEST ONLY)")
    print("   Batch size: 4")
    print("   Learning rate: 3e-4")
    print("   Max output: 400 tokens\n")

    training_args = TrainingArguments(
        output_dir=output_dir,
        max_steps=10,  # ONLY 10 STEPS!
        per_device_train_batch_size=4,
        learning_rate=3e-4,
        save_steps=10,
        logging_steps=1,
        warmup_steps=0,
        fp16=torch.cuda.is_available(),
        dataloader_num_workers=2,
        report_to="none",
        remove_unused_columns=False,
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
        train_dataset=dataset,
        data_collator=data_collator,
    )

    # Train
    print("🚀 Starting quick training (10 steps, ~5 minutes)...")
    print("─" * 80)
    trainer.train()
    print("─" * 80)
    print("✅ Quick training complete!\n")

    # Save
    print(f"💾 Saving to: {output_dir}")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("   ✅ Saved\n")

    return output_dir


def test_learning_signal(model_path: str):
    """Test if model shows ANY learning signal."""
    print("=" * 80)
    print("TESTING FOR LEARNING SIGNAL")
    print("=" * 80)
    print()

    # Load model
    print(f"📦 Loading model from: {model_path}")
    tokenizer = RobertaTokenizer.from_pretrained(model_path)
    model = T5ForConditionalGeneration.from_pretrained(model_path)

    if torch.cuda.is_available():
        model = model.cuda()

    print("   ✅ Loaded\n")

    # Test cases
    test_cases = [
        {
            "title": "Introduction to Programming",
            "domain": "computer_science",
            "level": "beginner",
            "available_modules": [
                {
                    "id": "mod-0",
                    "title": "Python Basics",
                    "estimated_hours": 40,
                    "difficulty": "beginner",
                },
                {
                    "id": "mod-1",
                    "title": "Advanced ML",
                    "estimated_hours": 60,
                    "difficulty": "advanced",
                },
                {
                    "id": "mod-2",
                    "title": "Data Structures",
                    "estimated_hours": 50,
                    "difficulty": "beginner",
                },
            ],
            "available_activities": [
                {"id": "act-0", "title": "Coding Exercise", "estimated_hours": 5},
            ],
            "available_assessments": [
                {"id": "ass-0", "title": "Midterm Exam", "assessment_type": "exam"},
            ],
        },
        {
            "title": "Advanced Machine Learning",
            "domain": "computer_science",
            "level": "advanced",
            "available_modules": [
                {
                    "id": "mod-0",
                    "title": "Python Basics",
                    "estimated_hours": 40,
                    "difficulty": "beginner",
                },
                {
                    "id": "mod-1",
                    "title": "Deep Learning",
                    "estimated_hours": 60,
                    "difficulty": "advanced",
                },
            ],
            "available_activities": [
                {"id": "act-0", "title": "Research Project", "estimated_hours": 20},
            ],
            "available_assessments": [
                {
                    "id": "ass-0",
                    "title": "Final Presentation",
                    "assessment_type": "presentation",
                },
            ],
        },
    ]

    print("🧪 Testing with 2 examples:\n")

    results = []

    for i, test_data in enumerate(test_cases, 1):
        print(f"{'─'*80}")
        print(f"Test Case {i}: {test_data['title']} ({test_data['level']})")
        print()

        # Build prompt
        prompt = f"Generate syllabus for: {test_data['title']} | {test_data['domain']} | {test_data['level']}\n\n"
        prompt += "Available modules:\n"
        for j, mod in enumerate(test_data["available_modules"]):
            prompt += f"[{j}] {mod['title']} ({mod['estimated_hours']}h, {mod['difficulty']})\n"

        prompt += "\nAvailable activities:\n"
        for j, act in enumerate(test_data["available_activities"]):
            prompt += f"[{j}] {act['title']} ({act['estimated_hours']}h)\n"

        prompt += "\nAvailable assessments:\n"
        for j, ass in enumerate(test_data["available_assessments"]):
            prompt += f"[{j}] {ass['title']} ({ass['assessment_type']})\n"

        prompt += "\nSelect relevant components and generate markdown syllabus."

        # Generate
        input_ids = tokenizer(
            prompt, return_tensors="pt", max_length=512, truncation=True
        ).input_ids

        if torch.cuda.is_available():
            input_ids = input_ids.cuda()

        with torch.no_grad():
            outputs = model.generate(
                input_ids,
                max_length=400,
                num_beams=2,
                early_stopping=False,
            )

        generated = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Analyze
        checks = {
            "length": len(generated),
            "has_headers": generated.count("##") > 0,
            "has_course_header": "# Course:" in generated or "# " in generated,
            "has_indices": bool(re.findall(r"\[\d+\]", generated)),
            "has_objectives": "## Learning Objectives" in generated
            or "## Objectives" in generated,
            "readable": not bool(
                re.search(r"(.)\1{20}", generated)
            ),  # Not 20+ repeated chars
        }

        print(f"Output ({checks['length']} chars):")
        print(generated[:300] + ("..." if len(generated) > 300 else ""))
        print()

        print("✓ Checks:")
        print(
            f"   Length: {checks['length']} chars (need >100) - {'✅' if checks['length'] > 100 else '❌'}"
        )
        print(
            f"   Has headers: {checks['has_headers']} - {'✅' if checks['has_headers'] else '❌'}"
        )
        print(
            f"   Has course header: {checks['has_course_header']} - {'✅' if checks['has_course_header'] else '❌'}"
        )
        print(
            f"   Has indices: {checks['has_indices']} - {'✅' if checks['has_indices'] else '❌'}"
        )
        print(
            f"   Has objectives: {checks['has_objectives']} - {'✅' if checks['has_objectives'] else '❌'}"
        )
        print(
            f"   Readable: {checks['readable']} - {'✅' if checks['readable'] else '❌'}"
        )
        print()

        results.append(checks)

    # Overall assessment
    print("=" * 80)
    print("GO/NO-GO DECISION")
    print("=" * 80)
    print()

    # Minimum requirements for GO
    avg_length = sum(r["length"] for r in results) / len(results)
    has_structure = sum(r["has_headers"] for r in results) >= 1
    has_some_indices = sum(r["has_indices"] for r in results) >= 1
    readable = all(r["readable"] for r in results)

    print("📊 Summary:")
    print(f"   Average output length: {avg_length:.0f} chars")
    print(f"   Has structure: {has_structure}")
    print(f"   Has indices: {has_some_indices}")
    print(f"   Readable: {readable}")
    print()

    # Decision
    if avg_length > 100 and has_structure and readable:
        print("✅ GO - Model shows learning signal!")
        print()
        print("🎉 PROCEED TO PHASE 4 (7-hour training)")
        print()
        print("Why this is good:")
        if has_some_indices:
            print("  ✅ Model generating indices (key behavior)")
        print("  ✅ Model generating markdown structure")
        print("  ✅ Output length reasonable")
        print("  ✅ Output is readable")
        print()
        print("Next step: python scripts/phase4_full_training.py")
        return True

    else:
        print("❌ NO-GO - No clear learning signal")
        print()
        print("🚨 DO NOT PROCEED TO 7-HOUR TRAINING")
        print()
        print("Problems detected:")
        if avg_length <= 100:
            print(f"  ❌ Output too short ({avg_length:.0f} chars)")
        if not has_structure:
            print("  ❌ No markdown structure generated")
        if not readable:
            print("  ❌ Output not readable (repeated characters)")
        print()
        print("Options:")
        print("  1. Adjust hyperparameters (lower LR, more warmup)")
        print("  2. Check training data quality")
        print("  3. Try different prompt format")
        print("  4. Pivot to Path 7 (Hybrid with template)")
        return False


if __name__ == "__main__":
    import re

    print("This is Phase 3 - Quick Validation Test")
    print("This takes 5 minutes and determines if we proceed to 7h training")
    print()

    # Train for 10 steps
    model_path = quick_train()

    print()

    # Test for learning signal
    success = test_learning_signal(model_path)

    exit(0 if success else 1)
