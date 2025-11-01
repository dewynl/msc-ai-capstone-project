"""
Core evaluation orchestrator.

Coordinates test execution, metrics collection, and results storage.
Designed for robustness with proper error handling, progress tracking,
and crash recovery.
"""

import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from tqdm import tqdm

# Add parent to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from .config import EvaluationConfig, TestCaseConfig
from .metrics import EvaluationResult, MetricsCollector
from .storage import ResultsStorage

logger = logging.getLogger(__name__)


class SyllabusEvaluator:
    """Orchestrates comprehensive evaluation of syllabus generation system."""

    def __init__(
        self, config: EvaluationConfig, verbose: bool = True, dry_run: bool = False
    ):
        self.config = config
        self.verbose = verbose
        self.dry_run = dry_run
        self.config.validate()
        self.storage = ResultsStorage(self.config.output_dir)
        self.metrics = MetricsCollector(str(self.config.model_checkpoint))
        self.results: List[EvaluationResult] = []
        self._generator = None
        self._ranker = None
        self._rag_database = None

        logger.info("SyllabusEvaluator initialized")
        if verbose:
            print(self.config.summary())

    def run(self) -> Dict[str, Any]:
        """Execute complete evaluation suite."""
        logger.info("=" * 70)
        logger.info("STARTING EVALUATION RUN")
        logger.info("=" * 70)

        if self.dry_run:
            logger.info("DRY RUN MODE - No tests will be executed")
            return {"status": "dry_run", "tests": len(self.config.test_cases)}

        start_time = time.time()

        try:
            self._load_pipeline_components()
            self._run_test_suite()
            summary = self._generate_summary()

            elapsed = time.time() - start_time
            logger.info(f"Evaluation complete in {elapsed:.1f}s")
            logger.info(f"Results saved to: {self.config.output_dir}")

            return summary

        except KeyboardInterrupt:
            logger.warning("Evaluation interrupted by user")
            self._save_partial_results()
            raise

        except Exception as e:
            logger.error(f"Critical error during evaluation: {e}", exc_info=True)
            self._save_partial_results()
            raise RuntimeError(f"Evaluation failed: {e}")

    def _load_pipeline_components(self) -> None:
        """Initialize pipeline components (model, RAG database, ranker)."""
        logger.info("Loading pipeline components...")

        try:
            import json

            from model_inference import SyllabusGenerator
            from semantic_ranker import SemanticRanker

            logger.info(
                f"Loading RAG database from: {self.config.component_database_dir}"
            )

            with open(self.config.component_database_dir / "modules.json") as f:
                modules = json.load(f)
            with open(self.config.component_database_dir / "activities.json") as f:
                activities = json.load(f)
            with open(self.config.component_database_dir / "assessments.json") as f:
                assessments = json.load(f)

            self._rag_database = {
                "modules": modules,
                "activities": activities,
                "assessments": assessments,
            }

            logger.info(f"  Modules: {len(self._rag_database['modules'])}")
            logger.info(f"  Activities: {len(self._rag_database['activities'])}")
            logger.info(f"  Assessments: {len(self._rag_database['assessments'])}")

            logger.info(f"Loading model from: {self.config.model_checkpoint}")
            self._generator = SyllabusGenerator(
                model_path=str(self.config.model_checkpoint)
            )

            logger.info("Initializing semantic ranker...")
            self._ranker = SemanticRanker()

            logger.info("✓ All components loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load pipeline components: {e}", exc_info=True)
            raise RuntimeError(f"Component loading failed: {e}")

    def _run_test_suite(self) -> None:
        """Execute all test cases with progress tracking."""
        test_cases = self.config.test_cases
        total = len(test_cases)

        logger.info(f"Executing {total} test cases...")

        pbar = tqdm(
            test_cases,
            desc="Running tests",
            unit="test",
            disable=not self.verbose,
            ncols=100,
        )

        for i, test_case in enumerate(pbar, 1):
            try:
                if self.verbose:
                    pbar.set_description(f"Test {i}/{total}: {test_case.test_id[:30]}")

                result = self._run_single_test(test_case)
                self.results.append(result)
                self._save_result(result, test_case)

                logger.info(
                    f"[{i}/{total}] {test_case.test_id}: "
                    f"{'SUCCESS' if result.is_successful else 'FAILED'} "
                    f"(quality={result.overall_quality_score:.2f})"
                )

            except Exception as e:
                logger.error(
                    f"Test {test_case.test_id} raised exception: {e}", exc_info=True
                )
                error_result = self._create_error_result(test_case, str(e))
                self.results.append(error_result)
                self._save_result(error_result, test_case)

        logger.info(f"Test suite complete: {len(self.results)}/{total} executed")

    def _run_single_test(self, test_case: TestCaseConfig) -> EvaluationResult:
        """Execute a single test case end-to-end."""
        logger.debug(f"Starting test: {test_case.test_id}")

        self.metrics.start_timing("total_generation")

        try:
            from generate_syllabus import generate_complete_syllabus

            course_requirements = test_case.to_course_requirements()

            pipeline_output = generate_complete_syllabus(
                course_requirements=course_requirements,
                rag_database=self._rag_database,
                generator=self._generator,
                ranker=self._ranker,
            )

            self.metrics.end_timing("total_generation")

            result = self.metrics.create_result(
                test_id=test_case.test_id,
                domain=str(test_case.domain),
                level=str(test_case.level),
                course_title=test_case.course_title,
                description=test_case.description,
                pipeline_output=pipeline_output,
                full_output_path=self.config.output_dir
                / "full_outputs"
                / f"{test_case.test_id}.json",
                test_type=str(test_case.test_type),
            )

            return result

        except Exception as e:
            try:
                self.metrics.end_timing("total_generation")
            except Exception:
                pass
            logger.error(f"Test {test_case.test_id} failed: {e}")
            raise

    def _create_error_result(
        self, test_case: TestCaseConfig, error_message: str
    ) -> EvaluationResult:
        """Create evaluation result for a failed test."""
        from datetime import datetime

        return EvaluationResult(
            test_id=test_case.test_id,
            timestamp=datetime.now().isoformat(),
            domain=str(test_case.domain),
            level=str(test_case.level),
            course_title=test_case.course_title,
            description_length=len(test_case.description),
            generation_time_sec=0.0,
            model_inference_time_sec=0.0,
            parsing_time_sec=0.0,
            markdown_valid=False,
            pipeline_success=False,
            total_tokens_generated=0,
            model_checkpoint=str(self.config.model_checkpoint),
            num_modules=0,
            num_activities=0,
            num_assessments=0,
            total_components=0,
            avg_module_hours=0.0,
            has_learning_objectives=False,
            prerequisite_accuracy=0.0,
            difficulty_progression=0.0,
            topic_diversity=0.0,
            blooms_taxonomy_coverage=0.0,
            overall_quality_score=0.0,
            num_modules_available=0,
            num_modules_filtered=0,
            num_modules_ranked=0,
            semantic_ranking_time_sec=0.0,
            semantic_avg_score=0.0,
            semantic_min_score=0.0,
            semantic_max_score=0.0,
            quality_reranking_used=False,
            reranking_improved_quality=False,
            error_occurred=True,
            error_type="exception",
            warning_count=0,
            validation_issues=error_message[:500],
        )

    def _save_result(self, result: EvaluationResult, test_case: TestCaseConfig) -> None:
        """Save result to storage."""
        try:
            self.storage.save_result(result, full_output=None)
            if self.config.save_intermediate_outputs:
                pass

        except Exception as e:
            logger.error(f"Failed to save result for {test_case.test_id}: {e}")

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics and save."""
        logger.info("Generating summary statistics...")

        metadata = {
            "config": {
                "model_checkpoint": str(self.config.model_checkpoint),
                "random_seed": self.config.random_seed,
                "num_test_cases": len(self.config.test_cases),
                "quality_reranking_enabled": self.config.enable_quality_reranking,
            },
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        self.storage.save_summary(self.results, metadata=metadata)

        import json

        with open(self.storage.summary_path, "r") as f:
            return json.load(f)

    def _save_partial_results(self) -> None:
        """Save partial results when interrupted."""
        if not self.results:
            logger.warning("No results to save")
            return

        logger.info(f"Saving partial results ({len(self.results)} tests)...")
        try:
            self.storage.save_summary(
                self.results, metadata={"status": "partial", "interrupted": True}
            )
            logger.info("Partial results saved successfully")
        except Exception as e:
            logger.error(f"Failed to save partial results: {e}")
