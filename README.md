# MSc AI Capstone Project: Domain-Specific AI for Educational Syllabus Generation

## Project Overview

This repository contains the complete work for my MSc Artificial Intelligence capstone project, spanning 30 weeks of independent research and development.

### The Problem
Current large language models can generate text that looks like a syllabus, but they lack the specific educational structure and pedagogical understanding needed to create truly coherent, educationally sound course content.

### The Solution
A novel function calling architecture that combines neural language generation with programmatic construction:
- Takes course requirements as input (title, domain, level, description)
- Generates executable function calls that construct valid syllabi
- Integrates RAG (Retrieval-Augmented Generation) for component reusability
- Achieves reliable structural validity while preserving T5 semantic intelligence

### Technical Approach
**Core Innovation: Function Calling Architecture**
- Fine-tuned T5-small (60M parameters) generates educational function calls
- Format-agnostic intelligent parser extracts semantic content from any T5 output
- SyllabusBuilder execution engine ensures pedagogical validation and structural correctness
- RAG integration retrieves educational components from ChromaDB vector store
- Programmatic JSON construction guarantees valid output

**Training Data:**
- 4,403 synthetic educational components (modules, activities, assessments)
- Covers Computer Science, Mathematics, Physics, and Engineering domains
- Generated using Anthropic Claude API with educational framework validation

### Key Innovation
**Separating Semantics from Syntax:**
- Traditional approach: T5 → JSON (fails due to syntax precision requirements)
- Our approach: T5 → Function Calls → Programmatic JSON
- Preserves T5's educational intelligence while ensuring structural validity
- Enables smaller models (60M parameters) to achieve reliable structured generation through architectural innovation rather than parameter scaling

## Project Structure

```
├── README.md                          # This file
├── pyproject.toml                     # Python packaging and tool configuration
├── Makefile                          # Development automation commands
├── requirements.txt                  # Python dependencies
├── environment.yml                   # Conda environment specification
├── .pre-commit-config.yaml          # Code quality hooks
├── .env.example                      # Environment variables template
├── docs/                            # Documentation and project planning
│   ├── course-materials/            # Course units and project proposals
│   ├── literature-review/           # Research papers and analysis
│   └── progress/                    # Progress tracking and reports
├── src/                             # Source code implementation
│   ├── data/                        # Data processing modules
│   ├── models/                      # AI model architectures
│   ├── training/                    # Training scripts and utilities
│   ├── evaluation/                  # Evaluation metrics and testing
│   └── utils/                       # Utility functions
└── data/                           # Raw and processed datasets
    ├── raw/                        # Original data sources
    ├── processed/                  # Cleaned and preprocessed data
    └── synthetic/                  # Generated or augmented data
```

## Current Status

### Phase 1: Research and Planning (Weeks 1-8) - ✅ Complete
- ✅ Comprehensive literature review (neural architectures, educational AI, domain adaptation)
- ✅ Project proposal and ethical approval
- ✅ Methodology framework (design science research)
- ✅ Master literature database with 43 references

### Phase 2: Data Collection and Preprocessing (Weeks 9-14) - ✅ Complete
- ✅ Synthetic educational data generation (4,403 components)
- ✅ ChromaDB vector store implementation
- ✅ Educational framework validation pipeline
- ✅ Domain coverage: CS, Mathematics, Physics, Engineering

### Phase 3: Model Development (Weeks 15-22) - ✅ Complete
- ✅ Three-phase iterative development:
  - Phase 1: Direct T5 JSON generation (systematic failure analysis)
  - Phase 2: RAG-enhanced compositional architecture
  - Phase 3: Function calling breakthrough
- ✅ T5-small fine-tuning on function call generation
- ✅ Format-agnostic intelligent parser implementation
- ✅ SyllabusBuilder execution engine with pedagogical validation
- ✅ RAG integration with component retrieval pipeline

### Phase 4: Evaluation and Refinement (Weeks 23-26) - 🚧 In Progress
- ✅ Performance metrics: Reliable structural validity with high T5 utilization
- ✅ Comparative analysis across three architectural phases
- 🚧 Technical evaluation documentation
- 📋 Educational quality expert review

### Phase 5: Documentation and Finalization (Weeks 27-30) - 🚧 In Progress
- ✅ Dissertation: 14,952 words (115% of 13,000-word target)
  - ✅ Introduction (1,210 words)
  - ✅ Literature Review (5,156 words)
  - ✅ Ethical Considerations (1,213 words)
  - ✅ Methodology (2,933 words)
  - ✅ Implementation (2,358 words)
  - ✅ Annex A: Research Evolution (1,911 words)
  - 🚧 Evaluation chapter (in progress)
  - 📋 Learning & Reflection chapter
  - 📋 Conclusion chapter
- ✅ All Mermaid diagrams created and converted to PNG
- 📋 Final presentation preparation

## Implementation Highlights

**Function Calling Architecture Components:**
- `T5FunctionCallGenerator`: Neural function call generation
- `FunctionCallParser`: Format-agnostic intelligent parsing with information extraction
- `SyllabusBuilder`: Execution engine with educational validation
- `RAGIntegratedSyllabusBuilder`: Component-aware syllabus construction
- `ComponentRetrievalPipeline`: Vector database query and component retrieval

**Key Files:**
- `src/models/function_call_engine.py`: Core parser and generator
- `src/models/rag_integrated_generator.py`: RAG integration
- `src/training/t5_function_call_trainer.py`: T5 fine-tuning pipeline
- `scripts/custom_input_demo.py`: Interactive demo

## Progress Summary

**Technical Achievement**: Successfully developed and implemented novel function calling architecture that achieves reliable structured generation while preserving T5 semantic intelligence.

**Academic Progress**: Dissertation writing substantially complete (115% of word count target), with core technical chapters finished and evaluation/conclusion chapters remaining.

**Research Contribution**: Demonstrated that architectural innovation enables smaller models to achieve reliable structured generation without requiring parameter scaling.

**Next Priority**: Complete evaluation chapter documenting technical performance and educational quality assessment.

## Getting Started

### Prerequisites
- Python 3.10+
- CUDA-capable GPU (recommended)
- Access to Open Syllabus Project API

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

## Contact

Dewyn Liriano
MSc Artificial Intelligence
University of Essex Online

---

*This project represents original research contributing to the field of AI in education, specifically addressing the challenge of generating pedagogically sound educational content through domain-specific AI architectures.*
