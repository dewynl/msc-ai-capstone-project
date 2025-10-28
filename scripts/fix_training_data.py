#!/usr/bin/env python3
"""
Fix Training Data - Add .build() to all examples

This script fixes the critical bug where all 1,117 training examples
are missing the .build() call at the end.

Preserves the original file and creates a new fixed version.
"""

import json
from pathlib import Path


def fix_training_data(input_file: str, output_file: str):
    """Add .build() to all training examples."""

    print("🔧 Fixing Training Data")
    print("=" * 80)

    # Load original data
    print(f"\n📂 Loading: {input_file}")
    with open(input_file, "r") as f:
        data = json.load(f)

    print(f"   Total examples: {len(data)}")

    # Statistics
    fixed_count = 0
    already_had_build = 0

    # Fix each example
    print("\n🔨 Applying fixes...")
    for i, example in enumerate(data):
        output = example["output_calls"]

        # Check if already has .build()
        if ".build()" in output:
            already_had_build += 1
            continue

        # Add .build() at the end
        example["output_calls"] = output + "\nb.build()"
        fixed_count += 1

        if (i + 1) % 200 == 0:
            print(f"   Processed {i + 1}/{len(data)} examples...")

    print("\n✅ Fixes applied:")
    print(f"   - Added .build(): {fixed_count} examples")
    print(f"   - Already had .build(): {already_had_build} examples")

    # Validate
    print("\n🔍 Validating fixes...")
    all_have_build = all(".build()" in ex["output_calls"] for ex in data)

    if all_have_build:
        print("   ✅ All examples now have .build()")
    else:
        print("   ❌ ERROR: Some examples still missing .build()")
        return False

    # Check output lengths
    lengths = [len(ex["output_calls"]) for ex in data]
    avg_length = sum(lengths) / len(lengths)
    min_length = min(lengths)
    max_length = max(lengths)

    print("\n📊 Output Statistics:")
    print(f"   Average length: {avg_length:.0f} chars")
    print(f"   Min length: {min_length} chars")
    print(f"   Max length: {max_length} chars")
    print("   Target range: 800-1000 chars")

    if avg_length < 700:
        print("   ⚠️  WARNING: Average length still seems short")

    # Save fixed data
    print(f"\n💾 Saving fixed data: {output_file}")
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"   ✅ Saved {len(data)} fixed examples")

    # Show sample
    print("\n📝 Sample fixed output (first example, last 200 chars):")
    sample = data[0]["output_calls"]
    print(f"   ...{sample[-200:]}")

    return True


def main():
    """Fix the training data."""
    import argparse

    parser = argparse.ArgumentParser(description="Fix training data by adding .build()")
    parser.add_argument(
        "--input",
        type=str,
        default="data/training/rag_enhanced_t5_training_1300.json",
        help="Input file path",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/training/rag_enhanced_t5_training_1300_FIXED.json",
        help="Output file path",
    )
    args = parser.parse_args()

    success = fix_training_data(args.input, args.output)

    if success:
        print("\n" + "=" * 80)
        print("✅ SUCCESS - Training data fixed!")
        print(f"   Original: {args.input}")
        print(f"   Fixed: {args.output}")
        print("\n🚀 Next step: Train model with fixed data:")
        print("   python scripts/train_1300_examples.py \\")
        print(f"       --training-data {args.output} \\")
        print("       --output-dir models/codet5-1300examples-fixed")
    else:
        print("\n❌ FAILED - Check errors above")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
