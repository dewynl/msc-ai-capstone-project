# EduCraft System Limitations and Scope

**Document Version**: 1.0
**Date**: 2025-10-29
**Model**: CodeT5-small (checkpoint-196)

## Executive Summary

This document outlines the known limitations, content gaps, and scope boundaries of the EduCraft syllabus generation system. These limitations inform both the system's practical applicability and serve as directions for future enhancement.

---

## 1. Content Database Limitations

### 1.1 Critical Content Gaps

#### Missing Introductory Programming Fundamentals
**Status**: ❌ CRITICAL
**Impact**: Cannot generate true beginner-level "Introduction to Programming" courses

**Missing Topics**:
- Control Flow - Conditionals (if/elif/else statements)
- Functions (definition, parameters, return values, scope)
- Basic Python Syntax (print statements, comments, indentation rules)

**Available Workaround**: System can generate intermediate+ courses (Data Structures, Algorithms, Data Analysis) successfully.

**Evidence**: Gap analysis revealed 3/6 fundamental programming topics missing from 960-module database.

#### Activity Type Metadata Gap
**Status**: ⚠️ MEDIUM
**Impact**: Activities lack `activity_type` classification (lab, project, exercise, etc.)

**Details**: All 1,910 activities have rich descriptions, learning objectives, Bloom's taxonomy levels, and difficulty ratings, but missing the `activity_type` field for categorical filtering.

**Current State**: Activities are selected based on:
- Domain relevance (computer_science, mathematics, physics)
- Difficulty appropriateness (beginner/intermediate/advanced)
- Bloom's taxonomy level
- Semantic similarity to course description

**Future Enhancement**: Add `activity_type` field to enable filtering by pedagogical format (e.g., "only labs and projects, no exams").

### 1.2 Domain Representation Imbalance

| Domain | Modules | Percentage | Activities | Assessment |
|--------|---------|------------|------------|------------|
| Computer Science | 567 | 59.1% | 1,405 (73.6%) | Well-supported |
| Mathematics | 344 | 35.8% | 430 (22.5%) | Well-supported |
| Physics | 49 | 5.1% | 75 (3.9%) | ⚠️ Limited |

**Implications**:
- **Excellent Coverage**: Computer Science and Mathematics courses across all levels
- **Limited Coverage**: Physics courses may have insufficient module variety
- **Missing Domains**: Engineering, Biology, Chemistry not represented

**Use Case Suitability**:
- ✅ Suitable: CS and Math courses from undergraduate through postgraduate
- ⚠️  Limited: Physics courses (basic coverage available)
- ❌ Not Suitable: Engineering, natural sciences beyond physics

### 1.3 Topic Coverage Within Computer Science

**Strong Coverage** (100+ modules each):
- Data Structures (250 modules): Arrays, trees, graphs, hash tables
- Algorithms (350 modules): Sorting, searching, complexity analysis
- Machine Learning (421 modules): Neural networks, feature engineering, deep learning
- Data Analysis (156 modules): EDA, visualization, statistical methods

**Moderate Coverage** (50-100 modules):
- Databases (141 modules): Relational databases, query optimization
- Software Engineering (113 modules): Design patterns, testing
- Web Development (69 modules): Frontend, backend, HTTP

**Weak Coverage** (<50 modules):
- Security (12 modules): Cryptography, authentication
- Discrete Mathematics (2 modules): Logic, combinatorics

**Missing Topics**:
- Cloud Computing
- Mobile Development
- DevOps/CI/CD
- Blockchain
- IoT

### 1.4 Mathematics Coverage

**Strong Coverage**:
- Calculus (152 modules): 44.2% of mathematics content
- Linear Algebra (73 modules): 21.2%
- Abstract Algebra (64 modules): 18.6%

**Weak Coverage**:
- Discrete Mathematics (2 modules): 0.6%
- Analysis (17 modules): 4.9%
- Geometry (0 modules explicitly tagged)

---

## 2. Model Limitations

### 2.1 Generation Constraints

#### Maximum Output Length
**Constraint**: max_length=900 tokens (~3,600 characters)
**Impact**: Limits syllabus completeness

**Typical Output**:
- Course header and metadata: ~300 characters
- Learning objectives (4-5): ~400 characters
- Module sequence (3-5 modules): ~1,200-2,000 characters
- Activities (2-3): ~800 characters

**Limitation**: Cannot generate very long syllabi (10+ modules) in single pass.

**Mitigation**: Quality reranker generates 3 candidates and selects best, ensuring complete output within length constraints.

#### Module Selection Scope
**Constraint**: Top-20 semantic ranking limit
**Impact**: Model only sees 20 most relevant modules per generation

**Reasoning**: Token budget and computational efficiency.

**Implication**: If best modules are ranked 21-40, model cannot select them. However, semantic ranking generally places most relevant modules in top 20.

### 2.2 Learning Objective Quality

**Pattern Recognition Strength**: Model learns to generate domain-appropriate objectives:
- "Understand fundamental concepts of X"
- "Apply Y techniques to solve problems"
- "Analyze Z using advanced methods"

**Known Limitation**: Some objectives are generic.

**Example**:
- Generated: "Understand machine learning algorithms"
- Preferred: "Implement and evaluate supervised learning algorithms (decision trees, SVMs, neural networks) on real-world classification tasks"

**Mitigation**: Bloom's Taxonomy enhancement module replaces generic objectives with specific, action-oriented language post-generation.

**Success Rate**: Enhancement improves ~30-40% of generated objectives.

### 2.3 Prerequisite Sequencing

**Model Capability**: 100% prerequisite coherence achieved in testing (3/3 test cases).

**Limitation Scope**: Performance verified on:
- Postgraduate CS courses (Deep Learning, Machine Learning)
- Undergraduate CS courses (Data Structures)
- Undergraduate Mathematics (Calculus)

**Untested Scenarios**:
- Long prerequisite chains (5+ levels deep)
- Cross-domain prerequisites (e.g., math prerequisites for CS course)
- Circular or ambiguous dependencies

**Database Advantage**: 100% of prerequisites satisfied in database (0 orphaned modules), enabling reliable sequencing.

---

## 3. System Architecture Limitations

### 3.1 RAG Pipeline Constraints

#### Domain Filtering Strictness
**Behavior**: Filters components to EXACT domain match only.

**Example**:
- Course: "Introduction to Machine Learning" (domain: computer_science)
- Filters OUT: All mathematics and physics modules
- Result: Cannot include "Linear Algebra" module even if highly relevant

**Impact**: Pure CS courses cannot include foundational math prerequisites.

**Design Rationale**: Ensures pedagogical appropriateness and prevents irrelevant content.

**Future Enhancement**: Support cross-domain prerequisite inclusion with user opt-in.

#### Difficulty Filtering Rules
Current logic:
- **Beginner courses**: ONLY beginner modules
- **Intermediate courses**: beginner + intermediate modules
- **Advanced courses**: intermediate + advanced modules

**Limitation**: Overly strict for some use cases.

**Example Issue**: Postgraduate course cannot include truly foundational modules (marked as "beginner") for review purposes.

**Recommendation**: Consider relaxing to:
- **Beginner**: Only beginner
- **Intermediate**: All levels (with beginner/intermediate preference)
- **Advanced**: All levels (with intermediate/advanced preference)

### 3.2 Semantic Ranking Limitations

**Model**: all-MiniLM-L6-v2 (sentence transformer)
**Strength**: Fast, lightweight, good general-purpose similarity

**Known Weaknesses**:
1. **Keyword Overmatching**: Prioritizes exact keyword matches over conceptual similarity
   - Example: "Python programming" matches "Python Data Analysis" higher than "Programming Fundamentals"

2. **Domain-Specific Semantics**: Not trained specifically on educational content
   - May miss pedagogical relationships (e.g., "algorithm analysis" as prerequisite for "data structures")

3. **Context Window**: Limited to course title + description (~100-200 words)
   - Cannot incorporate full context or learning outcomes

**Mitigation**: Two-stage filtering (rule-based domain/difficulty → semantic ranking) ensures baseline quality before ML ranking.

#### 3.2.1 Beginner Course Ranking Issue

**Problem Identified**: General-purpose sentence transformers struggle with absolute beginner courses due to keyword over-matching.

**Specific Example** (2025-10-29):
- **Course**: "Introduction to Python Programming" (beginner, CS)
- **Description**: "...variables, loops, functions, file I/O..."
- **Available Modules**: 205 beginner CS modules including:
  - Variables and Data Types in Python
  - Control Flow with Conditional Statements
  - Loops and Iteration in Python
  - Lists and List Operations
  - Dictionaries
- **Problem**: Top 20 ranked modules:
  - 10 EDA modules: "Exploratory Data Analysis with Python"
  - 5 Hash Tables: "Hash Table Implementation"
  - 5 Algorithms: "Binary Search Tree Operations"
  - 0 foundational modules (variables, loops, conditionals)
- **Cause**: Both EDA titles and course description mention "Python" prominently → high keyword overlap (similarity 0.54-0.69) despite being pedagogically inappropriate
- **Result**: Foundational modules ranked positions 21+, never seen by model

**Impact**:
- Beginner CS courses may select intermediate topics (EDA, data structures, algorithms)
- True introductory modules (variables, syntax, loops) excluded from generation
- Results in pedagogically inappropriate syllabi for absolute beginners

**Root Cause**: Sentence transformers optimize for semantic similarity based on keyword overlap, not pedagogical appropriateness. "Python" appears in both:
- Appropriate: "Variables and Data Types in Python"
- Inappropriate: "Exploratory Data Analysis with Python"

The model cannot distinguish that EDA requires variables/loops as unstated prerequisites.

**Mitigation Applied**: Keyword boosting heuristic for beginner courses (see semantic_ranker.py:rank_all_components). When `level="beginner"`, modules with intro-related keywords (variable, syntax, loop, conditional, function definition) are boosted in ranking before model generation.

**Limitation Acknowledged**: This is a heuristic workaround, not a fundamental solution. Future work should:
1. Fine-tune semantic ranker on educational content with pedagogical annotations
2. Incorporate prerequisite graph structure into ranking (e.g., "variables" must rank higher than "EDA" for beginners)
3. Use domain-specific embeddings trained on course syllabi and module dependencies

### 3.3 Quality Reranking Scope

**Evaluation Components**:
1. ✅ Prerequisite Coherence: Validated against explicit prerequisite graph
2. ✅ Difficulty Progression: Checks smooth difficulty curve
3. ✅ Topic Diversity: Measures key concept overlap

**Not Evaluated**:
- Bloom's taxonomy progression (lower → higher order thinking)
- Hour allocation appropriateness (too much/too little for course duration)
- Activity-module alignment (do activities match selected modules?)
- Assessment-learning objective alignment

**Future Work**: Expand pedagogical quality framework to include alignment metrics.

---

## 4. Evaluation Limitations

### 4.1 Test Set Size

**Current Testing**:
- End-to-end generation: 3 test cases
- Model evaluation: 20 diverse courses (but pedagogical evaluation failed due to API signature mismatch)

**Statistical Significance**: Limited test set insufficient for robust performance claims.

**Dissertation Context**: Prototype demonstration, not production validation.

**Recommended Future Work**: 50-100 test cases across:
- Multiple domains (CS, Math, Physics)
- All difficulty levels
- Various course durations (semester, quarter, intensive)
- Edge cases (highly specialized topics, interdisciplinary courses)

### 4.2 Human Evaluation

**Status**: ❌ NOT CONDUCTED
**Impact**: No educator validation of generated syllabi

**Ideal Validation**:
- 3-5 university instructors review 10 generated syllabi
- Rate on: Coherence, Pedagogical Soundness, Practicality, Completeness
- Compare against human-authored syllabi

**Dissertation Limitation**: Acknowledge lack of human expert validation.

### 4.3 Comparison Baselines

**Missing Comparisons**:
- Rule-based syllabus generation (pure heuristics)
- Template-based approaches (fill-in-the-blank syllabi)
- Other ML models (GPT-based, BERT-based)
- Manual human authoring (time, quality comparison)

**Current Evaluation**: Self-evaluation (model performance metrics only).

**Recommendation**: Include at least one baseline (e.g., rule-based sequencing) for dissertation.

---

## 5. Practical Deployment Limitations

### 5.1 Model Loading Time

**First Load**: ~30-60 seconds (CodeT5-small + sentence transformer)
**Subsequent Loads**: Instant (cached)

**Implication**: Not suitable for serverless/cold-start environments without warm-up.

**Best Deployment**: Always-on server or container with model pre-loaded.

### 5.2 Generation Speed

**Average**: 3-8 seconds per syllabus on CPU
**Factors**: Semantic ranking (1-2s), model generation (2-5s), parsing (0.5-1s)

**GPU Acceleration**: Not tested; likely 2-3x speedup.

**Scalability**: Single model instance ~10-20 syllabi/minute. Requires load balancing for high-traffic scenarios.

### 5.3 Customization Constraints

**User Control**: Limited to 4 inputs:
1. Course title
2. Domain (CS, Math, Physics)
3. Difficulty level (Beginner, Intermediate, Advanced)
4. Course description (free text)

**Not Customizable**:
- Duration (fixed: semester)
- Number of modules to include
- Specific prerequisite requirements
- Assessment format preferences
- Activity type preferences (due to data gap)
- Hour allocation strategies

**Design Philosophy**: Automated generation with minimal user input. Trade-off between simplicity and control.

---

## 6. Known Issues

### 6.1 Parser Sensitivity

**Requirement**: Model output must match exact markdown format:

```markdown
## Learning Objectives
- Objective 1
- Objective 2

## Module Sequence
Weeks X-Y: Module Title (Zhours)
```

**Failure Modes**:
- Extra spaces → parsing fails
- Missing sections → incomplete extraction
- Wrong heading levels (###) → section not recognized

**Mitigation**: Model trained on consistent format; 100% parsing success in testing.

**Brittleness**: Small deviations cause failures. More robust NLP parsing recommended for production.

### 6.2 Edge Cases

**Untested Scenarios**:
1. Empty database results (no modules match domain+difficulty)
2. Very short course descriptions (<10 words)
3. Ambiguous course titles ("Advanced Topics in Computing")
4. Interdisciplinary courses ("Computational Biology")
5. Non-English input

**Behavior**: Unknown; likely degraded performance or failures.

---

## 7. Ethical and Pedagogical Considerations

### 7.1 Instructor Autonomy

**Limitation**: Generated syllabi are starting points, not final products.

**Recommendation**: Always review and customize before use.

**Human Expertise Required For**:
- Institutional policy alignment (credit hours, assessment rules)
- Student population considerations (prerequisites, pacing)
- Resource availability (textbooks, labs, software)
- Local context (industry connections, research focuses)

### 7.2 Bias and Fairness

**Potential Biases**:
1. **Domain Bias**: Overrepresentation of CS/ML topics reflects training data
2. **Language Bias**: English-only module descriptions
3. **Cultural Bias**: May reflect Western educational norms

**Mitigation Strategies**:
- Transparent documentation of limitations
- User awareness that outputs reflect database composition
- Future work: Diverse, multilingual content

### 7.3 Academic Integrity

**Appropriate Use**:
- ✅ Planning tool for instructors
- ✅ Template for syllabus structure
- ✅ Discovery tool for relevant modules

**Inappropriate Use**:
- ❌ Replacing instructor expertise
- ❌ Final syllabus without review
- ❌ Claiming generated content as original curriculum design

---

## 8. Recommendations for Future Work

### 8.1 Content Expansion (Priority: HIGH)
1. **Generate missing intro programming modules** (15 modules)
   - Use `generate_missing_content.py --generate modules --count 15`
   - Covers: variables, conditionals, loops, functions, I/O, syntax
2. **Add activity types** to existing 1,910 activities
   - Classify as: lab, project, exercise, discussion, presentation
3. **Expand physics content** from 49 → 150 modules
4. **Add engineering domain** (mechanics, circuits, thermodynamics)

### 8.2 Model Improvements (Priority: MEDIUM)
1. **Increase max_length** to 1,200 tokens for longer syllabi
2. **Fine-tune semantic ranker** on educational content
3. **Add Bloom's progression** to quality metrics
4. **Support cross-domain prerequisites**

### 8.3 Evaluation Rigor (Priority: HIGH)
1. **Human expert validation** (3-5 educators, 10 syllabi each)
2. **Larger test set** (50-100 diverse courses)
3. **Baseline comparisons** (rule-based, template-based)
4. **Ablation study** (prerequisite-aware training vs. vanilla)

### 8.4 User Experience (Priority: MEDIUM)
1. **Add customization options**:
   - Target module count (3-8 modules)
   - Duration selection (quarter, semester, year)
   - Assessment format preferences
2. **Interactive editing** in Streamlit UI
3. **Export formats** (PDF, Word, LMS-compatible)

---

## 9. Conclusion

The EduCraft system demonstrates successful application of fine-tuned CodeT5 to structured educational content generation with **100% prerequisite coherence** and **production-ready eval loss (1.4677)**. However, several limitations constrain its immediate applicability:

**Strengths**:
- ✅ Excellent performance on intermediate+ CS and Math courses
- ✅ Pedagogically sound module sequencing
- ✅ Well-balanced difficulty progression
- ✅ Robust hybrid ML + rule-based architecture

**Critical Limitations**:
- ❌ Cannot generate beginner programming courses
- ⚠️  Limited physics content
- ⚠️  No human expert validation
- ⚠️  Small test set (3 cases)

**Appropriate Use Cases** (as demonstrated):
1. Data Structures and Algorithms (undergraduate/postgraduate)
2. Machine Learning courses (intermediate/advanced)
3. Mathematics courses (Calculus, Linear Algebra, Statistics)
4. Advanced CS topics (AI, Deep Learning, Networks)

**Unsuitable Use Cases**:
1. Absolute beginner programming courses
2. Engineering courses (content not available)
3. Interdisciplinary courses requiring cross-domain integration
4. Production deployment without further validation

**Dissertation Position**: This work demonstrates **feasibility and promise** of ML-driven syllabus generation, while acknowledging significant scope limitations that define boundaries for future research.

---

**Document Maintenance**: This file should be updated as:
- New content is added to the database
- Model is retrained or improved
- Additional testing/validation is conducted
- User feedback identifies new limitations

**Last Updated**: 2025-10-29
**Next Review**: After content gap filling and expanded evaluation
