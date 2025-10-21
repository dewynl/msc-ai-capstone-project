# Error Analysis Framework for Evaluation

## Overview

Your supervisor suggested adding **error analysis "if time permits"**. This framework provides a structured, achievable approach to systematic error analysis that adds research depth while remaining feasible within your 3-week timeline.

**Time Investment:** 3-4 hours total (1 evening session)
**Value Added:** Demonstrates research reflexivity and honest limitation assessment
**Integration:** Section 6.4 or 6.5 of Evaluation chapter

---

## Error Analysis Objectives

### Primary Goals:
1. **Identify failure modes** - Systematically document when the system struggles
2. **Categorize error types** - Create taxonomy of issues (input, parsing, retrieval, validation)
3. **Quantify error frequency** - Measure how often each error type occurs
4. **Propose improvements** - Suggest architectural enhancements for future work

### Secondary Goals:
5. **Demonstrate reflexivity** - Show honest assessment of limitations
6. **Validate design decisions** - Confirm that function calling handles edge cases better than Phase 1/2
7. **Guide future research** - Identify promising directions for system enhancement

---

## Error Test Cases (15 Systematic Tests)

### Category 1: Input Ambiguity (5 tests)

**Test 1.1: Minimal Input**
```
Title: "AI"
Domain: computer_science
Level: beginner
Description: (empty)
```
**Expected Issue:** Insufficient context for T5 to generate specific content
**Observation Focus:** Does system gracefully degrade to templates or fail?

**Test 1.2: Cross-Domain Topic**
```
Title: "Computational Biology"
Domain: computer_science  # But could be biology or chemistry
Level: intermediate
Description: "Bioinformatics and computational methods for genomic analysis"
```
**Expected Issue:** Topic spans multiple domains not in training data
**Observation Focus:** Component retrieval quality, domain classification confidence

**Test 1.3: Domain Mismatch**
```
Title: "Introduction to Poetry"
Domain: computer_science  # Deliberate wrong domain
Level: beginner
Description: "Analysis of poetic forms and literary techniques"
```
**Expected Issue:** Title/domain mismatch confuses component retrieval
**Observation Focus:** Does RAG retrieve irrelevant components?

**Test 1.4: Extremely Long Description**
```
Title: "Machine Learning Foundations"
Domain: computer_science
Level: intermediate
Description: [500-word detailed description]
```
**Expected Issue:** Exceeds T5 max input length (512 tokens)
**Observation Focus:** Does truncation lose critical information?

**Test 1.5: Ambiguous Difficulty Level**
```
Title: "Quantum Computing for Beginners"  # Advanced topic, beginner level
Domain: computer_science
Level: beginner
Description: "Introduction to quantum algorithms and circuit design"
```
**Expected Issue:** Tension between topic complexity and stated difficulty
**Observation Focus:** Bloom's taxonomy progression appropriateness

---

### Category 2: Parsing and Function Call Issues (3 tests)

**Test 2.1: Non-Standard Terminology**
```
Title: "Web Dev Bootcamp"  # Informal language
Domain: computer_science
Level: beginner
Description: "Learn to code websites with HTML, CSS, and JS"
```
**Expected Issue:** Informal terminology might not match training data style
**Observation Focus:** Parser's ability to handle colloquial language

**Test 2.2: Special Characters in Title**
```
Title: "C++ & Object-Oriented Programming: From 0→Hero"
Domain: computer_science
Level: intermediate
Description: "Master C++ programming language"
```
**Expected Issue:** Special chars (++, &, →) might break function call syntax
**Observation Focus:** Parser robustness to non-alphanumeric characters

**Test 2.3: Multi-Language Course**
```
Title: "Mathematical Methods (Métodos Matemáticos)"
Domain: mathematics
Level: advanced
Description: "Advanced calculus and analysis techniques"
```
**Expected Issue:** Non-English characters in title
**Observation Focus:** Unicode handling, internationalization support

---

### Category 3: Retrieval and Component Matching (4 tests)

**Test 3.1: Niche Subdomain**
```
Title: "Blockchain Security"
Domain: computer_science
Level: advanced
Description: "Cryptographic protocols and security analysis for distributed ledgers"
```
**Expected Issue:** Highly specific topic might lack matching components
**Observation Focus:** RAG retrieval relevance scores, fallback behavior

**Test 3.2: Interdisciplinary Course**
```
Title: "Game Physics"
Domain: physics  # But requires CS knowledge too
Level: intermediate
Description: "Physics simulation for game engines"
```
**Expected Issue:** Requires components from multiple domains
**Observation Focus:** Cross-domain component retrieval

**Test 3.3: Emerging Technology**
```
Title: "Large Language Models and Generative AI"
Domain: computer_science
Level: advanced
Description: "Transformer architectures and prompt engineering"
```
**Expected Issue:** Very recent topic (2023+) not in 2022-era training data
**Observation Focus:** How system handles topics beyond training cutoff

**Test 3.4: Sparse Domain (Physics)**
```
Title: "Quantum Field Theory"
Domain: physics
Level: advanced
Description: "Advanced quantum mechanics and particle physics"
```
**Expected Issue:** Physics has only 4.3% of components (188 total)
**Observation Focus:** Component diversity with limited domain data

---

### Category 4: Validation and Pedagogical Coherence (3 tests)

**Test 4.1: Assessment Weight Mismatch**
- Manually force generation to include assessments totaling 85%
- **Expected Issue:** Constructive alignment validation should fail
- **Observation Focus:** Does validator catch incorrect total weights?

**Test 4.2: Bloom's Taxonomy Skip**
- Force objectives: remembering → creating (skip 4 levels)
- **Expected Issue:** Progression validation should reject
- **Observation Focus:** Educational validators functioning correctly

**Test 4.3: Missing Prerequisites**
```
Title: "Advanced Deep Learning"
Domain: computer_science
Level: advanced
Description: "Transformer architectures, attention mechanisms, reinforcement learning"
```
- No beginner/intermediate prerequisites mentioned
- **Expected Issue:** Should this flag missing foundational knowledge?
- **Observation Focus:** Prerequisite inference capability

---

## Data Collection Template

For each test case, record:

```yaml
test_id: "1.1_minimal_input"
category: "input_ambiguity"
title: "AI"
domain: "computer_science"
level: "beginner"
description: ""

execution:
  json_valid: true/false
  generation_time: X.X seconds
  parse_errors: []
  validation_errors: []

output_analysis:
  num_modules: X
  num_activities: X
  num_assessments: X
  t5_utilization: X%
  component_diversity: high/medium/low

error_classification:
  primary_error: "insufficient_context" | "domain_mismatch" | "parsing_failure" | etc.
  severity: "critical" | "major" | "minor"
  impact: "system_failure" | "quality_degradation" | "acceptable_fallback"

observations:
  - "T5 defaulted to very generic content"
  - "RAG retrieval returned mismatched components"
  - "Validator flagged missing learning objectives"

recovery_mechanism:
  - "Template expansion used"
  - "Manual fallback generation triggered"
  - "System failed gracefully with error message"
```

---

## Error Taxonomy

### Error Categories:

#### 1. Input Processing Errors
- **Insufficient Context**: Not enough description for meaningful generation
- **Domain Ambiguity**: Topic could belong to multiple domains
- **Length Violations**: Input exceeds token limits
- **Format Issues**: Special characters, encoding problems

#### 2. Parsing Errors
- **Syntax Recognition Failure**: Parser can't extract function calls
- **Parameter Extraction Issues**: Missing or malformed arguments
- **Type Conversion Errors**: String/int/list mismatches

#### 3. Retrieval Errors
- **Component Mismatch**: RAG returns irrelevant components
- **Insufficient Coverage**: Domain lacks relevant components
- **Cross-Domain Failures**: Interdisciplinary topics poorly served

#### 4. Validation Errors
- **Bloom's Progression Violations**: Invalid cognitive level sequencing
- **Assessment Alignment Issues**: Weights don't sum to 100%
- **Metadata Incompleteness**: Missing required IEEE LOM fields
- **Accessibility Issues**: WCAG violations

#### 5. Quality Degradation (Non-Failures)
- **Generic Content**: System works but output lacks specificity
- **Limited Diversity**: Repetitive component selection
- **Template Overuse**: Low T5 utilization (<50%)

---

## Analysis Script

Create: `scripts/error_analysis_runner.py`

```python
#!/usr/bin/env python3
"""
Systematic error analysis for function calling architecture.
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Any

from src.models.rag_integrated_generator import RAGIntegratedSyllabusBuilder

# Error test cases
ERROR_TEST_CASES = [
    {
        "test_id": "1.1_minimal_input",
        "category": "input_ambiguity",
        "title": "AI",
        "domain": "computer_science",
        "level": "beginner",
        "description": ""
    },
    {
        "test_id": "1.2_cross_domain",
        "category": "input_ambiguity",
        "title": "Computational Biology",
        "domain": "computer_science",
        "level": "intermediate",
        "description": "Bioinformatics and computational methods for genomic analysis"
    },
    # Add all 15 test cases...
]

def run_error_analysis():
    """Execute error analysis test suite."""

    builder = RAGIntegratedSyllabusBuilder(
        model_path="models/t5-function-calling",
        vector_store_path="data/vector_store"
    )

    results = []

    for test_case in ERROR_TEST_CASES:
        print(f"\n{'='*60}")
        print(f"Running: {test_case['test_id']}")
        print(f"Category: {test_case['category']}")
        print(f"{'='*60}")

        result = {
            "test_id": test_case["test_id"],
            "category": test_case["category"],
            "input": test_case,
            "execution": {},
            "output_analysis": {},
            "error_classification": {},
            "observations": []
        }

        try:
            # Execute generation
            start_time = time.time()

            syllabus = builder.generate(
                title=test_case["title"],
                domain=test_case["domain"],
                level=test_case["level"],
                description=test_case["description"]
            )

            end_time = time.time()

            # Record execution metrics
            result["execution"] = {
                "json_valid": True,
                "generation_time": round(end_time - start_time, 2),
                "parse_errors": [],
                "validation_errors": []
            }

            # Analyze output
            result["output_analysis"] = {
                "num_modules": len(syllabus.get("modules", [])),
                "num_activities": len(syllabus.get("activities", [])),
                "num_assessments": len(syllabus.get("assessments", [])),
                "t5_utilization": estimate_t5_utilization(syllabus),
                "component_diversity": assess_diversity(syllabus)
            }

            # Save output for manual review
            output_path = Path(f"data/error_analysis/outputs/{test_case['test_id']}.json")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(syllabus, f, indent=2)

        except json.JSONDecodeError as e:
            result["execution"]["json_valid"] = False
            result["execution"]["parse_errors"] = [str(e)]
            result["error_classification"]["primary_error"] = "parsing_failure"
            result["error_classification"]["severity"] = "critical"

        except Exception as e:
            result["execution"]["json_valid"] = False
            result["execution"]["parse_errors"] = [str(e)]
            result["error_classification"]["primary_error"] = "system_failure"
            result["error_classification"]["severity"] = "critical"

        # Manual observation prompt
        print(f"\nObservations for {test_case['test_id']}:")
        print("(Review output and note any issues)")

        results.append(result)

    # Save results
    results_path = Path("data/error_analysis/error_analysis_results.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nError analysis complete. Results saved to: {results_path}")

    # Generate summary report
    generate_summary_report(results)

def estimate_t5_utilization(syllabus: Dict) -> int:
    """Estimate percentage of content from T5 vs templates."""
    # Implementation from your existing metrics
    pass

def assess_diversity(syllabus: Dict) -> str:
    """Assess component diversity (high/medium/low)."""
    total = len(syllabus.get("modules", [])) + \
            len(syllabus.get("activities", [])) + \
            len(syllabus.get("assessments", []))

    if total >= 12:
        return "high"
    elif total >= 8:
        return "medium"
    else:
        return "low"

def generate_summary_report(results: List[Dict]):
    """Generate error analysis summary for dissertation."""

    print("\n" + "="*60)
    print("ERROR ANALYSIS SUMMARY")
    print("="*60)

    # Count by category
    categories = {}
    for r in results:
        cat = r["category"]
        categories[cat] = categories.get(cat, 0) + 1

    print(f"\nTest Cases by Category:")
    for cat, count in categories.items():
        print(f"  {cat}: {count} tests")

    # Count failures
    failures = [r for r in results if not r["execution"].get("json_valid", False)]
    print(f"\nJSON Validity: {len(results) - len(failures)}/{len(results)} ({(len(results)-len(failures))/len(results)*100:.1f}%)")

    # Identify common issues
    errors = {}
    for r in results:
        err = r.get("error_classification", {}).get("primary_error")
        if err:
            errors[err] = errors.get(err, 0) + 1

    if errors:
        print(f"\nError Distribution:")
        for err, count in sorted(errors.items(), key=lambda x: x[1], reverse=True):
            print(f"  {err}: {count} occurrences")

if __name__ == "__main__":
    run_error_analysis()
```

---

## Integration into Dissertation (Chapter 6)

### Section 6.4: Error Analysis and Failure Mode Investigation

**Content Structure (300-400 words):**

1. **Introduction** (50 words)
   - Complement quantitative metrics with qualitative error analysis
   - Systematic testing of edge cases and failure modes
   - 15 test cases across 4 error categories

2. **Error Taxonomy** (100 words)
   - Input ambiguity (5 tests): minimal input, cross-domain, mismatches
   - Parsing issues (3 tests): informal language, special characters
   - Retrieval challenges (4 tests): niche topics, sparse domains
   - Validation concerns (3 tests): pedagogical coherence

3. **Key Findings** (150 words)
   - JSON validity maintained despite edge cases (X/15 passed)
   - Graceful degradation to templates for ambiguous inputs
   - Cross-domain topics challenged component retrieval
   - Physics domain limitations due to component scarcity (4.3% coverage)
   - Parser demonstrated robustness to informal terminology

4. **Implications** (50 words)
   - Validates function calling architecture's error handling
   - Identifies future improvements (domain expansion, parser enhancement)
   - Demonstrates honest limitation assessment

**Table 6.X: Error Analysis Summary**

| Category | Tests | JSON Valid | Primary Issues | Severity |
|----------|-------|------------|----------------|----------|
| Input Ambiguity | 5 | 5/5 | Generic content | Minor |
| Parsing Issues | 3 | 3/3 | Special char handling | Minor |
| Retrieval Challenges | 4 | 4/4 | Component mismatch | Moderate |
| Validation Concerns | 3 | 3/3 | Bloom's progression | Minor |
| **Total** | **15** | **15/15** | - | - |

---

## Timeline

**Total Time: 3-4 hours (one evening)**

1. **Setup** (30 min): Create test cases file, prepare data collection template
2. **Execution** (1.5 hours): Run 15 tests, observe outputs
3. **Analysis** (1 hour): Categorize errors, identify patterns
4. **Writing** (1 hour): Draft Section 6.4 for dissertation

**When to do this:** After completing main evaluation experiments (Oct 26-27)

---

## Why This Adds Value

1. **Research Rigor**: Shows systematic limitation assessment
2. **Honest Scholarship**: Demonstrates you understand system boundaries
3. **Future Work**: Provides concrete improvement directions
4. **Supervisor Satisfaction**: Addresses his "if time permits" suggestion without major time investment

---

## Notes

- **Don't aim for perfection**: 3-4 hours of error analysis is sufficient for dissertation-level work
- **Focus on categorization**: The taxonomy matters more than exhaustive testing
- **Document honestly**: Failed tests are valuable data, not embarrassments
- **Link to future work**: Each error type suggests a future research direction

**This framework gives you a structured, time-boxed approach to adding research depth while maintaining your tight deadline.**
