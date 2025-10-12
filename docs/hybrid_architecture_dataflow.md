# Hybrid T5 + RAG + Template Architecture Data Flow

## Overview

The hybrid approach combines the strengths of all three methods:
- **T5 Model**: Generates intelligent, contextual educational content
- **RAG System**: Retrieves relevant educational components from vector store
- **Template System**: Ensures reliable JSON structure and field completeness

## Data Flow Diagram

```
INPUT: Course Requirements
├── title: "Introduction to Machine Learning"
├── domain: "computer_science"
├── level: "intermediate"
└── description: "Fundamentals of ML algorithms"

                    ↓
            ┌─────────────────┐
            │   DISPATCHER    │
            │   (Orchestrator)│
            └─────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
┌──────────────┐ ┌──────────┐ ┌─────────────┐
│ T5 CONTENT   │ │   RAG    │ │  TEMPLATE   │
│ GENERATOR    │ │ RETRIEVAL│ │ STRUCTURE   │
└──────────────┘ └──────────┘ └─────────────┘
        │           │           │
        ▼           ▼           ▼
┌──────────────┐ ┌──────────┐ ┌─────────────┐
│ Generated    │ │Retrieved │ │ JSON Schema │
│ Content      │ │Components│ │ Template    │
└──────────────┘ └──────────┘ └─────────────┘
        │           │           │
        └───────────┼───────────┘
                    ▼
            ┌─────────────────┐
            │    ASSEMBLER    │
            │  (JSON Builder) │
            └─────────────────┘
                    ▼
            Final Valid JSON Syllabus
```

## Detailed Component Flow

### 1. T5 Content Generation Path

```python
INPUT: Course Requirements
    ↓
T5 Content Generator
    ├── Generate Learning Objectives
    │   INPUT: "generate objectives for: Machine Learning, intermediate"
    │   OUTPUT: ["Master supervised learning algorithms", "Implement neural networks", ...]
    │
    ├── Generate Prerequisites
    │   INPUT: "generate prerequisites for: Machine Learning, computer_science"
    │   OUTPUT: "Linear algebra, Python programming, statistics"
    │
    ├── Generate Target Audience
    │   INPUT: "generate audience for: intermediate computer_science"
    │   OUTPUT: "Upper-level undergraduates with programming experience"
    │
    └── Generate Course Policies
        INPUT: "generate policies for: semester course, intermediate"
        OUTPUT: "Attendance required, late assignments penalized 10% per day"
```

### 2. RAG Component Retrieval Path

```python
INPUT: Course Requirements
    ↓
Query Processor
    ├── Extract search terms: ["machine", "learning", "computer_science", "intermediate"]
    ├── Generate component queries:
    │   ├── modules: "machine learning algorithms"
    │   ├── activities: "machine learning programming"
    │   └── assessments: "machine learning evaluation"
    ↓
Vector Store Search
    ├── Search modules collection → 6 relevant modules
    ├── Search activities collection → 8 relevant activities
    └── Search assessments collection → 4 relevant assessments
    ↓
Component Filtering & Selection
    ├── Filter by domain compatibility
    ├── Filter by difficulty level
    ├── Select diverse components
    └── OUTPUT: {modules: [3], activities: [5], assessments: [3]}
```

### 3. Template Structure Path

```python
INPUT: Requirements + T5 Content + RAG Components
    ↓
JSON Template Builder
    ├── course_info: {
    │   ├── title: requirements.title
    │   ├── domain: requirements.domain
    │   ├── level: requirements.level
    │   ├── description: requirements.description
    │   └── target_audience: t5_generated.target_audience
    │   }
    │
    ├── learning_objectives: t5_generated.objectives[:4]
    │
    ├── prerequisites: t5_generated.prerequisites
    │
    ├── modules: [
    │   │   for module in rag_components.modules:
    │   │       ├── title: module.title
    │   │       ├── description: enhance_with_t5(module.description)
    │   │       ├── key_concepts: module.key_concepts
    │   │       └── estimated_hours: module.estimated_hours
    │   ]
    │
    ├── activities: [
    │   │   for activity in rag_components.activities:
    │   │       ├── title: activity.title
    │   │       ├── description: activity.description
    │   │       ├── bloom_level: activity.bloom_level
    │   │       └── estimated_hours: activity.estimated_hours
    │   ]
    │
    └── assessments: [
        │   for assessment in rag_components.assessments:
        │       ├── title: assessment.title
        │       ├── type: assessment.assessment_type
        │       ├── description: enhance_with_t5(assessment.description)
        │       └── estimated_hours: assessment.estimated_hours
        ]
```

## Component Responsibilities

| Component | Input | Processing | Output |
|-----------|-------|------------|---------|
| **T5 Generator** | Course requirements | Text generation for educational content | Learning objectives, prerequisites, policies |
| **RAG System** | Course requirements | Semantic search + filtering | Relevant educational components |
| **Template Builder** | Requirements + T5 content + RAG components | Structured JSON assembly | Valid JSON syllabus |

## Data Processing Pipeline

### Phase 1: Parallel Content Generation
```
Course Requirements
    ├── → T5 Content Generator (async)
    └── → RAG Component Retriever (async)
```

### Phase 2: Content Enhancement
```
T5 Content + RAG Components
    ↓
Content Enhancer
    ├── Enhance module descriptions with T5
    ├── Generate assessment rubrics with T5
    └── Create activity instructions with T5
```

### Phase 3: Structured Assembly
```
Enhanced Content
    ↓
Template Assembler
    ├── Apply JSON schema validation
    ├── Ensure field completeness
    ├── Format data types correctly
    └── Generate final syllabus
```

## Advantages of Hybrid Approach

1. **Content Quality**: T5 generates contextually appropriate educational content
2. **Component Diversity**: RAG provides real educational components across domains
3. **Structural Reliability**: Template ensures valid JSON and complete fields
4. **Scalability**: Each component can be optimized independently
5. **Flexibility**: Can adjust the balance between generated vs retrieved content

## Implementation Strategy

### Current Status
- ✅ RAG System: Fully operational
- ✅ Template System: Fully operational
- ✅ T5 Model: Trained but JSON output unreliable

### Hybrid Implementation
- Use T5 for specific content generation tasks (objectives, prerequisites)
- Use RAG for educational component retrieval
- Use Template for reliable JSON structure
- Parse T5 output with regex/NLP instead of JSON parsing

This hybrid approach leverages the strengths of each method while avoiding their individual weaknesses.