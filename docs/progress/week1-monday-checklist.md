# Week 1 - Monday Evening Checklist
**Date:** October 13, 2025
**Time Available:** 3 hours (19:00-22:00)
**Goal:** Start evaluation experiments with 10 test cases

---

## 🎯 Tonight's Mission
Generate 10 syllabi across different domains and document results for evaluation chapter.

---

## ✅ Step-by-Step Tasks

### Setup (5 minutes)
- [ ] Open terminal in project directory: `/home/dewyn/dev/msc-ai-capstone-project`
- [ ] Activate conda environment (if using one)
- [ ] Quick test run: `python scripts/custom_input_demo.py` to verify everything works

### Experiments (2 hours)
Run 10 test cases covering:
- [ ] **Test 1-3:** Computer Science (beginner, intermediate, advanced)
- [ ] **Test 4-6:** Mathematics (beginner, intermediate, advanced)
- [ ] **Test 7-9:** Physics (beginner, intermediate, advanced)
- [ ] **Test 10:** Edge case (minimal input or complex requirements)

**For each test:**
1. Run: `python scripts/custom_input_demo.py`
2. Note generation time (displayed in output)
3. Check JSON validity (does it parse correctly?)
4. Save output to: `data/evaluation/test_[number]_[domain]_[level].json`
5. Take screenshot of terminal output
6. Record notes in spreadsheet (see below)

### Documentation (45 minutes)
- [ ] Create spreadsheet: `data/evaluation/experiment_results.csv`

**Columns to track:**
```csv
test_id,domain,level,generation_time_seconds,json_valid,t5_calls,num_modules,num_activities,num_assessments,notes
1,computer_science,beginner,2.3,true,5,4,12,3,"Clean output, good variety"
2,computer_science,intermediate,3.1,true,6,5,15,4,"..."
...
```

- [ ] Save all screenshots to: `docs/evaluation/screenshots/`
- [ ] Write brief summary of what you observed

### Wrap-up (10 minutes)
- [ ] Commit results: `git add data/evaluation/ docs/evaluation/`
- [ ] Commit: `git commit -m "Add Week 1 evaluation experiments - 10 test cases"`
- [ ] Review tomorrow's tasks in `realistic-weekly-schedule.md`
- [ ] Note any issues or questions for tomorrow

---

## 📊 Quick Data Template

Create this file: `data/evaluation/experiment_results.csv`

```csv
test_id,domain,level,generation_time_seconds,json_valid,t5_calls,num_modules,num_activities,num_assessments,notes
```

You'll fill this in as you run each test.

---

## 🚨 If Something Goes Wrong

**Script won't run?**
- Check if model exists: `ls models/t5-function-call-finetuned/`
- Verify ChromaDB exists: `ls chroma_db/`
- Check Python dependencies: `pip list | grep transformers`

**Generation fails?**
- Document the failure in notes column
- Take screenshot of error
- Continue with other tests
- This is valuable data for "Limitations" section!

**Running out of time?**
- Minimum: Complete 5 tests (better to have quality data on 5 than rushed data on 10)
- You can finish remaining tests on Tuesday

---

## 💡 Pro Tips

1. **Keep it simple tonight**: Just run tests and collect data, don't analyze yet
2. **Save everything**: Screenshots, JSON files, timing data - you'll need it for the dissertation
3. **Note surprises**: If something unexpected happens (good or bad), write it down
4. **Don't stress perfection**: This is raw experimental data, analysis comes Tuesday

---

## ✨ Success Criteria for Tonight

By 22:00, you should have:
- ✅ 5-10 test cases completed
- ✅ Results documented in CSV
- ✅ JSON outputs saved
- ✅ Screenshots captured
- ✅ Brief notes on observations

**That's it!** You're not writing the chapter tonight, just gathering the data.

---

**Tomorrow evening (Tuesday):** You'll analyze this data and create performance charts.

Good luck! 🚀
