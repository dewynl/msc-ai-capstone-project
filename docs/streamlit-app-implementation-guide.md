# Streamlit App Implementation Guide

**Purpose**: Build web interface for syllabus generation with full RAG + T5 functionality

**Timeline**: Work on this in a dedicated session (not today)

**Goal**: Get it working locally first, then deploy to cloud with 100% functionality

---

## Technical Constraints

**Current System**:
- ✅ Works perfectly locally (`python scripts/custom_input_demo.py`)
- ✅ ChromaDB: 87MB (manageable)
- ⚠️ T5 Model: 2.3GB (exceeds GitHub 100MB limit)

**Cloud Deployment Challenge**:
- Can't commit 2.3GB model to git
- Need strategy to handle large model files
- Must maintain full RAG + T5 functionality

---

## Phase 1: Build Local Streamlit App

### Step 1: Create `streamlit_app.py`

```python
import streamlit as st
import json
import time
from src.models.rag_integrated_generator import RAGIntegratedSyllabusBuilder

st.set_page_config(page_title="AI Syllabus Generator", page_icon="🎓")

st.title("🎓 AI Syllabus Generator")
st.write("Generate educational syllabi using function calling architecture + RAG")

# Load generator
@st.cache_resource
def load_generator():
    return RAGIntegratedSyllabusBuilder()

try:
    generator = load_generator()
    st.success("✅ System ready!")
except Exception as e:
    st.error(f"❌ Error loading system: {e}")
    st.stop()

# Input form
with st.form("syllabus_form"):
    col1, col2 = st.columns(2)

    with col1:
        title = st.text_input("Course Title", "Introduction to Machine Learning")
        domain = st.selectbox("Domain", ["computer_science", "mathematics", "physics"])

    with col2:
        level = st.selectbox("Level", ["beginner", "intermediate", "advanced"])
        duration = st.selectbox("Duration", ["semester", "quarter", "6-week", "custom"])

    description = st.text_area(
        "Course Description",
        "An introductory course covering fundamental concepts...",
        height=100
    )

    submitted = st.form_submit_button("🚀 Generate Syllabus", use_container_width=True)

if submitted:
    try:
        with st.spinner("Generating syllabus..."):
            start = time.time()

            result = generator.generate_syllabus({
                "title": title,
                "domain": domain,
                "level": level,
                "duration": duration,
                "description": description
            })

            elapsed = time.time() - start

        st.success(f"✅ Generated in {elapsed:.2f} seconds!")

        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Modules", result['metadata']['total_modules'])
        col2.metric("Activities", result['metadata']['total_activities'])
        col3.metric("Assessments", result['metadata']['total_assessments'])

        # Display tabs
        tab1, tab2 = st.tabs(["📄 Raw JSON", "📊 Formatted View"])

        with tab1:
            st.json(result)

        with tab2:
            # Course Info
            st.subheader("📚 Course Information")
            info = result['course_info']
            st.write(f"**Title:** {info['title']}")
            st.write(f"**Domain:** {info['domain'].replace('_', ' ').title()}")
            st.write(f"**Level:** {info['level'].title()}")
            st.write(f"**Duration:** {info['duration']}")

            # Learning Objectives
            if 'learning_objectives' in result:
                st.subheader("🎯 Learning Objectives")
                for i, obj in enumerate(result['learning_objectives'], 1):
                    st.write(f"{i}. {obj}")

            # Modules
            st.subheader("📖 Modules")
            for module in result['modules']:
                with st.expander(f"{module['title']} ({module['estimated_hours']} hours)"):
                    st.write(module['description'])
                    if 'key_concepts' in module:
                        st.write("**Key Concepts:**")
                        for concept in module['key_concepts'][:3]:  # Show first 3
                            st.write(f"- {concept}")

            # Activities
            st.subheader("✏️ Learning Activities")
            for activity in result['activities']:
                with st.expander(f"{activity['title']} - {activity['bloom_level'].title()}"):
                    st.write(activity['description'])
                    st.write(f"**Estimated time:** {activity['estimated_hours']} hours")

            # Assessments
            st.subheader("📝 Assessments")
            for assessment in result['assessments']:
                with st.expander(f"{assessment['title']} ({assessment['assessment_type'].title()})"):
                    st.write(assessment['description'])
                    st.write(f"**Duration:** {assessment['estimated_hours']} hours")

        # Download button
        json_str = json.dumps(result, indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"{title.replace(' ', '_').lower()}_syllabus.json",
            mime="application/json",
            use_container_width=True
        )

    except Exception as e:
        st.error(f"❌ Generation failed: {str(e)}")
        with st.expander("Debug Info"):
            st.code(str(e))

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    This tool demonstrates automated syllabus generation using:
    - **T5-small** fine-tuned on function calling
    - **RAG** with ChromaDB vector database
    - **3,346** educational components

    Part of MSc AI Capstone Project
    University of Essex Online
    """)

    st.header("🔬 System Stats")
    st.write("**RAG Components:** 3,346")
    st.write("**Domains:** CS, Math, Physics")
    st.write("**Levels:** Beginner to Advanced")
```

---

### Step 2: Test Locally

```bash
# Activate environment
cd /home/dewyn/dev/msc-ai-capstone-project
source .venv/bin/activate  # or: conda activate your-env

# Run Streamlit app
streamlit run streamlit_app.py
```

**Test Checklist**:
- [ ] App loads without errors
- [ ] Can generate CS syllabus (beginner)
- [ ] Can generate Math syllabus (intermediate)
- [ ] Can generate Physics syllabus (advanced)
- [ ] JSON displays correctly
- [ ] Formatted view displays correctly
- [ ] Download button works
- [ ] RAG retrieval working (check component IDs in JSON)

---

### Step 3: Commit to Git

```bash
git add streamlit_app.py
git commit -m "Add Streamlit web interface for syllabus generation"
git push origin dl/temp-progress-tracking
```

---

## Phase 2: Cloud Deployment Strategy

**Deployment Options** (to be determined in separate session):

### Option A: Hugging Face Spaces
- **Pros**: Built for ML apps, handles large models
- **Cons**: Need to learn platform, upload model separately
- **How**: Upload model to HF Hub, app loads from there

### Option B: Railway.app / Render.com
- **Pros**: Persistent storage, supports large files
- **Cons**: May require paid tier for 2.3GB
- **How**: Deploy with persistent volume for model

### Option C: Streamlit Cloud + Git LFS
- **Pros**: Simple deployment, familiar platform
- **Cons**: Git LFS has limits, may hit storage caps
- **How**: Use Git LFS for large files

**Decision**: Choose based on research and testing in deployment session

---

## Phase 3: Validation Materials (Monday)

### Google Form Questionnaire

**6 Sections, 10-12 Questions Total**:

**Section 1: Background** (2 questions)
- Your role in education (dropdown)
- Years of teaching experience (number)

**Section 2: Usability** (2 questions - 5-point Likert scale)
- The tool was easy to use
- Instructions were clear and intuitive

**Section 3: Educational Quality** (3 questions - 5-point scale)
- Generated content is pedagogically sound
- Learning objectives are appropriate for the level
- Content structure supports effective learning

**Section 4: Content Accuracy** (2 questions - 5-point scale)
- Content is relevant to the specified domain
- Difficulty level matches the selected course level

**Section 5: Practical Usefulness** (2 questions - 5-point scale)
- I would consider using this tool in my work
- This tool could save time compared to manual syllabus creation

**Section 6: Overall Feedback** (2 questions)
- Overall impression (1-5 scale)
- Suggestions for improvement (open text)

---

### User Guide Template

```markdown
# Educational AI Syllabus Generator - User Guide

## Testing Instructions (5-7 minutes)

**Step 1: Access the Tool**
Visit: [Deployment URL - to be provided]

**Step 2: Generate a Syllabus**
1. Enter course information:
   - **Course Title**: e.g., "Introduction to Data Science"
   - **Domain**: Select from dropdown (Computer Science, Mathematics, or Physics)
   - **Level**: Select difficulty (Beginner, Intermediate, or Advanced)
   - **Duration**: Select course length
   - **Description**: Brief course description (2-3 sentences)

2. Click "🚀 Generate Syllabus"

3. Review the generated output:
   - Check the "Formatted View" tab for readable display
   - Review modules, activities, and assessments
   - Note the pedagogical structure (learning objectives, Bloom's taxonomy)

4. (Optional) Try generating syllabi for different domains/levels

**Step 3: Complete Evaluation Survey**
Fill out the feedback survey: [Google Form URL]
Time: ~5 minutes

**Total Time Required**: 10-12 minutes

---

**Technical Note**: This system uses:
- Fine-tuned T5 language model for intelligent generation
- RAG (Retrieval-Augmented Generation) with 3,346 educational components
- Function calling architecture ensuring 100% valid JSON output

**Questions?** Contact: [Your email]

---

Thank you for contributing to this MSc AI research project!
```

---

### Recruitment Email Template

```
Subject: Quick expert feedback request: Educational AI tool (10 min)

Hi [Name],

I'm completing my MSc in Artificial Intelligence at University of Essex and
need expert feedback on an automated syllabus generation tool I've developed
as part of my capstone project.

**What I'm asking:**
- Test an AI-powered syllabus generator (5 minutes)
- Complete a brief evaluation survey (5 minutes)
- Total time: ~10 minutes

**Why your feedback matters:**
Your expertise as [educator/instructional designer] will help validate whether
AI can generate pedagogically sound educational content. Your feedback will be
cited in the evaluation chapter of my dissertation.

**Access:**
- Tool: [Deployment URL]
- Survey: [Google Form URL]
- User Guide: [Attached PDF]

**Deadline:** Friday, November 1st

The system uses a novel "function calling" architecture that achieves 100%
structural validity while integrating retrieval-augmented generation (RAG)
from a database of 3,346 educational components.

Your participation is completely voluntary and anonymous - no personal
identifiable information is collected.

Thank you for supporting my research!

Best regards,
[Your Name]
MSc Artificial Intelligence
University of Essex Online

---

Attachments:
- User_Guide.pdf
```

---

## Timeline Summary

**Today (Sunday Oct 26)**: Planning only - document created ✅

**Separate Session (TBD)**:
- Build Streamlit app (1-2 hours)
- Test locally (30 min)
- Commit to git (15 min)

**Monday Oct 28 Evening**:
- Create Google Form (1 hour)
- Create user guide PDF (30 min)
- Draft recruitment email (15 min)
- List 6-8 expert contacts (30 min)

**Deployment Session (TBD)**:
- Research deployment options (30 min)
- Choose platform (HF/Railway/Streamlit Cloud)
- Deploy with full RAG + T5 (1-2 hours)
- Test deployed version (30 min)

**Tuesday Oct 29**:
- Send recruitment emails to 6-8 experts

---

## Success Criteria

**Local App**:
- ✅ Generates valid syllabi for all 3 domains
- ✅ Shows RAG component retrieval (IDs visible)
- ✅ Formatted view displays clearly
- ✅ Download works
- ✅ Generation time < 10 seconds

**Cloud Deployment**:
- ✅ Public URL accessible
- ✅ Full RAG + T5 functionality (no compromises)
- ✅ ChromaDB working (87MB)
- ✅ T5 model loading (2.3GB - strategy TBD)
- ✅ Fast enough for interactive use

**Expert Validation**:
- ✅ 6-8 expert participants recruited
- ✅ Google Form responses collected
- ✅ Qualitative + quantitative feedback
- ✅ Write Section 6.11 with results

---

## Notes

- **RAG + T5 are MUST HAVE**: No compromises on functionality
- **2.3GB model deployment**: Will solve in separate session
- **Work schedule**: 3-4 hours evening after 5PM on weekdays
- **Target**: Full system deployed by end of next week (Nov 1)

---

**This document is the reference for implementation - not executing now.**
