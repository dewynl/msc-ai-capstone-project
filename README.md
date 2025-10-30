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
- Covers Computer Science, Mathematics, Physics, and Engineering domains
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
│   ├── chapter-6-evaluation.md      # Evaluation chapter
│   ├── chapter-7-learning-reflection.md
│   ├── chapter-8-conclusion.md
│   ├── master-literature-list.md    # References (43 sources)
│   └── expert-review-form-design.md
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

## Current Status

### Phase 1: Research and Planning (Weeks 1-8) - ✅ Complete
- ✅ Comprehensive literature review (neural architectures, educational AI, domain adaptation)
- ✅ Project proposal and ethical approval
- ✅ Methodology framework (design science research)
- ✅ Master literature database with 43 references

### Phase 2: Data Collection and Preprocessing (Weeks 9-14) - ✅ Complete
- ✅ Synthetic educational data generation (4,403 components)
- ✅ Component database implementation (simple JSON-based storage)
- ✅ Educational framework validation pipeline
- ✅ Domain coverage: CS, Mathematics, Physics, Engineering

### Phase 3: Model Development (Weeks 15-22) - ✅ Complete
- ✅ Iterative architectural exploration:
  - Approach 1: Direct T5 JSON generation (systematic failure analysis)
  - Approach 2: Function calling architecture
  - Approach 3: RAG-enhanced systems
  - **Final approach**: Markdown generation with hybrid pipeline
- ✅ CodeT5-small fine-tuning on 1,300 markdown examples
- ✅ Semantic ranking with BERT embeddings
- ✅ Quality validation and prerequisite coherence checking
- ✅ Streamlit web application deployment

### Phase 4: Evaluation and Refinement (Weeks 23-26) - ✅ Complete
- ✅ Performance metrics collection and analysis
- ✅ Comparative analysis across architectural approaches
- ✅ Technical evaluation completed
- 🚧 Educational quality expert review (in planning)

### Phase 5: Documentation and Finalization (Weeks 27-30) - 🚧 In Progress
- ✅ Dissertation: ~15,000 words (115% of 13,000-word target)
  - ✅ Introduction
  - ✅ Literature Review
  - ✅ Ethical Considerations
  - ✅ Methodology
  - ✅ Implementation
  - ✅ Annex A: Architectural Evolution
  - 🚧 Evaluation chapter (in progress)
  - 📋 Learning & Reflection chapter
  - 📋 Conclusion chapter
- ✅ All technical diagrams created
- 📋 Final presentation preparation

## Implementation Highlights

**Markdown Generation Architecture Components:**
- `SyllabusGenerator` (CodeT5-small): Direct markdown generation from course requirements
- `SemanticRanker`: BERT-based component ranking by semantic similarity
- `MarkdownSyllabusParser`: Structured JSON extraction from generated markdown
- `ObjectiveEnhancer`: Bloom's Taxonomy-based learning objective enhancement
- `SyllabusQualityReranker`: Prerequisite coherence validation

**Key Files:**
- `scripts/generate_syllabus.py`: Complete generation pipeline (filter → rank → generate → parse → enhance)
- `scripts/model_inference.py`: CodeT5 inference wrapper
- `scripts/semantic_ranker.py`: Component ranking with pedagogical boosting
- `src/inference/quality_reranker.py`: Quality-based candidate selection

## Progress Summary

**Technical Achievement**: Successfully developed hybrid ML + rule-based system combining CodeT5-small fine-tuned model with semantic ranking and quality validation for reliable syllabus generation.

**Academic Progress**: Dissertation writing substantially complete (115% of word count target), with core technical chapters finished and evaluation/conclusion chapters remaining.

**Research Contribution**: Demonstrated that combining small fine-tuned models with intelligent filtering, semantic ranking, and quality validation achieves reliable educational content generation.

**Next Priority**: Complete evaluation chapter documenting technical performance and educational quality assessment.

## Quick Start

### Running the Web Application

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

### Training the Model

```bash
# Generate training data
python scripts/generate_sequenced_training_data.py

# Train CodeT5 model (requires GPU)
python scripts/train_sequenced_codet5.py
```

## Development Setup

### Prerequisites
- Python 3.10+
- CUDA-capable GPU (recommended for training)
- 10GB+ disk space for model checkpoints

### Installation

**Quick Development Setup:**
```bash
# Clone the repository
git clone https://github.com/dewynl/msc-ai-capstone-project.git
cd msc-ai-capstone-project

# Complete development environment setup
make setup
```

**Manual Setup:**
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev,jupyter]"

# Install pre-commit hooks
pre-commit install
```

### Development Workflow

```bash
# Format code
make format

# Run linting checks
make lint

# Run tests with coverage
make test

# Clean cache files
make clean
```

## Development Tools

**Code Quality:**
- Black - Code formatting
- Ruff - Fast Python linting
- MyPy - Static type checking
- pre-commit - Git hooks for code quality

**Testing & Development:**
- pytest - Testing framework
- Jupyter Lab - Interactive development and documentation
- Make - Development automation

## Documentation

- **Project Proposal**: [docs/course-materials/](docs/course-materials/)
- **Literature Review**: [docs/literature-review/](docs/literature-review/)
- **Progress Reports**: [docs/progress/](docs/progress/)

## Contributing

This project uses modern Python development practices:

1. **Code Quality**: All code is automatically formatted with Black and linted with Ruff
2. **Type Checking**: MyPy ensures type safety
3. **Testing**: pytest for comprehensive testing
4. **Pre-commit Hooks**: Automatic quality checks before commits

To contribute:
```bash
# Setup development environment
make setup

# Make your changes, then run quality checks
make format
make lint
make test
```

## Model Performance

**Production Model**: CodeT5-small fine-tuned (codet5-sequenced/checkpoint-196)
- **Training**: 1,300 examples, 15 epochs, early stopping at epoch 14
- **Parameters**: 60M (CodeT5-small)
- **Architecture**: Markdown generation with semantic ranking pipeline
- **Output**: Structured JSON syllabi with educational component expansion
- **Validation**: Prerequisite coherence checking and Bloom's Taxonomy enhancement

**Key Metrics**:
- Structural validity: High (validated through markdown parsing)
- Component selection: Pedagogically appropriate (semantic ranking)
- Generation time: ~2-3 seconds per syllabus
- Model size: 3.4GB (5 checkpoints preserved)

## Contact

Dewyn Liriano
MSc Artificial Intelligence
University of Essex Online

---

*This project represents original research contributing to the field of AI in education, specifically addressing the challenge of generating pedagogically sound educational content through hybrid ML + rule-based architectures.*
