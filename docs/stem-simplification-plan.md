# STEM-Focused Syllabus Generation: Simplification Implementation Plan

## Overview
This document tracks the strategic pivot from multi-domain complexity to STEM-focused simplification for the MSc AI Capstone project on automated syllabus generation.

## Current State (As of September 14, 2025)

### ✅ What We Have
- **RAG-Enhanced Architecture**: Working T5 + ChromaDB system
- **Synthetic Data**: 22.1MB across 12 domains (over-complex)
  - 1,260 learning activities
  - 629 assessments  
  - 600+ modules
- **Vector Store**: 4,403 indexed components
- **T5 Model**: Fine-tuned T5-small on 352 syllabi
- **Performance**: 5.2s generation, 70.4 avg words, 6/8 components

### ❌ Current Problems
1. **Domain Overload**: 12 domains too complex for MSc scope
2. **Data Model Complexity**: Unnecessary fields (week numbers, prerequisites, domain tags)
3. **Synthetic Data Quality**: Spread thin across too many areas
4. **Evaluation Difficulty**: Hard to get credible expert review across all domains

## Target State: STEM-Focused System

### 🎯 Strategic Goals
1. **Domain Focus**: 4 STEM domains (Computer Science, Mathematics, Physics, Engineering)
2. **Simplified Data Model**: Remove complexity while maintaining pedagogical value
3. **Improved Quality**: Deeper, more credible synthetic data in focused areas
4. **Manageable Evaluation**: STEM experts can assess across related fields

### 📊 Success Criteria
- [ ] STEM-only synthetic dataset generated (CS, Math, Physics, Engineering)
- [ ] Simplified component schema implemented
- [ ] Vector store rebuilt with new data model
- [ ] T5 model retrained on simplified data
- [ ] Performance maintained or improved vs current system
- [ ] Educational coherence validated by STEM expert review

## Implementation Plan

### Phase 1: Data Model Redesign ✅ Status: Completed

#### 1.1 Define Simplified Schema ✅ COMPLETED
**Goal**: Create lean component structure without unnecessary complexity

**Components to Modify**:

```python
# NEW: Simplified Learning Activity
{
    "activity_id": str,
    "title": str,
    "description": str,
    "stem_domain": str,  # cs|math|physics|engineering
    "bloom_level": str,  # remember|understand|apply|analyze|evaluate|create
    "difficulty": str,   # beginner|intermediate|advanced
    "estimated_hours": int,  # 1-8 hours typical
    "learning_objectives": List[str],
    "instructions": str,
    "materials_needed": List[str],
    "assessment_method": str
}

# NEW: Simplified Assessment Component
{
    "assessment_id": str,
    "title": str,
    "description": str,
    "stem_domain": str,
    "assessment_type": str,  # exam|project|assignment|quiz|lab
    "difficulty": str,
    "estimated_hours": int,
    "learning_objectives": List[str],
    "criteria": List[str],
    "materials_needed": List[str]
}

# NEW: Simplified Course Module
{
    "module_id": str,
    "title": str,
    "description": str,
    "stem_domain": str,
    "key_concepts": List[str],
    "estimated_hours": int,
    "learning_objectives": List[str],
    "suggested_readings": List[str]
}
```

**Removed Fields**:
- ❌ `week_number` - T5 should determine sequencing
- ❌ `prerequisite_concepts` - Too complex for T5 to enforce
- ❌ `domain` (if too granular) - Replaced with `stem_domain`
- ❌ `estimated_workload` (complex) - Replaced with simple `estimated_hours`
- ❌ `module_id` references in activities - Removes rigid coupling

**Tasks**:
- [x] Update data models in `src/data/models.py` ✅ COMPLETED
- [x] Create schema validation functions ✅ COMPLETED  
- [ ] Update component generation prompts for STEM focus
- [x] Test schema with sample data generation ✅ COMPLETED

**✅ RESULTS ACHIEVED**:
- Created `src/data/models.py` with simplified dataclasses and enums
- Implemented full schema validation for all component types
- Successfully tested migration from complex to simple schema
- Generated sample data demonstrating new format works correctly
- All 4 STEM domains (CS, Math, Physics, Engineering) validated

#### 1.2 STEM Domain Content Strategy
**Goal**: Focus on 4 core STEM areas with natural overlap

**Domain Definitions**:
- **Computer Science**: Programming, algorithms, data structures, software engineering, AI/ML
- **Mathematics**: Calculus, algebra, statistics, discrete math, applied math
- **Physics**: Classical mechanics, electromagnetism, thermodynamics, quantum basics
- **Engineering**: System design, optimization, modeling, problem-solving methods

**Rationale**: These domains share:
- Mathematical foundations
- Logical reasoning patterns  
- Problem-solving methodologies
- Sequential skill building
- Quantitative assessment approaches

**Tasks**:
- [ ] Define content boundaries for each STEM domain
- [ ] Identify cross-domain concepts (math in physics, algorithms in engineering)
- [ ] Create domain-specific generation guidelines
- [ ] Plan expert reviewer recruitment for each domain

### Phase 2: Cost-Effective Data Migration ⏳ Status: Ready to Execute

#### 2.1 Extract Existing STEM Components ✅ COMPLETED
**Goal**: Salvage existing STEM components to minimize API costs and generation time

**Rationale**: Current dataset contains ~2,500 components across 12 domains. Extract STEM-relevant components first before expensive API generation.

**STEM Domain Mapping Strategy**:
```
Current Domain → New STEM Domain
"Computer Science" → computer_science
"Data Science" → computer_science  
"Mathematics" → mathematics
"Physics" → physics
"Software Development" → computer_science
```

**✅ ACTUAL RESULTS ACHIEVED** (September 21, 2025):
- **Cost Savings**: $66.92 saved in API calls (vs. predicted $2-4)
- **Time Savings**: 1,673 minutes saved in generation (vs. predicted 5-10 minutes)
- **Quality**: 100% validation success rate on extracted components
- **Actual extraction**: 3,346 STEM components from existing 4,395 total

**Component Distribution**:
- **Computer Science**: 2,226 components (excellent coverage)
- **Mathematics**: 945 components (strong coverage)  
- **Physics**: 175 components (adequate coverage)
- **Engineering**: 0 components (gap identified)

**Tasks**:
- [x] Create STEM extraction script (`src/data/extract_stem_components.py`) ✅ COMPLETED
- [x] Analyze current dataset for STEM component distribution ✅ COMPLETED
- [x] Extract and convert existing STEM components to simplified schema ✅ COMPLETED
- [x] Validate extracted components against new data model ✅ COMPLETED
- [x] Identify gaps in coverage (what's missing for target numbers) ✅ COMPLETED
- [x] Generate gap analysis report (how many new components needed) ✅ COMPLETED

**Key Insight**: Original dataset had no engineering components, requiring targeted generation for complete 4-STEM coverage.

#### 2.2 Update Generation Scripts ✅ COMPLETED  
**Goal**: Prepare API generation system for filling gaps only

**Scripts Created**:
- ✅ `src/data/stem_components_generator.py` (NEW - Created from scratch)
- ✅ Component-specific generation functions
- ✅ Data cleaning and validation pipelines

**Generation Strategy**:
- **Target Volume**: ~1000 total components (250 per STEM domain)
  - 150 learning activities per domain (600 total)
  - 60 assessments per domain (240 total)  
  - 40 modules per domain (160 total)
- **Quality over Quantity**: Deeper, more realistic STEM content
- **Cross-Domain Validation**: Ensure mathematical consistency

**Tasks**:
- [x] Update Claude API prompts for STEM-focused generation ✅ COMPLETED
- [x] Implement new schema in generation scripts ✅ COMPLETED
- [x] Add domain-specific validation rules ✅ COMPLETED
- [x] Generate Computer Science components (test domain) ✅ COMPLETED
- [ ] Generate only missing components after extraction (reduced scope)
- [ ] Run deduplication and quality checks on combined dataset
- [ ] Validate cross-domain mathematical consistency

**✅ RESULTS ACHIEVED**:
- Created complete STEM-focused generation system (`stem_components_generator.py`)
- Successfully tested with all 4 STEM domains (CS, Math, Physics, Engineering)
- Generated and validated test components: 4 activities + 2 assessments
- 100% validation success rate against simplified schema
- Confirmed API integration and component quality
- Ready for full-scale generation

#### 2.3 Gap-Filling Generation ⏳ Status: Pending extraction analysis
**Goal**: Use API generation only for missing components after extraction

**Revised Strategy** (After Extraction):
- **Extract first**: Salvage 200-400 existing STEM components
- **Analyze gaps**: Determine what's missing for target numbers
- **Generate efficiently**: Only create components needed to reach targets
- **Estimated new generation**: 100-150 components (vs original 260)

**Cost-Benefit Analysis**:
```
Original Plan: Generate 260 components × $0.02 = ~$5.20
New Plan: Extract 200 + Generate 60 × $0.02 = ~$1.20
Savings: $4.00 + 8 minutes generation time
```

#### 2.4 Training Data Assembly
**Goal**: Create simplified syllabi from combined extracted + generated components

**Assembly Strategy**:
- **Target**: 200-300 complete syllabi across STEM domains
- **Distribution**: 50-75 syllabi per domain
- **Component Sources**: Extracted existing + newly generated components
- **Natural Progression**: Let T5 learn STEM concept ordering from data

**Tasks**:
- [ ] Update syllabus assembly logic for new schema
- [ ] Combine extracted and generated components into unified dataset
- [ ] Generate Computer Science syllabi  
- [ ] Generate Mathematics syllabi
- [ ] Generate Physics syllabi
- [ ] Generate Engineering syllabi
- [ ] Create train/validation/test splits
- [ ] Validate assembled syllabi for pedagogical coherence

### Phase 3: System Updates 🔄 Status: In Progress

#### 3.1 Vector Store Rebuilding ✅ COMPLETED (September 21, 2025)
**Goal**: Rebuild ChromaDB with simplified components

**✅ COMPLETED TASKS**:
- [x] Domain reclassification: 1,747 components correctly classified across STEM domains
- [x] Vector store rebuilt with 7,166 components (up from 5,256)
- [x] Multi-domain distribution: CS (1,599), Math (795), Engineering (769), Physics (180), Biology (3), Chemistry (1)
- [x] Cross-domain search validation confirmed working
- [x] Performance maintained: ~0.05-0.09s query times

**✅ RESULTS ACHIEVED**:
- **Better Relevance**: Multi-domain classification improves semantic matching
- **Cross-Domain Queries**: System now returns results from multiple domains correctly
- **Quality Validation**: All 7,166 components indexed successfully

#### 3.2 RAG Pipeline Updates
**Goal**: Update retrieval and assembly logic for new data model

**Components to Update**:
- `src/rag/query_processor.py`
- `src/rag/retrieval_pipeline.py` 
- `src/rag/rag_t5_generator.py`

**Tasks**:
- [ ] Update query processing for STEM domains
- [ ] Modify component selection logic (no prerequisite checking)
- [ ] Update prompt templates for simplified schema
- [ ] Test component assembly without rigid sequencing
- [ ] Validate pedagogical coherence in generated content

### Phase 4: Model Retraining ⏳ Status: Not Started

#### 4.1 T5 Model Retraining
**Goal**: Retrain T5 on simplified STEM-focused data

**Training Configuration**:
- **Base Model**: Continue with T5-small for computational efficiency
- **Training Data**: 200-300 STEM syllabi with simplified schema
- **Training Strategy**: Standard fine-tuning approach
- **Validation**: Hold-out STEM syllabi for evaluation

**Tasks**:
- [ ] Prepare training data in T5 format with new schema
- [ ] Update training scripts for simplified input prompts
- [ ] Run training experiments with new data
- [ ] Monitor convergence and loss reduction
- [ ] Save best model checkpoints
- [ ] Compare performance with previous model

#### 4.2 Integration Testing
**Goal**: Ensure all components work together with new data model

**Test Scenarios**:
- End-to-end syllabus generation for each STEM domain
- Cross-domain component retrieval and assembly
- Educational coherence validation
- Performance benchmarking vs previous system

**Tasks**:
- [ ] Create integration test suite
- [ ] Test Computer Science syllabus generation
- [ ] Test Mathematics syllabus generation  
- [ ] Test Physics syllabus generation
- [ ] Test Engineering syllabus generation
- [ ] Validate component mixing across STEM domains
- [ ] Performance comparison with baseline system

### Phase 5: Evaluation and Validation ⏳ Status: Not Started

#### 5.1 Technical Evaluation
**Metrics to Maintain/Improve**:
- **Generation Speed**: Target <10 seconds per syllabus
- **Content Quality**: Target >70 words with structured elements
- **Component Integration**: Successful retrieval and assembly
- **Educational Coherence**: STEM progression validation

**Tasks**:
- [ ] Run comprehensive performance benchmarks
- [ ] Compare with previous multi-domain system
- [ ] Document improvements and regressions
- [ ] Validate technical requirements met

#### 5.2 Educational Quality Assessment
**Goal**: Validate pedagogical soundness with STEM experts

**Expert Review Strategy**:
- **Reviewers**: 2-3 STEM educators (CS, Math, Physics/Engineering)
- **Review Materials**: 10-15 generated syllabi across domains  
- **Evaluation Criteria**: Pedagogical coherence, concept progression, assessment alignment
- **Review Protocol**: Structured questionnaire and qualitative feedback

**Tasks**:
- [ ] Recruit STEM expert reviewers
- [ ] Generate review syllabi samples
- [ ] Create evaluation rubric and questionnaire
- [ ] Conduct expert review sessions
- [ ] Analyze feedback and ratings
- [ ] Document educational quality validation

## Risk Assessment and Mitigation

### High-Risk Items ⚠️

#### Risk 1: T5 Cannot Learn STEM Progression Without Prerequisites
**Impact**: Generated syllabi have illogical concept ordering
**Probability**: Medium
**Mitigation**: 
- Generate high-quality training data with natural STEM progression
- Monitor concept ordering during validation
- Add light sequencing hints in component descriptions if needed

#### Risk 2: STEM Domain Boundaries Too Rigid
**Impact**: System cannot handle interdisciplinary topics
**Probability**: Low  
**Mitigation**:
- Allow components to have multiple STEM domain tags
- Test cross-domain retrieval explicitly
- Include interdisciplinary examples in training data

#### Risk 3: Simplified Schema Loses Essential Information
**Impact**: Generated syllabi lack critical educational elements
**Probability**: Medium
**Mitigation**:
- Conduct early validation with simplified schema
- Expert review of schema design before full implementation
- Iterative refinement based on generation quality

### Medium-Risk Items ⚠️

#### Risk 4: Performance Regression vs Current System
**Impact**: New system performs worse than existing complex version
**Probability**: Low
**Mitigation**:
- Comprehensive benchmarking during development
- Keep current system as fallback during transition
- Focus on quality improvements even if some metrics decline

## Progress Tracking

### Completed ✅
- [x] Project state analysis and simplification strategy defined
- [x] STEM domain selection rationale documented
- [x] Simplified data model designed and implemented (`src/data/models.py`)
- [x] Implementation plan created
- [x] Schema validation functions created and tested (100% test pass rate)
- [x] STEM-focused component generator created (`src/data/stem_components_generator.py`)
- [x] API integration tested and validated with sample components
- [x] Cross-domain component generation verified (CS, Math, Physics, Engineering)

### In Progress 🔄
- [x] Phase 1: Data Model Redesign (COMPLETED)
- [x] Phase 2.1: STEM Component Extraction (COMPLETED - Outstanding results!)
- [x] Phase 3.1: Vector Store Rebuilding (COMPLETED - September 21, 2025)
- [ ] Phase 3.2: RAG Pipeline Updates (CURRENT)

### Next Up ⏭️
1. **Immediate**: Phase 3.2 - Update RAG pipeline for corrected multi-domain data
2. **This Week**: Retrain T5 model with STEM data (Phase 4.1)
3. **Next Week**: Integration testing and evaluation (Phase 4.2 & 5)
4. **Optional**: Generate additional engineering components if needed for coverage

### Blocked ❌
- None currently

## Context Preservation

### Key Technical Decisions
1. **STEM Focus Rationale**: Manageable scope, coherent educational domain, credible evaluation
2. **Schema Simplification**: Remove week numbers, prerequisites, complex workload tracking  
3. **Component Volume**: Reduce total components but increase quality per STEM domain
4. **T5 Strategy**: Trust model to learn natural STEM progression from quality training data

### Critical Files to Update
- `src/data/models.py` - Data schemas
- `src/data/generate_course_components.py` - Component generation
- `src/rag/vector_store.py` - Vector database operations
- `src/rag/rag_t5_generator.py` - Generation pipeline
- `src/training/t5_syllabus_trainer.py` - Model training

### Metrics to Preserve
- Generation speed and quality
- Component integration success
- Educational coherence validation
- System performance benchmarks

## Decision Log

### September 14, 2025
- **Decision**: Pivot from 12-domain system to 4 STEM domains
- **Rationale**: Complexity reduction for MSc scope, improved evaluation credibility
- **Impact**: Major data regeneration and system updates required

### September 21, 2025
- **Decision**: Proceed with extracted STEM components instead of full regeneration
- **Rationale**: Extraction yielded 3,346 high-quality components (16x better than predicted)
- **Impact**: $66.92 cost savings, accelerated timeline, proceed directly to Phase 3
- **Note**: Engineering domain gap identified - may generate targeted components if needed

### Next Decision Points
- [x] Schema validation with sample data generation ✅ COMPLETED
- [ ] Expert reviewer recruitment and evaluation protocol
- [ ] Performance threshold definition for success criteria
- [ ] Timeline adjustment for dissertation completion
- [ ] Engineering component generation necessity assessment

---

**Document Status**: Active Planning Document  
**Last Updated**: September 21, 2025  
**Next Review**: After Phase 3.1 completion (Vector Store Rebuilding)