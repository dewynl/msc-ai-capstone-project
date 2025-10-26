# MSc AI Capstone: Final Action Plan to Submission

**Today**: Friday, October 24, 2025
**Submission Deadline**: Monday, November 10, 2025 (17 days)
**Presentation**: Friday, November 14, 2025 (21 days)

---

## Executive Summary: What's Done vs What's Needed

### ✅ Completed (90% of work)
- **Evaluation complete**: 20 test cases run, 100% JSON validity, results analyzed
- **Chapter 6 drafted**: 1,580 words, comprehensive technical evaluation
- **Chapters 7-8 drafted**: Learning reflection + conclusion chapters written
- **Technical appendices complete**: Annex A, Annex B, PRISMA diagram
- **Dissertation**: 13,671 words (105.2% of core target)
- **Core implementation**: Function calling architecture working, tested, documented

### ❌ Outstanding Critical Items (10% remaining)
1. **Expert validation** (new supervisor requirement from Oct 21)
2. **Streamlit web app** (artifact requirement)
3. **Chapter integration** (consolidate 6-8 into main dissertation)
4. **Front matter** (Abstract, ToC, List of Figures)
5. **Final polish** (proofread, citations check)

---

## Critical Path: 17 Days to Submission

### DECISION POINT: Expert Validation Path

**Context**: Supervisor meeting Oct 21 added expert validation requirement (8-12 experts testing system, questionnaire, user guide). This was NOT in original plan.

**Two viable paths forward:**

#### Path A: Full Expert Validation (Recommended IF you have contacts ready)
- **Pros**: Satisfies supervisor's new requirement, adds academic rigor
- **Cons**: Requires 8-10 hours web app development + 1 week recruitment
- **Timeline**: Tight but achievable with your FranklinCovey and alma mater networks

#### Path B: Technical Evaluation Only (Backup plan)
- **Pros**: Lower risk, faster completion, technical evaluation already excellent
- **Cons**: Doesn't address supervisor's Oct 21 feedback directly
- **Timeline**: More buffer time for polish and refinement

**Decision criteria**:
1. Can you commit 6-8 hours this weekend to Streamlit app?
2. Can you recruit 6-8 experts within 3-4 days via existing contacts?
3. Did supervisor say expert validation is MANDATORY or RECOMMENDED?

**Recommendation**: Attempt Path A, with Path B as fallback if recruitment fails by Tuesday Oct 28.

---

## Week-by-Week Execution Plan

### WEEKEND (Oct 26-27): Web App Foundation [Path A]

**Saturday (Oct 26) - 8 hours**

**Morning (4 hours): Core Streamlit App**
```bash
# Create app structure
touch streamlit_app.py

# Implement core features:
# 1. Input form (title, domain, level, description)
# 2. Generate button → calls RAGIntegratedSyllabusBuilder
# 3. Display JSON output (st.json())
# 4. Download button (st.download_button())
```

**Afternoon (4 hours): Polish & Deploy**
```bash
# 1. Add basic styling and tabs
# 2. Create requirements.txt for Streamlit Cloud
# 3. Test locally with 3-5 examples
# 4. Handle errors gracefully (try/except blocks)
```

**Deliverable**: Working local Streamlit app

---

**Sunday (Oct 27) - 6 hours**

**Morning (3 hours): Deploy & Test**
```bash
# 1. Push to GitHub
# 2. Deploy to Streamlit Cloud (streamlit.io)
# 3. Test deployed version works
# 4. Fix any deployment issues (ChromaDB, model loading)
```

**Afternoon (3 hours): Validation Materials**
- Create Google Form questionnaire (30 min)
  - 6 sections: Usability, Educational Quality, Accuracy, Usefulness, Features, Overall
  - 10-12 questions total (mix Likert scale + open-ended)
- Create 1-page user guide PDF (1 hour)
  - "How to test the tool" + link to Google Form
- Draft recruitment email (30 min)
- Prepare participant information sheet (30 min)

**Deliverable**: Deployed app + complete validation package ready to send

**DECISION CHECKPOINT**: If deployment fails or app doesn't work → PIVOT TO PATH B

---

### WEEK 1 (Oct 28 - Nov 3): Expert Validation + Integration

**Monday (Oct 28) - 3 hours**
- **Morning**: Send recruitment emails to 10-15 contacts
  - FranklinCovey colleagues (5-7 people)
  - Alma mater CS department principal (1 person + can forward)
  - University faculty if accessible (2-3 people)
  - LinkedIn contacts if needed
- **Evening**: Show artifact to supervisor (schedule meeting)

**Tuesday (Oct 29) - 3 hours**
- Monitor expert responses (aim for 6-8 sign-ups minimum)
- Follow up with non-responders
- Begin integrating Chapters 6-8 into main dissertation

**Wednesday (Oct 30) - 3 hours**
- Complete chapter integration
- Verify all cross-references work
- Run: `python3 scripts/analyze_dissertation_progress.py`

**Thursday (Oct 31) - 3 hours**
- Continue expert monitoring (aim for 6-8 completed forms)
- Begin analyzing expert feedback if responses coming in
- Start front matter (Abstract draft)

**Friday (Nov 1) - 3 hours**
- Collect all expert responses (deadline for participants)
- Analyze quantitative results (average ratings per aspect)
- Identify qualitative themes from open responses

**Weekend (Nov 2-3) - 8 hours total**
- Write Section 6.11: Expert Validation Results (~500 words)
  - Methodology, participant overview, quantitative results, qualitative themes
- Add to Chapter 7 reflections: data limitations, scope decisions
- Complete front matter: Abstract, ToC, List of Figures, List of Tables

**FALLBACK**: If <6 expert responses by Nov 1 → Document attempt in limitations, proceed with technical evaluation only

---

### WEEK 2 (Nov 4-10): Final Polish & Submission

**Monday-Tuesday (Nov 4-5) - 6 hours total**
- Complete final read-through (print or tablet recommended)
- Fix all identified issues (typos, citations, formatting)
- Verify Harvard citation format throughout
- Check all figure captions and table numbers

**Wednesday (Nov 6) - 3 hours**
- Generate final PDF with correct formatting
- Verify university requirements (title page, page numbers, etc.)
- Create submission package (dissertation PDF, code repository link)

**Thursday (Nov 7) - 3 hours**
- Final verification checks
- Code repository cleanup (remove debug code, update README)
- Test all scripts work on fresh environment

**Friday (Nov 8) - 2 hours**
- Final PDF generation
- Backup all files to cloud storage
- Prepare for Monday submission

**Weekend (Nov 9-10) - Buffer**
- Rest and final review
- Address any last-minute issues
- Mental preparation

**Monday (Nov 10) - SUBMISSION DAY**
- Submit dissertation through official channel
- Submit code repository
- Verify receipt confirmation
- CELEBRATE 🎉

---

### WEEK 3 (Nov 11-14): Presentation Preparation

**Tuesday-Wednesday (Nov 12-13)**
- Create presentation slides (16-20 slides)
  - Introduction & problem (2 slides)
  - Literature review highlights (2 slides)
  - Methodology overview (2 slides)
  - Implementation (4 slides): 3-phase evolution, function calling architecture
  - Evaluation results (3 slides): performance metrics, expert validation
  - Conclusion & future work (2 slides)
- Prepare live demo (CLI + Streamlit if deployed)
- Record backup demo video (technical failure plan)

**Thursday (Nov 14) - PRESENTATION DAY**
- Deliver 20-minute presentation
- Demo working system
- Q&A session

---

## Streamlit App: Minimum Viable Product Spec

**ONLY build these features** (anything else is scope creep):

### Required Features
1. **Input Form**:
   - Course title (text input)
   - Domain (dropdown: CS, Math, Physics)
   - Level (dropdown: Beginner, Intermediate, Advanced)
   - Description (text area)
   - Generate button

2. **Output Display**:
   - JSON output with syntax highlighting (st.json())
   - Generation time displayed
   - Success/error message

3. **Download**:
   - Download JSON button (st.download_button())

4. **Error Handling**:
   - Try/except around generation
   - Clear error messages to user

### Nice-to-Have (ONLY if time permits)
- Formatted view in tabs (raw JSON + pretty table)
- Example presets (pre-filled inputs)
- Regeneration feature

### Out of Scope (DO NOT BUILD)
- PDF export (complex, time-consuming)
- User authentication (not needed for validation)
- Database persistence (not needed)
- Advanced styling (basic Streamlit theme is fine)

---

## Expert Validation: Streamlined Approach

### Questionnaire Structure (Google Form)

**Section 1: Background** (2 questions)
- Your role in education (dropdown)
- Years of experience teaching (number)

**Section 2: Usability** (2 questions, 5-point Likert)
- Easy to use?
- Instructions clear?

**Section 3: Educational Quality** (3 questions, 5-point Likert)
- Pedagogically sound?
- Appropriate Bloom's taxonomy levels?
- Learning objectives well-structured?

**Section 4: Content Accuracy** (2 questions, 5-point Likert)
- Content relevant to domain?
- Appropriate for difficulty level?

**Section 5: Practical Usefulness** (2 questions, 5-point Likert)
- Would you use this tool?
- Saves time compared to manual creation?

**Section 6: Overall** (2 questions)
- Overall impression (1-5 scale)
- Suggestions for improvement (open text)

**Total: 10-12 questions, ~5-7 minutes to complete**

### Recruitment Email Template

```
Subject: Quick feedback request: Educational AI tool (5-7 minutes)

Hi [Name],

I'm completing my MSc AI dissertation on automated course syllabus generation
and would value your expert feedback.

Could you test a simple web tool (5 min) and complete a brief questionnaire
(5 min)? Total time: ~10 minutes.

Tool: [Streamlit URL]
Survey: [Google Form URL]
User Guide: [Attached PDF]

Your feedback will inform my evaluation chapter and help validate the
educational quality of AI-generated content. Completely anonymous - no
personal data collected.

Deadline: Friday, November 1 (1 week)

Thank you for supporting my research!

[Your name]
MSc Artificial Intelligence, University of Essex
```

### Target Contacts (Aim for 10-15 invitations → 6-8 completions)
1. **FranklinCovey colleagues** (5-7 people with education/training background)
2. **Alma mater principal** (1 person + ask if can forward to other faculty)
3. **University faculty** (2-3 people if accessible)
4. **Professional network** (LinkedIn, teaching contacts)

### Success Criteria
- **Minimum viable**: 6 completed responses
- **Target**: 8-10 completed responses
- **Stretch**: 12+ completed responses

---

## Dissertation Integration Checklist

### Files to Integrate

**Current state**: Chapters 6-8 are in separate files
- `docs/chapter-6-evaluation.md` (1,580 words)
- `docs/chapter-7-learning-reflection.md` (860 words)
- `docs/chapter-8-conclusion.md` (900 words)

**Integration process**:
1. Open `docs/dissertation-trimmed-complete.md`
2. Add Chapter 6 content after Chapter 5
3. Add Section 6.11 (Expert Validation) if completed
4. Add Chapter 7 after Chapter 6
5. Add Chapter 8 after Chapter 7
6. Update section numbering if needed
7. Verify all figure references (Figure X.Y format)
8. Check all cross-references work

### Front Matter to Add

**Required components**:

1. **Title Page**
   - Dissertation title
   - Your name
   - MSc Artificial Intelligence
   - University of Essex Online
   - Submission date: November 10, 2025

2. **Abstract** (~300 words)
   - Research problem
   - Approach (function calling architecture)
   - Key findings (100% JSON validity, 85% T5 utilization)
   - Contribution (architectural innovation for smaller models)

3. **Table of Contents**
   - Auto-generate from chapter headings
   - Include subsection headings (up to 3 levels)

4. **List of Figures**
   - Extract all "Figure X.Y:" captions
   - Include page numbers

5. **List of Tables**
   - Extract all "Table X.Y:" captions
   - Include page numbers

6. **List of Abbreviations** (if needed)
   - RAG, T5, API, JSON, etc.

### Final Structure

```
1. Title Page
2. Abstract
3. Acknowledgments (optional)
4. Table of Contents
5. List of Figures
6. List of Tables
7. Chapter 1: Introduction
8. Chapter 2: Literature Review
9. Chapter 3: Ethical Considerations
10. Chapter 4: Methodology
11. Chapter 5: Implementation
12. Chapter 6: Evaluation
13. Chapter 7: Learning and Reflection
14. Chapter 8: Conclusion
15. References
16. Annex A: Research Approach Evolution
17. Annex B: Technical Appendix (if included)
```

---

## Risk Mitigation & Contingency Plans

### Risk 1: Expert validation recruitment fails

**Trigger**: <6 sign-ups by Tuesday Oct 28

**Mitigation**:
- Document recruitment attempt in methodology
- Proceed with technical evaluation only (Chapter 6 is strong without expert validation)
- Add to limitations: "Expert validation attempted but insufficient responses within dissertation timeframe"
- Technical contribution remains valid

---

### Risk 2: Streamlit deployment issues

**Trigger**: App doesn't work on Streamlit Cloud by Sunday evening

**Mitigation**:
- Keep local version with screenshots
- Document architecture in dissertation
- Show supervisor local demo (still meets "artifact" requirement)
- Focus on technical implementation documentation

---

### Risk 3: Running out of time for polish

**Trigger**: Behind schedule by Nov 4

**Mitigation**:
- **Priority 1**: Dissertation submitted (even if not perfect)
- **Priority 2**: Core chapters complete and integrated
- **Priority 3**: Front matter complete
- **Can sacrifice**: Expert validation section, perfect formatting, extensive proofreading

**Remember**: A submitted dissertation with minor typos > A perfect dissertation submitted late

---

### Risk 4: Supervisor feedback requires major changes

**Trigger**: Supervisor sees artifact (Oct 28) and requests significant modifications

**Mitigation**:
- Clarify if feedback is REQUIRED vs SUGGESTED
- If required: assess time impact, adjust schedule
- If suggested: document feedback, implement what's feasible, note rest as "future work"
- Protect submission deadline (non-negotiable)

---

## Time Budget Reality Check

### Total available hours: ~90 hours over 17 days
- **Weeknights** (3 hours × 12 nights): 36 hours
- **Weekends** (8 hours × 3 days): 24 hours
- **Final week** (Nov 4-10, extra effort): ~30 hours

### Work allocation:
- **Streamlit app**: 10 hours (Path A) or 0 hours (Path B)
- **Expert validation**: 10 hours (analysis, writing Section 6.11)
- **Chapter integration**: 6 hours
- **Front matter**: 6 hours
- **Final polish**: 12 hours
- **Presentation prep**: 12 hours
- **Buffer for issues**: 34-44 hours

**Conclusion**: Timeline is TIGHT but FEASIBLE if you execute immediately and don't add scope.

---

## What NOT to Do (Scope Control)

### ❌ Do NOT:
1. **Refactor existing code** - it works, leave it alone
2. **Add new features** to implementation - out of scope
3. **Expand training data** - no time, not needed for evaluation
4. **Re-train models** - current model performs well
5. **Write additional chapters** - you have enough content
6. **Perfect the Streamlit app** - MVP is sufficient
7. **Recruit >15 experts** - diminishing returns, use time elsewhere
8. **Add more test cases** - 20 is sufficient for evaluation
9. **Create fancy diagrams** - existing figures are good enough
10. **Overthink** - execute, don't perfect

### ✅ DO:
1. **Execute the critical path** - Streamlit app → expert validation → integration → submit
2. **Protect the submission deadline** - November 10 is non-negotiable
3. **Use existing work** - leverage custom_input_demo.py for Streamlit app
4. **Keep expert validation simple** - 10-12 questions, 6-8 experts minimum
5. **Time-box everything** - if task takes >2× estimated time, move on
6. **Ask for help** - supervisor, peers, if genuinely stuck
7. **Rest adequately** - tired work is bad work
8. **Maintain perspective** - you're 90% done, just need to finish

---

## Daily Check-In Template

**Copy this to your notes each evening:**

```
Date: [Today's date]
Hours worked: [X hours]
Completed: [List tasks completed]
Blockers: [Any issues encountered]
Tomorrow: [Top 2 priorities]
On track? [Yes/No - if no, what's the plan?]
```

---

## Success Metrics

### By November 10 (Submission):
- ✅ Dissertation submitted (13,000+ words)
- ✅ All chapters integrated
- ✅ Front matter complete
- ✅ Code repository clean and documented
- ✅ Streamlit app deployed (if Path A) OR technical evaluation complete (if Path B)
- ✅ Expert validation section written (if responses received)

### By November 14 (Presentation):
- ✅ Presentation slides complete (16-20 slides)
- ✅ Demo prepared (CLI + Streamlit if applicable)
- ✅ Q&A preparation done

---

## Final Motivation

**You have completed 90% of the work**:
- ✅ Novel technical contribution (function calling architecture)
- ✅ Working implementation with trained model
- ✅ Comprehensive evaluation (20 test cases, 100% validity)
- ✅ Well-written dissertation chapters (13,671 words)
- ✅ Supporting documentation (annexes, figures, PRISMA diagram)

**You only need to complete the final 10%**:
- 🔴 Web interface (1-2 days)
- 🔴 Expert validation (1 week) OR fallback to technical evaluation only
- 🔴 Integration (4 hours)
- 🔴 Front matter (6 hours)
- 🔴 Final polish (1-2 days)

**17 days is enough time IF you start NOW and execute systematically.**

**Remember**:
- Perfect is the enemy of done
- Submitted with minor flaws > Not submitted
- Your technical work is already strong
- This is the execution phase, not the research phase

---

**Next immediate action**: Decide Path A vs Path B, then start Streamlit app THIS WEEKEND if Path A.

Good luck! You've got this. 🚀
