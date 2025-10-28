#!/usr/bin/env python3
"""
Phase 3B: Extended Validation Test (100 steps)

Based on Phase 3 results, loss was still dropping (7.97 → 1.28).
Model learned indices but not structure yet.

This extends training to 100 steps (~10 minutes) to see if structure emerges.
"""

import json
import re

import torch
from datasets import Dataset
from transformers import (
    DataCollatorForSeq2Seq,
    RobertaTokenizer,
    T5ForConditionalGeneration,
    Trainer,
    TrainingArguments,
)


def load_training_data(data_path: str, max_examples: int = 200):
    """Load a small subset for extended test."""
    print(f"📂 Loading training data: {data_path}")

    with open(data_path) as f:
        data = json.load(f)

    # Use 200 examples for extended test
    data = data[:max_examples]

    print(f"   ✅ Loaded {len(data)} examples (extended test subset)\n")

    return data


def prepare_inputs(examples, tokenizer, max_input_length=512, max_output_length=400):
    """Tokenize inputs and outputs."""
    inputs = []
    outputs = []

    for ex in examples:
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


def extended_train(output_dir: str = "models/codet5-markdown-EXTENDED"):
    """Train for 100 steps to check if structure emerges."""
    print("=" * 80)
    print("PHASE 3B: EXTENDED VALIDATION TEST")
    print("=" * 80)
    print("\n🎯 Goal: Train 100 steps and check if markdown structure emerges")
    print("⏱️  Expected time: 10-15 minutes\n")
    print("💡 Rationale: Phase 3 showed indices learning (loss 7.97 → 1.28)")
    print("   Structure might emerge with more steps!\n")

    # Load model and tokenizer
    print("📦 Loading CodeT5-small...")
    tokenizer = RobertaTokenizer.from_pretrained("Salesforce/codet5-small")
    model = T5ForConditionalGeneration.from_pretrained("Salesforce/codet5-small")
    print("   ✅ Loaded\n")

    # Load data
    data = load_training_data(
        "data/training/markdown_training_1300.json", max_examples=200
    )

    # Prepare inputs
    print("🔄 Tokenizing data...")
    tokenized = prepare_inputs(data, tokenizer)
    dataset = Dataset.from_dict(tokenized)
    print("   ✅ Tokenized\n")

    # Training args
    print("⚙️  Training configuration:")
    print("   Steps: 100 (Extended test)")
    print("   Batch size: 4")
    print("   Learning rate: 3e-4")
    print("   Max output: 400 tokens")
    print("   Logging: Every 10 steps\n")

    training_args = TrainingArguments(
        output_dir=output_dir,
        max_steps=100,
        per_device_train_batch_size=4,
        learning_rate=3e-4,
        save_steps=100,
        logging_steps=10,
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
    print("🚀 Starting extended training (100 steps, ~10-15 minutes)...")
    print("─" * 80)
    trainer.train()
    print("─" * 80)
    print("✅ Extended training complete!\n")

    # Save
    print(f"💾 Saving to: {output_dir}")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("   ✅ Saved\n")

    return output_dir


def test_learning_signal(model_path: str):
    """Test if model shows markdown structure after 100 steps."""
    print("=" * 80)
    print("TESTING FOR STRUCTURE EMERGENCE")
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
        {
            "title": "Database Systems",
            "domain": "computer_science",
            "level": "intermediate",
            "available_modules": [
                {
                    "id": "mod-0",
                    "title": "SQL Fundamentals",
                    "estimated_hours": 30,
                    "difficulty": "beginner",
                },
                {
                    "id": "mod-1",
                    "title": "Database Design",
                    "estimated_hours": 40,
                    "difficulty": "intermediate",
                },
                {
                    "id": "mod-2",
                    "title": "Query Optimization",
                    "estimated_hours": 50,
                    "difficulty": "advanced",
                },
            ],
            "available_activities": [
                {"id": "act-0", "title": "Database Project", "estimated_hours": 10},
            ],
            "available_assessments": [
                {"id": "ass-0", "title": "Practical Exam", "assessment_type": "exam"},
            ],
        },
    ]

    print("🧪 Testing with 3 examples:\n")

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
            "has_headers": generated.count("##") >= 1,
            "has_course_header": "# Course:" in generated or "# " in generated[:50],
            "has_indices": bool(re.findall(r"\[\d+\]", generated)),
            "has_objectives_section": "## Learning Objectives" in generated
            or "## Objectives" in generated,
            "has_modules_section": "## Selected Modules" in generated
            or "## Modules" in generated,
            "readable": not bool(re.search(r"(.)\1{20}", generated)),
            "has_structure": generated.count("##") >= 2,  # At least 2 sections
        }

        print(f"Output ({checks['length']} chars):")
        print(generated[:400] + ("..." if len(generated) > 400 else ""))
        print()

        print("✓ Checks:")
        print(
            f"   Length: {checks['length']} chars - {'✅' if checks['length'] > 100 else '❌'}"
        )
        print(
            f"   Has course header: {checks['has_course_header']} - {'✅' if checks['has_course_header'] else '❌'}"
        )
        print(
            f"   Has sections (##): {checks['has_structure']} - {'✅' if checks['has_structure'] else '❌'}"
        )
        print(
            f"   Has objectives section: {checks['has_objectives_section']} - {'✅' if checks['has_objectives_section'] else '❌'}"
        )
        print(
            f"   Has modules section: {checks['has_modules_section']} - {'✅' if checks['has_modules_section'] else '❌'}"
        )
        print(
            f"   Has indices: {checks['has_indices']} - {'✅' if checks['has_indices'] else '❌'}"
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

    # Calculate metrics
    avg_length = sum(r["length"] for r in results) / len(results)
    has_structure = sum(r["has_structure"] for r in results) >= 2
    has_sections = (
        sum(r["has_objectives_section"] or r["has_modules_section"] for r in results)
        >= 2
    )
    has_indices = sum(r["has_indices"] for r in results) >= 2
    readable = all(r["readable"] for r in results)

    print("📊 Summary:")
    print(f"   Average output length: {avg_length:.0f} chars")
    print(f"   Has markdown structure: {has_structure}")
    print(f"   Has proper sections: {has_sections}")
    print(f"   Has indices: {has_indices}")
    print(f"   Readable: {readable}")
    print()

    # Decision
    if avg_length > 150 and has_structure and has_sections and has_indices and readable:
        print("✅ GO - Model shows both structure AND selection!")
        print()
        print("🎉 PROCEED TO PHASE 4 (7-hour training)")
        print()
        print("Evidence of learning:")
        print("  ✅ Generating markdown structure (headers, sections)")
        print("  ✅ Generating indices based on course level")
        print("  ✅ Output length appropriate")
        print("  ✅ Output is readable and structured")
        print()
        print("Next step: python scripts/phase4_full_training.py")
        return True

    elif has_indices and readable:
        print("⚠️  PARTIAL - Indices working, structure needs work")
        print()
        print("🤔 Model learned selection but not formatting")
        print()
        print("Options:")
        print("  1. Continue to full 7h training (might emerge with more data/epochs)")
        print("  2. Simplify output format (remove markdown, just indices)")
        print("  3. Pivot to Path 7 (Hybrid - template provides structure)")
        print()
        print("Recommendation: Pivot to Path 7 for 90% guaranteed success")
        return False

    else:
        print("❌ NO-GO - Still no clear learning signal")
        print()
        print("🚨 PIVOT TO PATH 7 (Hybrid with template)")
        print()
        print("Reason: 100 steps not enough for model to learn this task")
        return False


if __name__ == "__main__":
    print("Phase 3B - Extended Validation Test (100 steps)")
    print()

    # Train for 100 steps
    model_path = extended_train()

    print()

    # Test for structure emergence
    success = test_learning_signal(model_path)

    exit(0 if success else 1)
