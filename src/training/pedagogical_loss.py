"""
Pedagogical Loss Function for Curriculum Design

This module implements a custom loss function that encodes curriculum design
principles into the T5 model training process. This is the core ML contribution
of the MSc AI project.

Components:
1. L_prereq: Prerequisite coherence loss - penalizes when modules appear before prerequisites
2. L_diff: Difficulty progression loss - penalizes non-smooth difficulty curves
3. L_coverage: Topic diversity loss - rewards diverse topic coverage across the syllabus

Author: MSc AI Capstone Project
"""

import json
from collections import defaultdict
from typing import Dict, List, Tuple

import torch
import torch.nn as nn


class PedagogicalLoss(nn.Module):
    """
    Custom pedagogical loss function for curriculum design.

    Combines standard generation loss with curriculum design principles:
    - Prerequisite coherence
    - Smooth difficulty progression
    - Topic diversity
    """

    def __init__(
        self,
        modules_path: str,
        lambda_prereq: float = 1.0,
        lambda_diff: float = 0.5,
        lambda_coverage: float = 0.3,
    ):
        """
        Initialize pedagogical loss function.

        Args:
            modules_path: Path to modules.json with prerequisite data
            lambda_prereq: Weight for prerequisite coherence loss
            lambda_diff: Weight for difficulty progression loss
            lambda_coverage: Weight for topic diversity loss
        """
        super().__init__()

        self.lambda_prereq = lambda_prereq
        self.lambda_diff = lambda_diff
        self.lambda_coverage = lambda_coverage

        # Load module data with prerequisites
        with open(modules_path) as f:
            self.modules = json.load(f)

        # Build prerequisite graph: module_id -> [prerequisite_ids]
        self.prereq_graph = {m["id"]: m.get("prerequisites", []) for m in self.modules}

        # Build reverse index: module_id -> module_data
        self.module_index = {m["id"]: m for m in self.modules}

        # Difficulty encoding: beginner=0, intermediate=1, advanced=2
        self.difficulty_map = {"beginner": 0, "intermediate": 1, "advanced": 2}

    def forward(
        self,
        generation_loss: torch.Tensor,
        predicted_sequence: List[str],
        input_context: Dict,
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """
        Compute total pedagogical loss.

        Args:
            generation_loss: Standard T5 generation loss (cross-entropy)
            predicted_sequence: List of module IDs in predicted sequence
            input_context: Dict with course information (level, domain, etc.)

        Returns:
            total_loss: Combined loss with pedagogical components
            loss_components: Dict with individual loss values for logging
        """
        # Compute pedagogical loss components
        prereq_loss = self._prerequisite_coherence_loss(predicted_sequence)
        diff_loss = self._difficulty_progression_loss(predicted_sequence)
        coverage_loss = self._topic_diversity_loss(predicted_sequence, input_context)

        # Combined loss
        total_loss = (
            generation_loss
            + self.lambda_prereq * prereq_loss
            + self.lambda_diff * diff_loss
            + self.lambda_coverage * coverage_loss
        )

        # Return loss components for logging
        loss_components = {
            "generation_loss": generation_loss.item(),
            "prereq_loss": prereq_loss.item(),
            "difficulty_loss": diff_loss.item(),
            "coverage_loss": coverage_loss.item(),
            "total_loss": total_loss.item(),
        }

        return total_loss, loss_components

    def _prerequisite_coherence_loss(self, sequence: List[str]) -> torch.Tensor:
        """
        L_prereq: Penalize when modules appear before their prerequisites.

        For each module in sequence, check if its prerequisites appear earlier.
        Higher loss when prerequisites appear AFTER the module that requires them.

        Args:
            sequence: List of module IDs in predicted order

        Returns:
            prereq_loss: Tensor with prerequisite coherence penalty
        """
        violations = 0
        total_checks = 0

        # Build position index for fast lookup
        position = {mod_id: idx for idx, mod_id in enumerate(sequence)}

        for idx, module_id in enumerate(sequence):
            if module_id not in self.prereq_graph:
                continue

            prerequisites = self.prereq_graph[module_id]

            for prereq_id in prerequisites:
                if prereq_id not in position:
                    # Prerequisite not in sequence - minor penalty
                    violations += 0.5
                    total_checks += 1
                elif position[prereq_id] > idx:
                    # Prerequisite appears AFTER module - major penalty
                    # Weight by distance (further apart = worse)
                    distance = position[prereq_id] - idx
                    violations += 1.0 + (distance / len(sequence))
                    total_checks += 1
                else:
                    # Prerequisite correctly appears before module
                    total_checks += 1

        # Normalize by number of checks
        if total_checks == 0:
            return torch.tensor(0.0)

        violation_rate = violations / total_checks
        return torch.tensor(violation_rate, dtype=torch.float32)

    def _difficulty_progression_loss(self, sequence: List[str]) -> torch.Tensor:
        """
        L_diff: Penalize non-smooth difficulty progression.

        Ideal progression: beginner → intermediate → advanced
        Penalize large jumps (e.g., beginner → advanced without intermediate)

        Args:
            sequence: List of module IDs in predicted order

        Returns:
            diff_loss: Tensor with difficulty progression penalty
        """
        if len(sequence) < 2:
            return torch.tensor(0.0)

        difficulties = []
        for module_id in sequence:
            if module_id in self.module_index:
                diff_level = self.module_index[module_id].get(
                    "difficulty", "intermediate"
                )
                difficulties.append(self.difficulty_map.get(diff_level, 1))

        if len(difficulties) < 2:
            return torch.tensor(0.0)

        # Calculate difficulty jumps
        total_penalty = 0.0
        for i in range(len(difficulties) - 1):
            jump = difficulties[i + 1] - difficulties[i]

            if jump > 1:
                # Large upward jump (e.g., beginner → advanced)
                total_penalty += (jump - 1) * 1.0
            elif jump < -1:
                # Large downward jump (e.g., advanced → beginner)
                # Less penalty than upward, but still not ideal
                total_penalty += abs(jump + 1) * 0.5

        # Normalize by sequence length
        normalized_penalty = total_penalty / len(difficulties)
        return torch.tensor(normalized_penalty, dtype=torch.float32)

    def _topic_diversity_loss(
        self, sequence: List[str], input_context: Dict
    ) -> torch.Tensor:
        """
        L_coverage: Reward diverse topic coverage, penalize repetition.

        Uses key_concepts from modules to measure topic diversity.
        Higher loss when same concepts appear repeatedly without variety.

        Args:
            sequence: List of module IDs in predicted order
            input_context: Dict with course information

        Returns:
            coverage_loss: Tensor with topic diversity penalty
        """
        if len(sequence) == 0:
            return torch.tensor(0.0)

        # Collect all key concepts from sequence
        concept_counts = defaultdict(int)
        total_concepts = 0

        for module_id in sequence:
            if module_id in self.module_index:
                concepts = self.module_index[module_id].get("key_concepts", [])
                for concept in concepts:
                    concept_counts[concept] += 1
                    total_concepts += 1

        if total_concepts == 0:
            return torch.tensor(0.0)

        # Calculate diversity using normalized entropy
        # High entropy = good diversity, low entropy = repetitive
        unique_concepts = len(concept_counts)

        if unique_concepts <= 1:
            # Very low diversity - high penalty
            return torch.tensor(1.0)

        # Calculate Shannon entropy
        entropy = 0.0
        for count in concept_counts.values():
            prob = count / total_concepts
            if prob > 0:
                entropy -= prob * torch.log(torch.tensor(prob))

        # Normalize by max possible entropy (uniform distribution)
        max_entropy = torch.log(torch.tensor(float(unique_concepts)))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

        # Convert to loss (1 - normalized_entropy)
        # High entropy → low loss, low entropy → high loss
        diversity_loss = 1.0 - normalized_entropy

        return torch.tensor(diversity_loss, dtype=torch.float32)

    def evaluate_sequence_quality(self, sequence: List[str]) -> Dict[str, float]:
        """
        Evaluate pedagogical quality of a sequence without computing gradients.

        Useful for evaluation and validation.

        Args:
            sequence: List of module IDs in predicted order

        Returns:
            metrics: Dict with pedagogical quality metrics
        """
        with torch.no_grad():
            prereq_loss = self._prerequisite_coherence_loss(sequence)
            diff_loss = self._difficulty_progression_loss(sequence)
            coverage_loss = self._topic_diversity_loss(sequence, {})

            # Calculate prerequisite coverage
            prereq_violations = 0
            prereq_correct = 0
            position = {mod_id: idx for idx, mod_id in enumerate(sequence)}

            for idx, module_id in enumerate(sequence):
                if module_id not in self.prereq_graph:
                    continue
                prerequisites = self.prereq_graph[module_id]
                for prereq_id in prerequisites:
                    if prereq_id in position:
                        if position[prereq_id] > idx:
                            prereq_violations += 1
                        else:
                            prereq_correct += 1

            total_prereqs = prereq_violations + prereq_correct
            prereq_accuracy = (
                prereq_correct / total_prereqs if total_prereqs > 0 else 1.0
            )

            return {
                "prerequisite_loss": prereq_loss.item(),
                "difficulty_loss": diff_loss.item(),
                "coverage_loss": coverage_loss.item(),
                "prerequisite_accuracy": prereq_accuracy,
                "prerequisite_violations": prereq_violations,
                "prerequisite_correct": prereq_correct,
            }
