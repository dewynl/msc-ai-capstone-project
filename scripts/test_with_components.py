#!/usr/bin/env python3
"""Test model with TRAINING-FORMAT input (includes component lists)."""

import json

import torch
from transformers import RobertaTokenizer, T5ForConditionalGeneration


def test_with_components():
    """Test with component lists included (training format)."""
    print("🧪 Testing with COMPONENT LISTS (Training Format)")
    print("=" * 80)

    # Load model
    print("\n📦 Loading model...")
    tokenizer = RobertaTokenizer.from_pretrained("./models/codet5-1300examples")
    model = T5ForConditionalGeneration.from_pretrained("./models/codet5-1300examples")
    print("   ✅ Loaded")

    # Training-style input WITH component lists
    training_input = {
        "title": "Introduction to Programming",
        "domain": "computer_science",
        "level": "beginner",
        "duration": "semester",
        "description": "Learn programming fundamentals using Python",
        "available_modules": [
            {"id": "mod-1", "title": "Algorithm Analysis", "difficulty": "beginner"},
            {"id": "mod-2", "title": "Data Structures", "difficulty": "beginner"},
            {"id": "mod-3", "title": "Python Basics", "difficulty": "beginner"},
            {"id": "mod-4", "title": "Debugging Techniques", "difficulty": "beginner"},
        ],
        "available_activities": [
            {"id": "act-1", "title": "Coding Exercise 1", "type": "exercise"},
            {"id": "act-2", "title": "Programming Project", "type": "project"},
            {"id": "act-3", "title": "Code Review", "type": "review"},
        ],
        "available_assessments": [
            {"id": "ass-1", "title": "Midterm Exam", "type": "exam"},
            {"id": "ass-2", "title": "Final Project", "type": "assignment"},
        ],
    }

    prompt = f"Generate course syllabus: {json.dumps(training_input)}"

    print(f"\n📝 Input ({len(prompt)} chars):")
    print(prompt[:400] + "...")

    # Generate
    input_ids = tokenizer(
        prompt, return_tensors="pt", max_length=640, truncation=True
    ).input_ids

    print("\n⚙️  Generating...")
    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            max_length=536,
            num_beams=4,
            early_stopping=False,
            no_repeat_ngram_size=2,
        )

    generated = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print(f"\n📤 Generated Output ({len(generated)} chars):")
    print(generated)

    # Validation
    print("\n✅ Validation:")
    print(f"   Length: {len(generated)} chars (target: 800-1000)")
    print(f"   Has .build(): {'.build()' in generated}")
    print(f"   Has add_module: {'add_module' in generated}")
    print(f"   Has add_activity: {'add_activity' in generated}")
    print(f"   Has add_assessment: {'add_assessment' in generated}")
    print(f"   Has add_objective: {'add_objective' in generated}")

    # Count function calls
    lines = generated.split("\n")
    print("\n📊 Function Call Breakdown:")
    print(f"   Total lines: {len(lines)}")
    print(f"   set_info: {sum(1 for l in lines if 'set_info' in l)}")
    print(f"   add_objective: {sum(1 for l in lines if 'add_objective' in l)}")
    print(f"   add_module: {sum(1 for l in lines if 'add_module' in l)}")
    print(f"   add_activity: {sum(1 for l in lines if 'add_activity' in l)}")
    print(f"   add_assessment: {sum(1 for l in lines if 'add_assessment' in l)}")
    print(f"   build(): {sum(1 for l in lines if 'build()' in l)}")


if __name__ == "__main__":
    test_with_components()
