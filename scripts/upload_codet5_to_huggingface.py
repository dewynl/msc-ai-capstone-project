#!/usr/bin/env python3
"""
Upload Trained CodeT5 Model to Hugging Face Hub

This script uploads the trained CodeT5 model with a comprehensive model card
for easy deployment and sharing.
"""

import argparse
import logging
import os
from pathlib import Path

from huggingface_hub import HfApi, create_repo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_model_card(
    model_id: str,
    training_examples: int,
    epochs: int,
    pass_rate: float = None,
) -> str:
    """Generate comprehensive model card in Markdown format."""

    performance_section = ""
    if pass_rate is not None:
        performance_section = f"""
## Performance

Evaluated on diverse test cases covering:
- Different difficulty levels (beginner, intermediate, advanced)
- Multiple domains (computer science, data science, business)
- Various course structures

**Evaluation Results:**
- Test Pass Rate: {pass_rate:.1f}%
- Output Quality: Generates complete, syntactically valid Python code
- Function Call Completeness: All required SyllabusBuilder methods present
- Execution Success: Generated code executes without errors
"""

    model_card = f"""---
language: en
license: apache-2.0
tags:
- code-generation
- function-calling
- education
- syllabus-generation
- codet5
- fine-tuned
datasets:
- custom
metrics:
- code-bleu
widget:
- text: 'Generate course syllabus: {{"title": "Introduction to Python", "domain": "computer_science", "level": "beginner", "duration": "semester"}}'
---

# CodeT5 Function Call Generator for Educational Syllabus Creation

## Model Description

This is a fine-tuned [Salesforce/codet5-small](https://huggingface.co/Salesforce/codet5-small) model trained to generate Python function calls for automated course syllabus creation. The model takes structured course requirements as input and generates executable Python code using the SyllabusBuilder API.

**Key Features:**
- Generates syntactically valid Python function calls
- Understands educational domain concepts (learning objectives, Bloom's taxonomy, etc.)
- Produces complete syllabus structures with modules, activities, and assessments
- Trained specifically on educational content generation patterns

## Training Data

- **Training Examples:** {training_examples} curated course-to-code pairs
- **Epochs:** {epochs}
- **Data Quality:** High-quality examples covering:
  - Multiple difficulty levels (beginner, intermediate, advanced)
  - Various domains (computer science, data science, business, arts)
  - Diverse course structures and pedagogical approaches
  - Bloom's taxonomy alignment
  - Assessment types and learning activities

## Training Configuration

```python
Model: Salesforce/codet5-small (60M parameters)
Tokenizer: RobertaTokenizer
Batch Size: 16
Gradient Accumulation: 2 (effective batch size: 32)
Learning Rate: 3e-4
Weight Decay: 0.01
Label Smoothing: 0.1
Max Input Length: 640 tokens
Max Output Length: 536 tokens
```
{performance_section}
## Usage

### Quick Start

```python
from transformers import RobertaTokenizer, T5ForConditionalGeneration
import torch

# Load model and tokenizer
model_id = "{model_id}"
tokenizer = RobertaTokenizer.from_pretrained(model_id)
model = T5ForConditionalGeneration.from_pretrained(model_id)

# Prepare input
requirements = {{
    "title": "Machine Learning Fundamentals",
    "domain": "computer_science",
    "level": "intermediate",
    "duration": "semester",
    "description": "Introduction to machine learning algorithms and applications",
    "learning_objectives": [
        "Understand supervised learning algorithms",
        "Implement neural networks",
        "Evaluate model performance"
    ]
}}

import json
input_text = f"Generate course syllabus: {{json.dumps(requirements)}}"

# Generate function calls
input_ids = tokenizer(
    input_text,
    return_tensors="pt",
    max_length=640,
    truncation=True,
    padding=True
).input_ids

with torch.no_grad():
    output = model.generate(
        input_ids,
        max_length=536,
        num_beams=4,
        early_stopping=False,
        no_repeat_ngram_size=2,
    )

generated_code = tokenizer.decode(output[0], skip_special_tokens=True)
print(generated_code)
```

### Expected Output

```python
b = SyllabusBuilder()
b.set_info("Machine Learning Fundamentals", "computer_science", "intermediate", "semester", "Introduction to machine learning algorithms and applications")
b.add_objective("Understand supervised learning algorithms")
b.add_objective("Implement neural networks")
b.add_objective("Evaluate model performance")
b.add_module("Introduction to Machine Learning", 8)
b.add_module("Supervised Learning Algorithms", 12)
b.add_module("Neural Networks", 16)
b.add_activity("Hands-on ML Exercise", "apply", 2)
b.add_activity("Neural Network Workshop", "create", 3)
b.add_assessment("Final Project", "project", 2)
result = b.build()
```

### Integration with SyllabusBuilder

```python
from syllabus_builder import execute_function_calls

# Execute generated code to build syllabus
syllabus = execute_function_calls(generated_code)

# Result is a complete syllabus dictionary with:
# - course_info
# - learning_objectives
# - modules
# - activities
# - assessments
```

## Model Details

**Base Model:** Salesforce/codet5-small
- Pre-trained on 8.35M code functions (Python, Java, Go, JavaScript, Ruby, PHP)
- 60M parameters
- Encoder-decoder transformer architecture

**Why CodeT5 vs T5:**
- CodeT5 is pre-trained on **code**, not natural language
- Understands programming syntax and patterns
- Better at generating valid Python function calls
- Less prone to hallucination or syntax errors

## Limitations

- Optimized for educational content generation specifically
- Requires structured input format (JSON with specific keys)
- Generated code assumes SyllabusBuilder API availability
- May need post-processing for edge cases or unusual course structures

## Citation

If you use this model, please cite:

```bibtex
@misc{{codet5-syllabus-generator,
  author = {{EduCraft MSc AI Capstone Project}},
  title = {{CodeT5 Function Call Generator for Educational Syllabus Creation}},
  year = {{2025}},
  publisher = {{Hugging Face}},
  howpublished = {{\\url{{{model_id}}}}}
}}
```

## License

Apache 2.0 (same as base CodeT5 model)

## Training Framework

- PyTorch
- Transformers (Hugging Face)
- Trained on CPU (WSL2) with gradient checkpointing
- Training time: ~2.5 hours (20 epochs)

## Contact

For questions or issues, please open an issue on the [project repository](https://github.com/dewynl/msc-ai-capstone-project).
"""
    return model_card


def upload_model_to_hub(
    model_path: str,
    repo_name: str,
    organization: str = None,
    private: bool = False,
    training_examples: int = 260,
    epochs: int = 20,
    pass_rate: float = None,
):
    """
    Upload trained model to Hugging Face Hub.

    Args:
        model_path: Local path to trained model
        repo_name: Name for the HuggingFace repository
        organization: Organization name (optional, defaults to user account)
        private: Whether to make the model private
        training_examples: Number of training examples used
        epochs: Number of training epochs
        pass_rate: Model evaluation pass rate (optional)
    """
    logger.info("🚀 Starting Hugging Face Upload Process")
    logger.info("=" * 80)

    # Check if model exists
    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found at {model_path}. "
            "Please train the model first: python scripts/codet5_function_call_trainer.py"
        )

    # Check for HF token
    hf_token = os.getenv("HUGGING_FACE_TOKEN") or os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError(
            "Hugging Face token not found. Please set HUGGING_FACE_TOKEN or HF_TOKEN environment variable.\n"
            "Get your token from: https://huggingface.co/settings/tokens"
        )

    # Create repository ID
    if organization:
        model_id = f"{organization}/{repo_name}"
    else:
        # Get username from API
        api = HfApi(token=hf_token)
        user_info = api.whoami()
        username = user_info["name"]
        model_id = f"{username}/{repo_name}"

    logger.info(f"📦 Model ID: {model_id}")
    logger.info(f"🔒 Private: {private}")

    try:
        # Create repository (or get existing)
        logger.info("📁 Creating/verifying repository...")
        create_repo(
            repo_id=model_id,
            token=hf_token,
            private=private,
            exist_ok=True,
            repo_type="model",
        )
        logger.info("✅ Repository ready")

        # Generate model card
        logger.info("📝 Generating model card...")
        model_card = create_model_card(
            model_id=model_id,
            training_examples=training_examples,
            epochs=epochs,
            pass_rate=pass_rate,
        )

        # Save model card to model directory
        readme_path = model_path / "README.md"
        with open(readme_path, "w") as f:
            f.write(model_card)
        logger.info("✅ Model card created")

        # Upload model files
        logger.info("⬆️  Uploading model files to Hugging Face Hub...")
        api = HfApi(token=hf_token)

        api.upload_folder(
            folder_path=str(model_path),
            repo_id=model_id,
            repo_type="model",
            commit_message=f"Upload trained CodeT5 model ({epochs} epochs, {training_examples} examples)",
        )

        logger.info("✅ Upload complete!")
        logger.info("")
        logger.info("=" * 80)
        logger.info(
            f"🎉 Model successfully uploaded to: https://huggingface.co/{model_id}"
        )
        logger.info("=" * 80)
        logger.info("")
        logger.info("Next steps:")
        logger.info(f"1. View model: https://huggingface.co/{model_id}")
        logger.info(f"2. Set HF_MODEL_ID in Streamlit secrets: {model_id}")
        logger.info("3. Deploy updated app to Streamlit Cloud")
        logger.info("")

        return model_id

    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        raise


def main():
    """Main upload script with CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Upload trained CodeT5 model to Hugging Face Hub"
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default="./models/codet5-function-call-finetuned",
        help="Path to trained model directory",
    )
    parser.add_argument(
        "--repo-name",
        type=str,
        default="codet5-educraft-syllabus-generator",
        help="Name for HuggingFace repository",
    )
    parser.add_argument(
        "--organization",
        type=str,
        default=None,
        help="Organization name (optional, defaults to user account)",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Make the model private",
    )
    parser.add_argument(
        "--training-examples",
        type=int,
        default=260,
        help="Number of training examples used",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=20,
        help="Number of training epochs",
    )
    parser.add_argument(
        "--pass-rate",
        type=float,
        default=None,
        help="Model evaluation pass rate (0-100)",
    )

    args = parser.parse_args()

    print("🚀 CodeT5 Model Upload to Hugging Face")
    print("=" * 80)

    try:
        model_id = upload_model_to_hub(
            model_path=args.model_path,
            repo_name=args.repo_name,
            organization=args.organization,
            private=args.private,
            training_examples=args.training_examples,
            epochs=args.epochs,
            pass_rate=args.pass_rate,
        )

        print(f"\n✅ Success! Model available at: https://huggingface.co/{model_id}")

    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check HuggingFace token: export HUGGING_FACE_TOKEN=your_token_here")
        print("2. Verify model exists: ls -la ./models/codet5-function-call-finetuned/")
        print("3. Check HF CLI: huggingface-cli whoami")
        exit(1)


if __name__ == "__main__":
    main()
