#!/usr/bin/env python3
"""
Dissertation Word Count Analysis Tool

Analyzes dissertation progress against 13,000-word target with section-by-section breakdown.
Run after every edit to dissertation content files.
"""

import re
from datetime import datetime
from pathlib import Path


def clean_markdown_for_count(text: str) -> str:
    """Remove markdown syntax and code blocks for accurate word count."""
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Remove inline code
    text = re.sub(r"`[^`]+`", "", text)
    # Remove markdown links but keep text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Remove images
    text = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", "", text)
    # Remove headers markdown
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r"\*\*([^\*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^\*]+)\*", r"\1", text)
    # Remove horizontal rules
    text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)
    # Remove HTML comments
    text = re.sub(r"<!--[\s\S]*?-->", "", text)

    return text


def count_words(text: str) -> int:
    """Count words in text after cleaning markdown."""
    cleaned = clean_markdown_for_count(text)
    words = cleaned.split()
    return len(words)


def extract_section(
    content: str, section_pattern: str, next_section_pattern: str = None
) -> str:
    """Extract content between two section markers."""
    if next_section_pattern:
        pattern = f"{section_pattern}(.*?){next_section_pattern}"
    else:
        pattern = f"{section_pattern}(.*?)$"

    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1)
    return ""


def analyze_dissertation():
    """Analyze dissertation word count by section."""

    dissertation_path = Path("docs/dissertation.md")

    if not dissertation_path.exists():
        print(f"❌ Error: {dissertation_path} not found")
        return

    with open(dissertation_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Define section patterns
    sections = {
        "1. Introduction": (r"# 1\. Introduction", r"# 2\. Background"),
        "2. Background (Literature Review)": (r"# 2\. Background", r"# 3\. Ethical"),
        "3. Ethical and Professional Considerations": (
            r"# 3\. Ethical",
            r"# 4\. Methodology",
        ),
        "4. Methodology": (r"# 4\. Methodology", r"# 5\. Implementation"),
        "5. Implementation": (r"# 5\. Implementation", r"# 6\. Evaluation"),
        "6. Evaluation": (r"# 6\. Evaluation", r"# 7\. Learning"),
        "7. Learning and Reflection": (r"# 7\. Learning", r"# 8\. Conclusion"),
        "8. Conclusion": (r"# 8\. Conclusion", r"# References"),
        "Appendix: Research Approach Evolution": (
            r"# Appendix: Research Approach Evolution",
            None,
        ),
        "References": (r"# References", r"# Appendix"),
    }

    # Target word counts (approximate)
    targets = {
        "1. Introduction": 800,
        "2. Background (Literature Review)": 3000,
        "3. Ethical and Professional Considerations": 800,
        "4. Methodology": 1500,
        "5. Implementation": 2500,
        "6. Evaluation": 1500,
        "7. Learning and Reflection": 800,
        "8. Conclusion": 500,
        "Appendix: Research Approach Evolution": 0,  # Not counted toward main target
        "References": 0,  # Not counted
    }

    print("\n" + "=" * 80)
    print("DISSERTATION WORD COUNT ANALYSIS")
    print("=" * 80)
    print(f"Analyzed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Target: 13,000 words (main content excluding references/appendices)")
    print("=" * 80 + "\n")

    section_counts = {}
    total_words = 0
    main_content_words = 0

    for section_name, (start_pattern, end_pattern) in sections.items():
        section_text = extract_section(content, start_pattern, end_pattern)
        word_count = count_words(section_text)
        section_counts[section_name] = word_count

        target = targets.get(section_name, 0)

        # Calculate progress
        if target > 0:
            progress_pct = (word_count / target) * 100
            bar_length = 30
            filled = int((bar_length * word_count) / target) if target > 0 else 0
            filled = min(filled, bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)

            status = (
                "✅"
                if word_count >= target * 0.9
                else "🟡"
                if word_count >= target * 0.5
                else "🔴"
            )

            print(f"{status} {section_name}")
            print(f"   {bar} {word_count:,} / {target:,} words ({progress_pct:.1f}%)")
            print()

            main_content_words += word_count
        else:
            print(f"📄 {section_name}: {word_count:,} words (not counted toward target)")
            print()

        total_words += word_count

    print("=" * 80)
    print(
        f"MAIN CONTENT TOTAL: {main_content_words:,} / 13,000 words ({(main_content_words/13000)*100:.1f}%)"
    )
    print(f"DOCUMENT TOTAL (including refs/appendices): {total_words:,} words")
    print("=" * 80)

    # Overall progress bar
    overall_progress = (main_content_words / 13000) * 100
    bar_length = 50
    filled = int((bar_length * main_content_words) / 13000)
    filled = min(filled, bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\nOverall Progress: {bar} {overall_progress:.1f}%")

    # Remaining work
    remaining = max(0, 13000 - main_content_words)
    if remaining > 0:
        print(f"\n📝 Remaining: {remaining:,} words to reach 13,000-word target")
        print("   Main gaps:")
        for section_name, target in targets.items():
            if target > 0:
                current = section_counts.get(section_name, 0)
                gap = max(0, target - current)
                if gap > target * 0.1:  # More than 10% below target
                    print(f"   - {section_name}: {gap:,} words short")
    else:
        print(f"\n✅ Target achieved! {main_content_words - 13000:,} words over target.")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    analyze_dissertation()
