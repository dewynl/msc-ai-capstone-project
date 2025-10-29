"""
Test script for pedagogical loss function.

Tests each component with real module data to verify correct behavior.
"""

import sys

sys.path.append("src/training")

import json

import torch
from pedagogical_loss import PedagogicalLoss


def test_pedagogical_loss():
    """Test pedagogical loss with real module data."""

    print("=" * 80)
    print("PEDAGOGICAL LOSS FUNCTION TEST")
    print("=" * 80)

    # Initialize loss function
    print("\n1. Loading modules and initializing loss function...")
    loss_fn = PedagogicalLoss(
        modules_path="data/components/modules.json",
        lambda_prereq=1.0,
        lambda_diff=0.5,
        lambda_coverage=0.3,
    )
    print(f"   ✓ Loaded {len(loss_fn.modules)} modules")
    print(f"   ✓ Prerequisite graph: {len(loss_fn.prereq_graph)} entries")
    print(
        f"   ✓ Weights: λ_prereq={loss_fn.lambda_prereq}, λ_diff={loss_fn.lambda_diff}, λ_coverage={loss_fn.lambda_coverage}"
    )

    # Load some real module IDs for testing
    with open("data/components/modules.json") as f:
        modules = json.load(f)

    # Get CS modules with prerequisites
    cs_modules = [m for m in modules if m["domain"] == "computer_science"]
    modules_with_prereqs = [m for m in cs_modules if m.get("prerequisites", [])]

    print(f"\n2. Found {len(modules_with_prereqs)} CS modules with prerequisites")

    if len(modules_with_prereqs) == 0:
        print("   ⚠️  No modules with prerequisites found!")
        return

    # Test Case 1: Correct prerequisite ordering (low loss expected)
    print("\n" + "=" * 80)
    print("TEST CASE 1: Correct Prerequisite Ordering")
    print("=" * 80)

    # Find a module with prerequisites and build correct sequence
    test_module = modules_with_prereqs[0]
    prereqs = test_module.get("prerequisites", [])
    correct_sequence = prereqs + [test_module["id"]]

    print(f"\nTest module: {test_module['title'][:60]}")
    print(f"Prerequisites: {len(prereqs)}")
    print("Sequence: [prereq1, prereq2, ..., module]")

    metrics = loss_fn.evaluate_sequence_quality(correct_sequence)
    print("\nMetrics:")
    print(f"  Prerequisite Loss:    {metrics['prerequisite_loss']:.4f}")
    print(f"  Difficulty Loss:      {metrics['difficulty_loss']:.4f}")
    print(f"  Coverage Loss:        {metrics['coverage_loss']:.4f}")
    print(f"  Prereq Accuracy:      {metrics['prerequisite_accuracy']:.2%}")
    print(f"  Prereq Violations:    {metrics['prerequisite_violations']}")

    # Test Case 2: Incorrect prerequisite ordering (high loss expected)
    print("\n" + "=" * 80)
    print("TEST CASE 2: Incorrect Prerequisite Ordering")
    print("=" * 80)

    # Reverse the sequence - prerequisites come AFTER
    incorrect_sequence = [test_module["id"]] + prereqs

    print(f"\nTest module: {test_module['title'][:60]}")
    print("Sequence: [module, prereq1, prereq2, ...]  (WRONG ORDER)")

    metrics = loss_fn.evaluate_sequence_quality(incorrect_sequence)
    print("\nMetrics:")
    print(f"  Prerequisite Loss:    {metrics['prerequisite_loss']:.4f}")
    print(f"  Difficulty Loss:      {metrics['difficulty_loss']:.4f}")
    print(f"  Coverage Loss:        {metrics['coverage_loss']:.4f}")
    print(f"  Prereq Accuracy:      {metrics['prerequisite_accuracy']:.2%}")
    print(f"  Prereq Violations:    {metrics['prerequisite_violations']}")

    # Test Case 3: Mixed difficulty progression
    print("\n" + "=" * 80)
    print("TEST CASE 3: Difficulty Progression")
    print("=" * 80)

    # Get modules of different difficulties
    beginner = [m for m in cs_modules if m["difficulty"] == "beginner"][:3]
    intermediate = [m for m in cs_modules if m["difficulty"] == "intermediate"][:3]
    advanced = [m for m in cs_modules if m["difficulty"] == "advanced"][:3]

    # Good progression: beginner → intermediate → advanced
    good_sequence = [m["id"] for m in beginner + intermediate + advanced]
    print("\nGood progression: [beginner × 3] → [intermediate × 3] → [advanced × 3]")
    metrics = loss_fn.evaluate_sequence_quality(good_sequence)
    print(f"  Difficulty Loss: {metrics['difficulty_loss']:.4f}")

    # Bad progression: random jumps
    bad_sequence = [
        m["id"]
        for m in [
            beginner[0],
            advanced[0],
            beginner[1],
            intermediate[0],
            advanced[1],
            beginner[2],
        ]
    ]
    print("\nBad progression: [B, A, B, I, A, B]  (random jumps)")
    metrics = loss_fn.evaluate_sequence_quality(bad_sequence)
    print(f"  Difficulty Loss: {metrics['difficulty_loss']:.4f}")

    # Test Case 4: Topic diversity
    print("\n" + "=" * 80)
    print("TEST CASE 4: Topic Diversity")
    print("=" * 80)

    # Get 10 random CS modules for diversity test
    diverse_sequence = [m["id"] for m in cs_modules[:10]]
    print("\nDiverse sequence: 10 different CS modules")
    metrics = loss_fn.evaluate_sequence_quality(diverse_sequence)
    print(f"  Coverage Loss: {metrics['coverage_loss']:.4f}")

    # Repetitive sequence (same module repeated)
    repetitive_sequence = [cs_modules[0]["id"]] * 10
    print("\nRepetitive sequence: Same module × 10")
    metrics = loss_fn.evaluate_sequence_quality(repetitive_sequence)
    print(f"  Coverage Loss: {metrics['coverage_loss']:.4f}")

    # Test Case 5: Full forward pass with generation loss
    print("\n" + "=" * 80)
    print("TEST CASE 5: Full Forward Pass")
    print("=" * 80)

    # Simulate T5 generation loss
    fake_generation_loss = torch.tensor(2.5)
    test_sequence = [m["id"] for m in cs_modules[:15]]
    test_context = {"domain": "computer_science", "level": "intermediate"}

    total_loss, components = loss_fn(
        generation_loss=fake_generation_loss,
        predicted_sequence=test_sequence,
        input_context=test_context,
    )

    print("\nLoss Components:")
    print(f"  Generation Loss:      {components['generation_loss']:.4f}")
    print(f"  Prerequisite Loss:    {components['prereq_loss']:.4f}")
    print(f"  Difficulty Loss:      {components['difficulty_loss']:.4f}")
    print(f"  Coverage Loss:        {components['coverage_loss']:.4f}")
    print(f"  TOTAL LOSS:           {components['total_loss']:.4f}")

    print("\n" + "=" * 80)
    print("✓ All tests completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    test_pedagogical_loss()
