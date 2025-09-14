from typing import Any

from .query_processor import generate_component_queries
from .vector_store import SyllabusComponentStore


class ComponentRetrievalPipeline:
    """Retrieve relevant syllabus components based on course requirements"""

    def __init__(self, component_store: SyllabusComponentStore):
        self.component_store = component_store

    def retrieve_components(
        self, requirements: dict[str, Any], k_per_type: int = 3
    ) -> dict[str, list]:
        """Retrieve relevant syllabus components based on course requirements"""
        queries = generate_component_queries(requirements)
        retrieved = {}

        for component_type, query in queries.items():
            results = self.component_store.search(
                query, k=k_per_type, component_type=component_type
            )
            retrieved[component_type] = [result[0] for result in results]

        return retrieved

    def filter_by_domain_and_level(
        self, components: dict[str, list], requirements: dict[str, Any]
    ) -> dict[str, list]:
        """ "Apply domain and difficulty level filters to retrieved components"""
        # TODO: Filter components based on course requirements
        filtered = {}
        target_domain = requirements.get("domain", "").lower()

        for comp_type, comp_list in components.items():
            filtered[comp_type] = []
            for comp in comp_list:
                comp_domain = comp.get("domain", "").lower()
                if (
                    not target_domain
                    or target_domain in comp_domain
                    or comp_domain in target_domain
                ):
                    filtered[comp_type].append(comp)

        return filtered
