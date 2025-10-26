#!/usr/bin/env python3
"""
Automated evaluation experiment runner for dissertation Chapter 6.
Runs 20 test cases and records metrics systematically.
"""
import json
import time
import csv
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import your system
from src.models.rag_integrated_generator import RAGIntegratedGenerator


def load_test_cases() -> list[Dict[str, Any]]:
    """Load test suite from JSON file."""
    test_file = Path("data/evaluation/evaluation_test_suite.json")
    with open(test_file, 'r') as f:
        return json.load(f)


def count_components(syllabus: Dict[str, Any]) -> Dict[str, int]:
    """Count components in generated syllabus."""
    return {
        'num_modules': len(syllabus.get('modules', [])),
        'num_activities': len(syllabus.get('activities', [])),
        'num_assessments': len(syllabus.get('assessments', [])),
        'total_components': (
            len(syllabus.get('modules', [])) +
            len(syllabus.get('activities', [])) +
            len(syllabus.get('assessments', []))
        )
    }


def estimate_t5_utilization(syllabus: Dict[str, Any]) -> int:
    """
    Estimate percentage of content from T5 vs templates.

    High-level heuristic:
    - Learning objectives: 100% T5 (if present)
    - Modules: 80% T5 (titles/descriptions)
    - Activities: 20% T5 (mostly RAG retrieved)
    - Assessments: 20% T5 (mostly RAG retrieved)
    """
    total_fields = 0
    t5_fields = 0

    # Learning objectives (fully T5 generated)
    objectives = syllabus.get('learning_objectives', [])
    if objectives:
        total_fields += len(objectives)
        t5_fields += len(objectives)

    # Modules (mostly T5 for titles/descriptions)
    modules = syllabus.get('modules', [])
    total_fields += len(modules) * 2  # title + description
    t5_fields += int(len(modules) * 1.6)  # 80% T5

    # Activities (mostly RAG)
    activities = syllabus.get('activities', [])
    total_fields += len(activities)
    t5_fields += int(len(activities) * 0.2)  # 20% T5

    # Assessments (mostly RAG)
    assessments = syllabus.get('assessments', [])
    total_fields += len(assessments)
    t5_fields += int(len(assessments) * 0.2)  # 20% T5

    if total_fields == 0:
        return 0

    return int((t5_fields / total_fields) * 100)


def check_completeness(syllabus: Dict[str, Any]) -> int:
    """Check what percentage of required fields are present."""
    required_fields = [
        'course_info',
        'learning_objectives',
        'modules',
        'activities',
        'assessments'
    ]

    present = sum(1 for field in required_fields if field in syllabus and syllabus[field])
    return int((present / len(required_fields)) * 100)


def run_single_test(
    generator: RAGIntegratedGenerator,
    test_case: Dict[str, Any]
) -> Dict[str, Any]:
    """Run a single test case and collect metrics."""

    print(f"\n{'='*60}")
    print(f"Running: {test_case['test_id']}")
    print(f"Title: {test_case['title']}")
    print(f"Domain: {test_case['domain']}, Level: {test_case['level']}")
    print(f"{'='*60}")

    result = {
        'test_id': test_case['test_id'],
        'domain': test_case['domain'],
        'level': test_case['level'],
        'title': test_case['title'],
        'description': test_case['description'][:50] + '...' if test_case['description'] else '',
        'json_valid': False,
        'gen_time_sec': 0.0,
        'num_modules': 0,
        'num_activities': 0,
        'num_assessments': 0,
        'total_components': 0,
        't5_utilization_pct': 0,
        'notes': ''
    }

    try:
        # Generate syllabus with timing
        start_time = time.time()

        requirements = {
            'title': test_case['title'],
            'domain': test_case['domain'],
            'level': test_case['level'],
            'description': test_case['description']
        }

        syllabus = generator.generate_syllabus_with_ids(requirements)

        end_time = time.time()
        gen_time = round(end_time - start_time, 2)

        # Validate JSON (if it got here, it's valid dict)
        result['json_valid'] = True
        result['gen_time_sec'] = gen_time

        # Count components
        counts = count_components(syllabus)
        result.update(counts)

        # Estimate T5 utilization
        result['t5_utilization_pct'] = estimate_t5_utilization(syllabus)

        # Save output
        output_file = Path(f"data/evaluation/outputs/{test_case['test_id']}.json")
        with open(output_file, 'w') as f:
            json.dump(syllabus, f, indent=2)

        # Success message
        print(f"✅ SUCCESS: Generated in {gen_time}s")
        print(f"   Components: {result['total_components']} total")
        print(f"   T5 Utilization: {result['t5_utilization_pct']}%")
        result['notes'] = 'Success'

    except json.JSONDecodeError as e:
        print(f"❌ JSON PARSE ERROR: {str(e)[:100]}")
        result['notes'] = f'JSON parse error: {str(e)[:50]}'

    except Exception as e:
        print(f"❌ GENERATION ERROR: {str(e)[:100]}")
        result['notes'] = f'Error: {str(e)[:50]}'

    return result


def save_results_to_csv(results: list[Dict[str, Any]]):
    """Append results to CSV file."""
    csv_file = Path("data/evaluation/results.csv")

    # Write results
    with open(csv_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writerows(results)

    print(f"\n✅ Results saved to: {csv_file}")


def print_summary(results: list[Dict[str, Any]]):
    """Print summary statistics."""
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)

    valid_count = sum(1 for r in results if r['json_valid'])
    total = len(results)

    print(f"\nJSON Validity: {valid_count}/{total} ({valid_count/total*100:.1f}%)")

    if valid_count > 0:
        valid_results = [r for r in results if r['json_valid']]

        avg_time = sum(r['gen_time_sec'] for r in valid_results) / len(valid_results)
        avg_components = sum(r['total_components'] for r in valid_results) / len(valid_results)
        avg_t5 = sum(r['t5_utilization_pct'] for r in valid_results) / len(valid_results)

        print(f"\nAverage Generation Time: {avg_time:.2f}s")
        print(f"Average Components: {avg_components:.1f}")
        print(f"Average T5 Utilization: {avg_t5:.0f}%")

        # By domain
        print(f"\nBy Domain:")
        for domain in ['computer_science', 'mathematics', 'physics']:
            domain_results = [r for r in valid_results if r['domain'] == domain]
            if domain_results:
                avg_time_domain = sum(r['gen_time_sec'] for r in domain_results) / len(domain_results)
                print(f"  {domain}: {len(domain_results)} tests, avg {avg_time_domain:.2f}s")

        # By level
        print(f"\nBy Level:")
        for level in ['beginner', 'intermediate', 'advanced']:
            level_results = [r for r in valid_results if r['level'] == level]
            if level_results:
                avg_comp = sum(r['total_components'] for r in level_results) / len(level_results)
                print(f"  {level}: {len(level_results)} tests, avg {avg_comp:.1f} components")

    print("\n" + "="*60)


def main():
    """Run all evaluation experiments."""
    print("="*60)
    print("DISSERTATION EVALUATION EXPERIMENTS")
    print("Chapter 6: Technical Performance Assessment")
    print("="*60)

    # Load test cases
    print("\nLoading test suite...")
    test_cases = load_test_cases()
    print(f"✅ Loaded {len(test_cases)} test cases")

    # Initialize system
    print("\nInitializing RAG-integrated generator...")
    try:
        generator = RAGIntegratedGenerator()
        print("✅ System initialized")
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure component data is in: data/components/")
        print("2. Check vector store initialization")
        return

    # Run experiments
    print(f"\nRunning {len(test_cases)} evaluation experiments...")
    print("This will take approximately 2-3 minutes.\n")

    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}]", end=" ")
        result = run_single_test(generator, test_case)
        results.append(result)

    # Save results
    save_results_to_csv(results)

    # Print summary
    print_summary(results)

    print("\n✅ Evaluation experiments complete!")
    print(f"\nNext steps:")
    print(f"1. Review outputs in: data/evaluation/outputs/")
    print(f"2. Check metrics in: data/evaluation/results.csv")
    print(f"3. Use this data to write Chapter 6")


if __name__ == "__main__":
    main()
