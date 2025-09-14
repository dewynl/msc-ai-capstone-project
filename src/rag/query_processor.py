from typing import Any


def extract_search_terms(requirements: dict[str, Any]) -> list[str]:
    """Extract key search terms from course requirements"""
    terms = []
    if requirements.get("domain"):
        terms.append(requirements["domain"])
    if requirements.get("level"):
        terms.append(requirements["level"])
    return terms


def generate_component_queries(requirements: dict[str, Any]) -> dict[str, str]:
    """Generate specific queries for each component type"""
    return {
        "modules": f"course modules for {requirements.get('domain', '')} at {requirements.get('level', '')} level",
        "activities": f"learning activities for {requirements.get('domain', '')} students",
        "assessments": f"assessments for {requirements.get('domain', '')} course",
    }
