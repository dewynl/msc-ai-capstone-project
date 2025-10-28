# Next Steps: Streamlit Integration (Phase 7)

**Status:** Ready to Begin
**Estimated Time:** 2-3 hours
**Prerequisites:** ✅ All complete

---

## Overview

Integrate the trained CodeT5 model into the existing Streamlit application with difficulty-aware filtering.

---

## Required Components

### 1. RAG Filter Module
**File:** `scripts/rag_filter.py`

```python
def filter_components_by_difficulty(components, course_level, component_type='modules'):
    """
    Filter RAG components by difficulty to match course level.

    CRITICAL: This ensures model only sees appropriate components,
    matching the training data distribution.
    """
    if component_type != 'modules':
        return components  # Activities/assessments don't need filtering

    if course_level == "beginner":
        return [c for c in components if c.get('difficulty') == 'beginner']
    elif course_level == "intermediate":
        return [c for c in components if c.get('difficulty') in ['beginner', 'intermediate']]
    else:  # advanced
        return [c for c in components if c.get('difficulty') in ['intermediate', 'advanced']]
```

### 2. Model Inference Module
**File:** `scripts/model_inference.py`

```python
from transformers import RobertaTokenizer, T5ForConditionalGeneration
import torch

class SyllabusGenerator:
    def __init__(self, model_path="models/codet5-markdown-FULL"):
        self.tokenizer = RobertaTokenizer.from_pretrained(model_path)
        self.model = T5ForConditionalGeneration.from_pretrained(model_path)

        if torch.cuda.is_available():
            self.model = self.model.cuda()

    def generate(self, prompt, max_length=400):
        """Generate markdown syllabus from prompt."""
        input_ids = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True
        ).input_ids

        if torch.cuda.is_available():
            input_ids = input_ids.cuda()

        with torch.no_grad():
            outputs = self.model.generate(
                input_ids,
                max_length=max_length,
                num_beams=2,
                early_stopping=False,
            )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
```

### 3. Integration Function
**File:** `scripts/generate_syllabus.py`

```python
from rag_filter import filter_components_by_difficulty
from model_inference import SyllabusGenerator
from markdown_syllabus_parser import MarkdownSyllabusParser, expand_with_database_details
from enhance_objectives import enhance_objectives, detect_generic_objectives

def generate_complete_syllabus(course_requirements, rag_database):
    """
    Complete pipeline: Filter → Generate → Parse → Enhance → Expand

    Args:
        course_requirements: dict with title, domain, level, duration
        rag_database: dict with modules, activities, assessments

    Returns:
        dict with json, markdown_simple, markdown_rich, warnings
    """

    # 1. Filter by difficulty (CRITICAL STEP - Rule-based)
    filtered_modules = filter_components_by_difficulty(
        rag_database['modules'],
        course_requirements['level'],
        'modules'
    )

    filtered_activities = rag_database['activities']  # No filtering
    filtered_assessments = rag_database['assessments']  # No filtering

    # 2. Build prompt
    prompt = build_prompt(
        course_requirements,
        filtered_modules,
        filtered_activities,
        filtered_assessments
    )

    # 3. Generate markdown (ML-based)
    generator = SyllabusGenerator()
    markdown_simple = generator.generate(prompt)

    # 4. Parse to JSON (Hybrid)
    parser = MarkdownSyllabusParser()
    rag_context = {
        'available_modules': filtered_modules,  # Same filtered set!
        'available_activities': filtered_activities,
        'available_assessments': filtered_assessments
    }

    parse_result = parser.parse(markdown_simple, rag_context)

    if not parse_result.success:
        # Fallback: template-based generation
        return generate_fallback_syllabus(course_requirements, rag_database)

    # 5. Enhance objectives (Rule-based - Bloom's Taxonomy)
    if detect_generic_objectives(parse_result.syllabus['learning_objectives']):
        parse_result.syllabus['learning_objectives'] = enhance_objectives(
            parse_result.syllabus['learning_objectives'],
            course_requirements,
            parse_result.syllabus['modules']
        )

    # 6. Expand with rich details (Hybrid)
    markdown_rich = expand_with_database_details(
        parse_result.syllabus,
        rag_context
    )

    return {
        'success': True,
        'json': parse_result.syllabus,
        'markdown_simple': markdown_simple,
        'markdown_rich': markdown_rich,
        'warnings': parse_result.warnings,
        'metadata': {
            'filtered_modules_count': len(filtered_modules),
            'total_modules_count': len(rag_database['modules']),
            'selected_modules_count': len(parse_result.syllabus['modules'])
        }
    }

def build_prompt(course_req, modules, activities, assessments):
    """Build prompt in training format."""
    prompt = f"Generate syllabus for: {course_req['title']} | {course_req['domain']} | {course_req['level']}\n\n"

    prompt += "Available modules:\n"
    for i, mod in enumerate(modules[:20]):  # Limit to 20
        prompt += f"[{i}] {mod['title']} ({mod.get('estimated_hours', 0)}h, {mod.get('difficulty', 'N/A')})\n"

    prompt += "\nAvailable activities:\n"
    for i, act in enumerate(activities[:15]):  # Limit to 15
        prompt += f"[{i}] {act['title']} ({act.get('estimated_hours', 0)}h)\n"

    prompt += "\nAvailable assessments:\n"
    for i, ass in enumerate(assessments[:5]):  # Limit to 5
        prompt += f"[{i}] {ass['title']} ({ass.get('assessment_type', 'N/A')})\n"

    prompt += "\nSelect relevant components and generate markdown syllabus."

    return prompt
```

---

## Streamlit Integration Points

### Current Flow (to replace)
```python
# Old: Direct database calls or template
syllabus = create_syllabus_template(course_info, selected_modules)
```

### New Flow
```python
# New: ML-powered with filtering
from scripts.generate_syllabus import generate_complete_syllabus

# Prepare inputs
course_requirements = {
    'title': st.text_input("Course Title"),
    'domain': st.selectbox("Domain", [...]),
    'level': st.selectbox("Level", ['beginner', 'intermediate', 'advanced']),
    'duration': st.selectbox("Duration", [...])
}

rag_database = {
    'modules': get_all_modules_from_db(),
    'activities': get_all_activities_from_db(),
    'assessments': get_all_assessments_from_db()
}

# Generate
if st.button("Generate Syllabus"):
    with st.spinner("Generating syllabus..."):
        result = generate_complete_syllabus(course_requirements, rag_database)

        if result['success']:
            # Show tabs
            tab1, tab2, tab3 = st.tabs(["📄 JSON", "📝 Simple Markdown", "📚 Rich Markdown"])

            with tab1:
                st.json(result['json'])
                st.download_button("Download JSON", json.dumps(result['json']))

            with tab2:
                st.markdown(result['markdown_simple'])
                st.download_button("Download Markdown", result['markdown_simple'])

            with tab3:
                st.markdown(result['markdown_rich'])
                st.download_button("Download Rich Markdown", result['markdown_rich'])

            # Show warnings if any
            if result['warnings']:
                st.warning(f"Warnings: {', '.join(result['warnings'])}")

            # Show metadata
            with st.expander("Generation Details"):
                st.write(f"Filtered from {result['metadata']['total_modules_count']} modules to {result['metadata']['filtered_modules_count']} appropriate ones")
                st.write(f"Model selected {result['metadata']['selected_modules_count']} modules")
        else:
            st.error("Generation failed. Using template fallback.")
```

---

## Testing Checklist

- [ ] Test beginner course → only beginner modules shown
- [ ] Test intermediate course → beginner + intermediate modules shown
- [ ] Test advanced course → intermediate + advanced modules shown
- [ ] Test empty module list (edge case)
- [ ] Test very long course title
- [ ] Test special characters in title
- [ ] Test all domains
- [ ] Test all duration types
- [ ] Verify JSON output is valid
- [ ] Verify markdown renders correctly
- [ ] Test download buttons work
- [ ] Check latency (should be 2-3 seconds CPU)
- [ ] Test fallback when parsing fails

---

## Deployment Checklist

- [ ] Model files copied to production
- [ ] Dependencies installed (transformers, torch)
- [ ] RAG filter implemented
- [ ] Parser module accessible
- [ ] Integration function tested
- [ ] Streamlit app updated
- [ ] Error handling added
- [ ] Logging configured
- [ ] Performance monitoring added
- [ ] User documentation updated

---

## Performance Expectations

- **Latency:** 2-3 seconds (CPU), <1 second (GPU)
- **Success Rate:** 100% structure, 100% appropriate selections
- **Memory:** ~500MB model + ~100MB tokenizer
- **Concurrent Users:** 30-40 requests/minute (single CPU)

---

## Fallback Strategy

If model generation fails:

```python
def generate_fallback_syllabus(course_requirements, rag_database):
    """Template-based fallback for reliability."""

    # Use simple rule-based selection
    filtered_modules = filter_components_by_difficulty(
        rag_database['modules'],
        course_requirements['level']
    )

    # Select first 3-4 by hours
    sorted_modules = sorted(filtered_modules, key=lambda x: x.get('estimated_hours', 0))
    selected = sorted_modules[:4]

    # Build template
    return build_template_syllabus(course_requirements, selected)
```

---

## Success Criteria

- ✅ Generates valid JSON 100% of time
- ✅ Selects only appropriate difficulty modules
- ✅ Latency < 5 seconds
- ✅ No crashes on edge cases
- ✅ Fallback works if needed
- ✅ User can download all formats

---

## Files to Create

1. `scripts/rag_filter.py` - Difficulty filtering (30 lines) ⚙️
2. `scripts/model_inference.py` - Model wrapper (50 lines) ⚙️
3. `scripts/generate_syllabus.py` - Pipeline (150 lines) ⚙️
4. `scripts/fallback_generator.py` - Template fallback (100 lines) ⚙️
5. ✅ `scripts/enhance_objectives.py` - Bloom's Taxonomy enhancement (200 lines) - **COMPLETED**
6. Update existing Streamlit app with integration ⚙️

**Total Estimated Lines:** ~600 lines of integration code (including objectives enhancement)
**Time:** 2-3 hours

---

## Post-Integration

1. Run full test suite
2. Collect user feedback
3. Monitor performance metrics
4. Iterate on objectives quality
5. Consider future improvements (CodeT5-base upgrade, etc.)

---

## Ready to Proceed? ✅

All prerequisites complete:
- ✅ Model trained and validated
- ✅ Parser tested (10/10)
- ✅ Architecture documented
- ✅ Limitations understood
- ✅ Integration plan clear

**Next Command:**
```bash
python scripts/phase7_streamlit_integration.py
```
