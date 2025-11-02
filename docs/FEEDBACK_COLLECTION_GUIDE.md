# 🎯 Feedback Collection Quick Start Guide

**Goal:** Collect 50 diverse user ratings to enable Model v2 fine-tuning

**Current Progress:** 1/50 ratings (49 remaining)

**Estimated Time:** 1.5-2 hours total

---

## 📋 Step-by-Step Process

### 1. Start the Streamlit App

```bash
cd /home/dewyn/dev/msc-ai-capstone-project
streamlit run streamlit_app.py
```

### 2. Generate Syllabi Systematically

Use the course list from: `scripts/feedback/generate_diverse_syllabi.py`

**Recommended Workflow (Batches of 10):**
1. Generate 10 syllabi back-to-back (~15-20 minutes)
2. Rate all 10 while fresh in memory (~5 minutes)
3. Take a short break
4. Repeat 5 times = 50 syllabi

### 3. Rating Guidelines

**What to Consider (Rate 1-10):**
- ✅ **Pedagogical coherence:** Do topics flow logically?
- ✅ **Difficulty progression:** Does it build from simple to complex?
- ✅ **Topic coverage:** Are all important topics included?
- ✅ **Learning objectives:** Are they clear, measurable, and appropriate?
- ✅ **Prerequisites:** Do module dependencies make sense?

**Be Honest - Variation is Good!**
- Don't rate everything 7-8
- If something is genuinely poor → rate 2-4
- If something is excellent → rate 9-10
- We want diverse feedback for training

### 4. Check Progress Regularly

```bash
python3 scripts/feedback/check_feedback_progress.py
```

This shows:
- Total ratings collected
- Average score
- High-quality syllabi count (≥7/10)
- Progress bar toward 50-rating threshold
- Score distribution

---

## 🎓 Recommended Course Order

**Start with familiar domains (faster rating):**
1. Computer Science Beginner (10 courses) - ~20 min generation + 5 min rating
2. Computer Science Intermediate (10 courses) - ~20 min generation + 5 min rating
3. Mathematics Beginner (5 courses) - ~10 min generation + 3 min rating
4. Physics Beginner (3 courses) - ~6 min generation + 2 min rating

**Take break here (25 ratings done)**

5. Computer Science Advanced (7 courses) - ~15 min generation + 4 min rating
6. Mathematics Intermediate (5 courses) - ~10 min generation + 3 min rating
7. Mathematics Advanced (3 courses) - ~6 min generation + 2 min rating
8. Physics Intermediate (4 courses) - ~8 min generation + 2 min rating
9. Physics Advanced (3 courses) - ~6 min generation + 2 min rating

**Total: 50 ratings (50 ratings done)**

---

## 📊 After Reaching 50 Ratings

### Step 1: Verify Data Quality

```bash
python3 scripts/feedback/check_feedback_progress.py
```

Should show:
- ✅ Total: 50+ ratings
- ✅ High quality (≥7/10): ~15-20 syllabi (30-40%)
- ✅ Score distribution: varied across 1-10

### Step 2: Fine-Tune Model v2

```bash
python3 scripts/feedback/fine_tune_from_feedback.py
```

**This will:**
1. Export high-quality syllabi (≥7/10) from Supabase
2. Convert to training format (markdown)
3. Fine-tune CodeT5 with conservative parameters:
   - Learning rate: 2e-6
   - Epochs: 2
   - Batch size: 4
4. Save new model checkpoint to `models/codet5-sequenced/checkpoint-feedback-{timestamp}`

**Expected Duration:** 10-30 minutes depending on data size

### Step 3: Evaluate Model v2 vs Model v1

```bash
# Re-run evaluation on same test set with new model
python scripts/evaluation/evaluator.py --model models/codet5-sequenced/checkpoint-feedback-{timestamp}
```

Compare metrics:
- Prerequisite accuracy
- Semantic coherence
- Difficulty progression
- Bloom's taxonomy coverage
- Overall composite quality

### Step 4: Statistical Analysis

Run paired t-test comparing Model v1 vs Model v2 performance on identical test cases.

### Step 5: Document Results

Add findings to dissertation Chapter 6 (Evaluation).

---

## 💡 Tips for Efficient Collection

**Speed Up Generation:**
- Keep course requirements template open in a text file
- Copy-paste systematically
- Don't overthink - just generate and rate

**Rating Consistency:**
- Create a mental rubric for 1-10 scale
- Example:
  - 1-3: Poor (major issues, missing content)
  - 4-6: Fair (works but has noticeable problems)
  - 7-8: Good (solid quality, minor improvements possible)
  - 9-10: Excellent (publication-ready quality)

**Take Breaks:**
- After every 10 syllabi
- Prevents rating fatigue
- Maintains judgment quality

---

## 🚨 Troubleshooting

**Streamlit crashes:**
```bash
# Restart app
streamlit run streamlit_app.py
```

**Feedback not saving:**
- Check Supabase credentials in `.env`
- Verify RLS policies are applied (see `docs/supabase-feedback-schema.sql`)

**Progress not updating:**
```bash
# Re-check database
python3 scripts/feedback/check_feedback_progress.py
```

---

## 📈 Expected Timeline

| Activity | Duration | Cumulative |
|----------|----------|------------|
| Generate 50 syllabi | ~90-120 min | 120 min |
| Rate 50 syllabi | ~25-30 min | 150 min |
| Fine-tune Model v2 | ~10-30 min | 180 min |
| Evaluate & compare | ~20-30 min | 210 min |
| Statistical analysis | ~15-20 min | 230 min |
| **Total** | **~3.5-4 hours** | - |

Most of this can be done in one focused session!

---

## ✅ Success Criteria

- [ ] 50+ total ratings collected
- [ ] ~15-20 high-quality syllabi (≥7/10)
- [ ] Varied score distribution (not all 7-8)
- [ ] Diverse domain coverage (CS, Math, Physics)
- [ ] All difficulty levels represented (beginner, intermediate, advanced)
- [ ] Model v2 fine-tuned successfully
- [ ] Comparative evaluation completed
- [ ] Statistical significance tested
- [ ] Results documented in dissertation

---

Good luck! Remember: **Quality over speed** - honest ratings make better training data. 🚀
