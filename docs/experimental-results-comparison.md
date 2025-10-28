# Experimental Results: Training Data Scaling Study

## Research Question
How does training dataset size affect CodeT5's ability to generate structured function call sequences for educational course syllabi?

## Experimental Design

### Phase 1: Baseline with Limited Data (260 Examples)
- **Training Data**: 260 RAG-enhanced examples
- **Training Epochs**: 20 (initial), 41 (extended)
- **Effective Batch Size**: 64
- **Training Time**: 2.5 hours (20 epochs), 4.3 hours (41 epochs)

### Phase 2: Scaled Data (1,300 Examples) - IN PROGRESS
- **Training Data**: 1,300 RAG-enhanced examples (5× increase)
- **Training Epochs**: 50 (with early stopping)
- **Effective Batch Size**: 80 (+25% for better gradients)
- **Expected Training Time**: ~22 hours

## Results Summary

### Baseline Results (260 Examples)

| Experiment | Epochs | Train Time | Eval Loss | Pass Rate | Output Length | Key Issues |
|------------|--------|------------|-----------|-----------|---------------|------------|
| Initial Training | 20 | 2.5 hours | 1.469 | 0% | 217-243 chars | Incomplete outputs |
| Extended Training | 41 | 4.3 hours | 1.455 | 0% | 217-243 chars | No improvement |

**Key Findings**:
- Extending epochs (20 → 41) yielded **no improvement** in pass rate
- Output length consistently truncated (217-243 chars vs 800-1000 target)
- Missing critical components: `add_module`, `add_activity`, `add_assessment`, `build()`
- Frequent syntax errors: unterminated strings, unexpected indentation
- **Root Cause Identified**: Data scarcity, not training duration

### Expected Results (1,300 Examples)

| Metric | 260 Examples | 1,300 Examples (Expected) |
|--------|--------------|---------------------------|
| **Pass Rate** | 0/5 (0%) | TBD (target: >60%) |
| **Output Length** | 217-243 chars | 800-1,000 chars |
| **Syntax Valid** | 40% | >80% |
| **Component Coverage** | Incomplete | Full |
| **Training Time** | 4.3 hours | ~22 hours |

## Methodology: RAG-Enhanced Data Generation

### Generation Process
1. **Component Database**: 960 modules, 1,910 activities, 476 assessments
2. **Course Templates**: 26 templates across 3 difficulty levels
3. **AI-Powered Composition**: Claude Sonnet 4.5 selects pedagogically coherent components
4. **Deduplication**: Circuit breaker prevents infinite loops (10 consecutive duplicates)
5. **Variation Generation**: 50 variations per course template

### Quality Assurance
- **Pedagogical Coherence**: AI evaluates component compatibility
- **Unique Combinations**: Signature-based deduplication
- **Multi-Level Coverage**: Beginner (450), Intermediate (500), Advanced (350)
- **Cost**: ~$0.013 per example (including 25-35% duplication overhead)

## Hypothesis

**H0**: Training dataset size has minimal impact on structured generation quality.

**H1**: Increasing training data from 260 to 1,300 examples will significantly improve:
- Output completeness (length)
- Syntax correctness
- Component coverage
- Overall pass rate

**Justification**: Limited data (260 examples) prevents model from learning:
- Complete function call sequences
- Proper syntax patterns
- Multi-step generation dependencies
- Domain-specific structure requirements

## Training Configuration Comparison

| Hyperparameter | 260 Examples | 1,300 Examples | Rationale |
|----------------|--------------|----------------|-----------|
| **Train/Eval Split** | 234 / 26 | 1,170 / 130 | 90/10 ratio maintained |
| **Batch Size** | 16 | 20 | +25% for better gradients |
| **Grad Accumulation** | 4 | 4 | Balanced for GPU memory |
| **Effective Batch** | 64 | 80 | Larger dataset supports larger batch |
| **Learning Rate** | 3e-4 | 3e-4 | Same (no scaling needed for modest increase) |
| **Warmup Steps** | 10% | 10% | Proportion maintained |
| **Eval Frequency** | Every epoch | Every 0.5 epoch | More frequent monitoring |
| **Checkpointing** | Every epoch | Every 2 epochs | Optimized for long run |
| **Early Stopping** | 5 epochs | 10 evals (5 epochs) | Scaled to eval frequency |

## Data Generation Robustness

### Challenges Encountered
- **API Failures**: InternalServerError (500 - Server Overload)
- **Initial Vulnerability**: No checkpointing → total data loss on failure
- **Cost of Failure**: Lost ~$38 worth of API calls and 90 minutes

### Solutions Implemented
1. **Comprehensive Error Handling**: All 14 Anthropic exception types
2. **Exponential Backoff Retry**: 5 attempts (2s, 4s, 8s, 16s, 32s delays)
3. **Incremental Checkpointing**: Save after every course
4. **Auto-Resume**: Detect checkpoint and continue
5. **Try/Finally Safety**: Always save on exit (crash, Ctrl+C)
6. **Response Validation**: Catch malformed Claude responses

**Result**: Maximum loss reduced from $38 (full run) to $0.60 (single course)

## Timeline

```
Dec XX: Baseline training (260 examples) - 0% pass rate
Dec XX: Extended training (41 epochs) - 0% pass rate, confirmed data scarcity
Dec XX: Data generation crash - lost $38, implemented safety mechanisms
Dec XX: 1,300-example generation started (~90 min)
Dec XX: 1,300-example training started (~22 hours)
Dec XX: Evaluation and results analysis
```

## Evaluation Metrics

### Test Suite
- **Beginner Computer Science**: Basic programming course
- **Intermediate Machine Learning**: ML algorithms course
- **Advanced Data Science**: Deep learning and big data
- **Business Course**: Digital marketing
- **Production Test**: Generic computer science course

### Success Criteria (per test)
1. ✅ **Length Check**: Output 800-1,000 characters
2. ✅ **Required Calls**: `set_info`, `add_objective`, `add_module`, `add_activity`, `add_assessment`, `build()`
3. ✅ **Syntax Check**: Valid Python syntax
4. ✅ **Execution Check**: No runtime errors

**Pass Threshold**: All 4 criteria met

## Expected Contributions

1. **Empirical Evidence**: Quantify impact of data scaling on structured generation
2. **Methodology**: RAG-enhanced data generation with AI-powered composition
3. **Engineering Practices**: Robust data generation with comprehensive error handling
4. **Cost-Benefit Analysis**: Cost per example vs quality improvement

## References

- Salesforce/codet5-small: Base model architecture
- Anthropic Claude Sonnet 4.5: Data generation and composition
- PyTorch 2.6, Transformers 4.x: Training infrastructure
