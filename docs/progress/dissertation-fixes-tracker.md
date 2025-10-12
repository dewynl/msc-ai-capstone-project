# Dissertation Fixes Progress Tracker

**Created**: 2025-10-12
**Last Updated**: 2025-10-12
**Total Issues**: 11 items across 3 priority levels

---

## Progress Overview

- 🔴 **Critical Issues**: 3 items (MUST fix before submission)
- ⚠️ **High Priority**: 5 items (SHOULD fix before Ch 6-8)
- 📋 **Moderate Priority**: 3 items (Can do during finalization)

**Overall Status**: 0/11 completed (0%)

---

## 🔴 CRITICAL PRIORITY (Must Fix Before Submission)

### ❌ CRITICAL-1: Chapter 5.1 / Annex A Duplication
**Status**: Not Started
**Criterion Violated**: C5 (Old approaches only mentioned in main doc, details in annex)
**Effort**: 2-3 hours
**Priority**: HIGHEST

**Problem**:
- Chapter 5.1 (Lines 656-786) contains ~1,300 words of detailed Phase 1/2 analysis
- Duplicates content in Annex A.2-A.4
- Includes code snippets, detailed metrics, failure analysis
- Violates requirement that old approaches be briefly mentioned with details in annex

**Solution**: Replace Lines 656-786 with ~400-word overview + Annex references

**Files to Modify**:
- `docs/dissertation.md` - Lines 656-786

**Acceptance Criteria**:
- [ ] Chapter 5.1 reduced to ~400 words
- [ ] Explicit references to Annex A.2, A.3, A.4 added
- [ ] No code snippets in Chapter 5.1
- [ ] No detailed performance metrics in Chapter 5.1
- [ ] Section 5.1.2 (data generation) condensed but preserved
- [ ] Annex A remains comprehensive (no changes needed there)

**Decision Made**: Pending
**Action Plan**: Pending

---

### ❌ CRITICAL-2: UK/US English Inconsistencies
**Status**: Not Started
**Criterion Violated**: C4 (UK English style)
**Effort**: 1 hour
**Priority**: HIGHEST

**Problem**:
- Mixed American/British spellings throughout (Lines: multiple)
- "specialized" → should be "specialised"
- "optimization" → should be "optimisation"
- "modeling" → should be "modelling"
- "analyze" → should be "analyse"
- "organization" → should be "organisation"

**Solution**: Systematic find-and-replace + manual verification

**Files to Modify**:
- `docs/dissertation.md` - All instances

**Acceptance Criteria**:
- [ ] All "specialized" → "specialised"
- [ ] All "optimization" → "optimisation"
- [ ] All "organization" → "organisation"
- [ ] All "modeling" → "modelling"
- [ ] All "analyze/analyzed/analyzing" → "analyse/analysed/analysing"
- [ ] All "behavior" → "behaviour"
- [ ] All "center" → "centre" (context-dependent)
- [ ] All "recognize" → "recognise"
- [ ] All "emphasize" → "emphasise"
- [ ] Citations/code preserved with original spelling
- [ ] Manual verification completed

**Decision Made**: Pending
**Action Plan**: Pending

---

### ❌ CRITICAL-3: Objective-Achievement Mismatch
**Status**: Not Started
**Criterion Violated**: C2 (Claims match implementation)
**Effort**: 30 minutes
**Priority**: HIGHEST

**Problem**:
- Section 1.3.2 (Lines 34-36) states: "Collect 500+ syllabi from OER"
- Actual: Generated 180 synthetic syllabi (36% of stated target)
- Methodology mismatch: "collect" vs "generate"
- Scope mismatch: "diverse domains" vs "STEM focus"

**Solution**: Revise objective + add explanation in limitations

**Files to Modify**:
- `docs/dissertation.md` - Lines 34-36 (objective)
- `docs/dissertation.md` - After Line 93 (new limitations paragraph)

**Acceptance Criteria**:
- [ ] Section 1.3.2 objective revised to reflect 180 synthetic syllabi
- [ ] Objective mentions STEM focus explicitly
- [ ] Objective mentions "generate" not "collect"
- [ ] New paragraph added to Section 1.5.2 explaining pivot
- [ ] Explanation covers: ethics, quality, focus reasons
- [ ] Positive framing (adaptive methodology, not failure)

**Decision Made**: Pending
**Action Plan**: Pending

---

## ⚠️ HIGH PRIORITY (Should Address Before Ch 6-8)

### ❌ HIGH-1: "100% Success" Claims
**Status**: Not Started
**Criterion**: C1 (Up to date with current approaches)
**Effort**: 30 minutes
**Priority**: HIGH

**Problem**:
- Line 536: "ensures 100% function call execution success"
- Line 932: "achieving **100% function call execution success**"
- Line 969: "100% (guaranteed valid)"
- Inconsistent with README tone-down (commit 35f547b)

**Solution**: Replace with measured academic language

**Files to Modify**:
- `docs/dissertation.md` - Lines 536, 932, 969

**Acceptance Criteria**:
- [ ] Line 536: "100%" → "reliable" or "effectively guaranteed"
- [ ] Line 932: "100%" → "reliable" or "near-universal"
- [ ] Line 969: "100%" → "effectively guaranteed valid"
- [ ] Consistent measured language throughout

**Decision Made**: Pending
**Action Plan**: Pending

---

### ❌ HIGH-2: Unverified Performance Metrics
**Status**: Not Started
**Criterion**: C1 (Up to date with current approaches)
**Effort**: Variable (depends on data availability)
**Priority**: HIGH

**Problem**:
- Section 5.2.6 (Lines 976-988) claims specific percentages:
  - "85% of function calls execute without errors"
  - "95% semantic preservation"
  - "100% component integration"
- No documented evaluation methodology
- Unclear if measured or estimated

**Solution**: Document in Ch 6 OR replace with qualitative descriptions

**Files to Modify**:
- `docs/dissertation.md` - Lines 976-988
- Potentially Chapter 6 (if documenting measurements)

**Acceptance Criteria**:
- [ ] Decision made: document measurements OR revise to qualitative
- [ ] If documenting: Ch 6 includes methodology
- [ ] If revising: qualitative language (e.g., "high accuracy", "effective preservation")
- [ ] Consistency with README language

**Decision Made**: Pending
**Action Plan**: Pending

---

### ❌ HIGH-3: Error Recovery Success Rates
**Status**: Not Started
**Criterion**: C1 (Up to date with current approaches)
**Effort**: Variable (depends on data availability)
**Priority**: HIGH

**Problem**:
- Section 5.2.6 (Lines 982-988) claims:
  - "98% recovery rate for minor syntax errors"
  - "89% recovery for malformed parameters"
  - "100% recovery for missing fields"
- Highly specific percentages suggest rigorous testing
- No documented test methodology

**Solution**: Document in Ch 6 OR replace with qualitative assessment

**Files to Modify**:
- `docs/dissertation.md` - Lines 982-988
- Potentially Chapter 6 (if documenting)

**Acceptance Criteria**:
- [ ] Decision made: document OR revise
- [ ] If documenting: test methodology in Ch 6
- [ ] If revising: qualitative language
- [ ] Consistent with overall tone

**Decision Made**: Pending
**Action Plan**: Pending

---

### ❌ HIGH-4: Quantitative Objectives Verification
**Status**: Not Started
**Criterion**: C2 (Claims match implementation)
**Effort**: Variable
**Priority**: HIGH

**Problem**:
Multiple objectives state specific percentages without verification:
- Line 41: "80% automated preprocessing accuracy"
- Line 42: "10% improvement over generic embeddings"
- Line 47: "20% training loss reduction"
- Line 48: "85%+ domain classification accuracy"

**Solution**: Document measurements OR revise to qualitative

**Files to Modify**:
- `docs/dissertation.md` - Lines 41, 42, 47, 48

**Acceptance Criteria**:
- [ ] Line 41: Verified or revised
- [ ] Line 42: Verified or revised (suggested: "optimised for educational terminology")
- [ ] Line 47: Verified or revised (suggested: "systematic hyperparameter optimisation")
- [ ] Line 48: Verified or revised
- [ ] All changes maintain objective structure

**Decision Made**: Pending
**Action Plan**: Pending

---

### ❌ HIGH-5: Scope Statement Clarity
**Status**: Not Started
**Criterion**: C2 (Claims match implementation)
**Effort**: 5 minutes
**Priority**: HIGH

**Problem**:
- Line 79 states: "STEM and humanities subjects"
- Actual: STEM only (CS, Math, Physics, Engineering)
- Explained in Annex A.6.1 but not in main scope section

**Solution**: Update scope statement with forward reference

**Files to Modify**:
- `docs/dissertation.md` - Line 79

**Acceptance Criteria**:
- [ ] Line 79 updated to reflect STEM-only focus
- [ ] Forward reference to Annex A.6.1 added
- [ ] Mention of future humanities extension preserved

**Decision Made**: Pending
**Action Plan**: Pending

---

## 📋 MODERATE PRIORITY (Finalization Phase)

### ❌ MODERATE-1: References Section Incomplete
**Status**: Not Started (Expected)
**Criterion**: C3 (Harvard citations)
**Effort**: Moderate
**Priority**: LOW (do after Ch 6-8)

**Problem**:
- Line 1278: References placeholder
- Expected at this stage (Ch 6-8 not written yet)
- Will need full Harvard reference list

**Solution**: Complete after Ch 6-8 written

**Files to Modify**:
- `docs/dissertation.md` - Lines 1276-1278
- `docs/master-literature-list.md` - Source reference

**Acceptance Criteria**:
- [ ] All in-text citations have reference entries
- [ ] Harvard format consistent
- [ ] Alphabetized by author surname
- [ ] 43 references from master list included
- [ ] Cross-check all citations verified

**Decision Made**: Wait until Ch 6-8 complete
**Action Plan**: Scheduled for final phase

---

### ❌ MODERATE-2: Cross-References to Annex
**Status**: Not Started
**Effort**: 30 minutes
**Priority**: MODERATE

**Problem**:
- After restructuring Ch 5.1, other chapters may need Annex references
- Chapter 4 (Methodology) mentions iterative approach
- Chapter 6 (Evaluation) will compare phases
- Need consistent referencing pattern

**Solution**: Add explicit Annex A references throughout

**Files to Modify**:
- `docs/dissertation.md` - Chapters 4, 5, 6 (where Phase 1/2 mentioned)

**Acceptance Criteria**:
- [ ] Chapter 4: Annex references where mentioning iterative approach
- [ ] Chapter 5: Annex references for Phase 1/2 mentions
- [ ] Chapter 6: Annex references for baseline comparisons
- [ ] Consistent reference format: "(see Annex A.X for...)"

**Decision Made**: Pending
**Action Plan**: Do during Ch 5.1 restructuring

---

### ❌ MODERATE-3: Final Consistency Pass
**Status**: Not Started
**Effort**: 1-2 hours
**Priority**: MODERATE (final stage)

**Problem**:
- After all changes, need comprehensive consistency check
- Verify terminology consistency
- Check figure references
- Validate cross-references

**Solution**: Systematic final review

**Files to Modify**:
- `docs/dissertation.md` - All sections

**Acceptance Criteria**:
- [ ] All figure references correct
- [ ] All cross-references valid
- [ ] Terminology consistent (UK English)
- [ ] Section numbering correct
- [ ] Table of contents matches (if applicable)
- [ ] Word count verified

**Decision Made**: Wait until all other fixes complete
**Action Plan**: Final step before submission

---

## Completion Tracking

### Critical Issues (3 total)
- [ ] CRITICAL-1: Chapter 5.1 restructuring (2-3 hours)
- [ ] CRITICAL-2: UK English consistency (1 hour)
- [ ] CRITICAL-3: Objective alignment (30 min)

**Critical Subtotal**: 0/3 complete (0%)
**Estimated Time**: 4-5 hours

### High Priority Issues (5 total)
- [ ] HIGH-1: "100%" claims tone-down (30 min)
- [ ] HIGH-2: Performance metrics verification (variable)
- [ ] HIGH-3: Error recovery rates verification (variable)
- [ ] HIGH-4: Quantitative objectives verification (variable)
- [ ] HIGH-5: Scope statement update (5 min)

**High Priority Subtotal**: 0/5 complete (0%)
**Estimated Time**: 2-3 hours (if all qualitative revisions)

### Moderate Priority Issues (3 total)
- [ ] MODERATE-1: References section (after Ch 6-8)
- [ ] MODERATE-2: Cross-references (30 min)
- [ ] MODERATE-3: Final consistency (1-2 hours)

**Moderate Priority Subtotal**: 0/3 complete (0%)
**Estimated Time**: 2-3 hours

---

## Work Session Log

### Session 1: [Date TBD]
**Focus**: Critical issues discussion and decision-making
**Status**: Pending
**Notes**: Going through each issue with options/pros/cons

---

## Notes

- All line numbers refer to current dissertation.md (1,285 lines, 14,952 words)
- Word count target: 13,000 words (currently 115%)
- After critical fixes: estimated ~14,000 words (108%)
- Leaves room for Ch 6-8 additions

---

**Next Action**: Review CRITICAL-1 (Chapter 5.1 restructuring) with user for decision
