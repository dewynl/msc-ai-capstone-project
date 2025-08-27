#!/usr/bin/env python3
"""
Run Accuracy Test
Example script showing how to use the accuracy evaluator
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evaluation.accuracy_evaluator import quick_accuracy_test
from src.rag.rag_system import generate_rag_syllabus


def main():
    """Run accuracy test with sample courses"""

    # Sample test cases
    test_requirements = [
        {
            "title": "Data Science Fundamentals",
            "domain": "Data Science",
            "level": "undergraduate",
        },
        {
            "title": "Computer Science Theory",
            "domain": "Computer Science",
            "level": "graduate",
        },
        {
            "title": "Web Development Bootcamp",
            "domain": "Software Development",
            "level": "professional",
        },
        {
            "title": "Project Management Essentials",
            "domain": "Project Management",
            "level": "professional",
        },
    ]

    # Run the test
    evaluation_data = quick_accuracy_test(generate_rag_syllabus, test_requirements)

    # Optionally save results
    from src.evaluation.accuracy_evaluator import SyllabusAccuracyEvaluator

    evaluator = SyllabusAccuracyEvaluator()
    evaluator.save_evaluation_results(evaluation_data, "latest_accuracy_test.json")


if __name__ == "__main__":
    main()
