"""
RAG System Accuracy Evaluator
Comprehensive evaluation metrics for syllabus generation quality and accuracy
"""

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any


@dataclass
class EvaluationResults:
    """Structured results from accuracy evaluation"""

    overall_score: float
    domain_score: float
    structure_score: float
    content_score: float
    formatting_score: float
    detailed_metrics: dict[str, float]


class SyllabusAccuracyEvaluator:
    """Evaluates syllabus generation accuracy across multiple dimensions"""

    def __init__(self):
        self.domain_keywords = {
            "computer science": [
                "algorithm",
                "data structure",
                "programming",
                "software",
                "coding",
            ],
            "data science": [
                "data",
                "analysis",
                "statistics",
                "machine learning",
                "visualization",
            ],
            "mathematics": ["equation", "function", "calculus", "algebra", "geometry"],
            "physics": ["force", "energy", "wave", "quantum", "electromagnetic"],
            "software development": [
                "development",
                "programming",
                "coding",
                "application",
                "software",
            ],
            "aws cloud": ["aws", "cloud", "ec2", "lambda", "s3"],
            "project management": [
                "project",
                "management",
                "planning",
                "resource",
                "timeline",
            ],
            "leadership": [
                "leadership",
                "team",
                "management",
                "communication",
                "decision",
            ],
        }

        self.required_sections = [
            "course description",
            "learning objectives",
            "learning sequence",
            "assessment strategy",
            "grading scale",
            "course policies",
        ]

    def evaluate_domain_accuracy(
        self, result: dict[str, Any], requirements: dict[str, Any]
    ) -> dict[str, float]:
        """Evaluate domain-specific accuracy"""

        required_domain = requirements.get("domain", "").lower()
        content = result.get("syllabus_content", "").lower()
        retrieved = result.get("retrieved_components", {})

        metrics = {}

        # Domain consistency - Are retrieved components from correct domain?
        total_components = sum(len(comps) for comps in retrieved.values())
        domain_matches = 0

        for comp_type, components in retrieved.items():
            for comp in components:
                comp_domain = comp.get("domain", "").lower()
                if required_domain in comp_domain or comp_domain in required_domain:
                    domain_matches += 1

        metrics["domain_consistency"] = (
            domain_matches / total_components if total_components > 0 else 0
        )

        # Content domain relevance - Does generated content mention correct domain?
        relevant_keywords = self.domain_keywords.get(required_domain, [])
        if relevant_keywords:
            keyword_matches = sum(
                1 for keyword in relevant_keywords if keyword in content
            )
            metrics["content_domain_relevance"] = keyword_matches / len(
                relevant_keywords
            )
        else:
            metrics["content_domain_relevance"] = 0.5  # Neutral for unknown domains

        return metrics

    def evaluate_structural_quality(self, content: str) -> dict[str, float]:
        """Evaluate structural quality of generated syllabus"""

        metrics = {}

        # Required sections presence
        sections_found = 0
        for section in self.required_sections:
            if section.lower() in content.lower():
                sections_found += 1

        metrics["structural_completeness"] = sections_found / len(
            self.required_sections
        )

        # Assessment table quality
        has_assessment_table = "|" in content and "percentage" in content.lower()
        metrics["assessment_table_present"] = 1.0 if has_assessment_table else 0.0

        # Learning module structure
        module_pattern = r"learning module \d+|module \d+"
        modules_found = len(re.findall(module_pattern, content.lower()))
        metrics["module_structure"] = min(modules_found / 5, 1.0)  # Expect 3-5 modules

        # Learning objectives quality
        objectives_section = re.search(
            r"learning objectives.*?(?=##|$)", content, re.IGNORECASE | re.DOTALL
        )
        if objectives_section:
            objectives_text = objectives_section.group()
            bullet_points = len(re.findall(r"[•\-\*]\s", objectives_text))
            metrics["learning_objectives_count"] = min(
                bullet_points / 5, 1.0
            )  # Expect ~5 objectives
        else:
            metrics["learning_objectives_count"] = 0.0

        return metrics

    def evaluate_content_quality(
        self, content: str, retrieved: dict[str, list]
    ) -> dict[str, float]:
        """Evaluate content quality and coherence"""

        metrics = {}

        # Content length appropriateness
        word_count = len(content.split())
        if 1000 <= word_count <= 3000:
            metrics["length_appropriateness"] = 1.0
        elif word_count < 500:
            metrics["length_appropriateness"] = 0.2  # Too short
        elif word_count > 5000:
            metrics["length_appropriateness"] = 0.6  # Too long
        else:
            metrics["length_appropriateness"] = 0.8  # Close to ideal

        # Repetition detection
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        unique_lines = set(lines)
        metrics["content_uniqueness"] = len(unique_lines) / len(lines) if lines else 0

        # Component utilization - How well are retrieved components used?
        total_components = sum(len(comps) for comps in retrieved.values())
        component_mentions = 0

        for comp_type, components in retrieved.items():
            for comp in components:
                comp_title = comp.get("title", "")
                title_words = [
                    word for word in comp_title.lower().split() if len(word) > 4
                ]
                if any(word in content.lower() for word in title_words[:3]):
                    component_mentions += 1

        metrics["component_utilization"] = (
            component_mentions / total_components if total_components > 0 else 0
        )

        return metrics

    def evaluate_professional_formatting(self, content: str) -> dict[str, float]:
        """Evaluate professional formatting quality"""

        metrics = {}

        # Markdown formatting quality
        headers = len(re.findall(r"^#+\s", content, re.MULTILINE))
        metrics["header_structure"] = min(headers / 8, 1.0)  # Expect ~8 main headers

        # Table formatting
        tables = content.count("|")
        metrics["table_formatting"] = min(tables / 20, 1.0) if tables > 0 else 0

        # List formatting
        lists = len(re.findall(r"^[\-\*•]\s", content, re.MULTILINE))
        metrics["list_formatting"] = min(lists / 10, 1.0)  # Expect multiple lists

        # No obvious AI artifacts
        ai_artifacts = [
            "as an ai",
            "i cannot",
            "i don't have",
            "generated with",
            "note:",
            "please note",
            "[insert",
            "placeholder",
        ]
        artifacts_found = sum(
            1 for artifact in ai_artifacts if artifact in content.lower()
        )
        metrics["professional_tone"] = max(0, 1.0 - (artifacts_found * 0.3))

        return metrics

    def evaluate_single_syllabus(
        self, result: dict[str, Any], requirements: dict[str, Any]
    ) -> EvaluationResults:
        """Evaluate a single generated syllabus"""

        if "validation_error" in result:
            return EvaluationResults(
                overall_score=0.0,
                domain_score=0.0,
                structure_score=0.0,
                content_score=0.0,
                formatting_score=0.0,
                detailed_metrics={"validation_failed": True},
            )

        content = result["syllabus_content"]
        retrieved = result["retrieved_components"]

        # Evaluate different aspects
        domain_metrics = self.evaluate_domain_accuracy(result, requirements)
        structural_metrics = self.evaluate_structural_quality(content)
        content_metrics = self.evaluate_content_quality(content, retrieved)
        formatting_metrics = self.evaluate_professional_formatting(content)

        # Calculate category scores
        domain_score = sum(domain_metrics.values()) / len(domain_metrics)
        structure_score = sum(structural_metrics.values()) / len(structural_metrics)
        content_score = sum(content_metrics.values()) / len(content_metrics)
        formatting_score = sum(formatting_metrics.values()) / len(formatting_metrics)

        # Overall score
        overall_score = (
            domain_score + structure_score + content_score + formatting_score
        ) / 4

        # Combine all detailed metrics
        detailed_metrics = {
            **{f"domain_{k}": v for k, v in domain_metrics.items()},
            **{f"structure_{k}": v for k, v in structural_metrics.items()},
            **{f"content_{k}": v for k, v in content_metrics.items()},
            **{f"formatting_{k}": v for k, v in formatting_metrics.items()},
        }

        return EvaluationResults(
            overall_score=overall_score,
            domain_score=domain_score,
            structure_score=structure_score,
            content_score=content_score,
            formatting_score=formatting_score,
            detailed_metrics=detailed_metrics,
        )

    def evaluate_multiple_syllabi(
        self, test_cases: list[tuple[dict[str, Any], dict[str, Any]]]
    ) -> dict[str, Any]:
        """Evaluate multiple syllabi and return aggregated results"""

        results = []
        category_scores = defaultdict(list)

        for i, (result, requirements) in enumerate(test_cases, 1):
            eval_result = self.evaluate_single_syllabus(result, requirements)
            results.append(
                {"case_id": i, "requirements": requirements, "evaluation": eval_result}
            )

            # Aggregate scores
            category_scores["overall"].append(eval_result.overall_score)
            category_scores["domain"].append(eval_result.domain_score)
            category_scores["structure"].append(eval_result.structure_score)
            category_scores["content"].append(eval_result.content_score)
            category_scores["formatting"].append(eval_result.formatting_score)

        # Calculate averages
        averages = {
            category: sum(scores) / len(scores)
            for category, scores in category_scores.items()
        }

        return {
            "system_averages": averages,
            "individual_results": results,
            "total_cases": len(test_cases),
            "success_rate": len(
                [r for r in results if r["evaluation"].overall_score > 0]
            )
            / len(results),
        }

    def print_evaluation_summary(self, evaluation_data: dict[str, Any]) -> None:
        """Print a formatted summary of evaluation results"""

        print("🎯 RAG SYSTEM ACCURACY EVALUATION")
        print("=" * 50)

        averages = evaluation_data["system_averages"]
        print(f"Overall System Score: {averages['overall']:.3f}/1.000")
        print(f"Success Rate: {evaluation_data['success_rate']:.1%}")
        print(f"Total Test Cases: {evaluation_data['total_cases']}")

        print("\nCategory Breakdown:")
        print(f"  Domain Accuracy:     {averages['domain']:.3f}")
        print(f"  Structural Quality:  {averages['structure']:.3f}")
        print(f"  Content Quality:     {averages['content']:.3f}")
        print(f"  Professional Format: {averages['formatting']:.3f}")

        # Individual results summary
        print("\nIndividual Results:")
        for result in evaluation_data["individual_results"]:
            req = result["requirements"]
            eval_res = result["evaluation"]
            print(f"  {req['title']} ({req['domain']}): {eval_res.overall_score:.2f}")

    def save_evaluation_results(
        self,
        evaluation_data: dict[str, Any],
        filename: str = "accuracy_evaluation.json",
    ) -> None:
        """Save evaluation results to JSON file"""

        # Convert EvaluationResults objects to dictionaries for JSON serialization
        serializable_data = evaluation_data.copy()
        for result in serializable_data["individual_results"]:
            eval_result = result["evaluation"]
            result["evaluation"] = {
                "overall_score": eval_result.overall_score,
                "domain_score": eval_result.domain_score,
                "structure_score": eval_result.structure_score,
                "content_score": eval_result.content_score,
                "formatting_score": eval_result.formatting_score,
                "detailed_metrics": eval_result.detailed_metrics,
            }

        with open(filename, "w") as f:
            json.dump(serializable_data, f, indent=2)

        print(f"\n📄 Detailed results saved to: {filename}")


def quick_accuracy_test(
    rag_generate_function, test_requirements: list[dict[str, Any]]
) -> dict[str, Any]:
    """Quick accuracy test function for development use"""

    evaluator = SyllabusAccuracyEvaluator()
    test_cases = []

    print("🧪 Running Quick Accuracy Test...")

    for i, requirements in enumerate(test_requirements, 1):
        print(
            f"  Generating syllabus {i}/{len(test_requirements)}: {requirements['title']}"
        )
        result = rag_generate_function(requirements)
        test_cases.append((result, requirements))

    evaluation_data = evaluator.evaluate_multiple_syllabi(test_cases)
    evaluator.print_evaluation_summary(evaluation_data)

    return evaluation_data
