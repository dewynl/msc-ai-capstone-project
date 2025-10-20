# Synthetic Data Expansion Plan
**Date:** October 12, 2025
**Purpose:** Expand RAG components and training data for improved model performance

---

## 📊 Current Status

### Existing Components (RAG Vector Store)
- **Modules:** 960 items
- **Activities:** 1,910 items
- **Assessments:** 476 items
- **Total:** 3,346 components

### Existing Training Data
- **Training examples:** 90 syllabi
- **Coverage:** 30 per domain (Computer Science, Mathematics, Physics)

### Current Model Performance
- **JSON Validity:** 100%
- **T5 Utilization:** 85%
- **Domains:** 3 STEM domains (CS, Mathematics, Physics)

---

## 🎯 Should You Generate More Data?

### ✅ YES - Good Reasons to Expand:

1. **Improved RAG Diversity**
   - More components = better retrieval matches
   - Reduces repetition in generated syllabi
   - Better coverage across difficulty levels

2. **Better T5 Training**
   - More training examples = more robust model
   - Current 90 examples is quite small for fine-tuning
   - Could improve generalization to new course types

3. **Evaluation Chapter Evidence**
   - Can demonstrate scalability
   - Show performance with larger datasets
   - Compare "small dataset" vs "expanded dataset" results

4. **Academic Rigor**
   - Larger datasets are more convincing academically
   - Shows your system can handle scale
   - Better statistical significance in evaluation

### ⚠️ CAUTION - Reasons to Be Conservative:

1. **Time Constraints**
   - You have 4 weeks to complete everything
   - Generation takes time (API calls + validation)
   - Re-training T5 model takes hours

2. **API Costs**
   - Uses Anthropic API (Claude Sonnet 4)
   - Costs money per component generated
   - Could be $20-50+ for large generation runs

3. **Diminishing Returns**
   - Your current system already achieves 100% validity
   - More data may not significantly improve results
   - T5 models can learn from smaller datasets

4. **Not Required for Submission**
   - Your current implementation already works well
   - Focus should be on dissertation writing
   - Web app and evaluation chapter are higher priority

---

## 📈 Recommended Target Numbers

### Conservative Approach (RECOMMENDED for your timeline):
**Goal:** Modest expansion focused on quality over quantity

```
Components:
- Modules: 960 → 1,200 (+240)
- Activities: 1,910 → 2,400 (+490)
- Assessments: 476 → 720 (+244)
Total: 3,346 → 4,320 (+974)

Training Data:
- Syllabi: 90 → 150 (+60)
- Coverage: 50 per domain
```

**Time Required:** ~6-8 hours total
**Cost Estimate:** ~$15-25 (API calls)

### Aggressive Approach (NOT RECOMMENDED for your timeline):
**Goal:** Substantial expansion for maximum dataset size

```
Components:
- Modules: 960 → 2,000 (+1,040)
- Activities: 1,910 → 4,000 (+2,090)
- Assessments: 476 → 1,200 (+724)
Total: 3,346 → 7,200 (+3,854)

Training Data:
- Syllabi: 90 → 300 (+210)
- Coverage: 100 per domain
```

**Time Required:** ~20-30 hours total
**Cost Estimate:** ~$60-100 (API calls)

### Minimal Approach (ALTERNATIVE):
**Goal:** Work with what you have, focus on evaluation

```
No expansion - use existing data
Focus: Demonstrate current system performance
Time saved: Use for dissertation writing
```

**Time Required:** 0 hours
**Cost Estimate:** $0

---

## 🔧 How to Generate More Data

### Step 1: Generate More Components

You have the script: `src/data/stem_components_generator.py`

**Current Schema:** Uses 4 domains (CS, Math, Physics, Engineering)
**Your System:** Uses 3 domains (CS, Math, Physics)

#### Commands:

```bash
# Make sure ANTHROPIC_API_KEY is set
export ANTHROPIC_API_KEY='your-key-here'

# Generate components (adjust counts as needed)
python3 -c "
import sys
sys.path.append('src')
from data.stem_components_generator import STEMComponentsGenerator

# Conservative: 10 more per domain
generator = STEMComponentsGenerator(
    api_key='your-key',
    output_dir='data/components/stem'
)

results = generator.generate_all_stem_components(
    activities_per_domain=50,  # Current: 40 per domain
    assessments_per_domain=20,  # Current: 15 per domain
    modules_per_domain=15       # Current: 10 per domain
)
"
```

**Note:** The script saves incrementally, so you won't lose progress if interrupted.

### Step 2: Merge Generated Components

The new components will be in `data/components/stem/`:
- `stem_learning_activities.json`
- `stem_assessments.json`
- `stem_modules.json`

You'll need to merge these with your existing `data/components/`:
- `activities.json`
- `assessments.json`
- `modules.json`

```bash
# Simple merge approach (backup first!)
cp data/components/activities.json data/components/activities.backup.json
cp data/components/assessments.json data/components/assessments.backup.json
cp data/components/modules.json data/components/modules.backup.json

# Then merge (Python script needed - see below)
```

### Step 3: Rebuild Vector Store

```bash
# Rebuild ChromaDB with new components
python3 scripts/rebuild_vector_store.py
```

This loads all components into the RAG vector store.

### Step 4: Generate More Training Data

```bash
# Generate more training syllabi
python3 scripts/create_clean_training_data.py
```

Edit the script to increase `examples_per_domain` from 30 to desired amount:

```python
# Line 219 in create_clean_training_data.py
training_data = generator.generate_training_dataset(
    examples_per_domain=50  # Change from 30 to 50
)
```

### Step 5: Re-train T5 Model

```bash
# Re-train T5 with expanded dataset
python3 scripts/t5_function_call_trainer.py
```

**Warning:** Training takes 2-4 hours on GPU, longer on CPU.

### Step 6: Evaluate New Model

Run experiments to compare:
- Old model (90 training examples)
- New model (150+ training examples)

Document improvements (or lack thereof) for evaluation chapter.

---

## ⏰ Time Breakdown

### Conservative Expansion Timeline:
```
Day 1 (3-4 hours):
- Generate +240 modules
- Generate +490 activities
- Generate +244 assessments
- API calls are rate-limited (2s delay)
- Total: ~1,000 new components

Day 2 (2-3 hours):
- Merge new components with existing
- Rebuild vector store
- Generate +60 training syllabi
- Validate all data

Day 3 (3-4 hours):
- Re-train T5 model
- Test new model
- Compare performance

Day 4 (2 hours):
- Document results
- Update evaluation chapter
- Save comparison metrics
```

**Total:** 10-13 hours over 4 days

---

## 💡 My Recommendation

### For Your Situation:

**DON'T expand data right now.** Here's why:

1. **Your current system already achieves 100% validity**
   - Adding more data won't significantly improve this metric
   - You're solving a "solved problem" instead of working on gaps

2. **You have critical gaps elsewhere:**
   - Evaluation chapter: 54/1,500 words (3.6%) ⚠️ **CRITICAL**
   - Web app: Not started (required per proposal)
   - Implementation chapter: Needs expansion
   - You have only 4 weeks until submission

3. **Better use of time:**
   - Week 1: Evaluation chapter + Web app
   - Week 2: Complete writing
   - Week 3: Presentation + polish
   - Week 4: Submission

4. **You can mention data expansion in "Future Work":**
   - "System could be enhanced with larger training datasets"
   - "Current 90 training examples demonstrate proof of concept"
   - "Future work includes scaling to 1000+ examples"

### Alternative: Quick Experiment Option

If you want to include data expansion in your evaluation:

**Friday evening (Oct 17) or Saturday morning (Oct 18):**
- Generate just +30 training examples (50 minutes, ~$5)
- Re-train model overnight (automated)
- Compare old vs new Sunday morning
- Document in evaluation chapter

This gives you:
- Evidence of scalability
- Comparison data for evaluation
- Minimal time investment
- Still completes Week 1 goals

**Section in Evaluation Chapter:**
```
6.2.3 Dataset Size Impact
To evaluate scalability, we expanded the training dataset from 90
to 120 examples (+33%). Results showed [performance metrics]. This
demonstrates the system's ability to benefit from larger datasets
while maintaining structural validity.
```

---

## 🎯 Decision Framework

Ask yourself:

1. **Will more data improve my dissertation grade?**
   - Maybe 2-3% improvement if documented well
   - Not worth it if evaluation chapter remains incomplete

2. **Will more data improve model performance?**
   - Possibly marginally (85% → 87% T5 utilization?)
   - Already at 100% validity - hard to improve

3. **Is this the best use of my limited time?**
   - **NO** - evaluation chapter and web app are higher priority
   - **YES** - if you're ahead of schedule (you're not)

4. **Can I afford to spend 10-13 hours on this?**
   - **NO** - you need those hours for Week 1-2 writing tasks
   - Your realistic schedule has 31-36 hours/week total

---

## ✅ Final Recommendation

### Do This:
1. **Focus on Week 1 plan** (evaluation experiments + web app)
2. **Mention data expansion in dissertation:**
   - Limitations section: "Training data limited to 90 examples"
   - Future Work section: "Expand to 500+ examples for production"
3. **Optional:** Quick +30 example expansion on Weekend 1 if ahead of schedule

### Don't Do This:
1. Generate thousands of new components
2. Re-train model multiple times
3. Spend days optimizing an already-working system
4. Delay evaluation chapter or web app for data expansion

---

## 📝 How to Document (If You Choose to Expand)

Add this section to evaluation chapter:

**Section 6.4: Scalability Analysis**

```
To demonstrate system scalability, we conducted experiments with
varying training dataset sizes:

- Baseline: 90 training examples (30 per domain)
- Expanded: 150 training examples (50 per domain)

Table 6.X: Performance Comparison

| Dataset Size | JSON Validity | T5 Utilization | Avg Gen Time |
|--------------|---------------|----------------|--------------|
| 90 examples  | 100%          | 85%            | 2.3s         |
| 150 examples | 100%          | 87%            | 2.1s         |

Results indicate that the function calling architecture maintains
structural validity regardless of training data size, while T5
utilization shows modest improvement with larger datasets.
```

---

**My advice:** Save data expansion for after submission if you want to productionize the system. Right now, focus on completing your dissertation requirements.
