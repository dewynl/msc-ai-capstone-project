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

            # Debug: Show snippet of generated output (first 800 chars)
            print(f"  Generated {len(syllabus)} chars, preview:\n{syllabus[:800]}\n...")

            # Extract module sequence from generated syllabus
            module_sequence = self._extract_module_sequence(
                syllabus, available_module_ids
            )

            # Extract activities and assessments (for completeness scoring)
            activity_sequence = self._extract_component_indices(
                syllabus, "## Selected Activities"
            )
            assessment_sequence = self._extract_component_indices(
                syllabus, "## Selected Assessments"
            )

            # Debug: Check if sections exist in output
            has_activities_section = "## Selected Activities" in syllabus
            has_assessments_section = "## Selected Assessments" in syllabus
            if not has_activities_section:
                print("    ⚠️ No '## Selected Activities' section found in output")
            if not has_assessments_section:
                print("    ⚠️ No '## Selected Assessments' section found in output")

            # Evaluate pedagogical quality
            if len(module_sequence) > 0:
                metrics = self.pedagogical_loss.evaluate_sequence_quality(
                    module_sequence
                )

                # Add component counts for completeness scoring
                metrics["module_count"] = len(module_sequence)
                metrics["activity_count"] = len(activity_sequence)
                metrics["assessment_count"] = len(assessment_sequence)

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
                    f"Diff: {1-metrics['difficulty_loss']:.2f}, "
                    f"Modules: {metrics['module_count']}, "
                    f"Activities: {metrics['activity_count']}, "
                    f"Assessments: {metrics['assessment_count']})"
                )
            else:
                print(f"  Candidate {i+1}: Failed to parse module sequence")
                print(f"    Generated text (last 500 chars): ...{syllabus[-500:]}")

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

        # Generate with SIMPLE parameters (match successful test)
        # IMPORTANT: repetition_penalty and no_repeat_ngram_size break generation!
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            num_beams=1,
            do_sample=(temperature > 0),  # First candidate greedy, others sampled
            temperature=temperature if temperature > 0 else None,
            top_p=0.9 if temperature > 0 else None,
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

    def _extract_component_indices(
        self, syllabus_text: str, section_header: str
    ) -> List[int]:
        """
        Extract component indices from sections like '## Selected Activities'.
        Deduplicates indices to match parser behavior.

        Args:
            syllabus_text: Generated syllabus markdown
            section_header: Section header to look for (e.g., "## Selected Activities")

        Returns:
            List of unique indices (deduplicated, order preserved)
        """
        # Find section
        section_pattern = rf"{re.escape(section_header)}\s*\n(.*?)(?=\n##|\Z)"
        section_match = re.search(section_pattern, syllabus_text, re.DOTALL)

        if not section_match:
            return []

        section_text = section_match.group(1)

        # Extract all [digit] patterns
        indices_str = re.findall(r"\[(\d+)\]", section_text)

        # Convert to integers and deduplicate (preserve order)
        seen = set()
        indices = []
        for idx_str in indices_str:
            idx = int(idx_str)
            if idx not in seen:
                seen.add(idx)
                indices.append(idx)

        return indices

    def _calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """
        Calculate overall quality score from pedagogical metrics.

        Combines:
        - Prerequisite accuracy (40% weight)
        - Difficulty progression (25% weight)
        - Topic diversity (15% weight)
        - Completeness (20% weight) - penalizes missing activities/assessments

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

        # Completeness check: Prefer syllabi with multiple modules, activities, AND assessments
        module_count = metrics.get("module_count", 0)
        activity_count = metrics.get("activity_count", 0)
        assessment_count = metrics.get("assessment_count", 0)

        # Base completeness: do we have all three types?
        has_all_types = module_count > 0 and activity_count > 0 and assessment_count > 0

        if has_all_types:
            # Reward more modules (training avg is 3.5, min 2, max 5)
            # Linear scale: 1→0.3, 2→0.5, 3→0.7, 4→0.85, 5→1.0
            module_score = min(1.0, (module_count - 1) / 4 * 0.7 + 0.3)

            # Reward reasonable activity count (training avg 3.1, range 2-4)
            # Linear scale: 1→0.5, 2→0.67, 3→0.83, 4→1.0
            activity_score = min(1.0, activity_count / 4 + 0.25)

            # Reward reasonable assessment count (training avg 2.0, range 1-3)
            # Linear scale: 1→0.6, 2→0.8, 3→1.0
            assessment_score = min(1.0, assessment_count / 3 + 0.33)

            # Weighted combination (modules most important)
            completeness_score = (
                0.5 * module_score + 0.3 * activity_score + 0.2 * assessment_score
            )
        elif module_count > 0 and (activity_count > 0 or assessment_count > 0):
            completeness_score = 0.6  # Partial: modules + one other
        elif module_count > 0:
            completeness_score = 0.3  # Minimal: modules only
        else:
            completeness_score = 0.0  # No modules at all

        # Weighted combination (adjusted to include completeness)
        quality_score = (
            0.4 * prereq_score
            + 0.25 * diff_score
            + 0.15 * coverage_score
            + 0.20 * completeness_score
        )

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
