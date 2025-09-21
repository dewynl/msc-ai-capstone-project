#!/usr/bin/env python3
"""
Domain classifier for educational components
Reclassifies components based on content analysis
"""

import json
import re
from pathlib import Path
from typing import Dict, List


class DomainClassifier:
    def __init__(self):
        self.domain_keywords = {
            'mathematics': [
                'calculus', 'algebra', 'geometry', 'trigonometry', 'statistics', 'probability',
                'derivatives', 'integrals', 'equations', 'mathematical', 'theorem', 'proof',
                'linear algebra', 'differential', 'matrix', 'vector', 'function', 'polynomial',
                'graph theory', 'discrete math', 'number theory', 'optimization', 'analysis'
            ],
            'physics': [
                'physics', 'force', 'motion', 'energy', 'momentum', 'velocity', 'acceleration',
                'newton', 'thermodynamics', 'electromagnetism', 'quantum', 'mechanics',
                'gravity', 'wave', 'particle', 'electromagnetic', 'kinetic', 'potential',
                'collision', 'friction', 'pressure', 'temperature', 'heat', 'light'
            ],
            'computer_science': [
                'programming', 'algorithm', 'data structure', 'software', 'computer',
                'coding', 'python', 'java', 'javascript', 'database', 'network',
                'artificial intelligence', 'machine learning', 'cybersecurity', 'web',
                'application', 'development', 'debugging', 'syntax', 'variable',
                'function', 'class', 'object oriented', 'recursion', 'sorting',
                'engineering', 'design', 'system', 'architecture', 'distributed',
                'aws', 'cloud', 'binary', 'distributed system', 'failure analysis',
                'efficiency analysis', 'implementation', 'churn prediction',
                'bias variance', 'cross validation', 'model', 'data mining',
                'visualization', 'correlation', 'feature importance', 'random forest'
            ]
        }

    def classify_component(self, component: Dict) -> str:
        """Classify a component based on its title and description"""
        text = f"{component.get('title', '')} {component.get('description', '')}".lower()

        domain_scores = {}
        for domain, keywords in self.domain_keywords.items():
            score = 0
            for keyword in keywords:
                        score += len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', text))
            domain_scores[domain] = score

        best_domain = max(domain_scores.items(), key=lambda x: x[1])

        if best_domain[1] > 0:
            return best_domain[0]
        else:
            return 'computer_science'

    def reclassify_file(self, input_file: Path, output_file: Path = None) -> Dict:
        """Reclassify domains in a component file"""
        if output_file is None:
            output_file = input_file

        with open(input_file, 'r') as f:
            components = json.load(f)

        classification_stats = {'total': len(components)}
        domain_changes = {}

        for component in components:
            old_domain = component.get('domain', 'unknown')
            new_domain = self.classify_component(component)
            component['domain'] = new_domain

            if old_domain != new_domain:
                key = f"{old_domain} -> {new_domain}"
                domain_changes[key] = domain_changes.get(key, 0) + 1

        with open(output_file, 'w') as f:
            json.dump(components, f, indent=2)

        final_domains = {}
        for component in components:
            domain = component['domain']
            final_domains[domain] = final_domains.get(domain, 0) + 1

        classification_stats['changes'] = domain_changes
        classification_stats['final_distribution'] = final_domains

        return classification_stats


def main():
    """Reclassify all component files"""
    print("🔄 Reclassifying Component Domains")
    print("=" * 35)

    classifier = DomainClassifier()
    data_dir = Path("data/components")

    files_to_process = ["activities.json", "assessments.json", "modules.json"]

    total_stats = {}

    for filename in files_to_process:
        file_path = data_dir / filename
        if not file_path.exists():
            print(f"⚠️  {filename} not found, skipping...")
            continue

        print(f"\n📝 Processing {filename}...")
        stats = classifier.reclassify_file(file_path)
        total_stats[filename] = stats

        print(f"   Total components: {stats['total']}")
        print(f"   Domain changes: {len(stats['changes'])}")

        if stats['changes']:
            print("   Changes made:")
            for change, count in stats['changes'].items():
                print(f"     • {change}: {count} components")

        print("   Final distribution:")
        for domain, count in sorted(stats['final_distribution'].items()):
            print(f"     • {domain}: {count} components")

    print(f"\n✅ Domain reclassification completed!")

    print("\n📊 Overall Summary:")
    for filename, stats in total_stats.items():
        changes_made = sum(stats['changes'].values()) if stats['changes'] else 0
        print(f"  {filename}: {changes_made}/{stats['total']} components reclassified")


if __name__ == "__main__":
    main()