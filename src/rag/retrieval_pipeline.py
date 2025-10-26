from typing import Any, Dict, List

from .query_processor import (
    enhance_query_with_context,
    generate_component_queries,
    validate_domain,
)
from .vector_store import SyllabusComponentStore


class ComponentRetrievalPipeline:
    """Retrieve relevant syllabus components based on course requirements with STEM focus"""

    def __init__(self, component_store: SyllabusComponentStore):
        self.component_store = component_store

    def retrieve_components(
        self, requirements: dict[str, Any], k_per_type: int = 5
    ) -> dict[str, list]:
        """Retrieve relevant syllabus components with enhanced STEM-focused queries"""
        queries = generate_component_queries(requirements)
        retrieved = {}

        domain = requirements.get("domain", "")
        if domain and not validate_domain(domain):
            print(f"Warning: Domain '{domain}' is not in our focus areas")

        for component_type, query in queries.items():
            enhanced_query = enhance_query_with_context(query, requirements)

            # Search vector store with plural component type (how they're stored)
            results = self.component_store.search(
                enhanced_query, k=k_per_type * 2, component_type=component_type
            )
            retrieved[component_type] = [result[0] for result in results]

        # Apply domain and level filtering
        filtered = self.filter_by_domain_and_level(retrieved, requirements)

        # Limit to requested number after filtering
        for comp_type in filtered:
            filtered[comp_type] = filtered[comp_type][:k_per_type]

        return filtered

    def filter_by_domain_and_level(
        self, components: dict[str, list], requirements: dict[str, Any]
    ) -> dict[str, list]:
        """Apply enhanced domain and difficulty level filters with STEM focus"""
        filtered = {}
        target_domain = requirements.get("domain", "").lower()
        target_level = requirements.get("level", "").lower()

        for comp_type, comp_list in components.items():
            filtered[comp_type] = []
            for comp in comp_list:
                comp_domain = comp.get("domain", "").lower()
                comp_difficulty = comp.get("difficulty", "").lower()

                domain_match = (
                    not target_domain
                    or target_domain == comp_domain
                    or self._is_related_domain(target_domain, comp_domain)
                )

                level_match = (
                    not target_level
                    or target_level == comp_difficulty
                    or self._is_compatible_level(target_level, comp_difficulty)
                )

                if domain_match and level_match:
                    filtered[comp_type].append(comp)

        return filtered

    def _is_related_domain(self, target: str, component: str) -> bool:
        """Check if domains are related"""
        domain_relationships = {
            "computer_science": ["mathematics"],
            "mathematics": ["computer_science", "physics"],
            "physics": ["mathematics"],
        }

        return component in domain_relationships.get(target, [])

    def _is_compatible_level(self, target: str, component: str) -> bool:
        """Check if difficulty levels are compatible"""
        level_hierarchy = {
            "beginner": ["beginner", "intermediate"],
            "intermediate": ["beginner", "intermediate", "advanced"],
            "advanced": ["intermediate", "advanced"],
        }

        return component in level_hierarchy.get(target, [target])

    def get_diverse_components(
        self, requirements: dict[str, Any], target_counts: Dict[str, int] = None
    ) -> Dict[str, List]:
        """Retrieve diverse components across STEM domains with specified counts"""
        if target_counts is None:
            target_counts = {"modules": 3, "activities": 5, "assessments": 3}

        all_components = self.retrieve_components(requirements, k_per_type=10)

        filtered_components = self.filter_by_domain_and_level(
            all_components, requirements
        )

        diverse_components = {}
        for comp_type, target_count in target_counts.items():
            components = filtered_components.get(comp_type, [])

            diverse_set = self._select_diverse_by_domain(components, target_count)
            diverse_components[comp_type] = diverse_set

        return diverse_components

    def _select_diverse_by_domain(
        self, components: List[Dict], target_count: int
    ) -> List[Dict]:
        """Select components to maximize domain diversity"""
        if len(components) <= target_count:
            return components

        selected = []
        domains_used = set()

        for comp in components:
            domain = comp.get("domain", "")
            if domain not in domains_used and len(selected) < target_count:
                selected.append(comp)
                domains_used.add(domain)

        for comp in components:
            if comp not in selected and len(selected) < target_count:
                selected.append(comp)

        return selected[:target_count]
