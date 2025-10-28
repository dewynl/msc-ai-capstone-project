#!/usr/bin/env python3
"""
Phase 0: Token Length Validation

Verify that our compact prompt format fits within CodeT5's 512 token limit.
This is the first GO/NO-GO gate. If this fails, we must redesign the prompt
or pivot to a different approach.

CRITICAL: Do not proceed to Phase 1 without this passing.
"""

import json
from pathlib import Path

from transformers import RobertaTokenizer


def build_ultra_compact_prompt(example: dict) -> str:
    """
    Build the most compact prompt possible while keeping essential info.

    Model needs:
    - Course context (title, domain, level)
    - Available components with indices
    - Instruction to select

    Model does NOT need:
    - Long descriptions
    - Detailed prerequisites
    - Complex metadata
    """
    # Extract JSON from input_text string
    input_text = example["input_text"]
    json_str = input_text.replace("Generate course syllabus: ", "")
    input_data = json.loads(json_str)

    # Course context (very compact)
    prompt = f"Generate syllabus for: {input_data['title']} | {input_data['domain']} | {input_data['level']}\n\n"

    # Available modules (titles only - no descriptions!)
    prompt += "Available modules:\n"
    for i, mod in enumerate(input_data.get("available_modules", [])[:20]):
        # Just index + title, that's it!
        prompt += f"[{i}] {mod['title']}\n"

    # Available activities
    prompt += "\nAvailable activities:\n"
    for i, act in enumerate(input_data.get("available_activities", [])[:15]):
        prompt += f"[{i}] {act['title']}\n"

    # Available assessments
    prompt += "\nAvailable assessments:\n"
    for i, ass in enumerate(input_data.get("available_assessments", [])[:5]):
        prompt += f"[{i}] {ass['title']}\n"

    # Instruction
    prompt += (
        "\nSelect relevant components and generate course syllabus in markdown format."
    )

    return prompt


def build_medium_compact_prompt(example: dict) -> str:
    """
    Build a medium-compact prompt with minimal metadata.

    Includes hours and difficulty for better selection context.
    """
    # Extract JSON from input_text string
    input_text = example["input_text"]
    json_str = input_text.replace("Generate course syllabus: ", "")
    input_data = json.loads(json_str)

    prompt = f"Generate syllabus for: {input_data['title']} | {input_data['domain']} | {input_data['level']}\n\n"

    # Modules with minimal metadata
    prompt += "Available modules:\n"
    for i, mod in enumerate(input_data.get("available_modules", [])[:20]):
        prompt += f"[{i}] {mod['title']} ({mod.get('estimated_hours', 0)}h, {mod.get('difficulty', 'N/A')})\n"

    # Activities
    prompt += "\nAvailable activities:\n"
    for i, act in enumerate(input_data.get("available_activities", [])[:15]):
        prompt += f"[{i}] {act['title']} ({act.get('estimated_hours', 0)}h)\n"

    # Assessments
    prompt += "\nAvailable assessments:\n"
    for i, ass in enumerate(input_data.get("available_assessments", [])[:5]):
        prompt += f"[{i}] {ass['title']} ({ass.get('assessment_type', 'N/A')})\n"

    prompt += "\nSelect relevant components and generate markdown syllabus."

    return prompt


def analyze_token_distribution(prompt: str, tokenizer) -> dict:
    """Analyze where tokens are being used."""

    lines = prompt.split("\n")
    distribution = {}

    for line in lines:
        if "modules:" in line.lower():
            section = "modules_header"
        elif "activities:" in line.lower():
            section = "activities_header"
        elif "assessments:" in line.lower():
            section = "assessments_header"
        elif line.startswith("["):
            section = "component_line"
        else:
            section = "other"

        tokens = tokenizer(line).input_ids
        distribution[section] = distribution.get(section, 0) + len(tokens)

    return distribution


def main():
    print("=" * 80)
    print("PHASE 0: TOKEN LENGTH VALIDATION")
    print("=" * 80)
    print("\n🎯 Goal: Verify prompts fit in CodeT5's 512 token limit")
    print("⚠️  CRITICAL: This is a GO/NO-GO gate\n")

    # Load tokenizer
    print("📦 Loading RoBERTa tokenizer (used by CodeT5)...")
    try:
        tokenizer = RobertaTokenizer.from_pretrained("Salesforce/codet5-small")
        print("   ✅ Loaded successfully\n")
    except Exception as e:
        print(f"   ❌ Failed to load: {e}")
        print("   Trying local cache...")
        tokenizer = RobertaTokenizer.from_pretrained("./models/codet5-1300examples")
        print("   ✅ Loaded from cache\n")

    # Load training data
    data_path = Path("data/training/rag_enhanced_t5_training_1300_FIXED.json")
    print(f"📂 Loading training data: {data_path}")

    if not data_path.exists():
        print(f"   ❌ File not found: {data_path}")
        return False

    with open(data_path) as f:
        data = json.load(f)

    print(f"   ✅ Loaded {len(data)} examples\n")

    # Find examples with varying component counts
    examples_to_test = []

    # Helper to extract JSON from example
    def get_input_data(ex):
        json_str = ex["input_text"].replace("Generate course syllabus: ", "")
        return json.loads(json_str)

    # Example with most modules
    max_modules = max(
        data, key=lambda x: len(get_input_data(x).get("available_modules", []))
    )
    examples_to_test.append(("Max modules", max_modules))

    # Example with most activities
    max_activities = max(
        data, key=lambda x: len(get_input_data(x).get("available_activities", []))
    )
    examples_to_test.append(("Max activities", max_activities))

    # Random middle example
    examples_to_test.append(("Average case", data[len(data) // 2]))

    # Example with minimal components (edge case)
    min_components = min(
        data, key=lambda x: len(get_input_data(x).get("available_modules", []))
    )
    examples_to_test.append(("Min components", min_components))

    print("📊 Testing 4 examples (worst case, best case, average):\n")

    results = []

    for label, example in examples_to_test:
        input_data = get_input_data(example)
        num_modules = len(input_data.get("available_modules", []))
        num_activities = len(input_data.get("available_activities", []))
        num_assessments = len(input_data.get("available_assessments", []))

        print(f"{'─'*80}")
        print(f"Test Case: {label}")
        print(
            f"Components: {num_modules} modules, {num_activities} activities, {num_assessments} assessments"
        )
        print()

        # Test ultra-compact
        prompt_ultra = build_ultra_compact_prompt(example)
        tokens_ultra = tokenizer(prompt_ultra, return_tensors="pt").input_ids

        print("  Ultra-Compact Format:")
        print(f"    Characters: {len(prompt_ultra)}")
        print(f"    Tokens: {tokens_ultra.shape[1]}")
        print(
            f"    Status: {'✅ FITS' if tokens_ultra.shape[1] <= 512 else '❌ EXCEEDS'} (512 limit)"
        )

        # Test medium-compact
        prompt_medium = build_medium_compact_prompt(example)
        tokens_medium = tokenizer(prompt_medium, return_tensors="pt").input_ids

        print("\n  Medium-Compact Format (with hours/difficulty):")
        print(f"    Characters: {len(prompt_medium)}")
        print(f"    Tokens: {tokens_medium.shape[1]}")
        print(
            f"    Status: {'✅ FITS' if tokens_medium.shape[1] <= 512 else '❌ EXCEEDS'} (512 limit)"
        )

        results.append(
            {
                "label": label,
                "components": (num_modules, num_activities, num_assessments),
                "ultra_tokens": tokens_ultra.shape[1],
                "medium_tokens": tokens_medium.shape[1],
                "ultra_fits": tokens_ultra.shape[1] <= 512,
                "medium_fits": tokens_medium.shape[1] <= 512,
            }
        )

        print()

    # Summary
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print()

    ultra_all_fit = all(r["ultra_fits"] for r in results)
    medium_all_fit = all(r["medium_fits"] for r in results)

    print("📋 Results by Format:\n")
    print("  Ultra-Compact (titles only):")
    print(f"    All examples fit: {'✅ YES' if ultra_all_fit else '❌ NO'}")
    print(f"    Max tokens: {max(r['ultra_tokens'] for r in results)}/512")
    print(
        f"    Avg tokens: {sum(r['ultra_tokens'] for r in results)/len(results):.0f}/512"
    )
    print()
    print("  Medium-Compact (titles + metadata):")
    print(f"    All examples fit: {'✅ YES' if medium_all_fit else '❌ NO'}")
    print(f"    Max tokens: {max(r['medium_tokens'] for r in results)}/512")
    print(
        f"    Avg tokens: {sum(r['medium_tokens'] for r in results)/len(results):.0f}/512"
    )
    print()

    # Decision
    print("=" * 80)
    print("GO/NO-GO DECISION")
    print("=" * 80)
    print()

    if medium_all_fit:
        print("✅ GO - Proceed with Phase 1")
        print()
        print("📝 Recommendation: Use MEDIUM-COMPACT format")
        print("   - Includes hours and difficulty (helps model selection)")
        print("   - Still fits comfortably in 512 tokens")
        print("   - Provides good context for learning")
        print()
        print("🚀 Next step: Phase 1 - Convert training data")
        return True, "medium"

    elif ultra_all_fit:
        print("⚠️  CONDITIONAL GO - Can proceed with limitations")
        print()
        print("📝 Recommendation: Use ULTRA-COMPACT format")
        print("   - Titles only, no metadata")
        print("   - Less context for model (might affect quality)")
        print("   - Still viable, proceed with caution")
        print()
        print("🚀 Next step: Phase 1 - Convert training data (ultra-compact)")
        return True, "ultra"

    else:
        print("❌ NO-GO - Token limit exceeded")
        print()
        print("❌ Even ultra-compact format exceeds 512 tokens")
        print()
        print("Options:")
        print("  1. Limit to 10 modules per request (reduces coverage)")
        print("  2. Increase max_length to 640 tokens (may affect training)")
        print("  3. Pivot to Path 7 (Hybrid with template)")
        print()
        print("⚠️  DO NOT PROCEED to Phase 1 without resolving this issue")
        return False, None

    print("=" * 80)


if __name__ == "__main__":
    success, format_type = main()

    # Save result for next phase
    if success:
        result = {"success": True, "format": format_type, "timestamp": "2025-10-28"}
        with open("phase0_result.json", "w") as f:
            json.dump(result, f, indent=2)
        print("\n💾 Result saved to: phase0_result.json")

    exit(0 if success else 1)
