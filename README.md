# MSc AI Capstone Project: Domain-Specific AI for Educational Syllabus Generation

## Project Overview

This repository contains the complete work for my MSc Artificial Intelligence capstone project, spanning 30 weeks of independent research and development.

### The Problem
Current large language models can generate text that looks like a syllabus, but they lack the specific educational structure and pedagogical understanding needed to create truly coherent, educationally sound course content.

### The Solution
Build a domain-specific AI model that:
- Takes minimal inputs (course description, learning objectives, problem statements)
- Generates structured, coherent course syllabi
- Understands educational frameworks and learning progression
- Maintains pedagogical quality throughout the content

### Technical Approach
- Custom neural architecture specifically designed for educational content structure
- Specialized word embeddings trained on educational terminology
- Sequence-to-sequence modeling with attention mechanisms
- Training data from Open Syllabus Project API and educational resources

### Key Innovation
Creating a purpose-built system that understands:
- Educational content structure
- Learning objective alignment
- Pedagogical progression
- Domain-specific educational quality metrics

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

### Phase 1: Research and Planning (Weeks 1-8) - 95% Complete ✅
- ✅ Comprehensive literature review completed (neural architectures, educational content generation)
- ✅ Detailed project proposal and ethical approval
- ✅ Methodology framework established (design science research)
- ✅ Master literature database with 43 references established
- ✅ Dissertation writing advanced (Introduction and Literature Review complete)

### Phase 2: Data Collection and Preprocessing (Weeks 9-14) - Ready to Begin 🚧
- 🚧 Open Syllabus Project API integration
- 🚧 Data cleaning and preprocessing pipeline
- 🚧 Educational framework analysis implementation

### Phase 3: Model Development (Weeks 15-22) - Architecture Planned 📋
- 📋 Custom transformer architecture documented
- 📋 Educational component specifications defined
- 📋 Training pipeline design completed

### Phase 4: Evaluation and Refinement (Weeks 23-26) - Framework Designed 📋
- 📋 Technical evaluation metrics defined (ROUGE, BERTScore)
- 📋 Educational quality assessment protocols established
- 📋 Expert review framework designed

### Phase 5: Documentation and Finalization (Weeks 27-30) - In Progress 📝
- 📝 Dissertation writing active (Introduction and Literature Review complete)
- 📝 Chapter 3 (Ethical Considerations) ready to write
- 📋 Technical documentation templates prepared
- 📋 Presentation framework outlined

## Progress Summary

**Academic Foundation**: Strong progress with comprehensive documentation, literature review, and dissertation writing underway.

**Technical Implementation**: Architecture designed and documented, ready for implementation phase.

**Project Management**: 22 active tasks tracked across all phases with clear sprint planning.

**Next Priority**: Transition from academic planning to technical implementation (Phase 2 data collection).

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
