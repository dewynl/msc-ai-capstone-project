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
@st.cache_resource(show_spinner=False)
def load_generator():
    """Load CodeT5 model for syllabus generation (cached)."""
    sys.path.insert(0, str(Path(__file__).parent / "scripts"))
    from model_inference import SyllabusGenerator

    return SyllabusGenerator()


@st.cache_resource(show_spinner=False)
def load_ranker():
    """Load semantic ranker for component ranking (cached)."""
    sys.path.insert(0, str(Path(__file__).parent / "scripts"))
    from semantic_ranker import SemanticRanker

    return SemanticRanker()


@st.cache_resource
def get_db_manager():
    """Get Supabase manager (cached)."""
    return get_supabase_manager()


@st.cache_data(ttl=60)
def load_rag_database():
    """Load educational components from JSON files (cached)."""
    import json
    from pathlib import Path

    base_dir = Path(__file__).parent
    components_dir = base_dir / "data" / "components"

    modules_file = components_dir / "modules.json"
    with open(modules_file) as f:
        modules = json.load(f)

    for module in modules:
        if "module_id" in module:
            module["id"] = module.pop("module_id")

    activities_file = components_dir / "activities.json"
    with open(activities_file) as f:
        activities = json.load(f)

    for activity in activities:
        if "activity_id" in activity:
            activity["id"] = activity.pop("activity_id")

    assessments_file = components_dir / "assessments.json"
    with open(assessments_file) as f:
        assessments = json.load(f)

    for assessment in assessments:
        if "assessment_id" in assessment:
            assessment["id"] = assessment.pop("assessment_id")

    return {"modules": modules, "activities": activities, "assessments": assessments}


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


def render_evaluation_results_sidebar():
    """Render evaluation results from dissertation in sidebar."""
    with st.sidebar:
        st.markdown("### 📊 System Evaluation Results")
        st.caption("*From MSc Dissertation Study (35 test cases)*")

        st.metric(
            "Pipeline Success Rate",
            "77.1%",
            help="27/35 test cases completed successfully",
        )
        st.metric(
            "Prerequisite Accuracy",
            "27.8%",
            delta="-72.2%",
            delta_color="inverse",
            help="Percentage of prerequisite dependencies correctly ordered",
        )
        st.metric(
            "Difficulty Progression",
            "90.0%",
            help="Module difficulty increases appropriately",
        )
        st.metric(
            "Topic Diversity", "80.0%", help="Coverage of diverse educational topics"
        )

        st.markdown("---")
        st.caption("**Domain Coverage:**")
        st.caption("✅ Computer Science: 100%")
        st.caption("✅ Mathematics: 100%")
        st.caption("✅ Physics: 100%")
        st.caption("⚠️ Engineering: 0%")
        st.caption("⚠️ Interdisciplinary: 0%")

        st.markdown("---")
        st.caption(
            "**Key Insight:** System excels at structural generation but struggles with semantic prerequisite chains. See dissertation Chapter 6 for full analysis."
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
        if st.button("🖥️ Introduction to Programming", use_container_width=True):
            st.session_state.preset = {
                "title": "Introduction to Python Programming",
                "domain": "computer_science",
                "level": "beginner",
                "description": "Foundational programming concepts using Python, including variables, data types, control flow (conditionals and loops), functions, lists, dictionaries, string manipulation, file I/O, and error handling.",
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


def render_formatted_syllabus(syllabus, rag_database=None):
    """Render formatted syllabus view with RAG component highlighting.

    Args:
        syllabus: Syllabus JSON (modules/activities/assessments are UUIDs)
        rag_database: RAG database with full component objects (optional)
    """
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

    # Modules (UUIDs - need to expand if database available)
    st.markdown("### 📚 Modules")
    module_uuids = syllabus.get("modules", [])

    if module_uuids:
        # Build lookup if database available
        uuid_to_module = {}
        if rag_database:
            uuid_to_module = {m["id"]: m for m in rag_database.get("modules", [])}

        for i, module_uuid in enumerate(module_uuids, 1):
            # Try to get full module object
            module = uuid_to_module.get(module_uuid)

            if module:
                # Full module data available
                with st.expander(
                    f"**Module {i}: {module.get('title', 'Untitled')}** "
                    f"({module.get('estimated_hours', 0)} hours) - 🗄️ RAG"
                ):
                    st.info(f"📌 Retrieved from RAG Database: `{module_uuid}`")
                    st.write(f"**Description:** {module.get('description', 'N/A')}")
                    st.write(f"**Difficulty:** {module.get('difficulty', 'N/A')}")

                    key_concepts = module.get("key_concepts", [])
                    if key_concepts:
                        st.write(f"**Key Concepts:** {', '.join(key_concepts)}")
            else:
                # Only UUID available (no database)
                st.write(f"{i}. Module `{module_uuid}` (details not available)")
    else:
        st.write("_No modules selected_")

    # Activities (UUIDs)
    st.markdown("### 🎨 Learning Activities")
    activity_uuids = syllabus.get("activities", [])

    if activity_uuids:
        uuid_to_activity = {}
        if rag_database:
            uuid_to_activity = {a["id"]: a for a in rag_database.get("activities", [])}

        for i, activity_uuid in enumerate(activity_uuids, 1):
            activity = uuid_to_activity.get(activity_uuid)

            if activity:
                st.write(
                    f"{i}. **{activity.get('title', 'Untitled')}** "
                    f"(Bloom's: {activity.get('bloom_level', 'N/A').title()}, "
                    f"{activity.get('estimated_hours', 0)} hours)"
                )
                st.write(f"   _{activity.get('description', 'N/A')}_")
            else:
                st.write(f"{i}. Activity `{activity_uuid}` (details not available)")
    else:
        st.write("_No activities selected_")

    # Assessments (UUIDs)
    st.markdown("### 📝 Assessments")
    assessment_uuids = syllabus.get("assessments", [])

    if assessment_uuids:
        uuid_to_assessment = {}
        if rag_database:
            uuid_to_assessment = {
                a["id"]: a for a in rag_database.get("assessments", [])
            }

        for i, assessment_uuid in enumerate(assessment_uuids, 1):
            assessment = uuid_to_assessment.get(assessment_uuid)

            if assessment:
                st.write(
                    f"{i}. **{assessment.get('title', 'Untitled')}** "
                    f"(Type: {assessment.get('assessment_type', 'N/A').title()}, "
                    f"Duration: {assessment.get('estimated_hours', 0)} hours)"
                )
                st.write(f"   _{assessment.get('description', 'N/A')}_")
            else:
                st.write(f"{i}. Assessment `{assessment_uuid}` (details not available)")
    else:
        st.write("_No assessments selected_")


def render_technical_details(syllabus, generation_time):
    """Render technical details tab for supervisor demo."""
    st.markdown("### ⚙️ CodeT5 Hybrid ML + Rule-Based Architecture")

    # Visual pipeline
    st.markdown(
        """
        ```
        📝 User Input (Course Requirements: domain, level, description)
           ↓
        🔍 Domain + Difficulty RAG Filter (Rule-based)
           │  Step 1: Filter by domain (computer_science → CS modules only)
           │  Step 2: Filter by difficulty
           │    • Beginner → only beginner modules
           │    • Intermediate → beginner + intermediate
           │    • Advanced → intermediate + advanced
           │  Result: 960 modules → ~100-200 domain+difficulty matches
           ↓
        🤖 CodeT5-Small Model (60M params, ML-based)
           │  Sees filtered modules as context
           │  Generates markdown syllabus with indices
           │  Example: ## Selected Modules\n[0], [1], [2]
           ↓
        📋 Markdown Parser (Hybrid)
           │  Converts indices → database UUIDs
           │  [0] → uuid-mod-abc123 (from filtered context)
           ↓
        🎯 Bloom's Taxonomy Enhancement (Rule-based)
           │  Replaces generic objectives with pedagogical patterns
           │  "Master X fundamentals" → "Understand fundamental X principles"
           ↓
        📚 Template Expander (Hybrid)
           │  Adds rich database details to selections
           ↓
        ✅ Final Output (JSON + Rich Markdown)
        ```
        """
    )

    st.success(
        "**Hybrid Architecture**: Combines ML (CodeT5 generation) with Rules (difficulty filtering, "
        "Bloom's Taxonomy) for 100% structural validity + 100% pedagogically appropriate selections. "
        "Following established patterns in spaCy, modern NER, and information retrieval systems."
    )

    st.markdown("### 📊 RAG Retrieval Process")

    # Explain what happened
    st.markdown(
        """
    **How RAG worked for this syllabus:**

    1. **Domain + Difficulty Filtering (Rule-based)**: ALL components filtered by BOTH domain AND difficulty
       - Domain: Only components matching course domain (e.g., computer_science → CS only)
       - Difficulty: Only appropriate difficulty levels
         * Beginner courses → beginner components only
         * Intermediate courses → beginner + intermediate
         * Advanced courses → intermediate + advanced
       - Applied to: Modules, Activities, AND Assessments
    2. **Context Building**: Built prompt with filtered components as `[0] Component Title (hours, difficulty)`
    3. **Model Selection (ML-based)**: CodeT5 read the context and output indices like `[0], [1], [2], [3]`
    4. **Index Mapping (Hybrid)**: Converted indices to database UUIDs (e.g., `[0]` → `uuid-abc123`)
    5. **Bloom's Enhancement (Rule-based)**: Replaced generic objectives with pedagogical patterns
    6. **Database Expansion (Hybrid)**: Retrieved full details for selected UUIDs

    This is a **Retrieval-Augmented Generation** approach where:
    - RAG provides the **context** (pedagogically filtered components)
    - Model does **selection** (which components to use)
    - System does **expansion** (full details from database)

    **Why Filter Everything?** Ensures 100% pedagogical appropriateness - no advanced assessments in beginner courses, no irrelevant domains
    """
    )

    st.markdown("### 📊 This Syllabus - Metrics")

    # Get selected components (UUIDs)
    modules = syllabus.get("modules", [])
    activities = syllabus.get("activities", [])
    assessments = syllabus.get("assessments", [])
    objectives = syllabus.get("learning_objectives", [])

    total = len(modules) + len(activities) + len(assessments)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Generation Time", f"{generation_time:.2f}s")

    with col2:
        st.metric("Total Components", total)

    with col3:
        st.metric("Modules", len(modules))

    with col4:
        st.metric("Objectives", len(objectives))

    st.markdown("---")

    # Component IDs
    st.markdown("### 🔗 Selected Component UUIDs")

    with st.expander("Module UUIDs"):
        if modules:
            for mid in modules:
                st.code(mid, language=None)
        else:
            st.write("_No modules selected_")

    with st.expander("Activity UUIDs"):
        if activities:
            for aid in activities:
                st.code(aid, language=None)
        else:
            st.write("_No activities selected_")

    with st.expander("Assessment UUIDs"):
        if assessments:
            for aid in assessments:
                st.code(aid, language=None)
        else:
            st.write("_No assessments selected_")


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

    # Load generator FIRST (before any UI) to ensure CodeT5 model is ready
    # Show blocking full-page spinner on first load, instant on subsequent loads (cached)
    with st.spinner(
        "🤖 Loading AI System...\n\n"
        "Loading CodeT5 model (60M parameters) + Initializing hybrid pipeline\n\n"
        "This is a one-time load on first deployment and takes ~1 minute.\n\n"
        "Subsequent loads are instant via caching. Please wait..."
    ):
        generator = load_generator()

    # Header
    st.markdown('<p class="main-header">📚 EduCraft</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">AI-Powered Course Syllabus Generation</p>',
        unsafe_allow_html=True,
    )

    # Welcome message
    render_user_welcome(user)

    # Evaluation results sidebar
    render_evaluation_results_sidebar()

    # Example presets
    render_example_presets()

    st.markdown("---")

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
                    "🔄 Generating syllabus using Semantic Ranking + CodeT5 hybrid system...\n\n"
                    "Step 1: Filtering by domain + difficulty...\n"
                    "Step 2: Ranking by semantic similarity...\n"
                    "Step 3: Generating with CodeT5...\n"
                    "Step 4: Parsing and enhancing..."
                ):
                    try:
                        # Import generation pipeline
                        sys.path.insert(0, str(Path(__file__).parent / "scripts"))
                        from generate_syllabus import generate_complete_syllabus

                        # Build requirements
                        requirements = {
                            "title": title,
                            "domain": domain,
                            "level": level,
                            "description": description,
                            "duration": "semester",  # Default duration
                        }

                        # Load RAG database from local files
                        rag_database = load_rag_database()

                        # Show what's being filtered
                        total_mods = len(rag_database["modules"])
                        total_acts = len(rag_database["activities"])
                        total_asms = len(rag_database["assessments"])

                        # Count domain matches
                        domain_mods = len(
                            [
                                m
                                for m in rag_database["modules"]
                                if m.get("domain") == domain
                            ]
                        )
                        domain_acts = len(
                            [
                                a
                                for a in rag_database["activities"]
                                if a.get("domain") == domain
                            ]
                        )
                        domain_asms = len(
                            [
                                a
                                for a in rag_database["assessments"]
                                if a.get("domain") == domain
                            ]
                        )

                        # Count domain + difficulty matches
                        level_domain_mods = len(
                            [
                                m
                                for m in rag_database["modules"]
                                if m.get("domain") == domain
                                and m.get("difficulty") == level
                            ]
                        )
                        level_domain_acts = len(
                            [
                                a
                                for a in rag_database["activities"]
                                if a.get("domain") == domain
                                and a.get("difficulty") == level
                            ]
                        )
                        level_domain_asms = len(
                            [
                                a
                                for a in rag_database["assessments"]
                                if a.get("domain") == domain
                                and a.get("difficulty") == level
                            ]
                        )

                        st.info(
                            f"📊 **Database Total:** {total_mods} modules, {total_acts} activities, {total_asms} assessments\n\n"
                            f"🔍 **Filtering by '{domain.replace('_', ' ').title()}' + '{level.title()}':**\n"
                            f"  - Modules: {level_domain_mods}\n"
                            f"  - Activities: {level_domain_acts}\n"
                            f"  - Assessments: {level_domain_asms}"
                        )

                        # Load models (cached)
                        generator = load_generator()
                        ranker = load_ranker()

                        # Generate with timing (using CodeT5 + Semantic Ranking pipeline)
                        start_time = time.time()
                        result = generate_complete_syllabus(
                            requirements, rag_database, generator, ranker
                        )
                        generation_time = time.time() - start_time

                        # Pipeline overview (simplified)
                        with st.expander("🔍 Pipeline Details"):
                            metadata = result.get("metadata", {})
                            filter_stats = metadata.get("filter_stats", {})
                            ranking_stats = metadata.get("ranking_stats", {})

                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric(
                                    "Filtered Modules",
                                    f"{filter_stats.get('filtered_components', 0)}",
                                )
                            with col_b:
                                mod_stats = ranking_stats.get("modules", {})
                                st.metric(
                                    "Top Ranked", f"{mod_stats.get('output_count', 0)}"
                                )
                            with col_c:
                                st.metric(
                                    "Selected",
                                    f"{metadata.get('selected_modules_count', 0)}",
                                )

                            if mod_stats.get("pedagogical_boost", False):
                                st.info(
                                    f"✅ {mod_stats.get('boost_count', 0)} intro modules boosted for beginner course"
                                )

                            warnings = result.get("warnings", [])
                            if warnings:
                                st.warning(
                                    f"⚠️ {len(warnings)} warning(s) - see Technical Details tab"
                                )

                        # Check if generation succeeded
                        if not result.get("success", False):
                            st.error(
                                f"❌ Generation failed: {result.get('error', 'Unknown error')}"
                            )
                            if "markdown_simple" in result:
                                with st.expander("🔍 Full Model Output"):
                                    st.code(
                                        result["markdown_simple"], language="markdown"
                                    )
                            return

                        # Extract syllabus from result
                        syllabus = result["json"]

                        st.success(
                            f"✅ Generated syllabus with {len(syllabus.get('modules', []))} modules, "
                            f"{len(syllabus.get('activities', []))} activities, "
                            f"{len(syllabus.get('learning_objectives', []))} objectives"
                        )

                        # Display pedagogical quality metrics
                        if "quality_metrics" in result:
                            st.subheader("📊 Pedagogical Quality Assessment")

                            metrics = result["quality_metrics"]

                            # Three-column metric display
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                prereq_acc = metrics.get("prerequisite_accuracy", 0)
                                st.metric(
                                    "Prerequisite Coherence",
                                    f"{prereq_acc:.0%}",
                                    delta=None,
                                    help="Percentage of modules correctly placed after their prerequisites",
                                )

                            with col2:
                                diff_score = 1 - metrics.get("difficulty_loss", 0)
                                st.metric(
                                    "Difficulty Progression",
                                    f"{diff_score*100:.0f}%",
                                    delta=None,
                                    help="Smoothness of difficulty curve (beginner → intermediate → advanced)",
                                )

                            with col3:
                                cov_score = 1 - metrics.get("coverage_loss", 0)
                                st.metric(
                                    "Topic Diversity",
                                    f"{cov_score*100:.0f}%",
                                    delta=None,
                                    help="Variety of topics covered vs repetitiveness",
                                )

                            # Quality warning banner
                            if not result.get("quality_acceptable", True):
                                st.warning(
                                    "⚠️ **Quality Notice**\n\n"
                                    "This syllabus was generated with quality below our threshold. "
                                    "Some modules may appear before their prerequisites, or the difficulty "
                                    "progression may not be optimal. Consider regenerating or manually reviewing."
                                )
                            else:
                                st.success(
                                    "✅ This syllabus meets our quality standards!"
                                )

                            # Expandable details
                            with st.expander("📋 Quality Details"):
                                st.write(
                                    "**Prerequisite Violations:**",
                                    metrics.get("prerequisite_violations", 0),
                                )
                                st.write(
                                    "**Prerequisite Correct:**",
                                    metrics.get("prerequisite_correct", 0),
                                )
                                st.write(
                                    "**Note:** Syllabus selected from 3 generated candidates based on quality score."
                                )

                        # Store in session for display (not saved yet)
                        st.session_state.current_syllabus = syllabus
                        st.session_state.current_generation_time = generation_time
                        st.session_state.current_rag_database = rag_database
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
            rag_db = st.session_state.get("current_rag_database", None)
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
                render_formatted_syllabus(syllabus, rag_db)

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
