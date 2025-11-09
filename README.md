# MSc AI Capstone Project: Domain-Specific AI for Educational Syllabus Generation

## Project Overview

This repository contains the complete work for my MSc Artificial Intelligence capstone project, spanning 30 weeks of independent research and development.

### The Problem
Current large language models can generate text that looks like a syllabus, but they lack the specific educational structure and pedagogical understanding needed to create truly coherent, educationally sound course content.

### The Solution
A hybrid ML + rule-based system that combines fine-tuned CodeT5-small with semantic ranking and quality validation:
- Takes course requirements as input (title, domain, level, description)
- Generates complete syllabi in structured markdown format
- Uses BERT-based semantic ranking to select pedagogically appropriate components
- Validates output quality through prerequisite coherence checking
- Achieves reliable structured generation with educational soundness

### Technical Approach
**Core Innovation: Hybrid Generation Pipeline**
- Fine-tuned CodeT5-small (60M parameters) generates complete markdown syllabi
- Domain/difficulty filtering ensures appropriate component selection
- BERT-based semantic ranking with pedagogical boosting (intro modules prioritized)
- Markdown-to-JSON parser extracts structured data with component expansion
- Bloom's Taxonomy-based objective enhancement
- Quality reranker validates prerequisite coherence

**Training Data:**
- 1,300 sequenced training examples (markdown format)
- 4,403 educational components (modules, activities, assessments)
- Covers Computer Science (59.5%), Mathematics (35.5%), Physics (5.1%)
- Component database enables RAG-style retrieval without vector stores

### Key Innovation
**Simplicity Through Integration:**
- Traditional approach: Complex RAG pipelines with vector databases
- Our approach: Filter → Semantic Rank → Generate → Parse → Enhance
- Combines small fine-tuned model with intelligent rule-based components
- Achieves reliable structured generation through architectural simplicity
- Demonstrates that hybrid approaches can match complex systems with less overhead

## Project Structure

```
├── README.md                          # This file
├── streamlit_app.py                   # Web interface for syllabus generation
├── pyproject.toml                     # Python packaging configuration
├── Makefile                          # Development automation commands
├── requirements.txt                  # Python dependencies
├── docs/                            # Dissertation and documentation
│   ├── dissertation.md              # Main dissertation document
│   ├── master-literature-list.md    # References (67 sources)
│   ├── figures/                     # Dissertation figures and screenshots
│   └── planning/                    # Project planning materials
├── scripts/                         # Generation pipeline and utilities
│   ├── generate_syllabus.py         # Main generation pipeline
│   ├── model_inference.py           # CodeT5 wrapper
│   ├── semantic_ranker.py           # Component ranking
│   ├── markdown_syllabus_parser.py  # Parser
│   ├── enhance_objectives.py        # Bloom's Taxonomy enhancement
│   ├── rag_filter.py                # Filtering logic
│   ├── train_sequenced_codet5.py    # Model training
│   └── test_trained_model.py        # Testing utilities
├── src/                             # Supporting modules
│   ├── inference/                   # Inference utilities
│   │   └── quality_reranker.py      # Quality validation
│   └── utils/                       # Shared utilities
│       └── supabase_client.py       # Database client
├── data/                           # Educational components and training data
│   ├── components/                  # RAG component database (10MB)
│   │   ├── modules.json             # 4,403 educational modules
│   │   ├── activities.json          # Learning activities
│   │   └── assessments.json         # Assessment types
│   ├── training/                    # Model training data (5.5MB)
│   │   ├── sequenced_t5_training.json
│   │   └── markdown_training_1300.json
│   └── evaluation/                  # Test suites
└── models/                         # Trained models
    └── codet5-sequenced/            # Production model (3.4GB)
        └── checkpoint-196/          # Final checkpoint
```

## Research Outcomes

**Technical Achievement**: Hybrid ML + rule-based system achieving 100% parseability across 32 test cases with strong performance in difficulty progression (90.6%) and topic diversity (87.3%). Demonstrates that task simplification—not model scaling—resolves structural generation bottlenecks.

**Academic Deliverables**: Complete dissertation (14,408 words, 110.8% of target) including research approach evolution documentation and reproducibility artifacts. Full bibliography of 67 sources spanning neural architectures, educational AI, and domain adaptation methods.

**Research Contribution**: Empirical validation that constrained output spaces enable smaller models (60M parameters) to achieve reliability through appropriate task formulation rather than parameter scaling. Five-dimensional pedagogical quality framework successfully distinguishes soft constraints learnable through training from hard constraints requiring explicit algorithmic enforcement.

## Quick Start

**Try the Live Demo**: https://educraft.streamlit.app/

The system is deployed and accessible for interactive testing. Specify course requirements and watch real-time syllabus generation with quality metrics.

### Running the Web Application Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run streamlit_app.py
```

The application provides an interactive web interface for:
- Entering course requirements (title, domain, level, description)
- Selecting target duration and audience
- Real-time syllabus generation with progress tracking
- Viewing structured JSON output
- Downloading generated syllabi

### Generating Syllabi via CLI

```bash
# Generate a complete syllabus
python scripts/generate_syllabus.py \
  --title "Deep Learning with PyTorch" \
  --domain "computer_science" \
  --level "advanced" \
  --description "Advanced neural networks using PyTorch"
```

### Reproducing Results

```bash
# Clone repository
git clone https://github.com/dewynl/msc-ai-capstone-project.git
cd msc-ai-capstone-project

# Setup environment (tested on WSL2 Ubuntu)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run evaluation on 32-test-set (requires trained model)
python scripts/evaluate_trained_model.py

# Generate training data (optional - data included in repo)
python scripts/generate_sequenced_training_data.py

# Train model from scratch (GPU optional but accelerates training)
python scripts/train_sequenced_codet5.py
```

**Prerequisites**: Python 3.10+, 10GB disk space

## Documentation

- **Dissertation**: [docs/dissertation.md](docs/dissertation.md) - Complete MSc dissertation (14,408 words)
- **Master Literature List**: [docs/master-literature-list.md](docs/master-literature-list.md) - Full bibliography (67 sources)
- **Live Demo**: [https://educraft.streamlit.app/](https://educraft.streamlit.app/)
- **Source Repository**: [https://github.com/dewynl/msc-ai-capstone-project](https://github.com/dewynl/msc-ai-capstone-project)

## Model Performance

**Production Model**: CodeT5-small fine-tuned (codet5-sequenced/checkpoint-196)
- **Training**: 1,300 examples, 13 epochs with early stopping
- **Parameters**: 60M (CodeT5-small)
- **Architecture**: Markdown generation with RAG-enhanced semantic ranking
- **Output**: Structured JSON syllabi with educational component expansion
- **Validation**: Five-dimensional pedagogical quality framework

**Evaluation Results** (32-syllabus test set across CS, Math, Physics):
- **Parseability**: 100% (32/32 syllabi structurally valid)
- **Difficulty Progression**: 90.6% ± 20.3% (81% achieve perfect progression)
- **Topic Diversity**: 87.3% ± 16.7% (59% achieve ≥90% diversity)
- **Prerequisite Accuracy**: 44.8% ± 46.0% (primary architectural limitation)
- **Bloom's Taxonomy Coverage**: 37.5% ± 17.8%
- **Semantic Relevance**: 40.0% ± 5.3% (MPNet cosine similarity)
- **Generation Time**: ~5 seconds per complete syllabus
- **Model Size**: 3.4GB (final checkpoint + tokenizer)

## Contact

Dewyn Liriano
MSc Artificial Intelligence
University of Essex Online

---

*This project represents original research contributing to the field of AI in education, specifically addressing the challenge of generating pedagogically sound educational content through hybrid ML + rule-based architectures.*
