# Comprehensive Evaluation Framework Documentation

**Version:** 1.0.0
**System:** CodeT5-based Educational Syllabus Generation
**Framework Type:** Production-grade, reproducible, statistically rigorous

---

## Overview

This evaluation framework provides comprehensive assessment of the syllabus generation system across multiple dimensions:

- **Technical Performance**: Generation time, structural validity, model efficiency
- **Pedagogical Quality**: Prerequisite coherence, difficulty progression, topic diversity
- **Cross-Domain Generalization**: Performance across CS, Math, Physics, Engineering
- **Edge Case Robustness**: Handling of minimal input, long descriptions, interdisciplinary topics

### Key Features

✅ **Reproducible**: Fixed random seeds, versioned configs
✅ **Statistically Rigorous**: N=35 tests for p<0.05 significance
✅ **Crash Recovery**: Incremental saves, resume capability
✅ **Observability**: Structured logging, progress bars, detailed metrics
✅ **Production-Ready**: Type-safe, error-isolated, well-documented

---

## Architecture

```
scripts/evaluation/
├── __init__.py           # Public API exports
├── config.py             # Type-safe configuration schemas
├── test_suite.py         # Test case generation (future)
├── evaluator.py          # Core orchestration logic
├── metrics.py            # Metrics calculation
└── storage.py            # Results persistence

configs/
└── evaluation_suite.json # 35 test cases across domains

data/evaluation/
├── evaluation_results.csv      # Main metrics (35 × 34 columns)
├── evaluation_summary.json     # Aggregated statistics
├── full_outputs/               # Complete pipeline outputs
│   └── test_*.json
└── errors.jsonl                # Error logs (streaming)
```

### Data Flow

```
1. Load Config (JSON)
   ↓
2. Initialize Pipeline Components (Model, RAG, Ranker)
   ↓
3. For Each Test Case:
   a. Generate syllabus via pipeline
   b. Collect 34 metrics
   c. Save to CSV + JSON (incremental)
   ↓
4. Generate Summary Statistics
   ↓
5. Create Analysis Tables (for dissertation)
```

---

## Installation & Setup

### Prerequisites

- Python 3.8+
- CUDA (optional, for GPU acceleration)
- ~10GB disk space for model + results

### Dependencies

```bash
# Core dependencies (should already be installed)
pip install torch transformers pandas tqdm
```

### Verify Setup

```bash
# Dry run to validate environment and config
python scripts/run_comprehensive_evaluation.py --dry-run
```

Expected output:
```
✓ Environment validation passed
✓ Configuration valid
DRY RUN MODE - Configuration validated successfully
Would execute 35 tests
```

---

## Usage

### Quick Start

```bash
# Run full evaluation suite (35 tests, ~2-3 minutes)
python scripts/run_comprehensive_evaluation.py
```

### Advanced Usage

```bash
# Custom configuration
python scripts/run_comprehensive_evaluation.py --config my_config.json

# Debug logging
python scripts/run_comprehensive_evaluation.py --log-level DEBUG

# Save logs to file
python scripts/run_comprehensive_evaluation.py --log-file evaluation.log

# Quiet mode (no progress bars)
python scripts/run_comprehensive_evaluation.py --quiet
```

### Configuration

Edit `configs/evaluation_suite.json` to customize:

```json
{
  "model_checkpoint": "models/codet5-sequenced/checkpoint-196",
  "output_dir": "data/evaluation",
  "random_seed": 42,
  "enable_quality_reranking": true,
  "num_quality_candidates": 3,
  "max_generation_time_sec": 30.0,
  "test_cases": [...]
}
```

---

## Test Suite Design

### Standard Tests (25 tests)

Stratified sampling across domains and difficulty levels:

| Domain | Beginner | Intermediate | Advanced | Total |
|--------|----------|--------------|----------|-------|
| **Computer Science** | 3 | 3 | 3 | **9** |
| **Mathematics** | 3 | 2 | 2 | **7** |
| **Physics** | 2 | 2 | 1 | **5** |
| **Engineering** | 2 | 1 | 1 | **4** |
| **Total** | **10** | **8** | **7** | **25** |

**Rationale:** Proportional to training data distribution (40% CS, 30% Math, 20% Physics, 10% Engineering)

### Edge Cases (10 tests)

Boundary condition testing:

1. **Minimal Input** - Title only, empty description
2. **Very Long Description** - 1000+ word requirement
3. **Cross-Domain** - Computational Physics (CS + Physics)
4. **Intensive Bootcamp** - 8-week duration (non-standard)
5. **Contradictory** - "Beginner Quantum Computing"
6. **Ambiguous Domain** - Statistics (Math or CS?)
7. **Niche Specialization** - Bioinformatics
8. **Interdisciplinary** - Data Science (CS + Math + Stats)
9. **Postgraduate Level** - Advanced NLP research
10. **Minimal Metadata** - Cryptography (short description)

---

## Metrics Collected (34 total)

### Test Metadata (6 metrics)
- `test_id`: Unique identifier
- `timestamp`: ISO-8601 timestamp
- `domain`: Educational domain
- `level`: Difficulty level
- `course_title`: Course name
- `description_length`: Input complexity indicator

### Technical Performance (7 metrics)
- `generation_time_sec`: End-to-end pipeline time
- `model_inference_time_sec`: CodeT5 generation only
- `parsing_time_sec`: Markdown→JSON parsing
- `markdown_valid`: Successfully parsed (boolean)
- `pipeline_success`: Overall success flag
- `total_tokens_generated`: Output length
- `model_checkpoint`: Model version

### Structural Metrics (6 metrics)
- `num_modules`: Count of modules
- `num_activities`: Count of activities
- `num_assessments`: Count of assessments
- `total_components`: Sum of above
- `avg_module_hours`: Average duration
- `has_learning_objectives`: Completeness check

### Pedagogical Quality (5 metrics)
- `prerequisite_accuracy`: 0.0-1.0 (respects prerequisites)
- `difficulty_progression`: 0.0-1.0 (smooth progression)
- `topic_diversity`: 0.0-1.0 (avoids repetition)
- `blooms_taxonomy_coverage`: 0.0-1.0 (cognitive levels)
- `overall_quality_score`: 0.0-1.0 (weighted composite)

### Pipeline Components (6 metrics)
- `num_modules_available`: Total in database
- `num_modules_filtered`: After domain/level filter
- `num_modules_ranked`: Top-k from semantic ranking
- `semantic_ranking_time_sec`: BERT embedding time
- `quality_reranking_used`: Whether reranker invoked
- `reranking_improved_quality`: Selection improvement

### Error Tracking (4 metrics)
- `error_occurred`: Any errors during pipeline
- `error_type`: Categorized error ("timeout", "parsing_failed", etc.)
- `warning_count`: Non-fatal issues
- `validation_issues`: Comma-separated list

---

## Interpreting Results

### Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| Success Rate | >90% | ✅/❌ |
| Avg Generation Time | <5 seconds | ✅/❌ |
| Prerequisite Accuracy | >85% | ✅/❌ |
| Overall Quality Score | >0.7 | ✅/❌ |

### Statistical Analysis

After evaluation completes, analyze with:

```python
import pandas as pd

# Load results
df = pd.read_csv('data/evaluation/evaluation_results.csv')

# Overall statistics
print(df.describe())

# By domain
print(df.groupby('domain')['overall_quality_score'].mean())

# By level
print(df.groupby('level')['generation_time_sec'].describe())

# Success rate
success_rate = df['pipeline_success'].mean()
print(f"Success rate: {success_rate:.1%}")
```

### Common Patterns

**Good Performance:**
- Prerequisite accuracy: >0.90
- Generation time: 1-3 seconds
- Quality score: >0.75
- No errors

**Acceptable Performance:**
- Prerequisite accuracy: 0.75-0.90
- Generation time: 3-5 seconds
- Quality score: 0.60-0.75
- Minor warnings only

**Poor Performance:**
- Prerequisite accuracy: <0.75
- Generation time: >5 seconds
- Quality score: <0.60
- Errors occurred

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Symptom:** `ModuleNotFoundError: No module named 'evaluation'`

**Solution:**
```bash
# Ensure you're in project root
cd /path/to/msc-ai-capstone-project

# Run from scripts/ directory or use absolute path
python scripts/run_comprehensive_evaluation.py
```

#### 2. Model Not Found

**Symptom:** `ValueError: Model checkpoint not found`

**Solution:**
```bash
# Verify model exists
ls -la models/codet5-sequenced/checkpoint-196/

# Update config path if needed
vim configs/evaluation_suite.json
# Set: "model_checkpoint": "models/codet5-sequenced/checkpoint-196"
```

#### 3. CUDA Out of Memory

**Symptom:** `RuntimeError: CUDA out of memory`

**Solution:**
```bash
# Force CPU mode
export CUDA_VISIBLE_DEVICES=""

# Or reduce batch size in model (not applicable for evaluation)
```

#### 4. Slow Performance

**Expected:** 2-3 minutes for 35 tests (with GPU)
**Actual:** >10 minutes

**Solutions:**
- Use GPU if available
- Close other applications
- Check thermal throttling

---

## Extending the Framework

### Adding New Test Cases

Edit `configs/evaluation_suite.json`:

```json
{
  "test_id": "test_036_my_new_test",
  "domain": "computer_science",
  "level": "intermediate",
  "test_type": "standard",
  "course_title": "My Course",
  "description": "Course description here",
  "duration": "semester",
  "expected_modules": 4,
  "tags": ["custom", "my_tag"]
}
```

### Adding New Metrics

1. Edit `scripts/evaluation/metrics.py`:
   ```python
   @dataclass
   class EvaluationResult:
       # Add new field
       my_new_metric: float
   ```

2. Update `CSV_FIELDNAMES` in `storage.py`

3. Update metric calculation in `MetricsCollector.create_result()`

### Custom Analysis

Create custom analysis scripts in `scripts/`:

```python
from evaluation.storage import ResultsStorage

storage = ResultsStorage("data/evaluation")
results = storage.load_results()

# Custom analysis
for result in results:
    if result.domain == "computer_science":
        print(f"{result.test_id}: {result.overall_quality_score}")
```

---

## For Dissertation (Chapter 6)

### Generating Tables

```bash
# After evaluation completes
python scripts/analyze_results.py
```

This generates tables for Chapter 6:
- Table 6.1: Overall Technical Performance
- Table 6.2: Performance by Domain
- Table 6.3: Performance by Difficulty Level
- Table 6.4: Architectural Phase Comparison
- Component Breakdown Analysis
- Edge Case Analysis
- Statistical Summary

### Key Findings to Report

1. **Success Rate**: What % of tests completed successfully?
2. **Generation Speed**: Median generation time
3. **Quality Scores**: Mean prerequisite accuracy, difficulty progression
4. **Domain Independence**: ANOVA test across domains
5. **Edge Case Robustness**: Success rate on edge cases

### Statistical Significance

With N=35 tests:
- **t-tests**: Compare means (e.g., beginner vs advanced performance)
- **ANOVA**: Test domain differences
- **Chi-square**: Test categorical associations

Example:
```python
from scipy import stats

# Compare CS vs Math quality scores
cs_scores = df[df['domain']=='computer_science']['overall_quality_score']
math_scores = df[df['domain']=='mathematics']['overall_quality_score']

t_stat, p_value = stats.ttest_ind(cs_scores, math_scores)
print(f"p-value: {p_value:.4f}")
# If p < 0.05, difference is statistically significant
```

---

## Version History

### v1.0.0 (2025-10-30)
- Initial release
- 35 test cases across 4 domains
- 34 metrics per test
- CSV + JSON storage
- Crash recovery support

---

## References

- Design Science Research Methodology (Hevner et al., 2004)
- Statistical Power Analysis (Cohen, 1988)
- Reproducible Research (Peng, 2011)

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review logs: `data/evaluation/errors.jsonl`
3. Enable debug logging: `--log-level DEBUG`

**Project Repository:** MSc AI Dissertation - Syllabus Generation
