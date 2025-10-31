# Evaluation Visualization Plan

**Purpose:** Create publication-quality visualizations for dissertation Chapter 6 (Evaluation & Results)

**Data Source:** `data/evaluation/evaluation_results.csv` (35 test cases, 27 successful)

---

## Priority 1: Core Findings (Essential for Dissertation)

### 1. Prerequisite Accuracy Distribution (Stacked Bar Chart)
**Key Finding:** 70.4% of syllabi have 0% prerequisite accuracy

```python
# Script: scripts/visualization/prerequisite_distribution.py
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/evaluation/evaluation_results.csv')
successful = df[df['pipeline_success'] == 1]

# Categorize
perfect = len(successful[successful['prerequisite_accuracy'] == 1.0])
partial = len(successful[(successful['prerequisite_accuracy'] > 0) &
                         (successful['prerequisite_accuracy'] < 1.0)])
none = len(successful[successful['prerequisite_accuracy'] == 0.0])

# Stacked bar showing: 25.9% perfect, 3.7% partial, 70.4% none
# Colors: Green, Yellow, Red
```

**Why Important:** Most striking negative finding - shows model weakness

---

### 2. Quality Profile Radar Chart
**Key Finding:** Uneven performance across pedagogical dimensions

```python
# Script: scripts/visualization/quality_radar.py
# Axes: Prerequisite (27.8%), Difficulty (90%), Diversity (80%), Bloom's (40.1%)
# Shows: Strong structural generation, weak semantic understanding
```

**Why Important:** Summarizes overall system strengths/weaknesses

---

### 3. Inverse Difficulty Curve (Box Plot)
**Key Finding:** Performance degrades as difficulty increases

```python
# Script: scripts/visualization/difficulty_analysis.py
# X-axis: Beginner (36.4%), Intermediate (27.8%), Advanced (16.7%), Postgraduate (0%)
# Y-axis: Prerequisite accuracy
# Shows: Counter-intuitive inverse relationship
```

**Why Important:** Proves prerequisite chains cause problems

---

### 4. RAG Pipeline Sankey Diagram
**Key Finding:** Dramatic filtering from 970 → 20 components

```python
# Script: scripts/visualization/rag_pipeline_flow.py
# Flow: 970 total → 205-402 filtered → 20 ranked → 3 selected
# Shows: Aggressive filtering effectiveness
```

**Why Important:** Demonstrates RAG component performance

---

### 5. Success Rate by Domain (Grouped Bar)
**Key Finding:** Clear domain coverage limitations

```python
# Script: scripts/visualization/domain_coverage.py
# CS: 13/13 success (100%)
# Math: 8/8 success (100%)
# Physics: 6/6 success (100%)
# Engineering: 0/4 success (0%)
# Interdisciplinary: 0/4 success (0%)
```

**Why Important:** Shows data-driven limitations

---

## Priority 2: Supporting Details

### 6. Generation Time vs Complexity (Scatter)
```python
# X: total_components (6-9)
# Y: generation_time_sec (7.9-23.4s)
# Color: domain
# Shows: Linear scaling, consistent performance
```

### 7. Component Template Effect (Grouped Bar)
```python
# By difficulty level
# Shows: Consistent 3 modules, 3 activities, 2-3 assessments
# Demonstrates lack of variation (template effect)
```

### 8. Module Hours Consistency (Line Chart)
```python
# X: Test case
# Y: avg_module_hours
# Shows: Tight clustering at 8.0 ± 0.39 hours
# Demonstrates rigid structure
```

---

## Priority 3: Advanced Analysis

### 9. Prerequisite Violation Heatmap
```python
# Rows: Test cases
# Columns: Module sequence positions (1-5)
# Color: Red (violation), Green (satisfied)
# Shows: WHERE in sequences violations occur
```

### 10. Quality Reranking Impact
```python
# Before/after comparison
# Shows: Candidate quality scores and selection
# Demonstrates reranking effectiveness
```

---

## Implementation Plan

### Step 1: Create Visualization Package
```bash
mkdir -p scripts/visualization
touch scripts/visualization/__init__.py
touch scripts/visualization/config.py  # Shared styling, colors, fonts
```

### Step 2: Shared Configuration
```python
# scripts/visualization/config.py
COLORS = {
    'success': '#2ecc71',   # Green
    'warning': '#f39c12',   # Yellow
    'danger': '#e74c3c',    # Red
    'primary': '#3498db',   # Blue
}

STYLE = {
    'figure_size': (10, 6),
    'dpi': 300,  # Publication quality
    'font_family': 'sans-serif',
    'font_size': 11,
}
```

### Step 3: Create Individual Scripts
Each visualization should:
1. Load data from CSV
2. Process/aggregate as needed
3. Generate plot with consistent styling
4. Save to `docs/figures/`
5. Print summary statistics

### Step 4: Master Script
```python
# scripts/visualization/generate_all.py
# Runs all visualizations in order
# Creates comprehensive figure set for dissertation
```

---

## Output Structure

```
docs/figures/
├── fig1_prerequisite_distribution.png
├── fig2_quality_radar.png
├── fig3_difficulty_curve.png
├── fig4_rag_pipeline_sankey.png
├── fig5_domain_success_rate.png
├── fig6_generation_time_scatter.png
├── fig7_component_template.png
├── fig8_module_hours_consistency.png
├── fig9_prerequisite_heatmap.png
└── fig10_reranking_impact.png
```

---

## Dependencies

```bash
pip install matplotlib seaborn plotly pandas numpy
```

For Sankey diagrams:
```bash
pip install plotly kaleido  # For static export
```

---

## Usage

```bash
# Generate all figures
python scripts/visualization/generate_all.py

# Generate specific figure
python scripts/visualization/prerequisite_distribution.py
```

---

## Notes

- Use **consistent color scheme** across all figures
- Export at **300 DPI** for print quality
- Include **error bars** where appropriate
- Add **statistical annotations** (mean, std, significance)
- Follow **academic publication standards**
- Save both **.png** (for dissertation) and **.svg** (for editing)

---

## Timeline

- **Priority 1 figures:** Essential for Chapter 6 (create first)
- **Priority 2 figures:** Supporting evidence (create second)
- **Priority 3 figures:** Optional depth (create if time permits)

**Estimated time:** 4-6 hours for Priority 1 figures

---

## References

- Matplotlib best practices: https://matplotlib.org/stable/tutorials/introductory/usage.html
- Academic figure design: Rougier et al. (2014) "Ten Simple Rules for Better Figures"
- Color accessibility: https://colorbrewer2.org/

---

**Status:** Planning phase
**Next Action:** Create `scripts/visualization/` package structure
**Owner:** Dewyn
**Last Updated:** 2025-10-31
