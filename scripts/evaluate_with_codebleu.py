#!/usr/bin/env python3
"""
CodeBLEU Evaluation for Generated Function Calls

CodeBLEU is a code-specific metric that measures:
1. N-gram match (BLEU)
2. Weighted n-gram match
3. Syntax match (AST-based)
4. Dataflow match

This provides better evaluation than standard BLEU for code generation.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List

import torch
from transformers import RobertaTokenizer, T5ForConditionalGeneration

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeBLEUEvaluator:
    """Evaluate CodeT5 model using CodeBLEU metrics."""

    def __init__(self, model_path: str = "./models/codet5-function-call-finetuned"):
        """Initialize evaluator with trained model."""
        self.model_path = Path(model_path)
        self.tokenizer = None
        self.model = None
        self.codebleu_available = False
        self._load_model()
        self._check_codebleu()

    def _load_model(self):
        """Load trained CodeT5 model."""
        try:
            if self.model_path.exists():
                logger.info(f"📁 Loading model from: {self.model_path}")
                self.tokenizer = RobertaTokenizer.from_pretrained(self.model_path)
                self.model = T5ForConditionalGeneration.from_pretrained(
                    self.model_path, use_safetensors=True
                )
                self.model.eval()
                logger.info("✅ Model loaded")
            else:
                raise FileNotFoundError(f"Model not found at {self.model_path}")
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise

    def _check_codebleu(self):
        """Check if CodeBLEU is installed."""
        try:
            import codebleu  # noqa: F401

            self.codebleu_available = True
            logger.info("✅ CodeBLEU package available")
        except ImportError:
            logger.warning(
                "⚠️  CodeBLEU not installed. Install with: pip install codebleu"
            )
            self.codebleu_available = False

    def generate_code(self, requirements: Dict) -> str:
        """Generate function calls from requirements."""
        input_text = f"Generate course syllabus: {json.dumps(requirements)}"

        input_ids = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=640,
            truncation=True,
            padding=True,
        ).input_ids

        with torch.no_grad():
            output = self.model.generate(
                input_ids,
                max_length=536,
                num_beams=4,
                early_stopping=False,
                no_repeat_ngram_size=2,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        return self.tokenizer.decode(output[0], skip_special_tokens=True)

    def calculate_codebleu(
        self, predictions: List[str], references: List[List[str]], lang: str = "python"
    ) -> Dict:
        """
        Calculate CodeBLEU score.

        Args:
            predictions: List of generated code strings
            references: List of reference code lists (multiple refs per prediction)
            lang: Programming language (default: python)

        Returns:
            Dictionary with CodeBLEU scores
        """
        if not self.codebleu_available:
            logger.error("CodeBLEU not available. Install with: pip install codebleu")
            return {}

        try:
            from codebleu import calc_codebleu

            result = calc_codebleu(
                references=references,
                predictions=predictions,
                lang=lang,
                weights=(0.25, 0.25, 0.25, 0.25),  # Equal weights for all components
            )

            return {
                "codebleu": result["codebleu"],
                "ngram_match_score": result["ngram_match_score"],
                "weighted_ngram_match_score": result["weighted_ngram_match_score"],
                "syntax_match_score": result["syntax_match_score"],
                "dataflow_match_score": result["dataflow_match_score"],
            }

        except Exception as e:
            logger.error(f"CodeBLEU calculation failed: {e}")
            return {}

    def load_training_data(
        self, data_path: str = "data/training/rag_enhanced_t5_training.json"
    ) -> List[Dict]:
        """Load training data for reference comparisons."""
        try:
            with open(data_path, "r") as f:
                data = json.load(f)
            logger.info(f"✅ Loaded {len(data)} training examples")
            return data
        except Exception as e:
            logger.error(f"Failed to load training data: {e}")
            return []

    def evaluate_on_test_set(
        self,
        test_size: int = 20,
        data_path: str = "data/training/rag_enhanced_t5_training.json",
    ) -> Dict:
        """
        Evaluate model on test examples using CodeBLEU.

        Args:
            test_size: Number of examples to test
            data_path: Path to training data

        Returns:
            Evaluation results with CodeBLEU scores
        """
        logger.info("🚀 Starting CodeBLEU Evaluation")
        logger.info("=" * 80)

        if not self.codebleu_available:
            logger.error("❌ CodeBLEU not available. Install with: pip install codebleu")
            return {}

        # Load training data
        data = self.load_training_data(data_path)
        if not data:
            logger.error("No training data available")
            return {}

        # Use last N examples as test set (not seen during early epochs)
        test_data = data[-test_size:]
        logger.info(f"📊 Testing on {len(test_data)} examples")

        predictions = []
        references = []

        for i, example in enumerate(test_data):
            logger.info(f"\nProcessing example {i+1}/{len(test_data)}...")

            # Parse input
            try:
                if isinstance(example["input"], str):
                    requirements = json.loads(
                        example["input"].replace("Generate course syllabus: ", "")
                    )
                else:
                    requirements = example["input"]
            except Exception as e:
                logger.warning(f"Failed to parse input: {e}")
                continue

            # Generate prediction
            try:
                generated = self.generate_code(requirements)
                predictions.append(generated)

                # Reference from training data
                reference = example["output"]
                references.append([reference])  # CodeBLEU expects list of lists

                logger.info(f"✅ Generated {len(generated)} chars")

            except Exception as e:
                logger.error(f"Generation failed: {e}")
                continue

        if not predictions:
            logger.error("No predictions generated")
            return {}

        # Calculate CodeBLEU
        logger.info("\n" + "=" * 80)
        logger.info("📈 Calculating CodeBLEU Scores...")
        logger.info("=" * 80)

        scores = self.calculate_codebleu(predictions, references, lang="python")

        if scores:
            logger.info("\n📊 CodeBLEU Results:")
            logger.info("=" * 80)
            logger.info(f"Overall CodeBLEU Score: {scores['codebleu']:.4f}")
            logger.info(f"  - N-gram Match:        {scores['ngram_match_score']:.4f}")
            logger.info(
                f"  - Weighted N-gram:     {scores['weighted_ngram_match_score']:.4f}"
            )
            logger.info(f"  - Syntax Match (AST):  {scores['syntax_match_score']:.4f}")
            logger.info(
                f"  - Dataflow Match:      {scores['dataflow_match_score']:.4f}"
            )
            logger.info("=" * 80)

            # Interpret scores
            codebleu_score = scores["codebleu"]
            if codebleu_score >= 0.75:
                logger.info("🎉 Excellent! Model generates high-quality code.")
            elif codebleu_score >= 0.60:
                logger.info("✅ Good! Model generates reasonable code.")
            elif codebleu_score >= 0.45:
                logger.info("⚠️  Fair. Model works but has room for improvement.")
            else:
                logger.info("❌ Poor. Model needs more training or tuning.")

        # Add detailed results
        results = {
            "test_size": len(predictions),
            "scores": scores,
            "predictions_sample": predictions[:3],  # First 3 for inspection
            "references_sample": [ref[0] for ref in references[:3]],
        }

        return results

    def evaluate_single_example(self, requirements: Dict, reference: str) -> Dict:
        """Evaluate a single example with CodeBLEU."""
        if not self.codebleu_available:
            logger.error("CodeBLEU not available")
            return {}

        logger.info("Generating prediction...")
        prediction = self.generate_code(requirements)

        logger.info("\n📝 Generated Code:")
        logger.info("-" * 80)
        logger.info(prediction)
        logger.info("-" * 80)

        logger.info("\n📚 Reference Code:")
        logger.info("-" * 80)
        logger.info(reference)
        logger.info("-" * 80)

        scores = self.calculate_codebleu([prediction], [[reference]], lang="python")

        if scores:
            logger.info("\n📊 CodeBLEU Scores:")
            logger.info(f"Overall: {scores['codebleu']:.4f}")
            logger.info(f"N-gram: {scores['ngram_match_score']:.4f}")
            logger.info(f"Syntax: {scores['syntax_match_score']:.4f}")
            logger.info(f"Dataflow: {scores['dataflow_match_score']:.4f}")

        return {"prediction": prediction, "reference": reference, "scores": scores}


def main():
    """Run CodeBLEU evaluation."""
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate CodeT5 with CodeBLEU")
    parser.add_argument(
        "--model-path",
        type=str,
        default="./models/codet5-function-call-finetuned",
        help="Path to trained model",
    )
    parser.add_argument(
        "--test-size",
        type=int,
        default=20,
        help="Number of test examples",
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="data/training/rag_enhanced_t5_training.json",
        help="Path to training data",
    )

    args = parser.parse_args()

    print("🚀 CodeBLEU Evaluation for CodeT5")
    print("=" * 80)

    # Check if codebleu is installed
    try:
        import codebleu  # noqa: F401

        print("✅ CodeBLEU package found")
    except ImportError:
        print("❌ CodeBLEU not installed!")
        print("\nInstallation instructions:")
        print("  pip install codebleu")
        print("\nOr with requirements:")
        print("  echo 'codebleu>=2.0.0' >> requirements.txt")
        print("  pip install -r requirements.txt")
        sys.exit(1)

    try:
        evaluator = CodeBLEUEvaluator(model_path=args.model_path)

        results = evaluator.evaluate_on_test_set(
            test_size=args.test_size, data_path=args.data_path
        )

        if results and "scores" in results and results["scores"]:
            # Save results
            output_file = "codebleu_evaluation_results.json"
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\n📄 Results saved to: {output_file}")

            # Exit with success/failure based on score
            if results["scores"]["codebleu"] >= 0.60:
                print("\n✅ Evaluation complete: Model quality is good!")
                sys.exit(0)
            else:
                print("\n⚠️  Evaluation complete: Model needs improvement.")
                sys.exit(0)
        else:
            print("\n❌ Evaluation failed to produce results")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
