"""
Results storage for evaluation framework.

Handles persistence to CSV, JSON, and JSONL formats with atomic writes
and proper error handling.
"""

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .metrics import EvaluationResult

logger = logging.getLogger(__name__)


class ResultsStorage:
    """
    Manages persistence of evaluation results.

    Architecture:
    - CSV: Main metrics for statistical analysis
    - JSON: Full outputs for case studies
    - JSONL: Error logs (streaming format)
    - Summary JSON: Aggregated statistics

    Features:
    - Atomic writes (tmp file → rename)
    - Automatic directory creation
    - Append mode for crash recovery
    - Structured logging
    """

    # CSV column order (34 columns)
    CSV_FIELDNAMES = [
        # Metadata (6)
        "test_id",
        "timestamp",
        "domain",
        "level",
        "course_title",
        "description_length",
        # Technical Performance (7)
        "generation_time_sec",
        "model_inference_time_sec",
        "parsing_time_sec",
        "markdown_valid",
        "pipeline_success",
        "total_tokens_generated",
        "model_checkpoint",
        # Structural Metrics (6)
        "num_modules",
        "num_activities",
        "num_assessments",
        "total_components",
        "avg_module_hours",
        "has_learning_objectives",
        # Pedagogical Quality (5)
        "prerequisite_accuracy",
        "difficulty_progression",
        "topic_diversity",
        "blooms_taxonomy_coverage",
        "overall_quality_score",
        # Pipeline Components (6)
        "num_modules_available",
        "num_modules_filtered",
        "num_modules_ranked",
        "semantic_ranking_time_sec",
        "quality_reranking_used",
        "reranking_improved_quality",
        # Error Tracking (4)
        "error_occurred",
        "error_type",
        "warning_count",
        "validation_issues",
    ]

    def __init__(self, output_dir: Path):
        """
        Initialize results storage.

        Args:
            output_dir: Base directory for all evaluation outputs

        Creates directory structure:
            output_dir/
            ├── evaluation_results.csv
            ├── evaluation_summary.json
            ├── full_outputs/
            │   └── test_*.json
            └── errors.jsonl
        """
        self.output_dir = Path(output_dir)
        self.csv_path = self.output_dir / "evaluation_results.csv"
        self.summary_path = self.output_dir / "evaluation_summary.json"
        self.full_outputs_dir = self.output_dir / "full_outputs"
        self.errors_path = self.output_dir / "errors.jsonl"

        self._setup_directories()
        self._initialize_csv()

    def _setup_directories(self) -> None:
        """Create output directory structure."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.full_outputs_dir.mkdir(exist_ok=True)

        logger.info(f"Initialized storage at: {self.output_dir}")

    def _initialize_csv(self) -> None:
        """Initialize CSV file with headers if it doesn't exist."""
        if not self.csv_path.exists():
            with open(self.csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.CSV_FIELDNAMES)
                writer.writeheader()
            logger.info(f"Created CSV file: {self.csv_path}")
        else:
            logger.info(f"Using existing CSV file: {self.csv_path}")

    def save_result(
        self, result: EvaluationResult, full_output: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Save evaluation result to CSV and optionally save full output to JSON.

        Args:
            result: Evaluation result to save
            full_output: Complete pipeline output (optional, for case studies)

        Raises:
            IOError: If write fails
        """
        try:
            # Save to CSV (append mode)
            self._append_to_csv(result)

            # Save full output to JSON if provided
            if full_output is not None:
                self._save_full_output(result.test_id, full_output)

            # Log error if occurred
            if result.error_occurred:
                self._log_error(result)

            logger.info(
                f"Saved result: {result.test_id} "
                f"(success={result.is_successful}, "
                f"quality={result.overall_quality_score:.2f})"
            )

        except Exception as e:
            logger.error(f"Failed to save result {result.test_id}: {e}")
            raise

    def _append_to_csv(self, result: EvaluationResult) -> None:
        """
        Append result to CSV using atomic write.

        Args:
            result: Evaluation result

        Raises:
            IOError: If write fails
        """
        # Write to temporary file first
        tmp_path = self.csv_path.with_suffix(".csv.tmp")

        try:
            # Read existing data
            existing_rows = []
            if self.csv_path.exists():
                with open(self.csv_path, "r", newline="") as f:
                    reader = csv.DictReader(f)
                    existing_rows = list(reader)

            # Append new result
            existing_rows.append(result.to_csv_row())

            # Write all data to temp file
            with open(tmp_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.CSV_FIELDNAMES)
                writer.writeheader()
                writer.writerows(existing_rows)

            # Atomic rename
            tmp_path.replace(self.csv_path)

        except Exception as e:
            # Clean up temp file on error
            if tmp_path.exists():
                tmp_path.unlink()
            raise IOError(f"Failed to write CSV: {e}")

    def _save_full_output(self, test_id: str, full_output: Dict[str, Any]) -> None:
        """
        Save complete pipeline output to JSON file.

        Args:
            test_id: Test case identifier
            full_output: Complete pipeline output dictionary
        """
        output_path = self.full_outputs_dir / f"{test_id}.json"

        try:
            with open(output_path, "w") as f:
                json.dump(full_output, f, indent=2, default=str)

            logger.debug(f"Saved full output: {output_path}")

        except Exception as e:
            logger.warning(f"Failed to save full output for {test_id}: {e}")

    def _log_error(self, result: EvaluationResult) -> None:
        """
        Log error to JSONL file.

        JSONL format allows streaming and easy grep analysis.

        Args:
            result: Evaluation result with error
        """
        error_entry = {
            "timestamp": result.timestamp,
            "test_id": result.test_id,
            "error_type": result.error_type,
            "domain": result.domain,
            "level": result.level,
            "validation_issues": result.validation_issues,
        }

        try:
            with open(self.errors_path, "a") as f:
                f.write(json.dumps(error_entry) + "\n")

        except Exception as e:
            logger.warning(f"Failed to log error for {result.test_id}: {e}")

    def save_summary(
        self, results: List[EvaluationResult], metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Save aggregated summary statistics.

        Args:
            results: All evaluation results
            metadata: Additional metadata (config, runtime info, etc.)
        """
        if not results:
            logger.warning("No results to summarize")
            return

        summary = self._calculate_summary_stats(results)

        if metadata:
            summary["metadata"] = metadata

        try:
            with open(self.summary_path, "w") as f:
                json.dump(summary, f, indent=2, default=str)

            logger.info(f"Saved summary: {self.summary_path}")

        except Exception as e:
            logger.error(f"Failed to save summary: {e}")

    def _calculate_summary_stats(
        self, results: List[EvaluationResult]
    ) -> Dict[str, Any]:
        """
        Calculate aggregate statistics from results.

        Args:
            results: List of evaluation results

        Returns:
            Dictionary with summary statistics
        """
        total = len(results)
        successful = sum(1 for r in results if r.is_successful)

        # Aggregate technical metrics
        avg_gen_time = sum(r.generation_time_sec for r in results) / total
        avg_components = sum(r.total_components for r in results) / total

        # Aggregate quality metrics (only from successful tests)
        successful_results = [r for r in results if r.is_successful]
        if successful_results:
            avg_quality = sum(
                r.overall_quality_score for r in successful_results
            ) / len(successful_results)
            avg_prereq = sum(r.prerequisite_accuracy for r in successful_results) / len(
                successful_results
            )
        else:
            avg_quality = 0.0
            avg_prereq = 0.0

        # Count by domain
        domain_counts = {}
        for r in results:
            domain_counts[r.domain] = domain_counts.get(r.domain, 0) + 1

        # Count by level
        level_counts = {}
        for r in results:
            level_counts[r.level] = level_counts.get(r.level, 0) + 1

        # Error analysis
        error_count = sum(1 for r in results if r.error_occurred)
        error_types = {}
        for r in results:
            if r.error_occurred and r.error_type:
                error_types[r.error_type] = error_types.get(r.error_type, 0) + 1

        return {
            "generated_at": datetime.now().isoformat(),
            "total_tests": total,
            "successful_tests": successful,
            "success_rate": successful / total if total > 0 else 0.0,
            "performance": {
                "avg_generation_time_sec": round(avg_gen_time, 3),
                "avg_components_per_syllabus": round(avg_components, 1),
            },
            "quality": {
                "avg_overall_quality_score": round(avg_quality, 3),
                "avg_prerequisite_accuracy": round(avg_prereq, 3),
            },
            "distribution": {
                "by_domain": domain_counts,
                "by_level": level_counts,
            },
            "errors": {
                "total_errors": error_count,
                "error_rate": error_count / total if total > 0 else 0.0,
                "error_types": error_types,
            },
        }

    def load_results(self) -> List[EvaluationResult]:
        """
        Load all results from CSV.

        Returns:
            List of evaluation results

        Raises:
            FileNotFoundError: If CSV doesn't exist
        """
        if not self.csv_path.exists():
            raise FileNotFoundError(f"No results file found: {self.csv_path}")

        results = []

        with open(self.csv_path, "r", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Convert string values back to appropriate types
                result = EvaluationResult(
                    test_id=row["test_id"],
                    timestamp=row["timestamp"],
                    domain=row["domain"],
                    level=row["level"],
                    course_title=row["course_title"],
                    description_length=int(row["description_length"]),
                    generation_time_sec=float(row["generation_time_sec"]),
                    model_inference_time_sec=float(row["model_inference_time_sec"]),
                    parsing_time_sec=float(row["parsing_time_sec"]),
                    markdown_valid=bool(int(row["markdown_valid"])),
                    pipeline_success=bool(int(row["pipeline_success"])),
                    total_tokens_generated=int(row["total_tokens_generated"]),
                    model_checkpoint=row["model_checkpoint"],
                    num_modules=int(row["num_modules"]),
                    num_activities=int(row["num_activities"]),
                    num_assessments=int(row["num_assessments"]),
                    total_components=int(row["total_components"]),
                    avg_module_hours=float(row["avg_module_hours"]),
                    has_learning_objectives=bool(int(row["has_learning_objectives"])),
                    prerequisite_accuracy=float(row["prerequisite_accuracy"]),
                    difficulty_progression=float(row["difficulty_progression"]),
                    topic_diversity=float(row["topic_diversity"]),
                    blooms_taxonomy_coverage=float(row["blooms_taxonomy_coverage"]),
                    overall_quality_score=float(row["overall_quality_score"]),
                    num_modules_available=int(row["num_modules_available"]),
                    num_modules_filtered=int(row["num_modules_filtered"]),
                    num_modules_ranked=int(row["num_modules_ranked"]),
                    semantic_ranking_time_sec=float(row["semantic_ranking_time_sec"]),
                    quality_reranking_used=bool(int(row["quality_reranking_used"])),
                    reranking_improved_quality=bool(
                        int(row["reranking_improved_quality"])
                    ),
                    error_occurred=bool(int(row["error_occurred"])),
                    error_type=row["error_type"] if row["error_type"] else None,
                    warning_count=int(row["warning_count"]),
                    validation_issues=row["validation_issues"]
                    if row["validation_issues"]
                    else None,
                )

                results.append(result)

        logger.info(f"Loaded {len(results)} results from CSV")
        return results

    def get_result(self, test_id: str) -> Optional[EvaluationResult]:
        """
        Retrieve a specific test result by ID.

        Args:
            test_id: Test case identifier

        Returns:
            Evaluation result or None if not found
        """
        results = self.load_results()
        for result in results:
            if result.test_id == test_id:
                return result
        return None

    def load_full_output(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Load complete pipeline output for a test case.

        Args:
            test_id: Test case identifier

        Returns:
            Full output dictionary or None if not found
        """
        output_path = self.full_outputs_dir / f"{test_id}.json"

        if not output_path.exists():
            logger.warning(f"Full output not found for {test_id}")
            return None

        try:
            with open(output_path, "r") as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Failed to load full output for {test_id}: {e}")
            return None
