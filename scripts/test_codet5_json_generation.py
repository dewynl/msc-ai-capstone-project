#!/usr/bin/env python3
"""
Test CodeT5 JSON Generation Capabilities

Compare CodeT5's ability to generate:
1. Python function calls (current approach)
2. JSON with IDs (lightweight approach)
3. JSON with selection indices (novel approach)
"""

import json

import torch
from transformers import RobertaTokenizer, T5ForConditionalGeneration


def test_format(model, tokenizer, prompt: str, format_name: str, max_length: int = 512):
    """Test a specific output format."""
    print(f"\n{'='*80}")
    print(f"Testing: {format_name}")
    print(f"{'='*80}")
    print(f"\nInput Prompt ({len(prompt)} chars):")
    print(prompt[:200] + "..." if len(prompt) > 200 else prompt)

    # Tokenize
    input_ids = tokenizer(
        prompt, return_tensors="pt", max_length=512, truncation=True
    ).input_ids

    # Generate
    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            max_length=max_length,
            num_beams=4,
            early_stopping=False,
            no_repeat_ngram_size=2,
        )

    # Decode
    generated = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print(f"\nGenerated Output ({len(generated)} chars):")
    print(generated)

    # Validate
    validation = validate_output(generated, format_name)
    print(f"\nValidation: {validation}")

    return generated, validation


def validate_output(output: str, format_name: str) -> str:
    """Validate the generated output."""
    if "Function Calls" in format_name:
        # Check Python syntax
        try:
            compile(output, "<string>", "exec")
            return "✅ Valid Python syntax"
        except SyntaxError as e:
            return f"❌ Syntax error: {e}"

    elif "JSON" in format_name:
        # Check JSON validity
        try:
            parsed = json.loads(output)
            return f"✅ Valid JSON with {len(parsed)} keys"
        except json.JSONDecodeError as e:
            return f"❌ JSON parse error: {e}"

    return "⚠️ Unknown format"


def main():
    """Run JSON generation tests."""
    print("🧪 CodeT5 JSON Generation Testing")
    print("=" * 80)

    # Load base CodeT5-small (pretrained, no fine-tuning)
    print("\n📦 Loading CodeT5-small (base pretrained model)...")
    model_name = "Salesforce/codet5-small"

    try:
        tokenizer = RobertaTokenizer.from_pretrained(model_name)
        model = T5ForConditionalGeneration.from_pretrained(model_name)
        print("   ✅ Model loaded successfully")
    except Exception as e:
        print(f"   ❌ Failed to load model: {e}")
        print("\n   Trying local model instead...")
        model_name = "./models/codet5-1300examples"
        tokenizer = RobertaTokenizer.from_pretrained(model_name)
        model = T5ForConditionalGeneration.from_pretrained(model_name)
        print("   ✅ Local model loaded")

    # Test case
    course_data = {
        "title": "Introduction to Programming",
        "domain": "computer_science",
        "level": "beginner",
        "description": "Learn Python programming fundamentals",
    }

    # TEST 1: Python Function Calls (current approach)
    prompt1 = f"""Generate Python function calls to build a course syllabus:
Course: {json.dumps(course_data)}

Expected format:
b = SyllabusBuilder()
b.set_info(title, domain, level, duration, description)
b.add_objective("...")
b.add_module_by_id("...")
b.build()
"""

    test_format(
        model, tokenizer, prompt1, "Format 1: Python Function Calls", max_length=300
    )

    # TEST 2: JSON with IDs (lightweight approach)
    prompt2 = f"""Generate JSON for a course syllabus:
Course: {json.dumps(course_data)}

Expected JSON format:
{{
  "course_info": {{"title": "...", "domain": "...", "level": "..."}},
  "learning_objectives": ["...", "..."],
  "module_ids": ["id1", "id2"],
  "activity_ids": ["id1", "id2"]
}}
"""

    test_format(
        model, tokenizer, prompt2, "Format 2: Lightweight JSON (IDs)", max_length=300
    )

    # TEST 3: JSON with Selection Indices (novel approach)
    prompt3 = f"""Generate JSON selecting from available modules:
Course: {json.dumps(course_data)}
Available modules:
  0: "Algorithm Analysis and Big O Notation"
  1: "Data Structures Fundamentals"
  2: "Python Programming Basics"
  3: "Web Development Fundamentals"

Select relevant modules by index:
{{
  "selected_module_indices": [0, 1, 2],
  "learning_objectives": ["...", "..."]
}}
"""

    test_format(
        model, tokenizer, prompt3, "Format 3: Selection JSON (Indices)", max_length=256
    )

    print("\n" + "=" * 80)
    print("📊 TESTING COMPLETE")
    print("=" * 80)
    print("\n💡 Insights:")
    print("   - If Function Calls work: Current approach might be viable")
    print("   - If JSON works better: Switch to JSON-based training")
    print("   - If Selection works best: Use index-based selection approach")


if __name__ == "__main__":
    main()
