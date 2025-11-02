#!/usr/bin/env python3
"""
Comprehensive Evaluation Suite for MSc AI Dissertation

Production-grade evaluation runner with complete observability,
error handling, and crash recovery.

Usage:
    python run_comprehensive_evaluation.py [--config CONFIG_PATH] [--dry-run]

Examples:
    # Run full evaluation with default config
    python run_comprehensive_evaluation.py

    # Dry run to validate config
    python run_comprehensive_evaluation.py --dry-run

    # Use custom config
    python run_comprehensive_evaluation.py --config my_config.json
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add evaluation module to path
sys.path.append(str(Path(__file__).parent))

from evaluation import EvaluationConfig, SyllabusEvaluator


def setup_logging(log_level: str = "INFO", log_file: Path = None) -> None:
    """
    Configure structured logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    """
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )


def print_banner():
    """Print evaluation suite banner."""
    print()
    print("=" * 70)
    print("MSc AI DISSERTATION - COMPREHENSIVE EVALUATION SUITE")
    print("=" * 70)
    print()
    print("  System: CodeT5-based Educational Syllabus Generation")
    print("  Evaluation Framework: v1.0.0")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("=" * 70)
    print()


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Run comprehensive evaluation suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full evaluation
  python run_comprehensive_evaluation.py

  # Validate configuration without running
  python run_comprehensive_evaluation.py --dry-run

  # Use custom config
  python run_comprehensive_evaluation.py --config my_config.json

  # Enable debug logging
  python run_comprehensive_evaluation.py --log-level DEBUG

For more information, see: docs/evaluation-framework.md
        """,
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).parent.parent / "configs" / "evaluation_suite.json",
        help="Path to evaluation configuration JSON (default: configs/evaluation_suite.json)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration without executing tests",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging verbosity (default: INFO)",
    )

    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Optional log file path (default: None, stdout only)",
    )

    parser.add_argument(
        "--quiet", action="store_true", help="Suppress progress bars and verbose output"
    )

    return parser.parse_args()


def validate_environment():
    """
    Validate environment before running evaluation.

    Checks:
    - Python version >= 3.8
    - Required packages installed
    - CUDA availability (optional, warns if not available)

    Raises:
        RuntimeError: If environment is invalid
    """
    logger = logging.getLogger(__name__)

    # Check Python version
    if sys.version_info < (3, 8):
        raise RuntimeError(
            f"Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}"
        )

    # Check required packages
    required_packages = [
        "torch",
        "transformers",
        "pandas",
        "tqdm",
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        raise RuntimeError(
            f"Missing required packages: {', '.join(missing)}\n"
            f"Install with: pip install {' '.join(missing)}"
        )

    # Check CUDA (optional)
    try:
        import torch

        if torch.cuda.is_available():
            logger.info(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            logger.warning("⚠ CUDA not available - using CPU (will be slower)")
    except Exception:
        pass

    logger.info("✓ Environment validation passed")


def main():
    """Main entry point."""
    args = parse_arguments()

    # Setup logging
    setup_logging(log_level=args.log_level, log_file=args.log_file)

    logger = logging.getLogger(__name__)

    try:
        # Print banner
        if not args.quiet:
            print_banner()

        # Validate environment
        logger.info("Validating environment...")
        validate_environment()

        # Load configuration
        logger.info(f"Loading configuration from: {args.config}")

        if not args.config.exists():
            logger.error(f"Configuration file not found: {args.config}")
            sys.exit(1)

        config = EvaluationConfig.from_json(args.config)

        # Validate configuration
        logger.info("Validating configuration...")
        config.validate()
        logger.info("✓ Configuration valid")

        # Create evaluator
        logger.info("Initializing evaluator...")
        evaluator = SyllabusEvaluator(
            config=config, verbose=not args.quiet, dry_run=args.dry_run
        )

        # Run evaluation
        if args.dry_run:
            logger.info("DRY RUN MODE - Configuration validated successfully")
            logger.info(f"Would execute {len(config.test_cases)} tests")
            print()
            print("✓ Dry run complete - configuration is valid")
            print(f"  To run evaluation: python {Path(__file__).name}")
            sys.exit(0)

        else:
            logger.info("Starting evaluation...")
            summary = evaluator.run()

            # Print summary
            print()
            print("=" * 70)
            print("EVALUATION COMPLETE")
            print("=" * 70)
            print()
            print(f"Total tests: {summary['total_tests']}")
            print(f"Successful: {summary['successful_tests']}")
            print(f"Success rate: {summary['success_rate']:.1%}")
            print()
            print(
                f"Avg generation time: {summary['performance']['avg_generation_time_sec']:.2f}s"
            )
            print(
                f"Avg quality score: {summary['quality']['avg_overall_quality_score']:.3f}"
            )
            print()
            print(f"Results saved to: {config.output_dir}")
            print(f"  - CSV: {config.output_dir / 'evaluation_results.csv'}")
            print(f"  - Summary: {config.output_dir / 'evaluation_summary.json'}")
            print(f"  - Full outputs: {config.output_dir / 'full_outputs/'}")
            print()
            print("=" * 70)

            # Exit with appropriate code
            if summary["success_rate"] < 1.0:
                logger.warning(
                    f"Some tests failed ({summary['errors']['total_errors']} errors)"
                )
                sys.exit(1)
            else:
                logger.info("All tests passed!")
                sys.exit(0)

    except KeyboardInterrupt:
        logger.warning("\n⚠ Evaluation interrupted by user")
        print()
        print("Evaluation interrupted. Partial results may have been saved.")
        print(f"Check: {args.config.parent.parent / 'data' / 'evaluation'}")
        sys.exit(130)  # Standard Unix exit code for SIGINT

    except Exception as e:
        logger.error(f"✗ Evaluation failed: {e}", exc_info=True)
        print()
        print(f"ERROR: {e}")
        print()
        print("Check logs for details.")
        if args.log_file:
            print(f"Log file: {args.log_file}")
        sys.exit(1)


if __name__ == "__main__":
    main()
