#!/usr/bin/env python3
"""
Expert Syllabus Retrieval System

Finds similar high-quality syllabi to show as reference examples.
This implements the RAG enhancement layer (Option 3).
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer


class ExpertSyllabusRetriever:
    """Retrieves similar expert syllabi based on semantic similarity."""

    def __init__(
        self, expert_syllabi_path: str = None, model_name: str = "all-mpnet-base-v2"
    ):
        """
        Initialize expert retrieval system.

        Args:
            expert_syllabi_path: Path to expert_syllabi.json (default: auto-detect)
            model_name: Sentence transformer model (default: all-mpnet-base-v2)
        """
        # Load expert syllabi
        if expert_syllabi_path is None:
            base_dir = Path(__file__).parent.parent.parent
            expert_syllabi_path = base_dir / "data" / "feedback" / "expert_syllabi.json"

        print(f"Loading expert syllabi from: {expert_syllabi_path}")
        with open(expert_syllabi_path) as f:
            data = json.load(f)
            self.expert_syllabi = data["expert_syllabi"]

        print(f"✓ Loaded {len(self.expert_syllabi)} expert syllabi")

        # Load semantic model (same as your semantic ranker)
        print(f"Loading sentence transformer: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("✓ Sentence transformer loaded")

        # Pre-compute embeddings for all experts
        self._compute_expert_embeddings()

    def _compute_expert_embeddings(self):
        """Pre-compute embeddings for all expert syllabi."""
        print("Computing embeddings for expert syllabi...")

        for expert in self.expert_syllabi:
            # Build text from requirements
            req = expert["requirements"]
            text = f"{req['title']} {req['description']} {req['domain']} {req['level']}"

            # Compute embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            expert["embedding"] = embedding

        print(f"✓ Computed embeddings for {len(self.expert_syllabi)} experts")

    def build_query_text(self, course_requirements: Dict) -> str:
        """
        Build query text from course requirements.

        Args:
            course_requirements: Dict with title, domain, level, description

        Returns:
            Combined query string
        """
        parts = []

        if "title" in course_requirements:
            parts.append(course_requirements["title"])

        if "description" in course_requirements:
            parts.append(course_requirements["description"])

        domain = course_requirements.get("domain", "")
        level = course_requirements.get("level", "")
        if domain or level:
            parts.append(f"{domain} {level}".strip())

        return " ".join(parts)

    def find_similar_experts(
        self, course_requirements: Dict, top_k: int = 3, min_similarity: float = 0.3
    ) -> List[Tuple[Dict, float]]:
        """
        Find expert syllabi similar to the given course requirements.

        Args:
            course_requirements: Dict with title, domain, level, description
            top_k: Number of similar experts to return
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            List of (expert_dict, similarity_score) tuples, sorted by similarity
        """
        # Build query embedding
        query_text = self.build_query_text(course_requirements)
        query_embedding = self.model.encode(query_text, convert_to_numpy=True)

        # Compute similarities
        similarities = []
        for expert in self.expert_syllabi:
            expert_embedding = expert["embedding"]

            # Cosine similarity
            similarity = np.dot(query_embedding, expert_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(expert_embedding)
            )

            if similarity >= min_similarity:
                similarities.append((expert, float(similarity)))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top K
        return similarities[:top_k]

    def format_expert_for_display(self, expert: Dict, similarity: float) -> Dict:
        """
        Format expert syllabus for UI display.

        Args:
            expert: Expert syllabus dict
            similarity: Similarity score (0-1)

        Returns:
            Formatted dict for display
        """
        req = expert["requirements"]
        metrics = expert["quality_metrics"]

        return {
            "title": req["title"],
            "domain": req["domain"],
            "level": req["level"],
            "similarity": f"{similarity:.1%}",
            "quality_score": f"{metrics['composite_quality']:.2f}/10",
            "prerequisite_accuracy": f"{metrics['prerequisite_accuracy']:.1%}",
            "semantic_match": f"{metrics['semantic_avg_score']:.3f}",
            "structure": f"{expert['structure']['num_modules']}M + {expert['structure']['num_activities']}A + {expert['structure']['num_assessments']}A",
        }

    def get_expert_recommendations(
        self, course_requirements: Dict, top_k: int = 2
    ) -> List[Dict]:
        """
        Get expert syllabus recommendations for display in UI.

        Args:
            course_requirements: User's course requirements
            top_k: Number of recommendations

        Returns:
            List of formatted expert recommendations
        """
        # Lower similarity threshold for UI display (0.15 = 15% similarity)
        # Users expect to see examples even if not perfectly similar
        similar_experts = self.find_similar_experts(
            course_requirements, top_k=top_k, min_similarity=0.15
        )

        if not similar_experts:
            return []

        recommendations = []
        for expert, similarity in similar_experts:
            formatted = self.format_expert_for_display(expert, similarity)
            recommendations.append(formatted)

        return recommendations


# Singleton instance for efficiency
_expert_retriever = None


def get_expert_retriever() -> ExpertSyllabusRetriever:
    """Get or create singleton expert retriever instance."""
    global _expert_retriever
    if _expert_retriever is None:
        _expert_retriever = ExpertSyllabusRetriever()
    return _expert_retriever


if __name__ == "__main__":
    # Test the expert retrieval system
    print("=" * 80)
    print("TESTING EXPERT RETRIEVAL SYSTEM")
    print("=" * 80)

    # Initialize retriever
    retriever = ExpertSyllabusRetriever()

    # Test case 1: Intro to Python
    print("\n" + "=" * 80)
    print("Test 1: Introduction to Python Programming")
    print("=" * 80)

    test_requirements_1 = {
        "title": "Introduction to Python Programming",
        "domain": "computer_science",
        "level": "beginner",
        "description": "Learn Python programming fundamentals, syntax, and basic data structures",
    }

    experts_1 = retriever.get_expert_recommendations(test_requirements_1, top_k=3)

    print(f"\nFound {len(experts_1)} similar expert syllabi:\n")
    for i, expert in enumerate(experts_1, 1):
        print(f"{i}. {expert['title']}")
        print(f"   Domain: {expert['domain']} | Level: {expert['level']}")
        print(f"   Similarity: {expert['similarity']}")
        print(f"   Quality: {expert['quality_score']}")
        print(f"   Structure: {expert['structure']}")
        print()

    # Test case 2: Machine Learning
    print("=" * 80)
    print("Test 2: Advanced Machine Learning")
    print("=" * 80)

    test_requirements_2 = {
        "title": "Advanced Machine Learning",
        "domain": "computer_science",
        "level": "advanced",
        "description": "Deep learning, neural networks, and advanced ML algorithms",
    }

    experts_2 = retriever.get_expert_recommendations(test_requirements_2, top_k=3)

    print(f"\nFound {len(experts_2)} similar expert syllabi:\n")
    for i, expert in enumerate(experts_2, 1):
        print(f"{i}. {expert['title']}")
        print(f"   Domain: {expert['domain']} | Level: {expert['level']}")
        print(f"   Similarity: {expert['similarity']}")
        print(f"   Quality: {expert['quality_score']}")
        print()

    print("=" * 80)
    print("✓ Expert retrieval system test complete!")
