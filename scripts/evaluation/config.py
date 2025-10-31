"""
Configuration schemas for evaluation framework.

Type-safe configuration using dataclasses and enums for compile-time safety.
Follows the principle: "Make invalid states unrepresentable."
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class Domain(str, Enum):
    """Educational domains for test stratification."""

    COMPUTER_SCIENCE = "computer_science"
    MATHEMATICS = "mathematics"
    PHYSICS = "physics"
    ENGINEERING = "engineering"
    INTERDISCIPLINARY = "interdisciplinary"  # For edge cases

    def __str__(self) -> str:
        return self.value


class Level(str, Enum):
    """Academic difficulty levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    POSTGRADUATE = "postgraduate"

    def __str__(self) -> str:
        return self.value


class TestType(str, Enum):
    """Test case categorization."""

    STANDARD = "standard"
    EDGE_CASE = "edge_case"
    STRESS_TEST = "stress_test"
    BASELINE = "baseline"

    def __str__(self) -> str:
        return self.value


@dataclass
class TestCaseConfig:
    """
    Configuration for a single test case.

    Attributes:
        test_id: Unique identifier (e.g., "test_001_cs_beginner_intro_prog")
        domain: Educational domain
        level: Difficulty level
        test_type: Category of test
        course_title: Human-readable course name
        description: Course description (input to system)
        duration: Expected course duration (semester, quarter, etc.)
        expected_modules: Expected number of modules (for validation)
        tags: Categorization tags (e.g., ["foundational", "programming"])
    """

    test_id: str
    domain: Domain
    level: Level
    test_type: TestType
    course_title: str
    description: str
    duration: str = "semester"
    expected_modules: Optional[int] = None
    tags: List[str] = field(default_factory=list)

    def to_course_requirements(self) -> Dict[str, Any]:
        """Convert to format expected by generate_syllabus pipeline."""
        return {
            "title": self.course_title,
            "domain": str(self.domain),
            "level": str(self.level),
            "duration": self.duration,
            "description": self.description,
        }

    def __str__(self) -> str:
        return f"TestCase({self.test_id}: {self.course_title})"


@dataclass
class EvaluationConfig:
    """
    Master configuration for entire evaluation run.

    Attributes:
        test_cases: List of test case configurations
        model_checkpoint: Path to trained model checkpoint
        output_dir: Directory for evaluation results
        component_database_dir: Path to RAG component database
        random_seed: For reproducibility
        enable_quality_reranking: Whether to use quality reranker
        num_quality_candidates: Number of candidates for reranking
        max_generation_time_sec: Timeout per test case
        save_intermediate_outputs: Save filtered/ranked modules
        log_level: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
    """

    test_cases: List[TestCaseConfig]
    model_checkpoint: Path
    output_dir: Path
    component_database_dir: Path
    random_seed: int = 42
    enable_quality_reranking: bool = True
    num_quality_candidates: int = 3
    max_generation_time_sec: float = 30.0
    save_intermediate_outputs: bool = False
    log_level: str = "INFO"

    @classmethod
    def from_json(cls, config_path: Path) -> "EvaluationConfig":
        """
        Load configuration from JSON file.

        Args:
            config_path: Path to JSON configuration file

        Returns:
            EvaluationConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            data = json.load(f)

        # Parse test cases
        test_cases = []
        for tc_data in data.get("test_cases", []):
            test_cases.append(
                TestCaseConfig(
                    test_id=tc_data["test_id"],
                    domain=Domain(tc_data["domain"]),
                    level=Level(tc_data["level"]),
                    test_type=TestType(tc_data.get("test_type", "standard")),
                    course_title=tc_data["course_title"],
                    description=tc_data["description"],
                    duration=tc_data.get("duration", "semester"),
                    expected_modules=tc_data.get("expected_modules"),
                    tags=tc_data.get("tags", []),
                )
            )

        return cls(
            test_cases=test_cases,
            model_checkpoint=Path(data["model_checkpoint"]),
            output_dir=Path(data["output_dir"]),
            component_database_dir=Path(data["component_database_dir"]),
            random_seed=data.get("random_seed", 42),
            enable_quality_reranking=data.get("enable_quality_reranking", True),
            num_quality_candidates=data.get("num_quality_candidates", 3),
            max_generation_time_sec=data.get("max_generation_time_sec", 30.0),
            save_intermediate_outputs=data.get("save_intermediate_outputs", False),
            log_level=data.get("log_level", "INFO"),
        )

    def validate(self) -> None:
        """
        Validate configuration before evaluation run.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.model_checkpoint.exists():
            raise ValueError(f"Model checkpoint not found: {self.model_checkpoint}")

        if not self.component_database_dir.exists():
            raise ValueError(
                f"Component database directory not found: {self.component_database_dir}"
            )

        if len(self.test_cases) == 0:
            raise ValueError("No test cases defined")

        # Check for duplicate test IDs
        test_ids = [tc.test_id for tc in self.test_cases]
        if len(test_ids) != len(set(test_ids)):
            duplicates = [tid for tid in test_ids if test_ids.count(tid) > 1]
            raise ValueError(f"Duplicate test IDs found: {duplicates}")

        if self.random_seed < 0:
            raise ValueError("Random seed must be non-negative")

        if self.max_generation_time_sec <= 0:
            raise ValueError("Max generation time must be positive")

    def get_test_case(self, test_id: str) -> Optional[TestCaseConfig]:
        """Retrieve test case by ID."""
        for tc in self.test_cases:
            if tc.test_id == test_id:
                return tc
        return None

    def get_test_cases_by_domain(self, domain: Domain) -> List[TestCaseConfig]:
        """Filter test cases by domain."""
        return [tc for tc in self.test_cases if tc.domain == domain]

    def get_test_cases_by_type(self, test_type: TestType) -> List[TestCaseConfig]:
        """Filter test cases by type."""
        return [tc for tc in self.test_cases if tc.test_type == test_type]

    def summary(self) -> str:
        """Generate human-readable summary of configuration."""
        lines = [
            "=" * 70,
            "EVALUATION CONFIGURATION SUMMARY",
            "=" * 70,
            f"Total test cases: {len(self.test_cases)}",
            f"Model checkpoint: {self.model_checkpoint}",
            f"Output directory: {self.output_dir}",
            f"Random seed: {self.random_seed}",
            f"Quality reranking: {'Enabled' if self.enable_quality_reranking else 'Disabled'}",
            "",
            "Test Distribution:",
        ]

        # Count by domain
        domain_counts = {}
        for tc in self.test_cases:
            domain_counts[tc.domain] = domain_counts.get(tc.domain, 0) + 1

        for domain, count in sorted(
            domain_counts.items(), key=lambda x: x[1], reverse=True
        ):
            lines.append(f"  {domain.value}: {count} tests")

        # Count by level
        lines.append("")
        lines.append("Difficulty Distribution:")
        level_counts = {}
        for tc in self.test_cases:
            level_counts[tc.level] = level_counts.get(tc.level, 0) + 1

        for level, count in sorted(
            level_counts.items(), key=lambda x: x[1], reverse=True
        ):
            lines.append(f"  {level.value}: {count} tests")

        # Count by type
        lines.append("")
        lines.append("Test Type Distribution:")
        type_counts = {}
        for tc in self.test_cases:
            type_counts[tc.test_type] = type_counts.get(tc.test_type, 0) + 1

        for test_type, count in sorted(
            type_counts.items(), key=lambda x: x[1], reverse=True
        ):
            lines.append(f"  {test_type.value}: {count} tests")

        lines.append("=" * 70)

        return "\n".join(lines)
