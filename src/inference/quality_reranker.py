"""
Quality-Based Reranking for Syllabus Generation

Generates multiple syllabus candidates and selects the best one using
pedagogical quality metrics (prerequisite coherence, difficulty progression, diversity).
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add src to path for pedagogical_loss import
sys.path.append(str(Path(__file__).parent.parent / "training"))
from pedagogical_loss import PedagogicalLoss


class SyllabusQualityReranker:
    """
    Generate multiple syllabus candidates and rank by pedagogical quality.

    Uses pedagogical loss metrics to select the best syllabus from N candidates.
    """

    def __init__(self, modules_path: str = "data/components/modules.json"):
        """
        Initialize quality reranker.

        Args:
            modules_path: Path to modules.json with prerequisite data
        """
        self.pedagogical_loss = PedagogicalLoss(modules_path)
        self.quality_threshold = 0.7  # Minimum acceptable quality score (0-1)

    def generate_with_quality_selection(
        self,
        model,
        tokenizer,
        input_text: str,
        available_module_ids: List[str],
        num_candidates: int = 3,
        temperature: float = 0.8,
        max_length: int = 1024,
    ) -> Tuple[str, Dict[str, float], bool]:
        """
        Generate multiple syllabus candidates and return the best one.

        Args:
            model: Trained T5/CodeT5 model
            tokenizer: Model tokenizer
            input_text: Input prompt for generation
            available_module_ids: List of module UUIDs available for this course
            num_candidates: Number of candidates to generate
            temperature: Sampling temperature for diversity
            max_length: Max generation length

        Returns:
            best_syllabus: The best syllabus text
            quality_metrics: Dict with quality scores
            is_acceptable: Whether quality meets threshold
        """
        candidates = []

        print(f"\n🎲 Generating {num_candidates} syllabus candidates...")

        for i in range(num_candidates):
            # Generate candidate with sampling for diversity
            syllabus = self._generate_single(
                model,
                tokenizer,
                input_text,
                temperature=temperature if i > 0 else 0.0,  # First one greedy
                max_length=max_length,
            )

            # Extract module sequence from generated syllabus
            module_sequence = self._extract_module_sequence(
                syllabus, available_module_ids
            )

            # Evaluate pedagogical quality
            if len(module_sequence) > 0:
                metrics = self.pedagogical_loss.evaluate_sequence_quality(
                    module_sequence
                )

                # Calculate overall quality score (0-1, higher is better)
                quality_score = self._calculate_quality_score(metrics)

                candidates.append(
                    {
                        "syllabus": syllabus,
                        "module_sequence": module_sequence,
                        "metrics": metrics,
                        "quality_score": quality_score,
                    }
                )

                print(
                    f"  Candidate {i+1}: Quality={quality_score:.2f} "
                    f"(Prereq: {metrics['prerequisite_accuracy']:.0%}, "
                    f"Diff: {1-metrics['difficulty_loss']:.2f})"
                )
            else:
                print(f"  Candidate {i+1}: Failed to parse module sequence")

        # Handle case where no valid candidates were generated
        if not candidates:
            return (
                "ERROR: Failed to generate valid syllabus",
                {"quality_score": 0.0},
                False,
            )

        # Select best candidate
        best = max(candidates, key=lambda x: x["quality_score"])
        is_acceptable = best["quality_score"] >= self.quality_threshold

        print(f"\n✓ Selected candidate with quality score: {best['quality_score']:.2f}")
        print(f"  Acceptable: {'YES ✓' if is_acceptable else 'NO ⚠️'}")

        return best["syllabus"], best["metrics"], is_acceptable

    def _generate_single(
        self,
        model,
        tokenizer,
        input_text: str,
        temperature: float = 0.8,
        max_length: int = 1024,
    ) -> str:
        """Generate a single syllabus candidate."""
        inputs = tokenizer(
            input_text, return_tensors="pt", max_length=512, truncation=True
        )

        # Generate
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            do_sample=(temperature > 0),
            temperature=temperature if temperature > 0 else None,
            top_p=0.9 if temperature > 0 else None,
            num_beams=1,
        )

        # Decode
        syllabus = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return syllabus

    def _extract_module_sequence(
        self, syllabus_text: str, available_module_ids: List[str]
    ) -> List[str]:
        """
        Extract module UUIDs from generated syllabus.

        The syllabus uses indices [0], [1], [2] which refer to modules
        from the available_module_ids list.

        Args:
            syllabus_text: Generated syllabus markdown
            available_module_ids: List of module UUIDs in order they appeared in input

        Returns:
            List of module UUIDs in the order they appear in syllabus
        """
        # Extract indices from format: "### Weeks 1-2: Title\n[0] Description..."
        pattern = r"###\s+Weeks[^\n]+\n\[(\d+)\]"
        matches = re.findall(pattern, syllabus_text)

        module_sequence = []
        for idx_str in matches:
            idx = int(idx_str)
            if 0 <= idx < len(available_module_ids):
                module_sequence.append(available_module_ids[idx])

        return module_sequence

    def _calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """
        Calculate overall quality score from pedagogical metrics.

        Combines:
        - Prerequisite accuracy (50% weight)
        - Difficulty progression (30% weight)
        - Topic diversity (20% weight)

        Returns: Score from 0.0 (worst) to 1.0 (perfect)
        """
        # Prerequisite accuracy (already 0-1, higher is better)
        prereq_score = metrics["prerequisite_accuracy"]

        # Difficulty progression (loss, so invert: 1-loss)
        # Difficulty loss typically 0-1, where 0 is perfect
        diff_score = max(0, 1 - metrics["difficulty_loss"])

        # Coverage/diversity (loss, so invert: 1-loss)
        # Coverage loss typically 0-1, where 0 is perfect
        coverage_score = max(0, 1 - metrics["coverage_loss"])

        # Weighted combination
        quality_score = 0.5 * prereq_score + 0.3 * diff_score + 0.2 * coverage_score

        return quality_score

    def get_quality_message(
        self, metrics: Dict[str, float], is_acceptable: bool
    ) -> str:
        """
        Generate user-friendly quality message.

        Args:
            metrics: Pedagogical quality metrics
            is_acceptable: Whether quality meets threshold

        Returns:
            Human-readable quality message
        """
        if is_acceptable:
            return (
                "✅ **High Quality Syllabus**\n\n"
                f"- Prerequisite Coherence: {metrics['prerequisite_accuracy']:.0%}\n"
                f"- Difficulty Progression: {(1-metrics['difficulty_loss'])*100:.0f}%\n"
                f"- Topic Diversity: {(1-metrics['coverage_loss'])*100:.0f}%"
            )
        else:
            issues = []
            if metrics["prerequisite_accuracy"] < 0.8:
                issues.append("⚠️ Some modules may appear before their prerequisites")
            if metrics["difficulty_loss"] > 0.3:
                issues.append("⚠️ Difficulty progression could be smoother")
            if metrics["coverage_loss"] > 0.5:
                issues.append("⚠️ Topic coverage may be repetitive")

            issues_text = (
                "\n".join(issues) if issues else "⚠️ Overall quality below threshold"
            )

            return (
                "⚠️ **Quality Warning**\n\n"
                f"{issues_text}\n\n"
                f"**Metrics:**\n"
                f"- Prerequisite Coherence: {metrics['prerequisite_accuracy']:.0%}\n"
                f"- Difficulty Progression: {(1-metrics['difficulty_loss'])*100:.0f}%\n"
                f"- Topic Diversity: {(1-metrics['coverage_loss'])*100:.0f}%\n\n"
                f"*Note: This is the best syllabus from {3} generated candidates.*"
            )
