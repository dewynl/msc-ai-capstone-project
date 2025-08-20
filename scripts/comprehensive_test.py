#!/usr/bin/env python3
"""
Comprehensive RAG System Testing
Test multiple courses across different domains and levels
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.rag_system import generate_rag_syllabus


def comprehensive_test():
    """Test RAG system across different domains"""

    # Diverse test courses
    test_courses = [
        {
            "title": "Introduction to Python Programming",
            "domain": "Computer Science",
            "level": "undergraduate",
            "description": "Learn Python programming fundamentals including syntax, data structures, and object-oriented programming",
        },
        {
            "title": "Advanced Data Science Methods",
            "domain": "Data Science",
            "level": "graduate",
            "description": "Advanced statistical methods and machine learning techniques for complex data analysis",
        },
        {
            "title": "Digital Marketing Strategy",
            "domain": "Business",
            "level": "professional",
            "description": "Modern digital marketing approaches including social media, SEO, and analytics",
        },
        {
            "title": "Linear Algebra for Engineers",
            "domain": "Mathematics",
            "level": "undergraduate",
            "description": "Mathematical foundations of linear algebra with engineering applications",
        },
        {
            "title": "Project Management Fundamentals",
            "domain": "Leadership",
            "level": "professional",
            "description": "Essential project management principles and methodologies for business",
        },
    ]

    print("🔬 Comprehensive RAG System Test")
    print(f"Testing {len(test_courses)} courses across different domains")
    print("=" * 80)

    results = []
    total_start = time.time()

    # Create output directory
    output_dir = Path("test_results")
    output_dir.mkdir(exist_ok=True)

    for i, course in enumerate(test_courses, 1):
        print(f"\n🧪 Test {i}/{len(test_courses)}: {course['title']}")
        print(f"   Domain: {course['domain']} | Level: {course['level']}")

        start_time = time.time()

        try:
            # Generate syllabus
            result = generate_rag_syllabus(course)
            generation_time = time.time() - start_time

            # Save syllabus
            filename = f"syllabus_{i}_{course['title'].replace(' ', '_').lower()}.md"
            filepath = output_dir / filename

            with open(filepath, "w") as f:
                f.write(result["syllabus_content"])

            # Analyze quality
            analysis = analyze_syllabus_quality(result["syllabus_content"], course)

            test_result = {
                "course": course,
                "success": True,
                "generation_time": generation_time,
                "output_file": str(filepath),
                "analysis": analysis,
                "retrieved_components": {
                    comp_type: len(comps)
                    for comp_type, comps in result["retrieved_components"].items()
                },
            }

            print(f"   ✅ Success ({generation_time:.2f}s)")
            print(f"   📁 Saved: {filename}")
            print(f"   📊 Quality Score: {analysis['quality_score']:.1f}/10")

        except Exception as e:
            test_result = {
                "course": course,
                "success": False,
                "error": str(e),
                "generation_time": time.time() - start_time,
            }
            print(f"   ❌ Failed: {e}")

        results.append(test_result)

    total_time = time.time() - total_start

    # Save comprehensive results
    results_file = output_dir / "comprehensive_test_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)

    # Success rate
    successful = [r for r in results if r.get("success", False)]
    print(
        f"Success Rate: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)"
    )

    if successful:
        # Performance metrics
        avg_time = sum(r["generation_time"] for r in successful) / len(successful)
        print(f"Average Generation Time: {avg_time:.2f}s")

        # Quality metrics
        quality_scores = [r["analysis"]["quality_score"] for r in successful]
        avg_quality = sum(quality_scores) / len(quality_scores)
        print(f"Average Quality Score: {avg_quality:.1f}/10")

        # Domain coverage
        domains = {r["course"]["domain"] for r in successful}
        print(f"Domains Tested: {len(domains)} ({', '.join(domains)})")

        # Component retrieval
        total_components = sum(
            sum(r["retrieved_components"].values()) for r in successful
        )
        print(f"Total Components Retrieved: {total_components}")

    print(f"\nTotal Test Time: {total_time:.2f}s")
    print(f"📁 Results saved in: {output_dir}")
    print(f"📄 Summary: {results_file}")

    return results


def analyze_syllabus_quality(content: str, course_info: dict) -> dict:
    """Analyze quality of generated syllabus"""

    analysis = {
        "length_chars": len(content),
        "length_words": len(content.split()),
        "length_lines": len(content.split("\n")),
    }

    # Structure checks
    structure_checks = {
        "has_title": content.startswith("#"),
        "has_headers": content.count("##") >= 3,
        "has_weekly_schedule": "Week 1:" in content and "Week" in content,
        "has_assessment_table": "|" in content and "points" in content.lower(),
        "has_learning_objectives": "objective" in content.lower() and "•" in content,
        "has_grading_scale": "grading" in content.lower()
        and ("A:" in content or "90" in content),
        "has_course_policies": "policy" in content.lower() or "Policy" in content,
        "has_required_materials": "textbook" in content.lower()
        or "materials" in content.lower(),
    }

    analysis["structure_score"] = (
        sum(structure_checks.values()) / len(structure_checks) * 10
    )

    # Content relevance
    title_words = set(course_info["title"].lower().split())
    domain_words = set(course_info["domain"].lower().split())
    content_words = set(content.lower().split())

    title_relevance = len(title_words.intersection(content_words)) / len(title_words)
    domain_relevance = len(domain_words.intersection(content_words)) / len(domain_words)

    analysis["content_relevance"] = (title_relevance + domain_relevance) / 2 * 10

    # Overall quality score (weighted average)
    analysis["quality_score"] = (
        analysis["structure_score"] * 0.6 + analysis["content_relevance"] * 0.4
    )

    analysis["structure_checks"] = structure_checks

    return analysis


if __name__ == "__main__":
    comprehensive_test()
