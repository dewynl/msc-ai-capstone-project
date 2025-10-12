"""
Simplified STEM-Focused Data Models for Educational Components

This module defines the simplified data schemas for STEM-focused syllabus generation,
removing complexity while maintaining pedagogical value.

Key Simplifications:
- STEM domains only: cs, math, physics, engineering
- Removed: week_number, prerequisite_concepts, complex workload
- Added: simplified estimated_hours, domain
- Focus: pedagogical value with reduced complexity
"""

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class Domain(Enum):
    """Domain classifications (STEM-focused)"""

    CS = "computer_science"  # Programming, algorithms, data structures, software engineering, AI/ML
    MATH = "mathematics"  # Calculus, algebra, statistics, discrete math, applied math
    PHYSICS = (
        "physics"  # Classical mechanics, electromagnetism, thermodynamics, quantum
    )
    ENGINEERING = (
        "engineering"  # System design, optimization, modeling, problem-solving
    )


class BloomLevel(Enum):
    """Bloom's Taxonomy levels for learning objectives"""

    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"


class DifficultyLevel(Enum):
    """Course difficulty levels"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class AssessmentType(Enum):
    """Types of assessments"""

    EXAM = "exam"
    PROJECT = "project"
    ASSIGNMENT = "assignment"
    QUIZ = "quiz"
    LAB = "lab"
    PRESENTATION = "presentation"


@dataclass
class LearningActivity:
    """Simplified learning activity component for STEM education"""

    # Core identifiers
    activity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""

    # Domain classification
    domain: Domain = Domain.CS
    bloom_level: BloomLevel = BloomLevel.UNDERSTAND
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER

    # Time estimation (simplified)
    estimated_hours: int = 1  # 1-8 hours typical

    # Educational content
    learning_objectives: List[str] = field(default_factory=list)
    instructions: str = ""
    materials_needed: List[str] = field(default_factory=list)
    assessment_method: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "activity_id": self.activity_id,
            "title": self.title,
            "description": self.description,
            "domain": self.domain.value,
            "bloom_level": self.bloom_level.value,
            "difficulty": self.difficulty.value,
            "estimated_hours": self.estimated_hours,
            "learning_objectives": self.learning_objectives,
            "instructions": self.instructions,
            "materials_needed": self.materials_needed,
            "assessment_method": self.assessment_method,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearningActivity":
        """Create instance from dictionary"""
        return cls(
            activity_id=data.get("activity_id", str(uuid.uuid4())),
            title=data.get("title", ""),
            description=data.get("description", ""),
            domain=Domain(data.get("domain", "computer_science")),
            bloom_level=BloomLevel(data.get("bloom_level", "understand")),
            difficulty=DifficultyLevel(data.get("difficulty", "beginner")),
            estimated_hours=data.get("estimated_hours", 1),
            learning_objectives=data.get("learning_objectives", []),
            instructions=data.get("instructions", ""),
            materials_needed=data.get("materials_needed", []),
            assessment_method=data.get("assessment_method", ""),
        )


@dataclass
class AssessmentComponent:
    """Simplified assessment component for STEM education"""

    # Core identifiers
    assessment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""

    # Domain classification
    domain: Domain = Domain.CS
    assessment_type: AssessmentType = AssessmentType.ASSIGNMENT
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER

    # Time estimation (simplified)
    estimated_hours: int = 2  # Time for students to complete

    # Educational content
    learning_objectives: List[str] = field(default_factory=list)
    criteria: List[str] = field(default_factory=list)  # Assessment criteria/rubric
    materials_needed: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "assessment_id": self.assessment_id,
            "title": self.title,
            "description": self.description,
            "domain": self.domain.value,
            "assessment_type": self.assessment_type.value,
            "difficulty": self.difficulty.value,
            "estimated_hours": self.estimated_hours,
            "learning_objectives": self.learning_objectives,
            "criteria": self.criteria,
            "materials_needed": self.materials_needed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssessmentComponent":
        """Create instance from dictionary"""
        return cls(
            assessment_id=data.get("assessment_id", str(uuid.uuid4())),
            title=data.get("title", ""),
            description=data.get("description", ""),
            domain=Domain(data.get("domain", "computer_science")),
            assessment_type=AssessmentType(data.get("assessment_type", "assignment")),
            difficulty=DifficultyLevel(data.get("difficulty", "beginner")),
            estimated_hours=data.get("estimated_hours", 2),
            learning_objectives=data.get("learning_objectives", []),
            criteria=data.get("criteria", []),
            materials_needed=data.get("materials_needed", []),
        )


@dataclass
class CourseModule:
    """Simplified course module component for STEM education"""

    # Core identifiers
    module_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""

    # Domain classification
    domain: Domain = Domain.CS
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER

    # Time estimation (simplified)
    estimated_hours: int = 3  # Total module time (lectures + study)

    # Educational content
    key_concepts: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    suggested_readings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "module_id": self.module_id,
            "title": self.title,
            "description": self.description,
            "domain": self.domain.value,
            "difficulty": self.difficulty.value,
            "estimated_hours": self.estimated_hours,
            "key_concepts": self.key_concepts,
            "learning_objectives": self.learning_objectives,
            "suggested_readings": self.suggested_readings,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CourseModule":
        """Create instance from dictionary"""
        return cls(
            module_id=data.get("module_id", str(uuid.uuid4())),
            title=data.get("title", ""),
            description=data.get("description", ""),
            domain=Domain(data.get("domain", "computer_science")),
            difficulty=DifficultyLevel(data.get("difficulty", "beginner")),
            estimated_hours=data.get("estimated_hours", 3),
            key_concepts=data.get("key_concepts", []),
            learning_objectives=data.get("learning_objectives", []),
            suggested_readings=data.get("suggested_readings", []),
        )


# Helper functions for component creation (backwards compatibility)
def create_learning_activity(**kwargs) -> Dict[str, Any]:
    """Create learning activity with simplified schema"""
    activity = LearningActivity(
        activity_id=kwargs.get("activity_id", str(uuid.uuid4())),
        title=kwargs.get("title", ""),
        description=kwargs.get("description", ""),
        domain=Domain(kwargs.get("stem_domain", "computer_science")),
        bloom_level=BloomLevel(kwargs.get("bloom_level", "understand")),
        difficulty=DifficultyLevel(kwargs.get("difficulty", "beginner")),
        estimated_hours=kwargs.get("estimated_hours", 1),
        learning_objectives=kwargs.get("learning_objectives", []),
        instructions=kwargs.get("instructions", ""),
        materials_needed=kwargs.get("materials_needed", []),
        assessment_method=kwargs.get("assessment_method", ""),
    )
    return activity.to_dict()


def create_assessment_component(**kwargs) -> Dict[str, Any]:
    """Create assessment component with simplified schema"""
    assessment = AssessmentComponent(
        assessment_id=kwargs.get("assessment_id", str(uuid.uuid4())),
        title=kwargs.get("title", ""),
        description=kwargs.get("description", ""),
        domain=Domain(kwargs.get("stem_domain", "computer_science")),
        assessment_type=AssessmentType(kwargs.get("assessment_type", "assignment")),
        difficulty=DifficultyLevel(kwargs.get("difficulty", "beginner")),
        estimated_hours=kwargs.get("estimated_hours", 2),
        learning_objectives=kwargs.get("learning_objectives", []),
        criteria=kwargs.get("criteria", []),
        materials_needed=kwargs.get("materials_needed", []),
    )
    return assessment.to_dict()


def create_module_component(**kwargs) -> Dict[str, Any]:
    """Create course module with simplified schema"""
    module = CourseModule(
        module_id=kwargs.get("module_id", str(uuid.uuid4())),
        title=kwargs.get("title", ""),
        description=kwargs.get("description", ""),
        domain=Domain(kwargs.get("stem_domain", "computer_science")),
        difficulty=DifficultyLevel(kwargs.get("difficulty", "beginner")),
        estimated_hours=kwargs.get("estimated_hours", 3),
        key_concepts=kwargs.get("key_concepts", []),
        learning_objectives=kwargs.get("learning_objectives", []),
        suggested_readings=kwargs.get("suggested_readings", []),
    )
    return module.to_dict()


# Schema validation functions
def validate_learning_activity(data: Dict[str, Any]) -> bool:
    """Validate learning activity data against schema"""
    required_fields = ["title", "description", "domain", "bloom_level"]
    try:
        for required_field in required_fields:
            if not data.get(required_field):
                return False

        # Validate enums
        Domain(data["domain"])
        BloomLevel(data["bloom_level"])
        DifficultyLevel(data.get("difficulty", "beginner"))

        # Validate hours range
        hours = data.get("estimated_hours", 1)
        if not isinstance(hours, int) or hours < 1 or hours > 20:
            return False

        return True
    except (ValueError, TypeError):
        return False


def validate_assessment_component(data: Dict[str, Any]) -> bool:
    """Validate assessment component data against schema"""
    required_fields = ["title", "description", "domain", "assessment_type"]
    try:
        for required_field in required_fields:
            if not data.get(required_field):
                return False

        # Validate enums
        Domain(data["domain"])
        AssessmentType(data["assessment_type"])
        DifficultyLevel(data.get("difficulty", "beginner"))

        # Validate hours range
        hours = data.get("estimated_hours", 2)
        if not isinstance(hours, int) or hours < 1 or hours > 40:
            return False

        return True
    except (ValueError, TypeError):
        return False


def validate_course_module(data: Dict[str, Any]) -> bool:
    """Validate course module data against schema"""
    required_fields = ["title", "description", "domain"]
    try:
        for required_field in required_fields:
            if not data.get(required_field):
                return False

        # Validate enums
        Domain(data["domain"])
        DifficultyLevel(data.get("difficulty", "beginner"))

        # Validate hours range
        hours = data.get("estimated_hours", 3)
        if not isinstance(hours, int) or hours < 1 or hours > 30:
            return False

        return True
    except (ValueError, TypeError):
        return False


# Domain content guidelines for generation
STEM_DOMAIN_GUIDELINES = {
    Domain.CS: {
        "name": "Computer Science",
        "areas": [
            "Programming",
            "Algorithms",
            "Data Structures",
            "Software Engineering",
            "AI/ML",
            "Systems",
        ],
        "typical_concepts": [
            "Variables",
            "Functions",
            "Loops",
            "Recursion",
            "Objects",
            "Databases",
        ],
        "math_foundation": ["Discrete Math", "Logic", "Statistics", "Linear Algebra"],
    },
    Domain.MATH: {
        "name": "Mathematics",
        "areas": [
            "Calculus",
            "Algebra",
            "Statistics",
            "Discrete Math",
            "Applied Math",
            "Analysis",
        ],
        "typical_concepts": [
            "Functions",
            "Derivatives",
            "Integrals",
            "Probability",
            "Matrices",
            "Proofs",
        ],
        "applications": ["Engineering", "Physics", "Computer Science", "Economics"],
    },
    Domain.PHYSICS: {
        "name": "Physics",
        "areas": [
            "Classical Mechanics",
            "Electromagnetism",
            "Thermodynamics",
            "Quantum",
            "Optics",
        ],
        "typical_concepts": [
            "Force",
            "Energy",
            "Wave",
            "Field",
            "Particle",
            "Conservation Laws",
        ],
        "math_foundation": [
            "Calculus",
            "Vectors",
            "Differential Equations",
            "Linear Algebra",
        ],
    },
    Domain.ENGINEERING: {
        "name": "Engineering",
        "areas": [
            "System Design",
            "Optimization",
            "Modeling",
            "Analysis",
            "Problem Solving",
        ],
        "typical_concepts": [
            "Design Process",
            "Constraints",
            "Trade-offs",
            "Testing",
            "Iteration",
        ],
        "math_foundation": [
            "Calculus",
            "Statistics",
            "Linear Algebra",
            "Differential Equations",
        ],
    },
}
