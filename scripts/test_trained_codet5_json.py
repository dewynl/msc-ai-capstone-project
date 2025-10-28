#!/usr/bin/env python3
"""Test our trained CodeT5 model's current output quality."""

import json

import torch
from transformers import RobertaTokenizer, T5ForConditionalGeneration


def test_trained_model():
    """Test the trained model with actual evaluation input."""
    print("🧪 Testing TRAINED CodeT5 Model")
    print("=" * 80)

    # Load our trained model
    print("\n📦 Loading trained model: models/codet5-1300examples")
    tokenizer = RobertaTokenizer.from_pretrained("./models/codet5-1300examples")
    model = T5ForConditionalGeneration.from_pretrained("./models/codet5-1300examples")
    print("   ✅ Model loaded")

    # Evaluation-style input (NO component lists - this is the problem!)
    eval_input = {
        "title": "Introduction to Programming",
        "domain": "computer_science",
        "level": "beginner",
        "duration": "semester",
        "description": "Learn programming fundamentals using Python",
        "learning_objectives": [
            "Understand basic programming concepts",
            "Write simple Python programs",
            "Debug code effectively",
        ],
    }

    prompt = f"Generate course syllabus: {json.dumps(eval_input)}"

    print(f"\n📝 Input ({len(prompt)} chars):")
    print(prompt)

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

    # Validate
    print("\n✅ Validation:")
    print(f"   Length: {len(generated)} chars (target: 800-1000)")
    print(f"   Has .build(): {'.build()' in generated}")
    print(f"   Has add_module: {'add_module' in generated}")
    print(f"   Has add_objective: {'add_objective' in generated}")

    # Try syntax check
    try:
        compile(generated, "<string>", "exec")
        print("   Syntax: ✅ Valid Python")
    except SyntaxError as e:
        print(f"   Syntax: ❌ {e}")

    return generated


if __name__ == "__main__":
    output = test_trained_model()
