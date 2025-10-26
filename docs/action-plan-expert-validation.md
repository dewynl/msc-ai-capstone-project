# Action Plan: Expert Validation & Final Dissertation Push

**Created**: October 21, 2024
**Dissertation Submission**: November 10, 2025
**Presentation**: November 14, 2025
**Supervisor Unavailable**: November 15-23, 2025

---

## Supervisor Feedback Summary (Oct 21 Meeting)

### New Requirements
1. **Expert Validation Study (MANDATORY)**
   - 8-12 expert respondents (educators/instructional designers)
   - User guide explaining how to test the tool
   - Evaluation questionnaire covering the whole tool
   - Participant information sheet (no PII collected)
   - Results go in Chapter 6 (Results/Evaluation)

2. **Dissertation Formatting (MISSING)**
   - Table of Contents
   - List of Tables
   - List of Figures/Diagrams
   - Abstract

3. **Presentation Requirements (Nov 14)**
   - 20 minutes total
   - ~1 min per chapter (8 slides)
   - 2-3 mins artifact demo
   - 1 minute ethics slide
   - 5 mins Q&A
   - **Show artifact to supervisor next week** (Oct 28 - Nov 3)

4. **Documentation Updates**
   - ✅ Document all architectural alternatives (already in Annex A)
   - ✅ PRISMA flow with key search terms (already created)
   - Add to Chapter 7: "In the future I would add more test data to train the model"
   - Add to Chapter 7: "More data influences results, but kept focused for dissertation scope"

---

## Decisions Made (Oct 21)

### Expert Validation Setup
- **Timeline**: Streamlit app ready by **Sunday Oct 27**
- **Deployment**: Streamlit Cloud (free, public URL)
- **Recruitment sources**:
  1. FranklinCovey colleagues ✅
  2. Alma mater CS department principal ✅
  3. Current university faculty
  4. Supervisor's suggested contacts
  5. LinkedIn (if time permits)
- **Anonymity**: Completely anonymous (no PII collected)
- **Ethics approval**: Not required (validation/review, not research study)
- **Incentive**: Non-monetary (acknowledgment in dissertation, early access)

### Streamlit App Features
1. **Input**: Course details (title, domain, level, description)
2. **Generate**: Create syllabus using function calling architecture
3. **Display**: Show formatted syllabus (readable view)
4. **Regenerate**: Add refinement notes → regenerate improved version
5. **Download**: Export as PDF
6. **Backend**: Store in database as JSON

### Evaluation Questionnaire (Google Form)
Cover these 6 aspects:
1. **Usability**: Easy to use? Clear instructions? Intuitive?
2. **Educational Quality**: Pedagogically sound? Appropriate Bloom's levels?
3. **Accuracy**: Relevant content for domain/level?
4. **Usefulness**: Would they use this? Saves time?
5. **Feature Completeness**: What's missing? What to add?
6. **Overall Impression**: Strengths? Weaknesses? Recommendations?

### User Guide
- **Format**: Brief 1-page PDF
- **Content**: "Enter course info → Generate → Review output → Fill survey"

---

## Timeline & Task Breakdown

### **This Week (Oct 21-27): Build Expert Validation Materials**

#### Monday-Tuesday (Oct 21-22)
- [ ] **Build Streamlit web interface** with features:
  - Input form (title, domain, level, description)
  - Generate syllabus button
  - Display formatted output
  - Refinement input + regenerate
  - Download as PDF
- [ ] **Deploy to Streamlit Cloud**
- [ ] **Test deployment** (verify RAG/ChromaDB works in cloud)

#### Wednesday (Oct 23)
- [ ] **Create Google Form questionnaire** (8-12 questions covering 6 aspects)
- [ ] **Create 1-page user guide** (PDF)
- [ ] **Create participant information sheet** (brief, mentions no PII)
- [ ] **Draft recruitment email/message**
- [ ] **Convert PRISMA diagram to image** (use mermaid.live or similar)

#### Thursday-Friday (Oct 24-25)
- [ ] **Recruit experts** - Send to:
  - FranklinCovey colleagues
  - Alma mater CS principal
  - Current university faculty
  - Supervisor's suggested contacts
  - Target: 15-20 invitations (to get 8-12 completions)

#### Weekend (Oct 26-27)
- [ ] **Follow up** with any non-responders
- [ ] **Buffer time** for any technical issues

---

### **Week 2 (Oct 28 - Nov 3): Collect Expert Feedback + Presentation**

#### Monday-Tuesday (Oct 28-29)
- [ ] **Schedule meeting with supervisor** to demo artifact
- [ ] **Show artifact to supervisor** (get feedback)
- [ ] **Monitor expert responses** (follow up if needed)

#### Wednesday-Thursday (Oct 30-31)
- [ ] **Collect all expert responses** (aim for 8-12 completions)
- [ ] **Analyze expert feedback**
  - Quantitative: Calculate average ratings, response distributions
  - Qualitative: Thematic analysis of open-ended responses

#### Friday-Sunday (Nov 1-3)
- [ ] **Write Section 6.11: Expert Validation Results** (~500 words)
  - Participant demographics (if collected)
  - Quantitative results (ratings per aspect)
  - Qualitative themes (common feedback)
  - Discussion of findings
- [ ] **Create presentation slides** (20 min format)
  - 8 chapter slides (~1 min each)
  - 1 ethics slide
  - Artifact demo plan (2-3 mins)

---

### **Week 3 (Nov 4-10): Final Polish & Submission**

#### Monday-Wednesday (Nov 4-6)
- [ ] **Integrate Chapters 6-8** into main dissertation
- [ ] **Add Section 6.11** (Expert Validation) to Chapter 6
- [ ] **Update Chapter 7** with data/focus reflections:
  - "In the future I would add more test data to train the model"
  - "More data influences results, but kept focused for dissertation scope"

#### Thursday-Friday (Nov 7-8)
- [ ] **Add dissertation front matter**:
  - Abstract (~300 words)
  - Table of Contents (auto-generate from headings)
  - List of Tables (extract all table captions)
  - List of Figures (extract all figure captions)
- [ ] **Insert PRISMA diagram image** into Chapter 2
- [ ] **Final proofread** (grammar, formatting, citations)

#### Weekend (Nov 9-10)
- [ ] **Final review** (read entire dissertation start-to-finish)
- [ ] **Address any last-minute issues**
- [ ] **Submit dissertation** (Monday Nov 10) ✅

---

### **Week 4 (Nov 11-14): Presentation Prep**

#### Tuesday-Wednesday (Nov 12-13)
- [ ] **Practice presentation** (20 min timing)
- [ ] **Prepare demo** (test artifact, have backup plan)
- [ ] **Submit presentation slides** (Thursday Nov 13 deadline)

#### Thursday-Friday (Nov 13-14)
- [ ] **Final practice run**
- [ ] **Artefact presentation** (Friday Nov 14) ✅

---

## Expert Validation Chapter Structure

**Section 6.11: Expert Validation Results** (add to Chapter 6)

Suggested subsections:
- **6.11.1 Validation Methodology**: How experts were recruited, what they tested
- **6.11.2 Participant Overview**: Number of respondents, backgrounds (anonymized)
- **6.11.3 Quantitative Results**: Ratings across 6 evaluation aspects
- **6.11.4 Qualitative Feedback**: Common themes, suggestions, concerns
- **6.11.5 Discussion**: What validation reveals about the system
- **6.11.6 Limitations**: Small sample size, short testing period

---

## Key Files & Locations

### Completed Deliverables
- ✅ `docs/chapter-6-evaluation.md` (1,580 words) - Technical evaluation results
- ✅ `docs/chapter-7-learning-reflection.md` (860 words) - Learning reflection
- ✅ `docs/chapter-8-conclusion.md` (900 words) - Conclusion & future work
- ✅ `docs/annex-b-technical-appendix.md` (2,200 words) - Technical details
- ✅ `docs/prisma-literature-search-flow.md` - PRISMA diagram (needs image conversion)
- ✅ `data/evaluation/evaluation_test_suite.json` - 20 test cases
- ✅ `data/evaluation/results.csv` - Evaluation results (100% JSON validity)
- ✅ `scripts/run_evaluation_experiments.py` - Automated test runner
- ✅ `scripts/analyze_results.py` - Results analysis & tables

### To Be Created This Week
- [ ] Streamlit web app (`app.py` or similar)
- [ ] Google Form questionnaire (online)
- [ ] User guide PDF (`docs/expert-validation-user-guide.pdf`)
- [ ] Participant info sheet (`docs/participant-information-sheet.pdf`)
- [ ] Recruitment email template (`docs/recruitment-email.md`)

### To Be Updated
- [ ] `docs/dissertation.md` - Integrate Chapters 6-8 + front matter
- [ ] `docs/chapter-6-evaluation.md` - Add Section 6.11 (Expert Validation)
- [ ] `docs/chapter-7-learning-reflection.md` - Add data/focus reflections

---

## Risk Mitigation

### Risk: Not enough expert responses
**Mitigation**:
- Recruit 15-20 people (target 8-12 completions, ~60% response rate)
- Follow up after 3 days
- Extend deadline slightly if needed (have until Nov 3)
- Minimum viable: 6-8 responses still valuable

### Risk: Streamlit Cloud doesn't support ChromaDB
**Mitigation**:
- Test deployment early (Tuesday Oct 22)
- Alternative: Use lightweight SQLite for demo, mention ChromaDB in docs
- Alternative: Deploy on personal server if needed

### Risk: Experts find major bugs
**Mitigation**:
- Thorough local testing before sharing
- Frame as "beta" - gather feedback on improvements
- Document issues as "future work" in dissertation

---

## Questions to Ask Supervisor (When Showing Artifact)

1. Does the Streamlit interface meet your expectations for the artifact?
2. Any features missing that I should add before expert validation?
3. Are the evaluation questions (Google Form) appropriate?
4. Should expert validation results be Section 6.11 or elsewhere in Chapter 6?
5. Any other feedback before I send to experts?

---

## Success Criteria

**Streamlit App (Oct 27)**:
- ✅ Deploys successfully to Streamlit Cloud
- ✅ Generates valid syllabi (100% JSON validity from evaluation)
- ✅ Displays formatted output clearly
- ✅ Allows refinement/regeneration
- ✅ Exports to PDF
- ✅ Professional, polished interface

**Expert Validation (Nov 3)**:
- ✅ 8-12 completed responses
- ✅ Covers all 6 evaluation aspects
- ✅ Mix of positive feedback + constructive suggestions
- ✅ Sufficient data for qualitative + quantitative analysis

**Dissertation (Nov 10)**:
- ✅ All chapters integrated (6, 7, 8)
- ✅ Expert validation results in Chapter 6
- ✅ Front matter complete (abstract, ToC, lists)
- ✅ PRISMA diagram inserted as image
- ✅ Final proofread & polished

**Presentation (Nov 14)**:
- ✅ 20-minute timing practiced
- ✅ Artifact demo smooth & professional
- ✅ Slides clear & concise
- ✅ Ready for Q&A

---

## Notes from Email Feedback (Supervisor - Earlier)

### Feedback Applied:
1. ✅ Move quantitative results to Chapter 6, keep methodology in Chapter 5
   - **Done**: Section 5.3 (Evaluation Methodology) added to Chapter 5
   - **Done**: Chapter 6 contains all quantitative results
2. ✅ Keep Annex A (research evolution), add Annex B (technical details)
   - **Done**: Annex B created (2,200 words)
3. ✅ Add PRISMA-style literature search flow diagram
   - **Done**: Created `docs/prisma-literature-search-flow.md`
   - **TODO**: Convert to image and insert in Chapter 2
4. ⚠️ Consider error analysis if time permits
   - **Status**: Framework created (`docs/error-analysis-framework.md`)
   - **Decision**: Not implementing fully due to time constraints (Nov 10 deadline)

---

**Last Updated**: October 21, 2024
**Next Review**: October 27, 2024 (after Streamlit app complete)
