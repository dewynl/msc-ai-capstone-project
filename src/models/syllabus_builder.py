#!/usr/bin/env python3
"""
SyllabusBuilder - Execution Engine for Function Call Approach

This class implements the builder pattern that T5 generates function calls for.
Instead of generating broken JSON, T5 generates executable function calls that
build a valid syllabus structure through this builder.
"""

import json
import re
from typing import Any, Dict, List, Optional


class SyllabusBuilder:
    """
    Builder class for constructing syllabi through function calls.

    This is the execution target for T5-generated function calls.
    Instead of JSON syntax precision, T5 generates calls like:

    b = SyllabusBuilder()
    b.set_info("Machine Learning", "computer_science", "advanced")
    b.add_objective("Learn neural networks")
    b.add_module("Deep Learning Fundamentals", 8)
    return b.build()
    """

    def __init__(self):
        """Initialize empty syllabus structure."""
        self.course_info = {}
        self.learning_objectives = []
        self.modules = []
        self.activities = []
        self.assessments = []

    def set_info(
        self,
        title: str,
        domain: str,
        level: str,
        duration: str = "semester",
        description: str = "",
    ) -> "SyllabusBuilder":
        """
        Set course information.

        Args:
            title: Course title
            domain: Subject domain (computer_science, mathematics, physics)
            level: Difficulty level (beginner, intermediate, advanced)
            duration: Course duration (default: semester)
            description: Course description

        Returns:
            Self for method chaining
        """
        self.course_info = {
            "title": title,
            "domain": domain,
            "level": level,
            "duration": duration,
            "description": description,
        }
        return self

    def set_course_info(
        self,
        title: str,
        domain: str,
        level: str,
        duration: str = "semester",
        description: str = "",
    ) -> "SyllabusBuilder":
        """Alias for set_info() for backward compatibility."""
        return self.set_info(title, domain, level, duration, description)

    def add_objective(self, objective: str) -> "SyllabusBuilder":
        """
        Add a learning objective.

        Args:
            objective: Learning objective text

        Returns:
            Self for method chaining
        """
        self.learning_objectives.append(objective)
        return self

    def add_learning_objective(self, objective: str) -> "SyllabusBuilder":
        """Alias for add_objective() for backward compatibility."""
        return self.add_objective(objective)

    def add_module(
        self,
        title: str,
        estimated_hours: int = 8,
        description: str = "",
        key_concepts: Optional[List[str]] = None,
    ) -> "SyllabusBuilder":
        """
        Add a course module.

        Args:
            title: Module title
            estimated_hours: Time required (default: 8 hours)
            description: Module description
            key_concepts: List of key concepts covered

        Returns:
            Self for method chaining
        """
        module = {
            "title": title,
            "estimated_hours": estimated_hours,
            "description": description or f"Module covering {title}",
            "key_concepts": key_concepts or [],
        }
        self.modules.append(module)
        return self

    def add_module_by_id(self, module_id: str) -> "SyllabusBuilder":
        """
        Add a module by retrieving it from the component database by ID.

        This method is used when T5 has been given RAG context with available
        component IDs and wants to reference actual database components.

        Args:
            module_id: UUID of the module to add

        Returns:
            Self for method chaining
        """
        try:
            # Load modules from database
            from pathlib import Path

            modules_file = Path("data/components/modules.json")
            if modules_file.exists():
                modules = json.load(open(modules_file))
                # Find module by ID
                for module in modules:
                    if module.get("module_id") == module_id:
                        # Add module with all its database details
                        module_data = {
                            "id": module_id,
                            "title": module.get("title", "Unknown Module"),
                            "description": module.get("description", ""),
                            "key_concepts": module.get("key_concepts", []),
                            "estimated_hours": module.get("estimated_hours", 8),
                            "domain": module.get("domain"),
                            "difficulty": module.get("difficulty"),
                            "source": "rag_retrieved",
                        }
                        self.modules.append(module_data)
                        return self

            # Fallback: If module not found, add placeholder
            self.modules.append(
                {
                    "id": module_id,
                    "title": f"Module {module_id[:8]}",
                    "description": "Module not found in database",
                    "key_concepts": [],
                    "estimated_hours": 8,
                    "source": "not_found",
                }
            )
        except Exception as e:
            # Fallback on error
            self.modules.append(
                {
                    "id": module_id,
                    "title": f"Module {module_id[:8]}",
                    "description": f"Error loading module: {e}",
                    "key_concepts": [],
                    "estimated_hours": 8,
                    "source": "error",
                }
            )
        return self

    def add_activity(
        self,
        title: str,
        bloom_level: str = "apply",
        estimated_hours: int = 1,
        description: str = "",
    ) -> "SyllabusBuilder":
        """
        Add a learning activity.

        Args:
            title: Activity title
            bloom_level: Bloom's taxonomy level (remember, understand, apply, analyze, evaluate, create)
            estimated_hours: Time required (default: 1 hour)
            description: Activity description

        Returns:
            Self for method chaining
        """
        activity = {
            "title": title,
            "bloom_level": bloom_level,
            "estimated_hours": estimated_hours,
            "description": description or f"Activity: {title}",
        }
        self.activities.append(activity)
        return self

    def add_activity_by_id(self, activity_id: str) -> "SyllabusBuilder":
        """
        Add an activity by retrieving it from the component database by ID.

        Args:
            activity_id: UUID of the activity to add

        Returns:
            Self for method chaining
        """
        try:
            from pathlib import Path

            activities_file = Path("data/components/activities.json")
            if activities_file.exists():
                activities = json.load(open(activities_file))
                for activity in activities:
                    if activity.get("activity_id") == activity_id:
                        activity_data = {
                            "id": activity_id,
                            "title": activity.get("title", "Unknown Activity"),
                            "description": activity.get("description", ""),
                            "bloom_level": activity.get("bloom_level", "apply"),
                            "estimated_hours": activity.get("estimated_hours", 1),
                            "domain": activity.get("domain"),
                            "difficulty": activity.get("difficulty"),
                            "source": "rag_retrieved",
                        }
                        self.activities.append(activity_data)
                        return self

            # Fallback
            self.activities.append(
                {
                    "id": activity_id,
                    "title": f"Activity {activity_id[:8]}",
                    "description": "Activity not found in database",
                    "bloom_level": "apply",
                    "estimated_hours": 1,
                    "source": "not_found",
                }
            )
        except Exception as e:
            self.activities.append(
                {
                    "id": activity_id,
                    "title": f"Activity {activity_id[:8]}",
                    "description": f"Error loading activity: {e}",
                    "bloom_level": "apply",
                    "estimated_hours": 1,
                    "source": "error",
                }
            )
        return self

    def add_assessment(
        self,
        title: str,
        assessment_type: str = "exam",
        estimated_hours: int = 2,
        description: str = "",
    ) -> "SyllabusBuilder":
        """
        Add an assessment.

        Args:
            title: Assessment title
            assessment_type: Type of assessment (exam, quiz, project, assignment)
            estimated_hours: Time required (default: 2 hours)
            description: Assessment description

        Returns:
            Self for method chaining
        """
        assessment = {
            "title": title,
            "assessment_type": assessment_type,
            "estimated_hours": estimated_hours,
            "description": description or f"{assessment_type.title()}: {title}",
        }
        self.assessments.append(assessment)
        return self

    def add_assessment_by_id(self, assessment_id: str) -> "SyllabusBuilder":
        """
        Add an assessment by retrieving it from the component database by ID.

        Args:
            assessment_id: UUID of the assessment to add

        Returns:
            Self for method chaining
        """
        try:
            from pathlib import Path

            assessments_file = Path("data/components/assessments.json")
            if assessments_file.exists():
                assessments = json.load(open(assessments_file))
                for assessment in assessments:
                    if assessment.get("assessment_id") == assessment_id:
                        assessment_data = {
                            "id": assessment_id,
                            "title": assessment.get("title", "Unknown Assessment"),
                            "description": assessment.get("description", ""),
                            "assessment_type": assessment.get(
                                "assessment_type", "exam"
                            ),
                            "estimated_hours": assessment.get("estimated_hours", 2),
                            "domain": assessment.get("domain"),
                            "difficulty": assessment.get("difficulty"),
                            "source": "rag_retrieved",
                        }
                        self.assessments.append(assessment_data)
                        return self

            # Fallback
            self.assessments.append(
                {
                    "id": assessment_id,
                    "title": f"Assessment {assessment_id[:8]}",
                    "description": "Assessment not found in database",
                    "assessment_type": "exam",
                    "estimated_hours": 2,
                    "source": "not_found",
                }
            )
        except Exception as e:
            self.assessments.append(
                {
                    "id": assessment_id,
                    "title": f"Assessment {assessment_id[:8]}",
                    "description": f"Error loading assessment: {e}",
                    "assessment_type": "exam",
                    "estimated_hours": 2,
                    "source": "error",
                }
            )
        return self

    def build(self) -> Dict[str, Any]:
        """
        Build and return the complete syllabus structure.

        Returns:
            Complete syllabus as dictionary (JSON-serializable)
        """
        syllabus = {
            "course_info": self.course_info,
            "learning_objectives": self.learning_objectives,
            "modules": self.modules,
            "activities": self.activities,
            "assessments": self.assessments,
        }

        # Add metadata
        syllabus["metadata"] = {
            "generated_by": "function_call_approach",
            "total_modules": len(self.modules),
            "total_activities": len(self.activities),
            "total_assessments": len(self.assessments),
            "estimated_total_hours": (
                sum(m.get("estimated_hours", 0) for m in self.modules)
                + sum(a.get("estimated_hours", 0) for a in self.activities)
                + sum(a.get("estimated_hours", 0) for a in self.assessments)
            ),
        }

        return syllabus

    def to_json(self, indent: int = 2) -> str:
        """
        Convert syllabus to JSON string.

        Args:
            indent: JSON indentation level

        Returns:
            JSON string representation
        """
        return json.dumps(self.build(), indent=indent)

    def reset(self) -> "SyllabusBuilder":
        """
        Reset builder to empty state.

        Returns:
            Self for method chaining
        """
        self.course_info = {}
        self.learning_objectives = []
        self.modules = []
        self.activities = []
        self.assessments = []
        return self

    def __str__(self) -> str:
        """String representation showing syllabus summary."""
        return (
            f"SyllabusBuilder("
            f"title='{self.course_info.get('title', 'Untitled')}', "
            f"modules={len(self.modules)}, "
            f"activities={len(self.activities)}, "
            f"assessments={len(self.assessments)})"
        )

    def __repr__(self) -> str:
        """Detailed string representation."""
        return self.__str__()


def execute_function_calls(
    function_calls: str, globals_dict: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Execute T5-generated function calls to build a syllabus.

    This is the core execution engine that takes T5's generated function calls
    and executes them safely to produce a valid syllabus structure.

    Args:
        function_calls: String containing function calls (generated by T5)
        globals_dict: Optional globals for execution context

    Returns:
        Complete syllabus dictionary

    Raises:
        ValueError: If function calls are invalid or unsafe
        SyntaxError: If function calls have syntax errors
    """
    if globals_dict is None:
        globals_dict = {"SyllabusBuilder": SyllabusBuilder}

    # Security: Only allow safe function calls
    allowed_functions = {
        "SyllabusBuilder",
        "b.set_info",
        "b.set_course_info",
        "b.add_objective",
        "b.add_learning_objective",
        "b.add_module",
        "b.add_module_by_id",
        "b.add_activity",
        "b.add_activity_by_id",
        "b.add_assessment",
        "b.add_assessment_by_id",
        "b.build",
        "return",
    }

    # Basic security check - look for actual dangerous function calls, not just keywords in strings
    dangerous_patterns = [
        r"\bimport\s+",
        r"\bexec\s*\(",
        r"\beval\s*\(",
        r"\bopen\s*\(",
        r"\b__\w+__",
        r"\bos\.",
        r"\bsys\.",
        r"\bsubprocess\.",
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, function_calls):
            raise ValueError(f"Potentially unsafe function call detected: {pattern}")

    try:
        # Create local execution environment
        local_dict = {}

        # Execute the function calls
        exec(function_calls, globals_dict, local_dict)  # nosec B102

        # The function calls should assign result to a variable or return it
        # Try common patterns
        if "syllabus" in local_dict:
            result = local_dict["syllabus"]
        elif "result" in local_dict:
            result = local_dict["result"]
        else:
            # If no explicit return variable, look for SyllabusBuilder instance
            for key, value in local_dict.items():
                if isinstance(value, SyllabusBuilder):
                    result = value.build()
                    break
            else:
                raise ValueError("No valid syllabus result found in function calls")

        # Ensure result is a dictionary
        if isinstance(result, SyllabusBuilder):
            result = result.build()

        if not isinstance(result, dict):
            raise ValueError(
                f"Function calls must return a dictionary, got {type(result)}"
            )

        return result

    except SyntaxError as e:
        raise SyntaxError(f"Invalid function call syntax: {e}")
    except Exception as e:
        raise ValueError(f"Function call execution failed: {e}")


# Example usage and testing
if __name__ == "__main__":
    # Test the builder directly
    print("🧪 Testing SyllabusBuilder directly...")

    builder = SyllabusBuilder()
    syllabus = (
        builder.set_info(
            "Machine Learning Fundamentals",
            "computer_science",
            "advanced",
            description="Advanced ML concepts and applications",
        )
        .add_objective("Understand neural network architectures")
        .add_objective("Implement deep learning models")
        .add_module("Neural Networks", 12, "Introduction to neural networks")
        .add_module("Deep Learning", 16, "Advanced deep learning techniques")
        .add_activity("Build a CNN", "create", 4)
        .add_activity("Implement backpropagation", "apply", 3)
        .add_assessment("Final Project", "project", 20)
        .build()
    )

    print("✅ Direct builder test successful!")
    print(f"Generated syllabus: {syllabus['course_info']['title']}")
    print(
        f"Total components: {syllabus['metadata']['total_modules']} modules, {syllabus['metadata']['total_activities']} activities"
    )

    # Test function call execution
    print("\n🧪 Testing function call execution...")

    test_calls = """
b = SyllabusBuilder()
b.set_info("Introduction to Python", "computer_science", "beginner")
b.add_objective("Learn Python syntax")
b.add_objective("Build simple programs")
b.add_module("Python Basics", 8)
b.add_activity("Hello World", "remember", 1)
b.add_assessment("Python Quiz", "quiz", 1)
syllabus = b.build()
"""

    try:
        result = execute_function_calls(test_calls)
        print("✅ Function call execution successful!")
        print(f"Generated syllabus: {result['course_info']['title']}")
        print(f"Learning objectives: {len(result['learning_objectives'])}")
    except Exception as e:
        print(f"❌ Function call execution failed: {e}")

    print("\n🎉 SyllabusBuilder implementation complete!")
