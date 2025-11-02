"""Shared configuration for all visualizations."""

from pathlib import Path

# Colors (colorblind-friendly palette)
COLORS = {
    "success": "#2ecc71",  # Green
    "warning": "#f39c12",  # Orange
    "danger": "#e74c3c",  # Red
    "primary": "#3498db",  # Blue
    "secondary": "#95a5a6",  # Gray
    "purple": "#9b59b6",
    "teal": "#1abc9c",
}

# Style settings
STYLE = {
    "figure_size": (10, 6),
    "dpi": 300,  # Publication quality
    "font_family": "sans-serif",
    "font_size": 11,
    "title_size": 14,
    "label_size": 12,
}

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_PATH = BASE_DIR / "data" / "evaluation" / "evaluation_results.csv"
OUTPUT_DIR = BASE_DIR / "docs" / "figures"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
