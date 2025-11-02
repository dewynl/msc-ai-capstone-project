"""
Metrics collection for evaluation framework.

Calculates technical performance metrics and pedagogical quality scores.
"""

import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class EvaluationResult:
    """Complete evaluation result for a single test case."""

    test_id: str
    timestamp: str
    domain: str
    level: str
    course_title: str
    description_length: int

    generation_time_sec: float
    model_inference_time_sec: float
    parsing_time_sec: float
    markdown_valid: bool
    pipeline_success: bool
    total_tokens_generated: int
    model_checkpoint: str

    num_modules: int
    num_activities: int
    num_assessments: int
    total_components: int
    avg_module_hours: float
    has_learning_objectives: bool

    prerequisite_accuracy: float
    difficulty_progression: float
    topic_diversity: float
    blooms_taxonomy_coverage: float
    overall_quality_score: float

    num_modules_available: int
    num_modules_filtered: int
    num_modules_ranked: int
    semantic_ranking_time_sec: float
    semantic_avg_score: float
    semantic_min_score: float
    semantic_max_score: float
    quality_reranking_used: bool
    reranking_improved_quality: bool

    error_occurred: bool
    error_type: Optional[str]
    warning_count: int
    validation_issues: Optional[str]

    full_output_path: Optional[str] = None
    test_type: str = "standard"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV export."""
        return asdict(self)

    def to_csv_row(self) -> Dict[str, Any]:
        """Convert to CSV row format with proper type handling."""
        data = self.to_dict()

        for key in [
            "markdown_valid",
            "pipeline_success",
            "has_learning_objectives",
            "quality_reranking_used",
            "reranking_improved_quality",
            "error_occurred",
        ]:
            data[key] = int(data[key])

        if data["error_type"] is None:
            data["error_type"] = ""
        if data["validation_issues"] is None:
            data["validation_issues"] = ""

        data.pop("full_output_path", None)
        data.pop("test_type", None)

        return data

    @property
    def is_successful(self) -> bool:
        """Check if test case passed all validation."""
        return self.pipeline_success and not self.error_occurred

    @property
    def quality_label(self) -> str:
        """Human-readable quality assessment."""
        if self.overall_quality_score >= 0.8:
            return "Excellent"
        elif self.overall_quality_score >= 0.6:
            return "Good"
        elif self.overall_quality_score >= 0.4:
            return "Acceptable"
        else:
            return "Poor"


class MetricsCollector:
    """Collects and calculates evaluation metrics."""

    def __init__(self, model_checkpoint: str):
        self.model_checkpoint = model_checkpoint
        self.start_time: Optional[float] = None
        self.timings: Dict[str, float] = {}

    def start_timing(self, label: str) -> None:
        """Start timing a specific operation."""
        self.timings[f"{label}_start"] = time.time()

    def end_timing(self, label: str) -> float:
        """End timing and return duration in seconds."""
        start_key = f"{label}_start"
        if start_key not in self.timings:
            raise ValueError(f"No start time recorded for '{label}'")

        duration = time.time() - self.timings[start_key]
        self.timings[label] = duration
        return duration

    def create_result(
        self,
        test_id: str,
        domain: str,
        level: str,
        course_title: str,
        description: str,
        pipeline_output: Dict[str, Any],
        full_output_path: Optional[Path] = None,
        test_type: str = "standard",
    ) -> EvaluationResult:
        """Create evaluation result from pipeline output."""
        success = pipeline_output.get("success", False)
        syllabus = pipeline_output.get("json", {})
        quality_metrics = pipeline_output.get("quality_metrics", {})

        metadata = pipeline_output.get("metadata", {})
        filter_stats = metadata.get("filter_stats", {})
        ranking_stats = metadata.get("ranking_stats", {})
        ranked_modules = metadata.get("ranked_modules", [])

        error_info = pipeline_output.get("error", None)
        warnings = pipeline_output.get("warnings", [])

        generation_time = self.timings.get("total_generation", 0.0)
        model_inference_time = 0.0
        parsing_time = 0.0

        module_uuids = syllabus.get("modules", [])
        activity_uuids = syllabus.get("activities", [])
        assessment_uuids = syllabus.get("assessments", [])

        num_modules = len(module_uuids)
        num_activities = len(activity_uuids)
        num_assessments = len(assessment_uuids)

        selected_modules = [m for m in ranked_modules if m.get("id") in module_uuids]
        if selected_modules:
            total_hours = sum(m.get("estimated_hours", 0) for m in selected_modules)
            avg_module_hours = total_hours / len(selected_modules)
        else:
            avg_module_hours = 0.0

        has_learning_objectives = bool(syllabus.get("learning_objectives"))

        prerequisite_accuracy = quality_metrics.get("prerequisite_accuracy", 0.0)
        difficulty_progression = quality_metrics.get("difficulty_loss", 0.0)
        difficulty_progression = max(0.0, 1.0 - difficulty_progression)
        topic_diversity = quality_metrics.get("coverage_loss", 1.0)
        topic_diversity = max(0.0, 1.0 - topic_diversity)

        blooms_coverage = self._calculate_blooms_coverage(selected_modules)
        overall_quality_score = quality_metrics.get("overall_quality_score", 0.0)

        num_modules_available = filter_stats.get("total_components", 0)
        num_modules_filtered = filter_stats.get("filtered_components", 0)
        num_modules_ranked = ranking_stats.get("modules", {}).get("output_count", 0)
        semantic_ranking_time = ranking_stats.get("ranking_time_sec", 0.0)

        modules_stats = ranking_stats.get("modules", {})
        semantic_avg_score = modules_stats.get("avg_score", 0.0)
        semantic_min_score = modules_stats.get("min_score", 0.0)
        semantic_max_score = modules_stats.get("max_score", 0.0)

        quality_reranking_used = quality_metrics.get("candidates_evaluated", 0) > 0
        reranking_improved = quality_metrics.get("quality_improved", False)

        error_occurred = error_info is not None
        error_type = self._categorize_error(error_info) if error_occurred else None
        warning_count = len(warnings)
        validation_issues = "; ".join(warnings[:3]) if warnings else None

        markdown_valid = pipeline_output.get("markdown_valid", False)

        generated_markdown = pipeline_output.get("generated_markdown", "")
        total_tokens = len(generated_markdown.split())

        return EvaluationResult(
            test_id=test_id,
            timestamp=datetime.now().isoformat(),
            domain=domain,
            level=level,
            course_title=course_title,
            description_length=len(description),
            generation_time_sec=round(generation_time, 3),
            model_inference_time_sec=round(model_inference_time, 3),
            parsing_time_sec=round(parsing_time, 3),
            markdown_valid=markdown_valid,
            pipeline_success=success,
            total_tokens_generated=total_tokens,
            model_checkpoint=str(self.model_checkpoint),
            num_modules=num_modules,
            num_activities=num_activities,
            num_assessments=num_assessments,
            total_components=num_modules + num_activities + num_assessments,
            avg_module_hours=round(avg_module_hours, 1),
            has_learning_objectives=has_learning_objectives,
            prerequisite_accuracy=round(prerequisite_accuracy, 3),
            difficulty_progression=round(difficulty_progression, 3),
            topic_diversity=round(topic_diversity, 3),
            blooms_taxonomy_coverage=round(blooms_coverage, 3),
            overall_quality_score=round(overall_quality_score, 3),
            num_modules_available=num_modules_available,
            num_modules_filtered=num_modules_filtered,
            num_modules_ranked=num_modules_ranked,
            semantic_ranking_time_sec=round(semantic_ranking_time, 3),
            semantic_avg_score=round(semantic_avg_score, 3),
            semantic_min_score=round(semantic_min_score, 3),
            semantic_max_score=round(semantic_max_score, 3),
            quality_reranking_used=quality_reranking_used,
            reranking_improved_quality=reranking_improved,
            error_occurred=error_occurred,
            error_type=error_type,
            warning_count=warning_count,
            validation_issues=validation_issues,
            full_output_path=str(full_output_path) if full_output_path else None,
            test_type=test_type,
        )

    def _calculate_blooms_coverage(self, modules: List[Dict[str, Any]]) -> float:
        """Calculate Bloom's taxonomy coverage score (0.0-1.0)."""
        blooms_levels = {
            "remember",
            "understand",
            "apply",
            "analyze",
            "evaluate",
            "create",
        }

        found_levels = set()

        for module in modules:
            objectives = module.get("learning_objectives", [])
            for obj in objectives:
                obj_lower = str(obj).lower()
                for level in blooms_levels:
                    if level in obj_lower:
                        found_levels.add(level)

        return len(found_levels) / len(blooms_levels)

    def _categorize_error(self, error_info: Any) -> str:
        """Categorize error type for analysis."""
        if error_info is None:
            return "none"

        error_str = str(error_info).lower()

        if "timeout" in error_str:
            return "timeout"
        elif "parse" in error_str or "parsing" in error_str:
            return "parsing_failed"
        elif "model" in error_str or "inference" in error_str:
            return "model_error"
        elif "memory" in error_str or "oom" in error_str:
            return "out_of_memory"
        elif "file" in error_str or "not found" in error_str:
            return "file_error"
        else:
            return "unknown_error"
