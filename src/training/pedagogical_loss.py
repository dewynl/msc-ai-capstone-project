"""
Pedagogical loss calculations for educational content evaluation.

Implements difficulty progression analysis, topic diversity measurement,
and prerequisite coherence checking for generated syllabi.
"""

import json
import re
from pathlib import Path
from typing import Dict, List


class PedagogicalLoss:
    """
    Calculates pedagogical quality metrics for module sequences.

    Stub implementation for evaluation framework.
    """

    def __init__(self, modules_path: str = "data/components/modules.json"):
        """
        Initialize with module database.

        Args:
            modules_path: Path to modules.json
        """
        self.modules_path = modules_path
        self.modules = {}
        self.prerequisites = {}

        # Load modules if path exists
        if Path(modules_path).exists():
            with open(modules_path, "r") as f:
                modules_data = json.load(f)
                for module in modules_data:
                    module_id = module.get("id") or module.get("uuid")
                    if module_id:
                        self.modules[module_id] = module
                        self.prerequisites[module_id] = module.get("prerequisites", [])

    def evaluate_sequence_quality(self, module_sequence: List[str]) -> Dict[str, float]:
        """
        Evaluate pedagogical quality of a module sequence.

        Args:
            module_sequence: List of module UUIDs in order

        Returns:
            Dictionary with quality metrics:
            - prerequisite_accuracy: 0.0-1.0 (higher is better)
            - difficulty_loss: 0.0-1.0 (lower is better, represents violations)
            - coverage_loss: 0.0-1.0 (lower is better, represents repetition)
        """
        if not module_sequence:
            return {
                "prerequisite_accuracy": 0.0,
                "difficulty_loss": 1.0,
                "coverage_loss": 1.0,
            }

        # Calculate prerequisite accuracy
        prerequisite_accuracy = self._check_prerequisites(module_sequence)

        # Calculate difficulty progression (REAL implementation)
        difficulty_loss = self._calculate_difficulty_loss(module_sequence)

        # Calculate topic diversity (REAL implementation)
        coverage_loss = self._calculate_topic_diversity_loss(module_sequence)

        return {
            "prerequisite_accuracy": prerequisite_accuracy,
            "difficulty_loss": difficulty_loss,
            "coverage_loss": coverage_loss,
        }

    def _check_prerequisites(self, module_sequence: List[str]) -> float:
        """
        Check if prerequisites are satisfied in sequence.

        Args:
            module_sequence: Ordered list of module IDs

        Returns:
            Accuracy score (0.0 to 1.0)
        """
        if not module_sequence:
            return 0.0

        seen = set()
        violations = 0
        total_prereqs = 0

        for module_id in module_sequence:
            prereqs = self.prerequisites.get(module_id, [])

            for prereq in prereqs:
                total_prereqs += 1
                if prereq not in seen:
                    violations += 1

            seen.add(module_id)

        if total_prereqs == 0:
            return 1.0  # No prerequisites = perfect score

        return 1.0 - (violations / total_prereqs)

    def _calculate_difficulty_loss(self, module_sequence: List[str]) -> float:
        """
        Calculate difficulty progression loss (0.0 = perfect, 1.0 = worst).

        Checks if difficulty levels increase monotonically through the sequence.
        Violations occur when a module is harder than the following module.

        Difficulty ordering: beginner < intermediate < advanced < expert < postgraduate

        Args:
            module_sequence: Ordered list of module UUIDs

        Returns:
            Loss score: 0.0 (perfect progression) to 1.0 (maximum violations)
        """
        if len(module_sequence) < 2:
            return 0.0  # No transitions to evaluate

        # Define difficulty hierarchy
        difficulty_order = {
            "beginner": 1,
            "introductory": 1,
            "intro": 1,
            "intermediate": 2,
            "advanced": 3,
            "expert": 4,
            "postgraduate": 5,
            "graduate": 5,
        }

        # Extract difficulty levels
        difficulties = []
        for module_id in module_sequence:
            module = self.modules.get(module_id)
            if module:
                difficulty = module.get("difficulty", "intermediate").lower()
                difficulties.append(
                    difficulty_order.get(difficulty, 2)
                )  # Default to intermediate
            else:
                difficulties.append(2)  # Unknown = intermediate

        # Count violations (regressions in difficulty)
        violations = 0
        transitions = 0

        for i in range(len(difficulties) - 1):
            current_diff = difficulties[i]
            next_diff = difficulties[i + 1]
            transitions += 1

            # Violation if difficulty decreases
            if next_diff < current_diff:
                violations += 1

        if transitions == 0:
            return 0.0

        # Loss = proportion of transitions that are violations
        return violations / transitions

    def _calculate_topic_diversity_loss(self, module_sequence: List[str]) -> float:
        """
        Calculate topic diversity loss using concept uniqueness (0.0 = perfect, 1.0 = worst).

        Measures how diverse the key concepts are across modules using stem-based
        uniqueness. High diversity = many unique concept stems. Low diversity =
        repeated concepts.

        Args:
            module_sequence: Ordered list of module UUIDs

        Returns:
            Loss score: 0.0 (perfect diversity) to 1.0 (no diversity)
        """
        if not module_sequence:
            return 1.0

        # Extract all key concepts from modules
        all_concepts = []
        for module_id in module_sequence:
            module = self.modules.get(module_id)
            if module and "key_concepts" in module:
                concepts = module.get("key_concepts", [])
                all_concepts.extend(concepts)

        if not all_concepts:
            return 0.5  # No concepts = neutral score

        # Extract concept stems (main keywords, ignore descriptions)
        concept_stems = self._extract_concept_stems(all_concepts)

        # Calculate uniqueness ratio
        total_concepts = len(concept_stems)
        unique_concepts = len(set(concept_stems))

        if total_concepts == 0:
            return 0.5

        # Diversity score: ratio of unique to total
        diversity_score = unique_concepts / total_concepts

        # Loss = 1 - diversity (high diversity = low loss)
        return 1.0 - diversity_score

    def _extract_concept_stems(self, concepts: List[str]) -> List[str]:
        """
        Extract main keyword stems from concept descriptions.

        Key concepts often have format: "Term - Description".
        We extract the main term before the dash/hyphen and normalize it.

        Args:
            concepts: List of concept strings

        Returns:
            List of normalized concept stems
        """
        stems = []
        for concept in concepts:
            # Split on dash/hyphen and take first part
            if " - " in concept:
                stem = concept.split(" - ")[0]
            elif " – " in concept:  # em-dash
                stem = concept.split(" – ")[0]
            else:
                # Take first few words if no dash
                words = concept.split()[:3]  # First 3 words
                stem = " ".join(words)

            # Normalize: lowercase, remove punctuation
            stem = re.sub(r"[^\w\s]", "", stem.lower().strip())

            if stem:
                stems.append(stem)

        return stems
