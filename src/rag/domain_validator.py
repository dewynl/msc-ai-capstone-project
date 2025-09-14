#!/usr/bin/env python3
"""
Enhanced Domain Validation for RAG System
Prevents nonsensical syllabus generation for unsupported domains
"""

from typing import Any


class DomainValidator:
    """Enhanced domain validation with confidence scoring"""

    def __init__(self):
        self.supported_domains = {
            "computer science": [
                "programming",
                "algorithm",
                "software",
                "data structure",
            ],
            "data science": ["data", "statistics", "machine learning", "analytics"],
            "mathematics": ["calculus", "algebra", "statistics", "theorem"],
            "physics": ["force", "energy", "quantum", "electromagnetic"],
            "leadership": ["management", "team", "communication", "decision"],
            "project management": ["project", "planning", "resource", "timeline"],
            "software development": ["development", "coding", "application"],
            "aws cloud": ["aws", "cloud", "ec2", "lambda", "s3"],
            "cisco networking": ["network", "cisco", "routing", "switching"],
            "pmp": ["certification", "project", "management"],
            "google analytics": ["analytics", "google", "web", "traffic"],
            "data analysis": ["analysis", "data", "visualization", "insights"],
        }

    def validate_domain_coverage(
        self, retrieved: dict[str, list], requirements: dict[str, Any]
    ) -> tuple[bool, str, float]:
        """
        Enhanced domain validation with confidence scoring

        Returns:
            (is_valid, error_message, confidence_score)
        """

        required_domain = requirements.get("domain", "").lower()
        course_title = requirements.get("title", "").lower()

        # Check if domain is in our supported list
        domain_supported = any(
            required_domain in domain or domain in required_domain
            for domain in self.supported_domains.keys()
        )

        if not domain_supported:
            return (
                False,
                f"Domain '{requirements.get('domain')}' is not in our supported domains: {list(self.supported_domains.keys())}",
                0.0,
            )

        # Count domain-relevant components
        relevant_count = 0
        total_count = 0
        relevance_scores = []

        for component_type, components in retrieved.items():
            for component in components:
                total_count += 1
                component_domain = component.get("domain", "").lower()
                component_title = component.get("title", "").lower()
                component_desc = component.get("description", "").lower()

                # Calculate component relevance score
                relevance_score = self._calculate_relevance_score(
                    required_domain,
                    course_title,
                    component_domain,
                    component_title,
                    component_desc,
                )

                relevance_scores.append(relevance_score)

                if relevance_score >= 0.6:  # Higher threshold for relevance
                    relevant_count += 1

        # Calculate overall confidence
        avg_relevance = (
            sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        )
        relevance_ratio = relevant_count / total_count if total_count > 0 else 0

        confidence_score = (avg_relevance + relevance_ratio) / 2

        # Enhanced validation criteria (balanced for real-world use)
        min_relevance_ratio = 0.3  # Balanced threshold
        min_relevant_count = 2  # Reasonable minimum
        min_confidence = 0.25  # Lower threshold for edge cases

        if (
            relevance_ratio < min_relevance_ratio
            or relevant_count < min_relevant_count
            or confidence_score < min_confidence
        ):
            return (
                False,
                f"Insufficient domain coverage for '{requirements.get('domain')}': "
                f"{relevant_count}/{total_count} components relevant "
                f"(need {min_relevant_count}+), "
                f"relevance ratio: {relevance_ratio:.1%} "
                f"(need {min_relevance_ratio:.0%}+), "
                f"confidence: {confidence_score:.1%} "
                f"(need {min_confidence:.0%}+)",
                confidence_score,
            )

        return True, "", confidence_score

    def _calculate_relevance_score(
        self,
        required_domain: str,
        course_title: str,
        component_domain: str,
        component_title: str,
        component_desc: str,
    ) -> float:
        """Calculate relevance score for a component"""

        score = 0.0

        # Direct domain match (highest weight)
        if required_domain in component_domain or component_domain in required_domain:
            score += 0.4

        # Keyword matching in domain
        domain_keywords = self.supported_domains.get(required_domain, [])
        component_text = f"{component_title} {component_desc}".lower()

        keyword_matches = sum(
            1 for keyword in domain_keywords if keyword in component_text
        )
        if domain_keywords:
            score += 0.3 * (keyword_matches / len(domain_keywords))

        # Title similarity
        title_words = set(course_title.split())
        component_words = set(component_title.split())
        title_overlap = len(title_words & component_words) / max(len(title_words), 1)
        score += 0.2 * title_overlap

        # Description relevance
        desc_overlap = sum(1 for word in title_words if word in component_desc)
        score += 0.1 * min(desc_overlap / max(len(title_words), 1), 1.0)

        return min(score, 1.0)

    def get_domain_coverage_report(self, retrieved: dict[str, list]) -> dict[str, Any]:
        """Generate detailed domain coverage report"""

        coverage = {}

        for component_type, components in retrieved.items():
            domains_in_type = {}
            for component in components:
                domain = component.get("domain", "unknown")
                domains_in_type[domain] = domains_in_type.get(domain, 0) + 1

            coverage[component_type] = domains_in_type

        return {
            "component_coverage": coverage,
            "supported_domains": list(self.supported_domains.keys()),
            "total_components": sum(len(comps) for comps in retrieved.values()),
        }

    def suggest_alternative_domains(self, requested_domain: str) -> list[str]:
        """Suggest alternative domains if requested domain is not supported"""

        requested_lower = requested_domain.lower()
        suggestions = []

        # Find domains with keyword overlap
        for domain, keywords in self.supported_domains.items():
            if any(
                keyword in requested_lower or requested_lower in keyword
                for keyword in keywords
            ):
                suggestions.append(domain)

        # If no keyword matches, suggest most general domains
        if not suggestions:
            suggestions = ["computer science", "data science", "mathematics"]

        return suggestions[:3]  # Return top 3 suggestions


def create_enhanced_insufficient_data_response(
    course_requirements: dict[str, Any],
    error_msg: str,
    confidence_score: float,
    retrieved: dict[str, list],
    validator: DomainValidator,
) -> str:
    """Create detailed insufficient data response with suggestions"""

    title = course_requirements.get("title", "Course")
    domain = course_requirements.get("domain", "")

    # Get coverage report and suggestions
    coverage_report = validator.get_domain_coverage_report(retrieved)
    suggestions = validator.suggest_alternative_domains(domain)

    response = f"""# {title}

## Insufficient Domain Data Available

I apologize, but I don't have sufficient relevant educational components to generate a high-quality syllabus for this course.

**Domain Coverage Analysis:**
- Requested Domain: {domain}
- Confidence Score: {confidence_score:.1%}
- Issue: {error_msg}

**Available Components Found:** {coverage_report['total_components']} total components
{_format_coverage_breakdown(coverage_report['component_coverage'])}

**Supported Domains:** {', '.join(coverage_report['supported_domains'])}

**Recommendations:**
1. Consider one of these similar supported domains: {', '.join(suggestions)}
2. Consult with subject matter experts in {domain}
3. This system works best for: Computer Science, Data Science, Mathematics, Leadership, and Project Management

**Alternative Approach:**
- Try rephrasing your domain to match supported areas
- Consider breaking complex topics into foundational components
- Focus on transferable skills that overlap with supported domains

---
*This response prevents generating irrelevant content when domain coverage is insufficient.*
*System confidence threshold: 50% (current: {confidence_score:.1%})*
"""

    return response


def _format_coverage_breakdown(coverage: dict[str, dict[str, int]]) -> str:
    """Format component coverage breakdown for display"""

    breakdown = []
    for comp_type, domains in coverage.items():
        domain_list = [f"{domain}({count})" for domain, count in domains.items()]
        breakdown.append(f"- {comp_type.title()}: {', '.join(domain_list)}")

    return "\n".join(breakdown) if breakdown else "- No components retrieved"
