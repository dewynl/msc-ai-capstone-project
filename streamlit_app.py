#!/usr/bin/env python3
"""
EduCraft - AI-Powered Course Syllabus Generator
MSc AI Capstone Project - Streamlit Web Interface
"""

import json
import sys
import time
from pathlib import Path

import streamlit as st

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.rag_integrated_generator import RAGIntegratedGenerator
from src.utils.supabase_client import get_supabase_manager

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="EduCraft - AI Syllabus Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================================
# STYLING
# ============================================================================
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# ============================================================================
# CACHED RESOURCES
# ============================================================================
@st.cache_resource(
    show_spinner="🔧 Building RAG vector database from 3,346 components... This may take 2-3 minutes on first load."
)
def load_generator():
    """Load RAG-integrated generator (cached to avoid reloading).

    On first load after deployment, this builds the ChromaDB vector store
    from component JSON files. Subsequent loads use the cached version.
    """
    return RAGIntegratedGenerator()


@st.cache_resource
def get_db_manager():
    """Get Supabase manager (cached singleton)."""
    return get_supabase_manager()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def render_email_gate():
    """Render the email entry gate for user identification."""
    st.markdown('<p class="main-header">📚 EduCraft</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">AI-Powered Course Syllabus Generation</p>',
        unsafe_allow_html=True,
    )

    st.info(
        "**Welcome!** Please enter a username to continue. "
        "This helps us track your generated syllabi and enables you to "
        "review your previous work."
    )

    with st.form("user_entry"):
        username = st.text_input(
            "Username *",
            placeholder="your_username",
            help="Your username is used only to link your generated syllabi",
        )

        st.markdown("---")
        submitted = st.form_submit_button(
            "Continue to Generator →", use_container_width=True
        )

        if submitted:
            if not username or not username.strip():
                st.error("⚠️ Please enter a username")
                return

            # Get or create user
            db = get_db_manager()
            user = db.get_or_create_user(username.strip())
            st.session_state.user = user
            st.rerun()

    # Privacy note
    st.caption(
        "ℹ️ **Privacy:** Your username is stored securely and used only for tracking "
        "your syllabi. No password required. Data will be deleted after the "
        "validation period concludes."
    )


def render_user_welcome(user):
    """Render welcome message and previous syllabi."""
    name = user.get("first_name") or user["username"]

    # Get user's previous syllabi
    db = get_db_manager()
    previous = db.get_user_syllabi(user["id"], limit=10)

    # Welcome message (using Streamlit native component for dark mode support)
    st.info(
        f"👋 **Welcome back, {name}!**  \n"
        f"You've generated **{len(previous)}** syllabus(es) so far"
    )

    # Show previous syllabi if any
    if previous:
        with st.expander(f"📚 Your Previous Syllabi ({len(previous)})"):
            for i, syl in enumerate(previous, 1):
                domain_display = syl["domain"].replace("_", " ").title()
                level_display = syl["level"].title()

                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(
                        f"{i}. **{syl['title']}** "
                        f"({domain_display}, {level_display}) - "
                        f"{syl['generated_at'][:10]} - "
                        f"{syl.get('generation_time_seconds', 0):.2f}s"
                    )
                with col2:
                    if st.button("👁️ View", key=f"view_{syl['id']}"):
                        # Load this syllabus from database
                        db = get_db_manager()
                        full_syllabus = db.get_syllabus_by_id(syl["id"])
                        if full_syllabus:
                            st.session_state.current_syllabus = full_syllabus[
                                "syllabus_json"
                            ]
                            st.session_state.current_generation_time = (
                                full_syllabus.get("generation_time_seconds", 0)
                            )
                            st.session_state.current_requirements = {
                                "title": full_syllabus["title"],
                                "domain": full_syllabus["domain"],
                                "level": full_syllabus["level"],
                                "description": full_syllabus["description"],
                            }
                            st.session_state.syllabus_saved = True  # Already saved
                            st.rerun()


def render_example_presets():
    """Render example preset buttons."""
    st.markdown("#### 🚀 Quick Start Examples")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🖥️ Computer Science", use_container_width=True):
            st.session_state.preset = {
                "title": "Introduction to Programming",
                "domain": "computer_science",
                "level": "beginner",
                "description": "Fundamental programming concepts using Python, including variables, control structures, functions, and basic data structures.",
            }
            st.rerun()

    with col2:
        if st.button("📐 Mathematics", use_container_width=True):
            st.session_state.preset = {
                "title": "Calculus II",
                "domain": "mathematics",
                "level": "intermediate",
                "description": "Advanced integration techniques, sequences and series, and introduction to multivariable calculus.",
            }
            st.rerun()

    with col3:
        if st.button("⚛️ Physics", use_container_width=True):
            st.session_state.preset = {
                "title": "Quantum Mechanics",
                "domain": "physics",
                "level": "advanced",
                "description": "Introduction to quantum theory, wave-particle duality, Schrödinger equation, and quantum systems.",
            }
            st.rerun()


def render_formatted_syllabus(syllabus):
    """Render formatted syllabus view with RAG component highlighting."""
    # Get database references to identify RAG components
    db_refs = syllabus.get("database_references", {})
    module_ids = db_refs.get("module_ids", [])
    activity_ids = db_refs.get("activity_ids", [])
    assessment_ids = db_refs.get("assessment_ids", [])

    # Course information
    st.markdown("### 📖 Course Information")
    course_info = syllabus.get("course_info", {})

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Title:** {course_info.get('title', 'N/A')}")
        st.write(
            f"**Domain:** {course_info.get('domain', 'N/A').replace('_', ' ').title()}"
        )
    with col2:
        st.write(f"**Level:** {course_info.get('level', 'N/A').title()}")
        st.write(f"**Duration:** {course_info.get('duration', 'N/A').title()}")

    st.write(f"**Description:** {course_info.get('description', 'N/A')}")

    # Learning objectives
    st.markdown("### 🎯 Learning Objectives")
    objectives = syllabus.get("learning_objectives", [])
    if objectives:
        for i, obj in enumerate(objectives, 1):
            st.write(f"{i}. {obj}")
    else:
        st.write("_No objectives specified_")

    # Modules
    st.markdown("### 📚 Modules")
    modules = syllabus.get("modules", [])
    if modules:
        for i, module in enumerate(modules, 1):
            # Check if this module is from RAG
            is_rag = i <= len(module_ids)
            badge = "🗄️ RAG" if is_rag else "🤖 T5"
            badge_color = "blue" if is_rag else "green"

            with st.expander(
                f"**Module {i}: {module.get('title', 'Untitled')}** "
                f"({module.get('estimated_hours', 0)} hours) - {badge}"
            ):
                if is_rag:
                    st.info(f"📌 Retrieved from RAG Database: `{module_ids[i-1]}`")
                else:
                    st.success("✨ Generated by T5 Model")

                st.write(f"**Description:** {module.get('description', 'N/A')}")
                if module.get("learning_objectives"):
                    st.write("**Objectives:**")
                    for obj in module["learning_objectives"]:
                        st.write(f"- {obj}")
    else:
        st.write("_No modules generated_")

    # Activities
    st.markdown("### 🎨 Learning Activities")
    activities = syllabus.get("activities", [])
    if activities:
        for i, activity in enumerate(activities, 1):
            st.write(
                f"{i}. **{activity.get('title', 'Untitled')}** "
                f"(Bloom's: {activity.get('bloom_level', 'N/A').title()}, "
                f"{activity.get('estimated_hours', 0)} hours)"
            )
            st.write(f"   _{activity.get('description', 'N/A')}_")
    else:
        st.write("_No activities generated_")

    # Assessments
    st.markdown("### 📝 Assessments")
    assessments = syllabus.get("assessments", [])
    if assessments:
        for i, assessment in enumerate(assessments, 1):
            st.write(
                f"{i}. **{assessment.get('title', 'Untitled')}** "
                f"(Type: {assessment.get('assessment_type', 'N/A').title()}, "
                f"Duration: {assessment.get('estimated_hours', 0)} hours)"
            )
            st.write(f"   _{assessment.get('description', 'N/A')}_")
    else:
        st.write("_No assessments generated_")


def render_technical_details(syllabus, generation_time):
    """Render technical details tab for supervisor demo."""
    st.markdown("### ⚙️ Phase 3 Architecture Pipeline")

    # Visual pipeline
    st.markdown(
        """
        ```
        📝 User Input
           ↓
        🤖 T5-Small Model (60M params)
           ↓
        📋 Function Call Generation
           │  Example: add_module(title="Intro to Python", estimated_hours=8)
           ↓
        🔍 Format-Agnostic Parser
           │  Extracts: {function: "add_module", args: {...}}
           ↓
        🔨 SyllabusBuilder Execution
           │  Programmatic construction
           ↓
        🗄️ RAG Integration (ChromaDB)
           │  Retrieves components from vector database
           ↓
        ✅ Valid JSON Output (100% validity)
        ```
        """
    )

    st.success(
        "**Key Innovation**: Function calling decouples semantic understanding (T5) from "
        "structural validity (SyllabusBuilder), achieving 100% JSON validity with flexible "
        "model contribution (varies per syllabus based on RAG availability)."
    )

    st.markdown("### 📊 This Syllabus - Generation Metrics")

    # Calculate component breakdown
    metadata = syllabus.get("metadata", {})
    rag_count = metadata.get("rag_retrieved_components", 0)
    gen_count = metadata.get("generated_components", 0)
    total = rag_count + gen_count

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Generation Time", f"{generation_time:.2f}s")

    with col2:
        st.metric("Total Components", total)

    with col3:
        rag_percent = (rag_count / total * 100) if total > 0 else 0
        st.metric("RAG Retrieved", f"{rag_count}", delta=f"{rag_percent:.0f}%")

    with col4:
        gen_percent = (gen_count / total * 100) if total > 0 else 0
        st.metric("T5 Generated", f"{gen_count}", delta=f"{gen_percent:.0f}%")

    # Visual breakdown
    if total > 0:
        st.progress(
            gen_count / total,
            text=f"T5 Contribution: {gen_percent:.1f}% ({gen_count}/{total} components)",
        )

    st.markdown("---")

    # Component IDs
    st.markdown("### 🔗 Database Component References")
    db_refs = syllabus.get("database_references", {})

    with st.expander("Module IDs"):
        module_ids = db_refs.get("module_ids", [])
        if module_ids:
            for mid in module_ids:
                st.code(mid, language=None)
        else:
            st.write("_No module IDs (components were generated)_")

    with st.expander("Activity IDs"):
        activity_ids = db_refs.get("activity_ids", [])
        if activity_ids:
            for aid in activity_ids:
                st.code(aid, language=None)
        else:
            st.write("_No activity IDs (components were generated)_")


# ============================================================================
# MAIN APP
# ============================================================================
def main():
    """Main application logic."""

    # Check if user is logged in
    if "user" not in st.session_state:
        render_email_gate()
        return

    # User is logged in - show main interface
    user = st.session_state.user

    # Header
    st.markdown('<p class="main-header">📚 EduCraft</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">AI-Powered Course Syllabus Generation</p>',
        unsafe_allow_html=True,
    )

    # Welcome message
    render_user_welcome(user)

    # Research Contribution Showcase
    st.markdown("### 🎓 MSc Research Contribution")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "JSON Validity Rate",
            "100%",
            delta="Phase 1: 0% → Phase 3: 100%",
            delta_color="normal",
        )
        st.caption("Function calling eliminates malformed JSON")

    with col2:
        st.metric(
            "Architecture", "Phase 3", delta="Function Calling", delta_color="off"
        )
        st.caption("T5 → Function Calls → Programmatic Builder")

    with col3:
        st.metric(
            "RAG Integration", "ChromaDB", delta="3,346 components", delta_color="off"
        )
        st.caption("Vector database for component retrieval")

    st.info(
        "💡 **Innovation**: Function calling decouples semantic understanding (T5) from "
        "structural validity (SyllabusBuilder), achieving 100% JSON validity with flexible "
        "RAG/generation ratios per syllabus."
    )

    st.markdown("---")

    # Example presets
    render_example_presets()

    st.markdown("---")

    # Information callout about RAG database build
    st.info(
        "ℹ️ **First Load Notice**: On initial deployment or after app restarts, the RAG vector "
        "database is built from 3,346 components (~2-3 minutes). Subsequent uses are instant via caching. "
        "During build, RAG-retrieved components will be available."
    )

    # Main generation interface
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 Course Requirements")

        # Apply preset if available
        preset = st.session_state.get("preset", {})

        # Input form
        with st.form("syllabus_form"):
            title = st.text_input(
                "Course Title *",
                value=preset.get("title", ""),
                placeholder="e.g., Machine Learning Fundamentals",
            )

            domain = st.selectbox(
                "Domain *",
                options=["computer_science", "mathematics", "physics"],
                index=["computer_science", "mathematics", "physics"].index(
                    preset.get("domain", "computer_science")
                ),
                format_func=lambda x: x.replace("_", " ").title(),
            )

            level = st.selectbox(
                "Difficulty Level *",
                options=["beginner", "intermediate", "advanced"],
                index=["beginner", "intermediate", "advanced"].index(
                    preset.get("level", "intermediate")
                ),
                format_func=lambda x: x.title(),
            )

            description = st.text_area(
                "Course Description *",
                value=preset.get("description", ""),
                height=120,
                placeholder="Describe the course content, objectives, and target audience...",
            )

            submitted = st.form_submit_button(
                "🚀 Generate Syllabus", use_container_width=True
            )

    with col2:
        st.subheader("📄 Generated Syllabus")

        if submitted:
            if not title.strip() or not description.strip():
                st.error("⚠️ Please provide both title and description")
            else:
                # Generate syllabus
                with st.spinner(
                    "🔄 Generating syllabus... (T5 → Function Calls → Execution)"
                ):
                    try:
                        # Load generator
                        generator = load_generator()

                        # Build requirements
                        requirements = {
                            "title": title,
                            "domain": domain,
                            "level": level,
                            "description": description,
                        }

                        # Generate with timing
                        start_time = time.time()
                        syllabus = generator.generate_syllabus_with_ids(requirements)
                        generation_time = time.time() - start_time

                        # Store in session for display (not saved yet)
                        st.session_state.current_syllabus = syllabus
                        st.session_state.current_generation_time = generation_time
                        st.session_state.current_requirements = {
                            "title": title,
                            "domain": domain,
                            "level": level,
                            "description": description,
                        }
                        st.session_state.syllabus_saved = False

                        # Clear preset after successful generation
                        if "preset" in st.session_state:
                            st.session_state.preset = {}

                        st.success(
                            f"✅ Generated successfully in {generation_time:.2f}s!"
                        )

                    except Exception as e:
                        st.error(f"❌ Generation Error: {str(e)}")
                        st.exception(e)

        # Display current syllabus if available
        if (
            "current_syllabus" in st.session_state
            and "current_requirements" in st.session_state
        ):
            syllabus = st.session_state.current_syllabus
            gen_time = st.session_state.current_generation_time
            requirements = st.session_state.current_requirements
            is_saved = st.session_state.get("syllabus_saved", False)

            # Metrics
            metrics_cols = st.columns(4)
            with metrics_cols[0]:
                st.metric("Modules", len(syllabus.get("modules", [])))
            with metrics_cols[1]:
                st.metric("Activities", len(syllabus.get("activities", [])))
            with metrics_cols[2]:
                st.metric("Assessments", len(syllabus.get("assessments", [])))
            with metrics_cols[3]:
                st.metric("Time", f"{gen_time:.2f}s")

            # Save button
            if not is_saved:
                if st.button(
                    "💾 Save This Syllabus to Database",
                    use_container_width=True,
                    type="primary",
                ):
                    db = get_db_manager()
                    db.save_syllabus(
                        user_id=user["id"],
                        title=requirements["title"],
                        domain=requirements["domain"],
                        level=requirements["level"],
                        description=requirements["description"],
                        syllabus_json=syllabus,
                        generation_time_seconds=gen_time,
                    )
                    st.session_state.syllabus_saved = True
                    st.success("✅ Syllabus saved successfully!")
                    st.rerun()
            else:
                st.success("✅ This syllabus has been saved to your database")

            st.markdown("---")

            # Tabs
            tab1, tab2, tab3 = st.tabs(
                ["📋 Formatted View", "🔧 Raw JSON", "⚙️ Technical Details"]
            )

            with tab1:
                render_formatted_syllabus(syllabus)

            with tab2:
                st.json(syllabus)

            with tab3:
                render_technical_details(syllabus, gen_time)

            # Download button
            safe_title = requirements["title"].replace(" ", "_").lower()[:30]
            filename = f"syllabus_{safe_title}.json"
            st.download_button(
                label="📥 Download JSON",
                data=json.dumps(syllabus, indent=2),
                file_name=filename,
                mime="application/json",
                use_container_width=True,
            )

    # Footer
    st.markdown("---")
    st.caption(
        "📚 **EduCraft** - MSc AI Capstone Project | "
        "University of Essex Online | "
        "Function Calling Architecture for Educational Content Generation"
    )


if __name__ == "__main__":
    main()
