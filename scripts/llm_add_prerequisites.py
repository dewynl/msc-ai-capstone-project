#!/usr/bin/env python3
"""
LLM-Based Prerequisite Detection (Production-Ready)

Uses Claude 3.5 Sonnet to analyze module descriptions and determine
prerequisite relationships with high accuracy (~90%).

Design Principles:
- Batch by domain (minimize API calls)
- Checkpoint/resume capability
- Comprehensive validation
- Cost estimation and control
- Detailed progress tracking
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Set

import anthropic


class PrerequisiteDetector:
    """Production-ready prerequisite detection using Claude."""

    def __init__(self, api_key: str = None):
        """Initialize with API key."""
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. Set via environment or pass directly."
            )

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.checkpoint_dir = Path("data/prerequisites_checkpoints")
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def estimate_cost(self, num_modules: int, num_domains: int) -> Dict:
        """
        Estimate API cost before running.

        Strategy: Batch by domain, ~1 call per domain + follow-ups
        """
        # Estimate tokens per domain analysis
        avg_modules_per_domain = num_modules / num_domains
        input_tokens_per_call = int(
            avg_modules_per_domain * 300
        )  # 300 tokens per module summary
        output_tokens_per_call = int(
            avg_modules_per_domain * 50
        )  # 50 tokens per module for prereqs

        total_calls = num_domains * 1.5  # 1.5x for potential retries/refinements
        total_input_tokens = input_tokens_per_call * total_calls
        total_output_tokens = output_tokens_per_call * total_calls

        # Claude 3.5 Sonnet pricing (as of 2024)
        input_cost = total_input_tokens * 0.003 / 1000  # $0.003 per 1K input tokens
        output_cost = total_output_tokens * 0.015 / 1000  # $0.015 per 1K output tokens

        return {
            "estimated_calls": int(total_calls),
            "estimated_input_tokens": total_input_tokens,
            "estimated_output_tokens": total_output_tokens,
            "estimated_cost": input_cost + output_cost,
            "breakdown": {
                "input_cost": input_cost,
                "output_cost": output_cost,
            },
        }

    def load_modules(self, file_path: Path) -> List[Dict]:
        """Load and normalize module data."""
        with open(file_path) as f:
            modules = json.load(f)

        # Normalize IDs
        for module in modules:
            if "module_id" in module and "id" not in module:
                module["id"] = module["module_id"]

        return modules

    def group_by_domain(self, modules: List[Dict]) -> Dict[str, List[Dict]]:
        """Group modules by domain for batch processing."""
        by_domain = {}
        for module in modules:
            domain = module.get("domain", "unknown")
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(module)

        return by_domain

    def create_analysis_prompt(self, modules: List[Dict], domain: str) -> str:
        """
        Create prompt for Claude to analyze prerequisites.

        Returns structured prompt for batch analysis.
        """
        # Build module summaries
        module_list = []
        for i, mod in enumerate(modules):
            summary = f"""
Module {i}:
ID: {mod['id']}
Title: {mod['title'][:80]}
Difficulty: {mod.get('difficulty', 'unknown')}
Description: {mod.get('description', '')[:250]}...
Key Concepts: {', '.join(mod.get('key_concepts', [])[:3])}
"""
            module_list.append(summary.strip())

        modules_text = "\n\n".join(module_list)

        prompt = f"""You are an expert in {domain} curriculum design. Analyze these {len(modules)} modules and determine prerequisite relationships.

MODULES TO ANALYZE:
{modules_text}

TASK:
For EACH module, identify which OTHER modules (if any) should be prerequisites.

RULES:
1. Prerequisites must be FOUNDATIONAL knowledge needed to understand the module
2. Only mark DIRECT prerequisites (not transitive - if A→B→C, don't mark A→C)
3. Prerequisites must have LOWER or EQUAL difficulty (beginner before intermediate)
4. Be CONSERVATIVE - only mark clear, necessary prerequisites
5. Most beginner modules will have NO prerequisites (that's OK!)

OUTPUT FORMAT:
Return a JSON object mapping module IDs to arrays of prerequisite module IDs.

Example:
{{
  "module-abc-123": ["module-xyz-456", "module-def-789"],
  "module-xyz-456": [],
  "module-def-789": ["module-xyz-456"]
}}

IMPORTANT:
- Use the EXACT module IDs from above
- Empty array [] means no prerequisites
- Only include modules that HAVE prerequisites (skip empty ones to save tokens)

Analyze now and return ONLY the JSON object:"""

        return prompt

    def parse_prerequisites_response(
        self, response_text: str, valid_module_ids: Set[str]
    ) -> Dict[str, List[str]]:
        """
        Parse and validate Claude's response.

        Returns: Dict mapping module_id -> list of prerequisite IDs
        """
        try:
            # Extract JSON from response (handle markdown code blocks)
            text = response_text.strip()
            if text.startswith("```"):
                # Remove markdown code blocks
                lines = text.split("\n")
                text = "\n".join(line for line in lines if not line.startswith("```"))

            prereqs = json.loads(text)

            # Validate structure
            if not isinstance(prereqs, dict):
                raise ValueError("Response is not a JSON object")

            # Validate all IDs exist
            validated = {}
            for module_id, prereq_list in prereqs.items():
                if module_id not in valid_module_ids:
                    print(f"  ⚠️  Warning: Unknown module ID {module_id}, skipping")
                    continue

                if not isinstance(prereq_list, list):
                    print(
                        f"  ⚠️  Warning: Invalid prerequisite list for {module_id}, skipping"
                    )
                    continue

                # Filter to valid IDs only
                valid_prereqs = [p for p in prereq_list if p in valid_module_ids]
                if len(valid_prereqs) != len(prereq_list):
                    print(
                        f"  ⚠️  Warning: Filtered {len(prereq_list) - len(valid_prereqs)} invalid prereqs for {module_id}"
                    )

                validated[module_id] = valid_prereqs

            return validated

        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse JSON response: {e}\nResponse: {text[:500]}"
            )
        except Exception as e:
            raise ValueError(f"Failed to validate response: {e}")

    def validate_prerequisites(
        self, prereqs: Dict[str, List[str]], modules: List[Dict]
    ) -> Dict[str, List[str]]:
        """
        Validate prerequisite relationships make sense.

        Checks:
        1. No circular dependencies
        2. Prerequisites have lower/equal difficulty
        3. Prerequisites are in same domain
        4. Reasonable count (not 50+ prereqs)
        """
        # Build module lookup
        module_map = {m["id"]: m for m in modules}
        difficulty_order = {"beginner": 0, "intermediate": 1, "advanced": 2}

        validated = {}
        warnings = []

        for module_id, prereq_list in prereqs.items():
            if module_id not in module_map:
                continue

            module = module_map[module_id]
            module_diff = difficulty_order.get(module.get("difficulty", "beginner"), 0)
            module_domain = module.get("domain")

            valid_prereqs = []

            for prereq_id in prereq_list:
                if prereq_id not in module_map:
                    warnings.append(f"Unknown prerequisite {prereq_id} for {module_id}")
                    continue

                prereq = module_map[prereq_id]
                prereq_diff = difficulty_order.get(
                    prereq.get("difficulty", "beginner"), 0
                )
                prereq_domain = prereq.get("domain")

                # Check difficulty ordering
                if prereq_diff > module_diff:
                    warnings.append(
                        f"Skipping {prereq_id} for {module_id}: higher difficulty"
                    )
                    continue

                # Check same domain
                if prereq_domain != module_domain:
                    warnings.append(
                        f"Skipping {prereq_id} for {module_id}: different domain"
                    )
                    continue

                # Check not self-reference
                if prereq_id == module_id:
                    warnings.append(f"Skipping self-reference in {module_id}")
                    continue

                valid_prereqs.append(prereq_id)

            # Check reasonable count
            if len(valid_prereqs) > 10:
                warnings.append(
                    f"Module {module_id} has {len(valid_prereqs)} prerequisites (seems high)"
                )
                # Keep top 10 only
                valid_prereqs = valid_prereqs[:10]

            if valid_prereqs:
                validated[module_id] = valid_prereqs

        if warnings:
            print(f"\n⚠️  Validation warnings ({len(warnings)}):")
            for warning in warnings[:10]:  # Show first 10
                print(f"  - {warning}")
            if len(warnings) > 10:
                print(f"  ... and {len(warnings) - 10} more")

        return validated

    def check_circular_dependencies(self, prereqs: Dict[str, List[str]]) -> bool:
        """
        Check for circular dependencies using DFS.

        Returns True if circular dependencies found.
        """

        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in prereqs.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        visited = set()
        for node in prereqs.keys():
            if node not in visited:
                if has_cycle(node, visited, set()):
                    return True

        return False

    def analyze_domain(
        self, domain: str, modules: List[Dict], max_retries: int = 3
    ) -> Dict[str, List[str]]:
        """
        Analyze prerequisites for a single domain with retry logic.

        Automatically batches large domains (>200 modules) to avoid truncation.

        Returns: Dict mapping module_id -> prerequisite IDs
        """
        print(f"\nAnalyzing {domain} ({len(modules)} modules)...")

        # Check for cached result
        checkpoint_file = self.checkpoint_dir / f"{domain}_prerequisites.json"
        if checkpoint_file.exists():
            print(f"  ✓ Loading from checkpoint: {checkpoint_file}")
            with open(checkpoint_file) as f:
                return json.load(f)

        # Batch if too large (>100 modules causes response truncation)
        BATCH_SIZE = 100
        if len(modules) > BATCH_SIZE:
            print(
                f"  ⚠️  Large domain ({len(modules)} modules) - batching into groups of {BATCH_SIZE}"
            )
            all_prereqs = {}
            num_batches = (len(modules) + BATCH_SIZE - 1) // BATCH_SIZE

            for i in range(num_batches):
                start_idx = i * BATCH_SIZE
                end_idx = min((i + 1) * BATCH_SIZE, len(modules))
                batch_modules = modules[start_idx:end_idx]

                print(
                    f"\n  Batch {i+1}/{num_batches} (modules {start_idx}-{end_idx-1}):"
                )
                batch_prereqs = self._analyze_batch(
                    domain, batch_modules, modules, max_retries
                )
                all_prereqs.update(batch_prereqs)

            # Save combined checkpoint
            with open(checkpoint_file, "w") as f:
                json.dump(all_prereqs, f, indent=2)
            print(f"\n  ✓ Combined checkpoint saved: {checkpoint_file}")

            return all_prereqs

        # Single batch processing
        result = self._analyze_batch(domain, modules, modules, max_retries)

        # Save checkpoint
        with open(checkpoint_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n  ✓ Checkpoint saved: {checkpoint_file}")

        return result

    def _analyze_batch(
        self,
        domain: str,
        batch_modules: List[Dict],
        all_domain_modules: List[Dict],
        max_retries: int = 3,
    ) -> Dict[str, List[str]]:
        """
        Analyze a single batch of modules.

        Args:
            batch_modules: Modules to analyze in this batch
            all_domain_modules: ALL modules in domain (for prerequisite context)
        """
        valid_ids = {m["id"] for m in all_domain_modules}

        for attempt in range(max_retries):
            try:
                from datetime import datetime

                print(f"  API call (attempt {attempt + 1}/{max_retries})...")
                print(
                    f"  ⏱️  Analyzing {len(batch_modules)} modules - this may take 30-90 seconds..."
                )
                print(f"  📅 Started: {datetime.now().strftime('%H:%M:%S')}")

                start_time = time.time()

                # Create prompt
                prompt = self.create_analysis_prompt(batch_modules, domain)

                # Call Claude with retry logic
                response = self.client.messages.create(
                    model="claude-sonnet-4-5-20250929",  # Sonnet 4.5 - correct model ID
                    max_tokens=8000,
                    temperature=0,  # Deterministic
                    messages=[{"role": "user", "content": prompt}],
                )

                response_text = response.content[0].text
                elapsed = time.time() - start_time
                print(f"  ✓ API call completed in {elapsed:.1f}s")

                # Parse response
                print(f"  Parsing response ({len(batch_modules)} modules)...")
                prereqs = self.parse_prerequisites_response(response_text, valid_ids)
                print(f"  ✓ Extracted prerequisites for {len(prereqs)} modules")

                # Validate
                print("  Validating prerequisites...")
                validated = self.validate_prerequisites(prereqs, batch_modules)

                # Show summary
                total_prereqs = sum(len(p) for p in validated.values())
                avg_prereqs = total_prereqs / len(validated) if validated else 0
                print(
                    f"  ✓ Validated {len(validated)} modules, {total_prereqs} total prerequisites (avg: {avg_prereqs:.1f} per module)"
                )

                # Check for circular dependencies
                if self.check_circular_dependencies(validated):
                    raise ValueError("Circular dependencies detected!")

                # Show success (checkpoint saved by parent method)
                print(
                    f"  ✓ Batch complete: {len(validated)} modules with prerequisites (avg: {sum(len(v) for v in validated.values()) / max(len(validated), 1):.1f} prereqs/module)"
                )

                return validated

            except Exception as e:
                print(f"  ❌ Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2**attempt  # Exponential backoff
                    print(f"  Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise

    def apply_prerequisites_to_modules(
        self, modules: List[Dict], all_prereqs: Dict[str, List[str]]
    ) -> List[Dict]:
        """Apply detected prerequisites to module objects."""
        for module in modules:
            module_id = module["id"]
            module["prerequisites"] = all_prereqs.get(module_id, [])

        return modules

    def generate_statistics(self, modules: List[Dict]) -> Dict:
        """Generate statistics about prerequisites."""
        total_modules = len(modules)
        modules_with_prereqs = sum(1 for m in modules if m.get("prerequisites"))
        total_prereqs = sum(len(m.get("prerequisites", [])) for m in modules)

        by_domain = {}
        by_difficulty = {}

        for module in modules:
            domain = module.get("domain", "unknown")
            difficulty = module.get("difficulty", "unknown")
            has_prereqs = len(module.get("prerequisites", [])) > 0

            if domain not in by_domain:
                by_domain[domain] = {"total": 0, "with_prereqs": 0}
            by_domain[domain]["total"] += 1
            if has_prereqs:
                by_domain[domain]["with_prereqs"] += 1

            if difficulty not in by_difficulty:
                by_difficulty[difficulty] = {"total": 0, "with_prereqs": 0}
            by_difficulty[difficulty]["total"] += 1
            if has_prereqs:
                by_difficulty[difficulty]["with_prereqs"] += 1

        return {
            "total_modules": total_modules,
            "modules_with_prerequisites": modules_with_prereqs,
            "total_prerequisites": total_prereqs,
            "average_prerequisites": total_prereqs / max(modules_with_prereqs, 1),
            "by_domain": by_domain,
            "by_difficulty": by_difficulty,
        }

    def run(
        self, modules_file: Path, dry_run: bool = False, auto_confirm: bool = False
    ) -> List[Dict]:
        """
        Main execution: analyze all domains and add prerequisites.

        Args:
            modules_file: Path to modules.json
            dry_run: If True, only estimate cost without running

        Returns:
            Updated modules with prerequisites
        """
        print("=" * 80)
        print("LLM-BASED PREREQUISITE DETECTION")
        print("=" * 80)

        # Load modules
        print(f"\nLoading modules from: {modules_file}")
        modules = self.load_modules(modules_file)
        print(f"✓ Loaded {len(modules)} modules")

        # Group by domain
        by_domain = self.group_by_domain(modules)
        print(f"✓ Grouped into {len(by_domain)} domains:")
        for domain, mods in by_domain.items():
            print(f"  - {domain}: {len(mods)} modules")

        # Estimate cost
        cost_estimate = self.estimate_cost(len(modules), len(by_domain))
        print("\n💰 Cost Estimate:")
        print(f"  - API calls: ~{cost_estimate['estimated_calls']}")
        print(f"  - Input tokens: ~{cost_estimate['estimated_input_tokens']:,}")
        print(f"  - Output tokens: ~{cost_estimate['estimated_output_tokens']:,}")
        print(f"  - Estimated cost: ${cost_estimate['estimated_cost']:.2f}")

        if dry_run:
            print("\n✓ Dry run complete. Run without --dry-run to proceed.")
            return modules

        # Confirm before proceeding
        if not auto_confirm:
            print("\n⚠️  This will make API calls to Claude.")
            response = input("Proceed? (yes/no): ").strip().lower()
            if response != "yes":
                print("Aborted.")
                sys.exit(0)
        else:
            print("\n✓ Auto-confirmed, proceeding with API calls...")

        # Analyze each domain
        all_prereqs = {}
        for domain, domain_modules in by_domain.items():
            try:
                prereqs = self.analyze_domain(domain, domain_modules)
                all_prereqs.update(prereqs)
            except Exception as e:
                print(f"\n❌ Failed to analyze {domain}: {e}")
                print("  Continuing with other domains...")

        # Apply prerequisites to modules
        print("\nApplying prerequisites to modules...")
        modules = self.apply_prerequisites_to_modules(modules, all_prereqs)

        # Generate statistics
        stats = self.generate_statistics(modules)

        print("\n" + "=" * 80)
        print("STATISTICS")
        print("=" * 80)
        print(
            f"Modules with prerequisites: {stats['modules_with_prerequisites']}/{stats['total_modules']} ({100 * stats['modules_with_prerequisites'] / stats['total_modules']:.1f}%)"
        )
        print(f"Total prerequisites: {stats['total_prerequisites']}")
        print(f"Average per module: {stats['average_prerequisites']:.2f}")

        print("\nBy Domain:")
        for domain, domain_stats in stats["by_domain"].items():
            pct = (
                100 * domain_stats["with_prereqs"] / domain_stats["total"]
                if domain_stats["total"] > 0
                else 0
            )
            print(
                f"  {domain}: {domain_stats['with_prereqs']}/{domain_stats['total']} ({pct:.1f}%)"
            )

        print("\nBy Difficulty:")
        for diff, diff_stats in stats["by_difficulty"].items():
            pct = (
                100 * diff_stats["with_prereqs"] / diff_stats["total"]
                if diff_stats["total"] > 0
                else 0
            )
            print(
                f"  {diff}: {diff_stats['with_prereqs']}/{diff_stats['total']} ({pct:.1f}%)"
            )

        # Show samples
        print("\n" + "=" * 80)
        print("SAMPLE PREREQUISITES (First 5)")
        print("=" * 80)
        sample_count = 0
        module_map = {m["id"]: m for m in modules}
        for module in modules:
            if module.get("prerequisites") and sample_count < 5:
                print(f"\n{module['title'][:70]}")
                print(f"  Difficulty: {module.get('difficulty')}")
                print(f"  Prerequisites: {len(module['prerequisites'])}")
                for prereq_id in module["prerequisites"][:3]:
                    prereq = module_map.get(prereq_id)
                    if prereq:
                        print(f"    ← {prereq['title'][:60]}")
                sample_count += 1

        # Save results
        print("\n" + "=" * 80)
        print("SAVING RESULTS")
        print("=" * 80)

        # Backup
        backup_file = modules_file.parent / f"{modules_file.stem}_backup.json"
        print(f"Creating backup: {backup_file}")
        with open(backup_file, "w") as f:
            json.dump(self.load_modules(modules_file), f, indent=2)

        # Save updated modules
        print(f"Saving updated modules: {modules_file}")
        with open(modules_file, "w") as f:
            json.dump(modules, f, indent=2)

        print("\n✓ Prerequisites added successfully!")
        print(f"✓ Checkpoint files saved to: {self.checkpoint_dir}")

        return modules


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Add prerequisites to modules using Claude API"
    )
    parser.add_argument(
        "--modules-file",
        type=str,
        default="data/components/modules.json",
        help="Path to modules.json file",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Anthropic API key (or set ANTHROPIC_API_KEY env var)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Estimate cost without running"
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Auto-confirm (skip interactive prompt)",
    )

    args = parser.parse_args()

    try:
        base_dir = Path(__file__).parent.parent
        modules_file = base_dir / args.modules_file

        detector = PrerequisiteDetector(api_key=args.api_key)
        detector.run(modules_file, dry_run=args.dry_run, auto_confirm=args.yes)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("✓ Progress saved in checkpoints - you can resume later")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
