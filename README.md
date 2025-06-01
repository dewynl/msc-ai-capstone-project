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
├── docs/                             # Documentation and project planning
│   ├── project-proposal/             # Initial project documents
│   ├── literature-review/            # Research papers and analysis
│   ├── methodology/                  # Research methodology documentation
│   ├── progress-reports/             # Weekly/milestone progress reports
│   └── final-dissertation/           # Final dissertation chapters
├── research/                         # Research materials and analysis
│   ├── literature/                   # Collected papers and sources
│   ├── analysis/                     # Research analysis and findings
│   └── datasets/                     # Data collection and preprocessing
├── src/                              # Source code implementation
│   ├── data/                         # Data processing modules
│   ├── models/                       # AI model architectures
│   ├── training/                     # Training scripts and utilities
│   ├── evaluation/                   # Evaluation metrics and testing
│   └── utils/                        # Utility functions
├── experiments/                      # Experimental code and results
│   ├── baseline/                     # Baseline model experiments
│   ├── custom-architecture/          # Custom model experiments
│   └── evaluation-results/           # Experiment results and analysis
├── data/                            # Raw and processed datasets
│   ├── raw/                         # Original data sources
│   ├── processed/                   # Cleaned and preprocessed data
│   └── synthetic/                   # Generated or augmented data
├── notebooks/                       # Jupyter notebooks for exploration
├── requirements.txt                 # Python dependencies
├── environment.yml                  # Conda environment specification
└── Notes/                          # Course notes (existing)
```

## Timeline (30 weeks)

### Phase 1: Research and Planning (Weeks 1-8)
- Literature review
- Data source identification
- Methodology refinement
- Project plan finalization

### Phase 2: Data Collection and Preprocessing (Weeks 9-14)
- Open Syllabus Project API integration
- Data cleaning and preprocessing
- Educational framework analysis

### Phase 3: Model Development (Weeks 15-22)
- Baseline model implementation
- Custom architecture development
- Training pipeline setup

### Phase 4: Evaluation and Refinement (Weeks 23-26)
- Model evaluation using ROUGE, BERTScore
- Educational quality assessment
- Bloom's taxonomy alignment analysis

### Phase 5: Documentation and Finalization (Weeks 27-30)
- Final dissertation writing
- Code documentation
- Results analysis and presentation

## Getting Started

### Prerequisites
- Python 3.8+
- CUDA-capable GPU (recommended)
- Access to Open Syllabus Project API

### Installation
```bash
# Clone the repository
git clone https://github.com/dewynl/msc-ai-capstone-project.git
cd msc-ai-capstone-project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Documentation

- **Project Proposal**: [docs/course-materials/](docs/course-materials/)
- **Literature Review**: [docs/literature-review/](docs/literature-review/)
- **Progress Reports**: [docs/progress-reports/](docs/progress-reports/)

## Contact

Dewyn Liriano  
MSc Artificial Intelligence  
University of Essex Online

---

*This project represents original research contributing to the field of AI in education, specifically addressing the challenge of generating pedagogically sound educational content through domain-specific AI architectures.*
