#!/usr/bin/env python3
"""
Comprehensive CodeT5 Model Evaluation Script

Tests the trained CodeT5 model on multiple course examples and validates:
1. Output length (should be ~800 chars, not 172 like failed T5)
2. Presence of all required function calls
3. Valid Python syntax
4. Functional correctness (code executes without errors)
"""

import json
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import torch
from transformers import RobertaTokenizer, T5ForConditionalGeneration

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.syllabus_builder import execute_function_calls

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeT5ModelEvaluator:
    """Comprehensive evaluator for trained CodeT5 model."""

    def __init__(self, model_path: str = "./models/codet5-function-call-finetuned"):
        """Initialize the evaluator with trained model."""
        self.model_path = Path(model_path)
        self.tokenizer = None
        self.model = None
        self.test_results = []
        self._load_model()

    def _load_model(self):
        """Load the trained CodeT5 model."""
        try:
            if self.model_path.exists():
                logger.info(f"📁 Loading trained model from: {self.model_path}")
                self.tokenizer = RobertaTokenizer.from_pretrained(self.model_path)
                self.model = T5ForConditionalGeneration.from_pretrained(
                    self.model_path, use_safetensors=True
                )
                logger.info("✅ Model loaded successfully")
            else:
                raise FileNotFoundError(
                    f"Model not found at {self.model_path}. "
                    "Please run training first: python scripts/codet5_function_call_trainer.py"
                )

            self.model.eval()

        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise

    def generate_function_calls(self, requirements: Dict) -> str:
        """Generate function calls for given requirements."""
        input_text = f"Generate course syllabus: {json.dumps(requirements)}"

        input_ids = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=640,
            truncation=True,
            padding=True,
        ).input_ids

        with torch.no_grad():
            generated_tokens = self.model.generate(
                input_ids,
                max_length=536,
                num_beams=4,
                early_stopping=False,
                no_repeat_ngram_size=2,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        generated_calls = self.tokenizer.decode(
            generated_tokens[0], skip_special_tokens=True
        )

        return generated_calls

    def validate_output_length(self, output: str) -> Tuple[bool, str]:
        """Check if output length is reasonable (not truncated like 172 chars)."""
        length = len(output)
        if length < 200:
            return (
                False,
                f"Output too short ({length} chars) - likely truncated/incomplete",
            )
        elif length > 1500:
            return False, f"Output too long ({length} chars) - may have repetition"
        else:
            return True, f"Output length good ({length} chars)"

    def validate_required_calls(self, output: str) -> Tuple[bool, List[str]]:
        """Check if all required function calls are present."""
        required_patterns = {
            "SyllabusBuilder": r"b\s*=\s*SyllabusBuilder\(\)",
            "set_info": r"b\.set_info\(",
            "add_objective": r"b\.add_objective\(",
            "add_module": r"b\.add_module\(",
            "add_activity": r"b\.add_activity\(",
            "add_assessment": r"b\.add_assessment\(",
            "build": r"b\.build\(\)",
        }

        missing = []
        for name, pattern in required_patterns.items():
            if not re.search(pattern, output):
                missing.append(name)

        if missing:
            return False, missing
        else:
            return True, []

    def validate_syntax(self, output: str) -> Tuple[bool, str]:
        """Check if generated code has valid Python syntax."""
        try:
            compile(output, "<string>", "exec")
            return True, "Valid Python syntax"
        except SyntaxError as e:
            return False, f"Syntax error: {e}"

    def validate_execution(self, output: str) -> Tuple[bool, str, Dict]:
        """Check if generated code executes without errors."""
        try:
            result = execute_function_calls(output)
            if not result or not isinstance(result, dict):
                return False, "Execution returned invalid result", {}

            # Check if result has expected structure
            expected_keys = ["course_info", "learning_objectives", "modules"]
            missing_keys = [key for key in expected_keys if key not in result]

            if missing_keys:
                return (
                    False,
                    f"Result missing keys: {missing_keys}",
                    result,
                )

            return True, "Execution successful", result
        except Exception as e:
            return False, f"Execution error: {e}", {}

    def run_test_case(self, test_name: str, requirements: Dict) -> Dict:
        """Run a single test case and return results."""
        logger.info(f"\n{'='*80}")
        logger.info(f"Testing: {test_name}")
        logger.info(f"{'='*80}")

        result = {
            "test_name": test_name,
            "requirements": requirements,
            "generated_output": "",
            "length_check": {"passed": False, "message": ""},
            "required_calls_check": {"passed": False, "missing": []},
            "syntax_check": {"passed": False, "message": ""},
            "execution_check": {"passed": False, "message": "", "syllabus": {}},
            "overall_pass": False,
        }

        try:
            # Generate function calls
            output = self.generate_function_calls(requirements)
            result["generated_output"] = output

            logger.info(f"\n📝 Generated Output ({len(output)} chars):")
            logger.info(output)

            # Run all validation checks
            length_pass, length_msg = self.validate_output_length(output)
            result["length_check"]["passed"] = length_pass
            result["length_check"]["message"] = length_msg
            logger.info(f"\n{'✅' if length_pass else '❌'} Length Check: {length_msg}")

            calls_pass, missing = self.validate_required_calls(output)
            result["required_calls_check"]["passed"] = calls_pass
            result["required_calls_check"]["missing"] = missing
            if calls_pass:
                logger.info("✅ Required Calls Check: All required calls present")
            else:
                logger.info(f"❌ Required Calls Check: Missing {missing}")

            syntax_pass, syntax_msg = self.validate_syntax(output)
            result["syntax_check"]["passed"] = syntax_pass
            result["syntax_check"]["message"] = syntax_msg
            logger.info(f"{'✅' if syntax_pass else '❌'} Syntax Check: {syntax_msg}")

            exec_pass, exec_msg, syllabus = self.validate_execution(output)
            result["execution_check"]["passed"] = exec_pass
            result["execution_check"]["message"] = exec_msg
            result["execution_check"]["syllabus"] = syllabus
            logger.info(f"{'✅' if exec_pass else '❌'} Execution Check: {exec_msg}")

            # Overall pass if all checks pass
            result["overall_pass"] = all(
                [length_pass, calls_pass, syntax_pass, exec_pass]
            )

            if result["overall_pass"]:
                logger.info(f"\n🎉 TEST PASSED: {test_name}")
            else:
                logger.info(f"\n❌ TEST FAILED: {test_name}")

        except Exception as e:
            logger.error(f"❌ Test failed with exception: {e}")
            result["execution_check"]["message"] = f"Exception: {e}"

        return result

    def run_evaluation_suite(self) -> Dict:
        """Run comprehensive evaluation on multiple test cases."""
        logger.info("🚀 Starting Comprehensive CodeT5 Model Evaluation")
        logger.info("=" * 80)

        # Test cases covering different difficulty levels and domains
        test_cases = [
            {
                "name": "Beginner Computer Science",
                "requirements": {
                    "title": "Introduction to Programming",
                    "domain": "computer_science",
                    "level": "beginner",
                    "duration": "semester",
                    "description": "Learn programming fundamentals using Python",
                    "learning_objectives": [
                        "Understand basic programming concepts",
                        "Write simple Python programs",
                        "Debug code effectively",
                    ],
                },
            },
            {
                "name": "Intermediate Machine Learning",
                "requirements": {
                    "title": "Machine Learning Fundamentals",
                    "domain": "computer_science",
                    "level": "intermediate",
                    "duration": "semester",
                    "description": "Introduction to machine learning algorithms",
                    "learning_objectives": [
                        "Understand supervised learning algorithms",
                        "Implement neural networks",
                        "Evaluate model performance",
                    ],
                },
            },
            {
                "name": "Advanced Data Science",
                "requirements": {
                    "title": "Advanced Data Science Techniques",
                    "domain": "data_science",
                    "level": "advanced",
                    "duration": "semester",
                    "description": "Deep learning and big data analytics",
                    "learning_objectives": [
                        "Design deep learning architectures",
                        "Process large-scale datasets",
                        "Deploy ML models in production",
                    ],
                },
            },
            {
                "name": "Business Course",
                "requirements": {
                    "title": "Digital Marketing Strategy",
                    "domain": "business",
                    "level": "intermediate",
                    "duration": "quarter",
                    "description": "Modern digital marketing techniques",
                    "learning_objectives": [
                        "Create digital marketing campaigns",
                        "Analyze marketing data",
                        "Optimize conversion rates",
                    ],
                },
            },
            {
                "name": "Quick Start Example (Production Test)",
                "requirements": {
                    "title": "Computer Science Course",
                    "domain": "computer_science",
                    "level": "intermediate",
                    "duration": "semester",
                    "description": "A comprehensive computer science course",
                },
            },
        ]

        # Run all test cases
        for test_case in test_cases:
            result = self.run_test_case(test_case["name"], test_case["requirements"])
            self.test_results.append(result)

        # Generate summary report
        return self._generate_summary_report()

    def _generate_summary_report(self) -> Dict:
        """Generate comprehensive summary report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["overall_pass"])

        report = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "detailed_results": self.test_results,
        }

        logger.info("\n" + "=" * 80)
        logger.info("📊 EVALUATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Pass Rate: {report['pass_rate']:.1f}%")
        logger.info("")

        # Detailed breakdown
        for result in self.test_results:
            status = "✅ PASS" if result["overall_pass"] else "❌ FAIL"
            logger.info(f"{status}: {result['test_name']}")
            if not result["overall_pass"]:
                if not result["length_check"]["passed"]:
                    logger.info(f"  - {result['length_check']['message']}")
                if not result["required_calls_check"]["passed"]:
                    logger.info(
                        f"  - Missing calls: {result['required_calls_check']['missing']}"
                    )
                if not result["syntax_check"]["passed"]:
                    logger.info(f"  - {result['syntax_check']['message']}")
                if not result["execution_check"]["passed"]:
                    logger.info(f"  - {result['execution_check']['message']}")

        logger.info("\n" + "=" * 80)

        if report["pass_rate"] == 100:
            logger.info("🎉 ALL TESTS PASSED! Model is ready for deployment.")
        elif report["pass_rate"] >= 80:
            logger.info(
                "⚠️  Most tests passed, but some issues remain. Review failures."
            )
        elif report["pass_rate"] >= 60:
            logger.info(
                "⚠️  Significant issues detected. Model may need more training."
            )
        else:
            logger.info("❌ Model failing most tests. More training required.")

        return report

    def save_report(self, filename: str = "codet5_evaluation_report.json"):
        """Save evaluation report to JSON file."""
        report = self._generate_summary_report()
        output_path = Path(filename)

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"\n📄 Detailed report saved to: {output_path}")
        return output_path


def main():
    """Run comprehensive model evaluation."""
    print("🚀 CodeT5 Model Evaluation Suite")
    print("=" * 80)

    try:
        # Initialize evaluator
        evaluator = CodeT5ModelEvaluator()

        # Run evaluation suite
        report = evaluator.run_evaluation_suite()

        # Save report
        evaluator.save_report()

        # Exit with appropriate code
        if report["pass_rate"] == 100:
            print("\n✅ Evaluation complete: Model ready for deployment!")
            sys.exit(0)
        elif report["pass_rate"] >= 60:
            print(
                "\n⚠️  Evaluation complete: Some issues detected, review recommended."
            )
            sys.exit(0)
        else:
            print("\n❌ Evaluation complete: Model needs more training.")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
