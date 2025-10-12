from typing import Any

DOMAIN_KEYWORDS = {
    "computer_science": [
        "programming",
        "algorithms",
        "software",
        "coding",
        "data structures",
        "machine learning",
        "artificial intelligence",
        "database",
        "network",
    ],
    "mathematics": [
        "calculus",
        "algebra",
        "statistics",
        "mathematical",
        "equations",
        "probability",
        "theorem",
        "proof",
        "optimization",
    ],
    "physics": [
        "mechanics",
        "forces",
        "energy",
        "motion",
        "electromagnetic",
        "thermodynamics",
        "quantum",
        "gravity",
        "wave",
    ],
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
    domain = requirements.get("domain", "").replace("_", " ")
    title = requirements.get("title", "")

    # Extract key terms from title that are likely to match content
    key_terms = []
    if title:
        # Get key subject words, skip common words
        words = title.lower().split()
        subject_words = [
            w for w in words if w not in ["to", "the", "of", "and", "in", "for", "with"]
        ]
        key_terms.extend(subject_words[:2])  # Take first 2 subject words

    if domain and domain not in " ".join(key_terms):
        key_terms.append(domain.replace("_", " "))

    # Use simple, focused query
    query = " ".join(key_terms[:2])  # Max 2 terms for better matching

    return {
        "modules": query,
        "activities": query,
        "assessments": query,
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
