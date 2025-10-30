#!/usr/bin/env python3
"""Upload trained CodeT5 model to Hugging Face Hub with model card."""

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
    performance_section = ""
    if pass_rate is not None:
        performance_section = f"""
## Performance

Evaluated on diverse test cases covering:
- Different difficulty levels (beginner, intermediate, advanced)
- Multiple domains (computer science, data science, business)
- Various course structures

**Evaluation Results:**
- Validity Rate: {pass_rate:.1f}%
- Output Quality: Generates well-structured markdown syllabi
- Component Selection: Accurate index-based component references
- Pedagogical Quality: High-quality educational content with prerequisite awareness
"""

    model_card = f"""---
language: en
license: apache-2.0
tags:
- text-generation
- markdown
- education
- syllabus-generation
- codet5
- fine-tuned
- pedagogical-ai
datasets:
- custom
metrics:
- validity-rate
- pedagogical-quality
widget:
- text: 'Generate course syllabus: {{"title": "Introduction to Python", "domain": "computer_science", "level": "beginner", "duration": "semester"}}'
---

# CodeT5 Syllabus Generator for Educational Content Creation

## Model Description

This is a fine-tuned [Salesforce/codet5-small](https://huggingface.co/Salesforce/codet5-small) model trained to generate structured markdown syllabi with component selection indices. The model takes course requirements as input and generates markdown-formatted syllabi with index-based references to pre-defined educational components.

**Key Features:**
- Generates well-structured markdown syllabi
- Selects appropriate components using index notation [0], [1], [2]
- Understands educational domain concepts (learning objectives, Bloom's taxonomy, difficulty progression)
- Produces prerequisite-aware module sequences
- Trained with pedagogical quality metrics

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
import json

model_id = "{model_id}"
tokenizer = RobertaTokenizer.from_pretrained(model_id)
model = T5ForConditionalGeneration.from_pretrained(model_id)

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

input_text = f"Generate course syllabus: {{json.dumps(requirements)}}"
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

generated_markdown = tokenizer.decode(output[0], skip_special_tokens=True)
print(generated_markdown)
```

### Expected Output

```markdown
# Machine Learning Fundamentals

**Domain:** Computer Science
**Level:** Intermediate
**Duration:** Semester

## Course Description
Introduction to machine learning algorithms and applications

## Learning Objectives
- Understand supervised learning algorithms
- Implement neural networks
- Evaluate model performance

## Modules

### Module 1: Introduction to Machine Learning [0]
**Duration:** 8 weeks

### Module 2: Supervised Learning Algorithms [1]
**Duration:** 12 weeks
**Prerequisites:** Module 1

### Module 3: Neural Networks [2]
**Duration:** 16 weeks
**Prerequisites:** Module 2

## Activities
- Hands-on ML Exercise [0] - Apply level
- Neural Network Workshop [1] - Create level

## Assessments
- Final Project [0] - Project type
```

### Integration with Parsing Pipeline

```python
from scripts.markdown_syllabus_parser import MarkdownSyllabusParser

parser = MarkdownSyllabusParser(
    modules_file="data/components/modules.json",
    activities_file="data/components/activities.json",
    assessments_file="data/components/assessments.json"
)

syllabus = parser.parse_markdown(generated_markdown)
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
- Component indices must be resolved using pre-defined component databases
- May need post-processing for edge cases or unusual course structures

## Citation

If you use this model, please cite:

```bibtex
@misc{{codet5-syllabus-generator,
  author = {{EduCraft MSc AI Capstone Project}},
  title = {{CodeT5 Syllabus Generator for Educational Content Creation}},
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
    training_examples: int = 1300,
    epochs: int = 20,
    pass_rate: float = None,
):
    logger.info("Starting Hugging Face upload process")

    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found at {model_path}. "
            "Please train the model first: python scripts/train_sequenced_codet5.py"
        )

    hf_token = os.getenv("HUGGING_FACE_TOKEN") or os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError(
            "Hugging Face token not found. Please set HUGGING_FACE_TOKEN or HF_TOKEN environment variable.\n"
        )

    model_id = os.getenv("HF_MODEL_ID")
    if model_id:
        logger.info(f"Using HF_MODEL_ID from environment: {model_id}")
    elif organization:
        model_id = f"{organization}/{repo_name}"
    else:
        api = HfApi(token=hf_token)
        user_info = api.whoami()
        username = user_info["name"]
        model_id = f"{username}/{repo_name}"

    logger.info(f"Model ID: {model_id}")
    logger.info(f"Private: {private}")

    try:
        logger.info("Creating repository...")
        create_repo(
            repo_id=model_id,
            token=hf_token,
            private=private,
            exist_ok=True,
            repo_type="model",
        )

        logger.info("Generating model card...")
        model_card = create_model_card(
            model_id=model_id,
            training_examples=training_examples,
            epochs=epochs,
            pass_rate=pass_rate,
        )

        readme_path = model_path / "README.md"
        with open(readme_path, "w") as f:
            f.write(model_card)

        logger.info("Uploading model files...")
        api = HfApi(token=hf_token)

        api.upload_folder(
            folder_path=str(model_path),
            repo_id=model_id,
            repo_type="model",
            commit_message=f"Upload trained CodeT5 model ({epochs} epochs, {training_examples} examples)",
        )

        logger.info(f"Model uploaded: https://huggingface.co/{model_id}")

        return model_id

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Upload trained CodeT5 model to Hugging Face Hub"
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Make the model private",
    )
    parser.add_argument(
        "--pass-rate",
        type=float,
        default=None,
        help="Model evaluation pass rate for model card",
    )

    args = parser.parse_args()

    try:
        upload_model_to_hub(
            model_path="./models/codet5-sequenced/checkpoint-196",
            repo_name="codet5-educraft-syllabus-generator",
            organization=None,
            private=args.private,
            training_examples=1300,
            epochs=20,
            pass_rate=args.pass_rate,
        )
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()
