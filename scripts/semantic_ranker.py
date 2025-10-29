#!/usr/bin/env python3
"""
Semantic Ranking for RAG Components

Uses sentence embeddings (BERT-based) to rank educational components
by semantic similarity to course requirements.

This is the second ML component in the hybrid architecture:
1. RAG Filter (rule-based) → filters by domain + difficulty
2. Semantic Ranker (ML-based) → ranks by relevance  ← THIS MODULE
3. CodeT5 Generator (ML-based) → generates structured markdown
4. Bloom's Enhancer (rule-based) → enhances objectives
5. Template Expander (hybrid) → expands to rich markdown

Purpose:
- Fixes the model selection problem (was always picking [0], [1], [2], [3])
- Ensures model sees most relevant components first
- Maintains ML approach (embeddings for semantic understanding)
"""

from typing import Dict, List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer


class SemanticRanker:
    """Ranks educational components by semantic similarity to course requirements."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize semantic ranker with pre-trained sentence transformer.

        Args:
            model_name: HuggingFace model name (default: all-MiniLM-L6-v2)
                       - Fast and lightweight (22M parameters)
                       - Good for semantic similarity
                       - 384-dimensional embeddings
        """
        print(f"Loading sentence transformer: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("✓ Sentence transformer loaded")

    def build_course_query(self, course_requirements: Dict) -> str:
        """
        Build semantic query from course requirements.

        Combines title, domain, level, and description into single text
        for embedding comparison.

        Args:
            course_requirements: Dict with title, domain, level, description, etc.

        Returns:
            Combined query string for semantic matching
        """
        parts = []

        # Title (most important)
        if "title" in course_requirements:
            parts.append(course_requirements["title"])

        # Description (very important for context)
        if "description" in course_requirements:
            parts.append(course_requirements["description"])

        # Domain and level (important for scope)
        domain = course_requirements.get("domain", "")
        level = course_requirements.get("level", "")
        if domain or level:
            scope = f"{domain} {level}".strip()
            parts.append(scope)

        # Duration (less important but provides context)
        duration = course_requirements.get("duration", "")
        if duration:
            parts.append(f"{duration} course")

        query = " ".join(parts)
        return query

    def build_component_text(self, component: Dict, component_type: str) -> str:
        """
        Build text representation of component for embedding.

        Args:
            component: Component dict with title, description, key_concepts, etc.
            component_type: 'modules', 'activities', or 'assessments'

        Returns:
            Combined text for semantic matching
        """
        parts = []

        # Title (most important)
        title = component.get("title", "")
        if title:
            parts.append(title)

        # Description (very important)
        description = component.get("description", "")
        if description:
            parts.append(description)

        # Key concepts (important for modules)
        key_concepts = component.get("key_concepts", [])
        if key_concepts:
            concepts_text = ", ".join(key_concepts)
            parts.append(f"Covers: {concepts_text}")

        # Learning outcomes (important for modules)
        learning_outcomes = component.get("learning_outcomes", [])
        if learning_outcomes:
            outcomes_text = "; ".join(learning_outcomes)
            parts.append(f"Outcomes: {outcomes_text}")

        # Prerequisites (context)
        prerequisites = component.get("prerequisites", [])
        if prerequisites:
            prereq_text = ", ".join(prerequisites)
            parts.append(f"Prerequisites: {prereq_text}")

        # Activity type or assessment type (context)
        if component_type == "activities":
            activity_type = component.get("activity_type", "")
            if activity_type:
                parts.append(f"Activity type: {activity_type}")
        elif component_type == "assessments":
            assessment_type = component.get("assessment_type", "")
            if assessment_type:
                parts.append(f"Assessment type: {assessment_type}")

        text = " ".join(parts)
        return text

    def rank_components(
        self,
        components: List[Dict],
        course_requirements: Dict,
        component_type: str,
        top_k: int = None,
    ) -> List[Tuple[Dict, float]]:
        """
        Rank components by semantic similarity to course requirements.

        Args:
            components: List of component dicts (already filtered by domain + difficulty)
            course_requirements: Course requirements dict
            component_type: 'modules', 'activities', or 'assessments'
            top_k: If specified, return only top K components (None = return all ranked)

        Returns:
            List of (component, score) tuples, sorted by score (descending)
        """
        if not components:
            return []

        # Build query embedding
        query_text = self.build_course_query(course_requirements)
        query_embedding = self.model.encode(query_text, convert_to_numpy=True)

        # Build component embeddings
        component_texts = [
            self.build_component_text(comp, component_type) for comp in components
        ]
        component_embeddings = self.model.encode(component_texts, convert_to_numpy=True)

        # Compute cosine similarity scores
        # Formula: similarity = (A · B) / (||A|| × ||B||)
        query_norm = np.linalg.norm(query_embedding)
        component_norms = np.linalg.norm(component_embeddings, axis=1)

        # Dot products
        similarities = np.dot(component_embeddings, query_embedding)

        # Normalize
        similarities = similarities / (query_norm * component_norms)

        # Create (component, score) tuples
        ranked = [(comp, float(score)) for comp, score in zip(components, similarities)]

        # Sort by score (descending)
        ranked.sort(key=lambda x: x[1], reverse=True)

        # Return top K if specified
        if top_k is not None:
            ranked = ranked[:top_k]

        return ranked

    def rank_all_components(
        self,
        modules: List[Dict],
        activities: List[Dict],
        assessments: List[Dict],
        course_requirements: Dict,
        top_k_modules: int = 20,
        top_k_activities: int = 15,
        top_k_assessments: int = 5,
    ) -> Dict[str, List[Dict]]:
        """
        Rank all component types and return top K for each.

        This is the main entry point for integration with the generation pipeline.

        Args:
            modules: Filtered modules (by domain + difficulty)
            activities: Filtered activities (by domain + difficulty)
            assessments: Filtered assessments (by domain + difficulty)
            course_requirements: Course requirements dict
            top_k_modules: Number of top modules to return (default: 20)
            top_k_activities: Number of top activities to return (default: 15)
            top_k_assessments: Number of top assessments to return (default: 5)

        Returns:
            Dict with:
                - modules: List of top K modules (ordered by relevance)
                - activities: List of top K activities (ordered by relevance)
                - assessments: List of top K assessments (ordered by relevance)
                - ranking_stats: Statistics about ranking process
        """
        print("Ranking components by semantic similarity...")

        # Rank modules
        ranked_modules = self.rank_components(
            modules, course_requirements, "modules", top_k=top_k_modules
        )

        # Rank activities
        ranked_activities = self.rank_components(
            activities, course_requirements, "activities", top_k=top_k_activities
        )

        # Rank assessments
        ranked_assessments = self.rank_components(
            assessments, course_requirements, "assessments", top_k=top_k_assessments
        )

        # Extract components (drop scores)
        top_modules = [comp for comp, score in ranked_modules]
        top_activities = [comp for comp, score in ranked_activities]
        top_assessments = [comp for comp, score in ranked_assessments]

        # Compute statistics
        ranking_stats = {
            "modules": {
                "input_count": len(modules),
                "output_count": len(top_modules),
                "avg_score": (
                    np.mean([score for _, score in ranked_modules])
                    if ranked_modules
                    else 0
                ),
                "min_score": (
                    min(score for _, score in ranked_modules) if ranked_modules else 0
                ),
                "max_score": (
                    max(score for _, score in ranked_modules) if ranked_modules else 0
                ),
            },
            "activities": {
                "input_count": len(activities),
                "output_count": len(top_activities),
                "avg_score": (
                    np.mean([score for _, score in ranked_activities])
                    if ranked_activities
                    else 0
                ),
                "min_score": (
                    min(score for _, score in ranked_activities)
                    if ranked_activities
                    else 0
                ),
                "max_score": (
                    max(score for _, score in ranked_activities)
                    if ranked_activities
                    else 0
                ),
            },
            "assessments": {
                "input_count": len(assessments),
                "output_count": len(top_assessments),
                "avg_score": (
                    np.mean([score for _, score in ranked_assessments])
                    if ranked_assessments
                    else 0
                ),
                "min_score": (
                    min(score for _, score in ranked_assessments)
                    if ranked_assessments
                    else 0
                ),
                "max_score": (
                    max(score for _, score in ranked_assessments)
                    if ranked_assessments
                    else 0
                ),
            },
        }

        print(f"   Modules: {len(modules)} → {len(top_modules)} (top K)")
        print(f"   Activities: {len(activities)} → {len(top_activities)} (top K)")
        print(f"   Assessments: {len(assessments)} → {len(top_assessments)} (top K)")

        return {
            "modules": top_modules,
            "activities": top_activities,
            "assessments": top_assessments,
            "ranking_stats": ranking_stats,
        }


if __name__ == "__main__":
    # Test the semantic ranker
    print("Testing Semantic Ranker...")
    print("=" * 80)

    # Create test data
    test_course = {
        "title": "Introduction to Machine Learning",
        "description": "Learn fundamental machine learning algorithms and applications",
        "domain": "computer_science",
        "level": "intermediate",
        "duration": "semester",
    }

    test_modules = [
        {
            "id": "mod-1",
            "title": "Neural Networks Basics",
            "description": "Introduction to artificial neural networks",
            "key_concepts": ["neurons", "backpropagation", "activation functions"],
            "difficulty": "intermediate",
            "domain": "computer_science",
        },
        {
            "id": "mod-2",
            "title": "Python Data Structures",
            "description": "Lists, dicts, and sets in Python",
            "key_concepts": ["lists", "dictionaries", "algorithms"],
            "difficulty": "beginner",
            "domain": "computer_science",
        },
        {
            "id": "mod-3",
            "title": "Deep Learning with TensorFlow",
            "description": "Building deep neural networks with TensorFlow",
            "key_concepts": ["tensorflow", "CNNs", "RNNs"],
            "difficulty": "intermediate",
            "domain": "computer_science",
        },
        {
            "id": "mod-4",
            "title": "Linear Algebra Fundamentals",
            "description": "Vectors, matrices, and linear transformations",
            "key_concepts": ["vectors", "matrices", "eigenvalues"],
            "difficulty": "intermediate",
            "domain": "computer_science",
        },
    ]

    # Initialize ranker
    ranker = SemanticRanker()

    # Rank modules
    print("\nRanking modules...")
    ranked = ranker.rank_components(test_modules, test_course, "modules")

    print("\nRanked Results (by relevance):")
    for i, (module, score) in enumerate(ranked, 1):
        print(f"{i}. {module['title']}: {score:.4f}")

    # Test full ranking
    print("\n" + "=" * 80)
    print("Testing full ranking with top K selection...")

    result = ranker.rank_all_components(
        modules=test_modules,
        activities=[],
        assessments=[],
        course_requirements=test_course,
        top_k_modules=2,
    )

    print("\nTop 2 modules selected:")
    for module in result["modules"]:
        print(f"  - {module['title']}")

    print("\nRanking stats:")
    print(f"  Input: {result['ranking_stats']['modules']['input_count']} modules")
    print(f"  Output: {result['ranking_stats']['modules']['output_count']} modules")
    print(f"  Avg score: {result['ranking_stats']['modules']['avg_score']:.4f}")

    print("\n✓ Semantic ranker test complete!")
