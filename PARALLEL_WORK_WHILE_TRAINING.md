# Parallel Work Plan: While Training Runs

**Training Status:** 30 min in progress, ~5 hours remaining
**CPU Usage:** 90%+ (WSL2 busy with training)
**Available:** Windows environment, light WSL2 tasks, web browser

---

## 🔥 High Priority (Dissertation Critical)

### 1. Dissertation Writing (3-5 hours) ⭐⭐⭐

**Location:** Word/Google Docs (Windows, no CPU needed)

#### **Chapter 3: Methodology**
*Estimated: 2 hours*

**3.1 Research Design**
```
- Explain experimental approach
- Justify CodeT5 selection over alternatives
- Describe function calling architecture
- Present RAG integration strategy
```

**Content Available:**
- `docs/technical-appendix-training-journey.md` (Phase 1-3)
- `docs/experimental-results-comparison.md`
- Architecture diagrams needed (see task #3 below)

**3.2 Data Collection**
```
- Claude Sonnet 4.5 for component generation
- RAG-enhanced syllabus composition
- Deduplication strategy
- Quality assurance measures
```

**Reference:** Technical appendix Phase 3, Phase 4

**3.3 Training Procedure**
```
- Hyperparameter selection rationale
- Training vs evaluation split (90/10)
- Early stopping strategy
- Hardware constraints and mitigations
```

**Reference:** Technical appendix Phase 5

#### **Chapter 1: Introduction**
*Estimated: 1 hour*

```
1.1 Background and Motivation
    - Educational technology challenges
    - Why LLMs struggle with structured outputs
    - Gap: Semantic intelligence + structural validity

1.2 Research Questions
    - RQ1: Can small models generate valid function sequences?
    - RQ2: Does RAG enhance educational domain knowledge?
    - RQ3: What data quantity needed for competence?

1.3 Contributions
    - Novel function calling architecture
    - RAG-enhanced data generation methodology
    - Empirical data scaling study (260 → 1,117 examples)

1.4 Dissertation Structure
    - Brief overview of chapters 2-6
```

#### **Chapter 2: Literature Review**
*Estimated: 2 hours*

**You have 43 references ready in:** `docs/master-literature-list.md`

**Structure:**
```
2.1 Large Language Models for Code Generation
    - T5, CodeT5, CodeGen, CodeParrot
    - Structured output challenges
    - Function calling vs free-form generation

2.2 Educational AI and Syllabus Generation
    - Current approaches (template-based, LLM-based)
    - Limitations of existing systems
    - Pedagogical validity requirements

2.3 Retrieval-Augmented Generation
    - RAG architecture principles
    - Domain-specific knowledge integration
    - Application to educational content

2.4 Model Fine-Tuning and Data Scaling
    - Scaling laws (Kaplan et al., 2020)
    - Data efficiency in fine-tuning
    - Small model effectiveness

2.5 Research Gap and Positioning
    - What existing work misses
    - How this research fills the gap
```

**Action Items:**
- [ ] Read/skim all 43 references (prioritize recent)
- [ ] Create synthesis table (approach, dataset size, results)
- [ ] Identify 3-5 key papers to cite heavily
- [ ] Write critical analysis (not just summary)

---

### 2. Prepare Enhanced Evaluation Framework (1-2 hours) ⭐⭐

**Goal:** Better metrics and visualizations for tomorrow's model evaluation

**Current evaluation:** `scripts/evaluate_codet5_model.py`
- Basic pass/fail on 5 test cases
- Checks: length, required calls, syntax, execution

**Enhancements to add:**

#### **A. Comparative Metrics**
```python
# Create: scripts/comparative_evaluation.py

def compare_models():
    """Compare 260-example vs 1,117-example models"""

    metrics = {
        'model_260': evaluate_model('./models/extended-standard-training'),
        'model_1117': evaluate_model('./models/codet5-1300examples')
    }

    # Generate comparison table
    comparison = {
        'Pass Rate': [metrics['model_260']['pass_rate'],
                      metrics['model_1117']['pass_rate']],
        'Avg Output Length': [...],
        'Syntax Error Rate': [...],
        'Component Coverage': [...]
    }

    # Export to dissertation-ready format
    export_latex_table(comparison)
    export_csv(comparison)
```

#### **B. Token Length Distribution Analysis**
```python
def analyze_output_lengths(model_path):
    """Measure token generation patterns"""

    test_cases = load_test_cases(50)  # More than 5
    outputs = []

    for test in test_cases:
        output = generate(test)
        outputs.append({
            'length': len(output),
            'num_function_calls': count_calls(output),
            'has_build': 'build()' in output
        })

    # Plot distribution
    plot_histogram(outputs)

    # Statistical summary
    return {
        'mean_length': np.mean([o['length'] for o in outputs]),
        'std_length': np.std([o['length'] for o in outputs]),
        'min_length': min([o['length'] for o in outputs]),
        'max_length': max([o['length'] for o in outputs]),
        'truncation_rate': sum([o['length'] < 500 for o in outputs]) / len(outputs)
    }
```

#### **C. Component Coverage Analysis**
```python
def analyze_component_usage(model_path):
    """Check if model uses diverse components"""

    # Generate 100 syllabi
    syllabi = [generate_syllabus(template) for template in templates]

    # Extract component IDs used
    module_ids = set()
    activity_ids = set()
    assessment_ids = set()

    for syllabus in syllabi:
        module_ids.update(extract_module_ids(syllabus))
        activity_ids.update(extract_activity_ids(syllabus))
        assessment_ids.update(extract_assessment_ids(syllabus))

    return {
        'unique_modules': len(module_ids),
        'unique_activities': len(activity_ids),
        'unique_assessments': len(assessment_ids),
        'total_unique': len(module_ids) + len(activity_ids) + len(assessment_ids),
        'coverage_rate': total_unique / total_available_components
    }
```

**Files to create:**
- `scripts/comparative_evaluation.py`
- `scripts/analysis/output_length_distribution.py`
- `scripts/analysis/component_coverage_analysis.py`
- `scripts/visualization/plot_results.py`

**Time:** 1-2 hours to implement, will save time tomorrow

---

### 3. Create Visualizations and Diagrams (1-2 hours) ⭐⭐

**Tools:** Draw.io, PowerPoint, Python (matplotlib/seaborn)

#### **Architecture Diagram**
```
┌─────────────────────────────────────────────────┐
│         User Input (Course Requirements)         │
│   (Title, Domain, Level, Duration, Description) │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│              RAG Component Retrieval             │
│  ┌──────────────────────────────────────────┐  │
│  │   ChromaDB Vector Store                  │  │
│  │   • 960 Modules                          │  │
│  │   • 1,910 Activities                     │  │
│  │   • 476 Assessments                      │  │
│  └──────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────┘
                 │ Retrieve Top-K candidates
                 ▼
┌─────────────────────────────────────────────────┐
│        Fine-tuned CodeT5 Model (60M)            │
│    Generates Function Call Sequence             │
│                                                  │
│  set_info(title, domain, level, ...)           │
│  add_objective("...")                            │
│  add_module_by_id("mod_123")                    │
│  add_activity_by_id("act_456")                  │
│  add_assessment_by_id("asmt_789")               │
│  build()                                         │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│        SyllabusBuilder Execution Engine         │
│  • Validates function call syntax               │
│  • Executes function calls sequentially         │
│  • Performs pedagogical validation              │
│  • Constructs JSON output                       │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│           Structured JSON Syllabus              │
│         (Guaranteed Valid Output)               │
└─────────────────────────────────────────────────┘
```

#### **Training Data Comparison**
```python
import matplotlib.pyplot as plt
import numpy as np

# Create comparison bar chart
models = ['Baseline\n(260 examples)', 'Scaled\n(1,117 examples)']
pass_rates = [0, 'TBD']  # Update tomorrow
output_lengths = [230, 'TBD']
training_times = [4.3, 5.5]

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Pass rate
axes[0].bar(models, [0, 0.6], color=['red', 'green'])  # Hypothetical
axes[0].set_title('Pass Rate Comparison')
axes[0].set_ylabel('Pass Rate (%)')

# Output length
axes[1].bar(models, [230, 850], color=['red', 'green'])
axes[1].set_title('Average Output Length')
axes[1].set_ylabel('Characters')

# Training time
axes[2].bar(models, [4.3, 5.5], color=['blue', 'blue'])
axes[2].set_title('Training Time')
axes[2].set_ylabel('Hours')

plt.tight_layout()
plt.savefig('docs/figures/model_comparison.png', dpi=300)
```

#### **Data Scaling Journey**
```
Data Scaling Impact on Model Performance

Examples →  260        1,117 (4.3× increase)
            ↓             ↓
Epochs →    41          15 (scaled down)
            ↓             ↓
Training
Intensity → 10,660    17,550 (1.65× increase)
            ↓             ↓
Pass Rate → 0%         TBD% (expected 60-80%)
            ↓             ↓
Output
Length →    230 chars  TBD chars (expected 800-1000)
```

**Diagrams needed:**
1. System architecture (high-level)
2. Training pipeline flowchart
3. Data generation process
4. Model comparison (before/after)
5. Component database structure
6. Evaluation methodology

**Save to:** `docs/figures/`

---

## 🟡 Medium Priority (Good to Have)

### 4. Streamlit App Improvements (2-3 hours)

**Location:** Can work in Windows or WSL2 (light CPU)

**Current app:** `streamlit_app/app.py`

**Improvements:**

#### **A. Better Error Handling**
```python
# Current: Basic try/except
# Add: User-friendly error messages

try:
    syllabus = generate_syllabus(params)
except ModelNotLoadedError:
    st.error("🚨 Model not loaded. Please check model path in settings.")
except InvalidInputError as e:
    st.warning(f"⚠️ Invalid input: {e.message}")
except Exception as e:
    st.error(f"❌ Unexpected error: {e}")
    st.info("💡 Try refreshing the page or checking your inputs.")
```

#### **B. Model Comparison Feature**
```python
# Add sidebar option to compare models
model_choice = st.sidebar.selectbox(
    "Select Model",
    ["Baseline (260 examples)", "Scaled (1,117 examples)", "Both (compare)"]
)

if model_choice == "Both (compare)":
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Baseline Model")
        syllabus_baseline = generate_with_model("./models/extended-standard-training")
        st.json(syllabus_baseline)

    with col2:
        st.subheader("Scaled Model")
        syllabus_scaled = generate_with_model("./models/codet5-1300examples")
        st.json(syllabus_scaled)
```

#### **C. Example Gallery**
```python
# Add pre-generated examples for quick testing
st.sidebar.markdown("## 📚 Example Courses")

examples = {
    "Intro to Python": {
        "title": "Introduction to Python Programming",
        "domain": "computer_science",
        "level": "beginner",
        ...
    },
    "Machine Learning": {...},
    "Web Development": {...}
}

if st.sidebar.button("Load Example: Intro to Python"):
    st.session_state.update(examples["Intro to Python"])
    st.rerun()
```

#### **D. Export Options**
```python
# Add download buttons
if syllabus:
    col1, col2, col3 = st.columns(3)

    with col1:
        json_str = json.dumps(syllabus, indent=2)
        st.download_button(
            "📄 Download JSON",
            json_str,
            "syllabus.json",
            "application/json"
        )

    with col2:
        pdf = generate_pdf(syllabus)
        st.download_button(
            "📕 Download PDF",
            pdf,
            "syllabus.pdf",
            "application/pdf"
        )

    with col3:
        markdown = convert_to_markdown(syllabus)
        st.download_button(
            "📝 Download Markdown",
            markdown,
            "syllabus.md",
            "text/markdown"
        )
```

**Time:** 2-3 hours for all improvements

---

### 5. Hugging Face Model Card Preparation (1 hour)

**Goal:** Ready-to-publish model card when results look good

**Template:** `MODEL_CARD.md`

```markdown
---
language: en
license: mit
tags:
- code-generation
- function-calling
- educational-content
- syllabus-generation
- codet5
datasets:
- custom
metrics:
- exact_match
- syntax_accuracy
model-index:
- name: codet5-educational-function-calling
  results:
  - task:
      type: text2text-generation
      name: Function Call Generation
    metrics:
    - type: pass_rate
      value: TBD  # Update after evaluation
      name: Pass Rate
---

# CodeT5 for Educational Function Calling

## Model Description

This model is a fine-tuned version of [Salesforce/codet5-small](https://huggingface.co/Salesforce/codet5-small)
trained on 1,117 examples of educational syllabus generation through function calls.

### Model Architecture

- **Base Model:** CodeT5-small (60M parameters)
- **Fine-tuning:** Educational function call generation
- **Training Data:** 1,117 RAG-enhanced examples
- **Training Duration:** 5.5 hours on CPU

## Intended Use

Generate structured course syllabi by producing valid Python function call sequences:

```python
from transformers import RobertaTokenizer, T5ForConditionalGeneration

tokenizer = RobertaTokenizer.from_pretrained("your-username/codet5-educational-function-calling")
model = T5ForConditionalGeneration.from_pretrained("your-username/codet5-educational-function-calling")

input_text = 'Generate course syllabus: {"title": "Introduction to Python", "domain": "computer_science", "level": "beginner", ...}'
inputs = tokenizer(input_text, return_tensors="pt")
outputs = model.generate(**inputs, max_length=512)
function_calls = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

## Training Data

- **Total Examples:** 1,117 unique syllabi
- **Domains:** Computer Science, Mathematics, Data Science, Business, Engineering
- **Difficulty Levels:** Beginner (450), Intermediate (500), Advanced (167)
- **Component Database:** 960 modules, 1,910 activities, 476 assessments

## Training Procedure

### Hyperparameters

```python
learning_rate: 3e-4
batch_size: 20
gradient_accumulation: 4 (effective batch: 80)
epochs: 15
warmup_steps: 18
lr_scheduler: linear
weight_decay: 0.01
label_smoothing: 0.1
```

### Training Hardware

- CPU: AMD Ryzen 7 7700X (8-core)
- RAM: 64GB
- Training Time: 5.5 hours

## Evaluation Results

### Test Suite Performance

| Metric | Baseline (260 examples) | Scaled (1,117 examples) |
|--------|-------------------------|-------------------------|
| Pass Rate | 0/5 (0%) | TBD/5 (TBD%) |
| Avg Output Length | 230 chars | TBD chars |
| Syntax Error Rate | 60% | TBD% |

## Limitations

- Trained on English educational content only
- Limited to predefined function call vocabulary
- Requires SyllabusBuilder execution engine for output

## Citation

```bibtex
@mastersthesis{your_thesis_2025,
  title={Domain-Specific AI for Educational Syllabus Generation},
  author={Your Name},
  year={2025},
  school={Your University}
}
```

## License

MIT License - See LICENSE file for details
```

**Save to:** `MODEL_CARD.md` (update after evaluation tomorrow)

---

### 6. README and Documentation Updates (1 hour)

**Update:** `README.md`

Add sections:
- Recent results (1,117-example training)
- Model comparison table
- Performance metrics
- Updated quick start guide

**Create:** `docs/FAQ.md`
```markdown
# Frequently Asked Questions

## Training

**Q: Why only 15 epochs for 1,117 examples?**
A: Training intensity = examples × epochs. 1,117 × 15 = 16,755 exposures,
   comparable to baseline 260 × 41 = 10,660. More epochs = overtraining.

**Q: Why CPU instead of GPU?**
A: WSL2 lacks AMD GPU support. Windows DirectML possible but risky for
   dissertation timeline. CPU training takes 5.5 hours (acceptable).

**Q: How much did data generation cost?**
A: ~$31 total ($21 for successful generation + $10 from failed run)

## Model

**Q: Why CodeT5 instead of GPT-4?**
A: Function calling architecture contribution requires trainable model.
   GPT-4 would be API-only, no architecture novelty.

**Q: Why only 60M parameters?**
A: Small model with right architecture > large model with wrong architecture.
   60M is sufficient for structured generation tasks.

## Data

**Q: Why 1,117 examples, not 1,300?**
A: Deduplication removed 183 duplicates. High-quality unique examples
   better than quantity with duplicates.

**Q: How long did data generation take?**
A: ~90 minutes (successful run after fixing infrastructure bugs)
```

---

## 🟢 Low Priority (Future Work)

### 7. Windows GPU Setup (if time permits)

**Only if:** You want to enable GPU for future iterations

**Follow:** `WINDOWS_GPU_SETUP.md`
**Time:** 30-60 minutes
**Benefit:** Future training runs take 0.5-1 hour instead of 6 hours

---

### 8. Code Cleanup and Refactoring (1-2 hours)

**Tasks:**
- Remove unused imports
- Add type hints consistently
- Improve docstrings
- Run linting (black, pylint)
- Update .pre-commit hooks

**Not urgent**, but good practice.

---

### 9. Related Work Deep Dive (2-3 hours)

**Goal:** Understand competitive approaches better

**Papers to read:**
1. **CodeT5 original paper** (Wang et al., 2021)
   - Understand architecture deeply
   - Compare to our fine-tuning approach

2. **Function calling in LLMs** (recent papers)
   - OpenAI function calling
   - Gorilla paper
   - ToolFormer

3. **Educational AI systems**
   - Course recommendation systems
   - Automated curriculum design
   - AI tutors and content generation

**Output:** Annotated bibliography for literature review

---

### 10. Notion Updates (30 min)

**Update your Notion workspace:**

**Task List Database** (`2190fb82-b534-8051-8407-c5b50bbec332`):
- Mark completed tasks
- Add new tasks for post-training evaluation
- Update sprint status

**Project Context** (`20c0fb82-b534-80e3-b48d-f4d9cc5bf464`):
- Document current status
- Add training results (when available)
- Link to new documents created

**Dissertation Progress** (`2190fb82-b534-8073-adb1-d9ca27dfb18a`):
- Update word count progress
- Add chapter outlines
- Track completion status

---

## 📅 Suggested 5-Hour Schedule

**Hour 1 (22:30-23:30):** Dissertation Chapter 1 (Introduction)
- Write background and motivation
- Articulate research questions
- Draft contributions

**Hour 2 (23:30-00:30):** Dissertation Chapter 3.1-3.2 (Methodology)
- Research design
- Data collection methodology
- Use technical appendix as source

**Hour 3 (00:30-01:30):** Create Visualizations
- Architecture diagram
- Training comparison charts
- Data scaling visualization

**Hour 4 (01:30-02:30):** Prepare Enhanced Evaluation
- Write comparative_evaluation.py
- Add output length analysis
- Create visualization scripts

**Hour 5 (02:30-03:30):** Streamlit App Improvements
- Error handling
- Model comparison feature
- Export options

**03:30:** Training completes! ✅

---

## ⚠️ Things to AVOID

**Don't do:**
- ❌ Heavy CPU tasks in WSL2 (will slow training)
- ❌ Restart WSL2 (will kill training)
- ❌ Large file operations in WSL2
- ❌ Running other Python scripts in same venv

**Safe to do:**
- ✅ Windows applications (Word, PowerPoint, browser)
- ✅ Light text editing in WSL2
- ✅ Monitoring training logs (`tail -f`)
- ✅ Web research and reading

---

## 🎯 Priority Ranking

If you have limited time, do in this order:

1. **Dissertation Chapter 1** (1 hour) - Critical for structure
2. **Dissertation Chapter 3** (1-2 hours) - Documents your work
3. **Create Visualizations** (1 hour) - Needed for dissertation
4. **Prepare Evaluation** (1 hour) - Saves time tomorrow
5. **Everything else** - Nice to have

---

**Current Status:** Training 30 min in, all documentation complete. You have 5 productive hours ahead! 🚀
