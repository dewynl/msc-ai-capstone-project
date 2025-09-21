from typing import Any


DOMAIN_KEYWORDS = {
    "computer_science": ["programming", "algorithms", "software", "coding", "data structures", "machine learning", "artificial intelligence", "database", "network"],
    "mathematics": ["calculus", "algebra", "statistics", "mathematical", "equations", "probability", "theorem", "proof", "optimization"],
    "physics": ["mechanics", "forces", "energy", "motion", "electromagnetic", "thermodynamics", "quantum", "gravity", "wave"]
}


def extract_search_terms(requirements: dict[str, Any]) -> list[str]:
    """Extract key search terms from course requirements with STEM domain enhancement"""
    terms = []

    domain = requirements.get("domain", "").lower()
    if domain:
        terms.append(domain)
        if domain in DOMAIN_KEYWORDS:
            terms.extend(DOMAIN_KEYWORDS[domain][:2])

    level = requirements.get("level", "").lower()
    if level:
        terms.append(level)
        if level in ["beginner", "introductory"]:
            terms.append("fundamentals")
        elif level in ["advanced", "graduate"]:
            terms.append("complex")

    if requirements.get("topics"):
        if isinstance(requirements["topics"], list):
            terms.extend(requirements["topics"])
        else:
            terms.append(requirements["topics"])

    return terms


def generate_component_queries(requirements: dict[str, Any]) -> dict[str, str]:
    """Generate specific queries for each component type with STEM focus"""
    domain = requirements.get('domain', '')
    level = requirements.get('level', '')
    topics = requirements.get('topics', '')

    base_context = f"{domain} {level} {topics}".strip()

    return {
        "modules": f"course modules topics concepts {base_context}",
        "activities": f"learning exercises projects hands-on {base_context}",
        "assessments": f"exams tests evaluations assignments {base_context}",
    }


def validate_domain(domain: str) -> bool:
    """Validate if domain is within our focus areas"""
    return domain.lower() in DOMAIN_KEYWORDS


def enhance_query_with_context(query: str, requirements: dict[str, Any]) -> str:
    """Enhance search query with contextual information"""
    domain = requirements.get("domain", "")
    level = requirements.get("level", "")

    enhanced_query = query

    if domain and domain.lower() not in query.lower():
        enhanced_query = f"{query} {domain}"

    if level and level.lower() not in query.lower():
        enhanced_query = f"{enhanced_query} {level}"

    return enhanced_query.strip()
