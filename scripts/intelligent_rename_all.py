#!/usr/bin/env python3
"""
Intelligent deduplication for ALL component types using actual content analysis.
"""

import json
from collections import defaultdict
from typing import Any


def analyze_activity_focus(activity: dict[str, Any]) -> str:
    """Analyze activity content to determine specific focus"""

    description = activity.get("description", "").lower()
    objectives = " ".join(activity.get("learning_objectives", [])).lower()
    bloom_level = activity.get("bloom_level", "").lower()
    duration = activity.get("estimated_duration", "")

    combined_text = description + " " + objectives

    # Extract key differentiators
    focus_indicators = {
        "visualization": ["visual", "chart", "graph", "plot", "dashboard"],
        "written_analysis": ["written", "report", "essay", "document", "explain"],
        "hands_on": ["hands-on", "coding", "programming", "implementation"],
        "comparison": ["compare", "contrast", "different", "versus", "alternative"],
        "business": ["business", "strategic", "decision", "impact", "roi"],
        "technical": ["technical", "algorithm", "statistical", "mathematical"],
        "collaborative": ["group", "team", "peer", "collaborative"],
        "individual": ["individual", "personal", "solo"],
        "short": ["quick", "brief", "short"]
        if "30" in str(duration) or "45" in str(duration)
        else [],
        "extended": ["detailed", "comprehensive", "in-depth"]
        if "90" in str(duration) or "120" in str(duration)
        else [],
    }

    scores = {}
    for focus, indicators in focus_indicators.items():
        score = sum(1 for indicator in indicators if indicator in combined_text)
        if score > 0:
            scores[focus] = score

    # Also consider Bloom's taxonomy level
    if "analyze" in bloom_level:
        scores["analytical"] = scores.get("analytical", 0) + 2
    elif "create" in bloom_level:
        scores["creative"] = scores.get("creative", 0) + 2
    elif "evaluate" in bloom_level:
        scores["evaluative"] = scores.get("evaluative", 0) + 2

    return max(scores.items(), key=lambda x: x[1])[0] if scores else "general"


def analyze_assessment_focus(assessment: dict[str, Any]) -> str:
    """Analyze assessment content to determine specific focus"""

    description = assessment.get("description", "").lower()
    assessment_type = assessment.get("type", "").lower()
    rubric = " ".join(assessment.get("rubric_criteria", [])).lower()

    combined_text = description + " " + rubric

    focus_indicators = {
        "portfolio": ["portfolio", "collection", "compilation"],
        "practical": ["practical", "hands-on", "implementation", "coding"],
        "theoretical": ["theoretical", "conceptual", "essay", "written"],
        "exam": ["exam", "test", "quiz", "timed"],
        "project": ["project", "build", "create", "develop"],
        "analysis": ["analysis", "analyze", "evaluation", "critique"],
        "presentation": ["presentation", "demo", "showcase", "present"],
        "collaborative": ["group", "team", "peer"],
        "comprehensive": ["comprehensive", "final", "capstone", "integration"],
    }

    scores = {}
    for focus, indicators in focus_indicators.items():
        score = sum(1 for indicator in indicators if indicator in combined_text)
        if score > 0:
            scores[focus] = score

    # Consider assessment type
    if "project" in assessment_type:
        scores["project"] = scores.get("project", 0) + 2
    elif "exam" in assessment_type:
        scores["exam"] = scores.get("exam", 0) + 2
    elif "portfolio" in assessment_type:
        scores["portfolio"] = scores.get("portfolio", 0) + 2

    return max(scores.items(), key=lambda x: x[1])[0] if scores else "general"


def intelligent_rename_activity(base_title: str, focus: str, variant_num: int) -> str:
    """Generate intelligent activity renames based on content focus"""

    # For Feature Importance activities
    if "Feature Importance in Random Forest" in base_title:
        focus_renames = {
            "visualization": "Visual Analysis of Random Forest Feature Importance",
            "written_analysis": "Written Interpretation of RF Feature Rankings",
            "comparison": "Comparative Analysis of Feature Importance Metrics",
            "business": "Business Impact Analysis via Feature Importance",
            "technical": "Technical Deep-Dive: RF Feature Importance",
            "short": "Quick Assessment: RF Feature Rankings",
            "extended": "Comprehensive RF Feature Importance Study",
        }
        return focus_renames.get(
            focus, f"Random Forest Feature Analysis Workshop {variant_num}"
        )

    # For Algorithm Complexity activities
    elif "Algorithm Complexity" in base_title:
        focus_renames = {
            "visualization": "Algorithm Complexity Visualization Challenge",
            "comparison": "Comparative Algorithm Complexity Analysis",
            "hands_on": "Hands-on Algorithm Complexity Testing",
            "collaborative": "Team-Based Algorithm Analysis Challenge",
            "individual": "Individual Algorithm Complexity Assessment",
        }
        return focus_renames.get(focus, f"Algorithm Complexity Exercise {variant_num}")

    # For Customer Segmentation Dashboard
    elif "Customer Segmentation Dashboard" in base_title:
        focus_renames = {
            "visualization": "Interactive Customer Segmentation Dashboard",
            "business": "Strategic Customer Segmentation Analysis",
            "hands_on": "Build-Your-Own Segmentation Dashboard",
            "collaborative": "Team Dashboard Development Project",
            "technical": "Advanced Segmentation Dashboard Engineering",
        }
        return focus_renames.get(focus, f"Customer Segmentation Project {variant_num}")

    # Generic fallback
    else:
        focus_suffixes = {
            "visualization": ": Visual Analysis",
            "written_analysis": ": Written Report",
            "hands_on": ": Practical Workshop",
            "comparison": ": Comparative Study",
            "business": ": Business Application",
            "technical": ": Technical Implementation",
            "collaborative": ": Team Exercise",
            "short": ": Quick Assessment",
            "extended": ": Comprehensive Study",
        }
        suffix = focus_suffixes.get(focus, f": Exercise {variant_num}")
        return f"{base_title}{suffix}"


def intelligent_rename_assessment(base_title: str, focus: str, variant_num: int) -> str:
    """Generate intelligent assessment renames based on content focus"""

    # For Mathematical Modeling Portfolio
    if "Mathematical Modeling Portfolio" in base_title:
        focus_renames = {
            "portfolio": "Mathematical Modeling Portfolio Collection",
            "practical": "Applied Mathematical Modeling Projects",
            "theoretical": "Theoretical Mathematical Modeling Analysis",
            "comprehensive": "Comprehensive Mathematical Modeling Portfolio",
        }
        return focus_renames.get(
            focus, f"Mathematical Modeling Assessment {variant_num}"
        )

    # For Customer Churn Prediction
    elif "Customer Churn Prediction" in base_title:
        focus_renames = {
            "analysis": "Customer Churn Prediction Analysis Report",
            "project": "Customer Churn Prediction Implementation Project",
            "practical": "Hands-on Customer Churn Modeling",
            "theoretical": "Theoretical Foundations of Churn Prediction",
            "presentation": "Customer Churn Analysis Presentation",
        }
        return focus_renames.get(focus, f"Customer Churn Assessment {variant_num}")

    # For Website Development
    elif "Website Development" in base_title:
        focus_renames = {
            "project": "Personal Website Development Project",
            "portfolio": "Website Portfolio Showcase",
            "practical": "Hands-on Website Implementation",
            "presentation": "Website Development Demonstration",
        }
        return focus_renames.get(focus, f"Website Development Task {variant_num}")

    # For Calculus and Linear Algebra Exam
    elif "Calculus and Linear Algebra" in base_title:
        focus_renames = {
            "exam": "Advanced Mathematics Integration Exam",
            "comprehensive": "Comprehensive Calculus-Linear Algebra Test",
            "practical": "Applied Mathematical Problem-Solving Exam",
            "theoretical": "Theoretical Mathematics Assessment",
        }
        return focus_renames.get(focus, f"Advanced Mathematics Exam {variant_num}")

    # Generic fallback
    else:
        focus_suffixes = {
            "portfolio": " Portfolio",
            "practical": " Practical Assessment",
            "theoretical": " Theoretical Exam",
            "project": " Implementation Project",
            "analysis": " Analysis Report",
            "presentation": " Presentation",
            "exam": " Examination",
            "comprehensive": " Comprehensive Assessment",
        }
        suffix = focus_suffixes.get(focus, f" Assessment {variant_num}")
        return f"{base_title}{suffix}"


def deduplicate_component_type(
    components: list[dict[str, Any]], component_type: str
) -> list[dict[str, Any]]:
    """Intelligently deduplicate a specific component type"""

    print(f"\n🧠 Intelligently analyzing {component_type}...")

    # Group by title
    title_groups = defaultdict(list)
    for comp in components:
        title = comp.get("title", "")
        title_groups[title].append(comp)

    deduplicated = []
    total_renamed = 0

    for title, group in title_groups.items():
        if len(group) == 1:
            deduplicated.extend(group)
        else:
            print(f"\n🔍 Analyzing {len(group)} {component_type}: '{title}'")

            # Analyze each component's focus
            analyzed_components = []
            for i, comp in enumerate(group):
                if component_type == "activities":
                    focus = analyze_activity_focus(comp)
                elif component_type == "assessments":
                    focus = analyze_assessment_focus(comp)
                else:
                    focus = "general"

                analyzed_components.append(
                    {
                        "component": comp,
                        "focus": focus,
                        "description_length": len(comp.get("description", "")),
                    }
                )
                print(
                    f"  {i+1}. Focus: '{focus}', Description: {len(comp.get('description', ''))} chars"
                )

            # Sort by description length (keep most detailed with original title)
            analyzed_components.sort(
                key=lambda x: x["description_length"], reverse=True
            )

            # Keep first with original title
            best_comp = analyzed_components[0]["component"]
            deduplicated.append(best_comp)
            print(
                f"  ✅ Keeping original title for most detailed {component_type[:-1]}"
            )

            # Rename the rest
            for i, analyzed in enumerate(analyzed_components[1:], 1):
                comp = analyzed["component"].copy()
                focus = analyzed["focus"]

                if component_type == "activities":
                    new_title = intelligent_rename_activity(title, focus, i)
                elif component_type == "assessments":
                    new_title = intelligent_rename_assessment(title, focus, i)
                else:
                    new_title = f"{title}: Variant {i}"

                comp["title"] = new_title
                comp["original_title"] = title
                comp["content_focus"] = focus

                deduplicated.append(comp)
                total_renamed += 1
                print(f"  ✏️  Renamed to: '{new_title}' (focus: {focus})")

    print(f"\n🎉 Renamed {total_renamed} {component_type}")
    return deduplicated


def main():
    """Main intelligent deduplication for all component types"""

    print("🚀 Starting intelligent deduplication of ALL components...")

    component_configs = [
        (
            "activities",
            "data/components/learning_activities.json",
            "data/components/learning_activities_cleaned.json",
        ),
        (
            "assessments",
            "data/components/assessments.json",
            "data/components/assessments_cleaned.json",
        ),
    ]

    for component_type, input_path, output_path in component_configs:
        print(f"\n📋 Processing {component_type}...")

        # Load original data
        with open(input_path) as f:
            original_components = json.load(f)

        print(f"📊 Original {component_type}: {len(original_components)}")

        # Perform intelligent deduplication
        deduplicated_components = deduplicate_component_type(
            original_components, component_type
        )

        print(f"📊 Final {component_type}: {len(deduplicated_components)}")

        # Save cleaned version
        with open(output_path, "w") as f:
            json.dump(deduplicated_components, f, indent=2)

        print(f"✅ Cleaned {component_type} saved to: {output_path}")

    print("\n🎉 All components intelligently deduplicated!")
    print(
        "📁 Original files preserved, cleaned versions created with '_cleaned' suffix"
    )


if __name__ == "__main__":
    main()
