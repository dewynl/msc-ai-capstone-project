"""
Comprehensive Evaluation Framework for MSc AI Dissertation

Production-grade evaluation infrastructure for the CodeT5-based
educational syllabus generation system.

Architecture:
- config.py: Type-safe configuration schemas
- test_suite.py: Test case generation and definitions
- evaluator.py: Core evaluation orchestration
- metrics.py: Pedagogical and technical metrics collection
- storage.py: Results persistence (CSV + JSON)
"""

__version__ = "1.0.0"
__author__ = "MSc AI Dissertation Project"

from .config import Domain, EvaluationConfig, Level, TestCaseConfig, TestType
from .evaluator import SyllabusEvaluator
from .metrics import EvaluationResult, MetricsCollector
from .storage import ResultsStorage

__all__ = [
    "EvaluationConfig",
    "TestCaseConfig",
    "Domain",
    "Level",
    "TestType",
    "SyllabusEvaluator",
    "MetricsCollector",
    "EvaluationResult",
    "ResultsStorage",
]
