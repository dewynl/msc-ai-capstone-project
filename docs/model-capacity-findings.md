# Model Capacity Findings: CodeT5-Small Limitations

## Executive Summary

Testing revealed **CodeT5-small (60M parameters) has a hard capacity limit of ~3 modules per syllabus**. This is a fundamental architectural constraint that significantly limits system utility for real-world courses.

## Experimental Results

### Test 1: 3 Modules (Training Average)
- **Status**: ✅ Generates coherent output
- **Output length**: ~900-1200 chars
- **Structure**: Complete with all sections
- **Quality**: Acceptable

### Test 2: 5 Modules (Training Maximum)
- **Status**: ❌ Complete failure
- **Output length**: 590-724 chars (35% shorter)
- **Structure**: Malformed
  - Modules appearing inside "## Learning Objectives" section
  - Missing "## Module Sequence" headers
  - Incomplete generation mid-sentence
- **Parser failures**: "Failed to parse module sequence"
- **Quality**: Unusable

## Root Cause Analysis

### Training Data Design
The training data in `create_clean_training_data.py` was deliberately limited:

```python
target_counts={"modules": 3, "activities": 4, "assessments": 2}
```

**Distribution**:
- Modules offered: 2-5 (avg 3.6)
- Model behavior: Selects 100% of offered components
- Input length: 560-1516 chars (avg 993)

### Why This Limitation Exists

1. **Model architecture**: CodeT5-small = 60M parameters, 512 token context window
2. **Conservative design**: Ensure reliable generation for small examples
3. **Training simplicity**: Easier to validate 3-module syllabi than complex 10-module courses

## Real-World Impact

### Typical Course Requirements
- **Introduction to Programming**: 8-10 modules
  - Variables, data types, control flow, loops, functions, lists, dictionaries, string manipulation, file I/O, error handling
- **Data Structures**: 10-12 modules
- **Machine Learning**: 8-10 modules

### Current System Capability
- **Maximum reliable output**: 3 modules
- **Coverage**: ~30-37% of a typical course
- **Result**: Incomplete, non-viable syllabi for real courses

## Attempted Solutions

### Option 1: Test Training Maximum (5 modules)
**Hypothesis**: Model saw examples with 5 modules during training, might handle it.

**Result**: ❌ FAILED
- Generated malformed output
- Incomplete sections
- Parser failures
- Unusable quality

**Conclusion**: Training maximum ≠ model capacity. Just because training data included 5-module examples doesn't mean the 60M parameter model learned to handle that complexity reliably.

### Option 2: Increase Context (Not Tested)
**Approach**: Use T5-base (220M params, longer context)

**Status**: Not implemented (requires retraining)

**Expected outcome**: ✅ Would likely support 8-10 modules

**Trade-offs**:
- 3.6x larger model (60M → 220M)
- Slower inference
- Higher memory requirements
- Requires retraining (days of compute)

## Implications for Dissertation

### System Limitations Section
1. **Fundamental constraint**: CodeT5-small cannot generate complete real-world syllabi
2. **Training vs inference mismatch**: Conservative training data limits production utility
3. **Trade-off**: Model size vs. system capability

### Future Work Recommendations
1. **Retrain with T5-base (220M)**: Support 8-10 modules
2. **Redesign training data**: Offer 10-15 modules, train model to select best 5-8
3. **Hierarchical generation**: Generate course outline first, then expand each section

### Evaluation Considerations
- System demonstrates **proof-of-concept** for AI syllabus generation
- Pedagogical quality evaluation valid for 3-module syllabi
- Real-world deployment requires larger model

## Conclusion

The 3-module limitation is **not a bug but a fundamental capacity constraint** of:
1. Model size (CodeT5-small = 60M parameters)
2. Training data design (intentionally limited to 3 modules average)
3. Conservative architecture choices

This represents a **significant compromise in system utility** but validates the core approach. Scaling to T5-base would resolve the limitation at cost of compute/inference speed.

## Metadata

- **Date**: 2025-01-29
- **Experiment**: Model capacity testing
- **Models tested**: CodeT5-small (60M params)
- **Training checkpoint**: checkpoint-196 (15 epochs, eval loss 1.4677)
- **Test cases**: 3 modules (success), 5 modules (failure)
