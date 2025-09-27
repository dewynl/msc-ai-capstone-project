# Figure 4.2: Core Function Calling Architecture Classes

```mermaid
classDiagram
    class FunctionCallSyllabusGenerator {
        +model: T5ForConditionalGeneration
        +tokenizer: T5Tokenizer
        +parser: FunctionCallParser
        +generate_syllabus(requirements)
        -preprocess_requirements(requirements)
        -postprocess_output(generated_text)
    }

    class FunctionCallParser {
        +parse_with_recovery(generated_text)
        -parse_clean_functions(text)
        -apply_repair_heuristics(text)
        -parse_partial_functions(text)
        +validate_function_syntax(func_call)
    }

    class SyllabusBuilder {
        +syllabus: Dict
        +create_course(title, domain, level)
        +add_objective(objective, bloom_level)
        +add_module(title, description, hours)
        +add_activity(title, description, bloom_level)
        +add_assessment(title, type, hours)
        +to_json() Dict
        -validate_educational_coherence()
        -apply_pedagogical_defaults()
    }

    class RAGIntegratedGenerator {
        +rag_pipeline: ComponentRetrievalPipeline
        +function_generator: FunctionCallSyllabusGenerator
        +generate_syllabus_with_ids(requirements)
        -retrieve_components(requirements)
        -integrate_component_ids(syllabus, components)
    }

    class ComponentRetrievalPipeline {
        +vector_store: SyllabusComponentStore
        +retrieve_components(requirements, k_per_type)
        -query_modules(query_text)
        -query_activities(query_text)
        -query_assessments(query_text)
    }

    class SyllabusComponentStore {
        +collection: ChromaDB
        +encoder: SentenceTransformer
        +add_component(component_data)
        +search_similar(query, k)
        +get_component_by_id(component_id)
    }

    %% Relationships
    FunctionCallSyllabusGenerator --> FunctionCallParser
    FunctionCallSyllabusGenerator --> SyllabusBuilder
    RAGIntegratedGenerator --> FunctionCallSyllabusGenerator
    RAGIntegratedGenerator --> ComponentRetrievalPipeline
    ComponentRetrievalPipeline --> SyllabusComponentStore

    %% Data flow annotations
    FunctionCallSyllabusGenerator -.->|"Function Calls"| FunctionCallParser
    FunctionCallParser -.->|"Parsed Functions"| SyllabusBuilder
    SyllabusBuilder -.->|"Valid JSON"| FunctionCallSyllabusGenerator
    ComponentRetrievalPipeline -.->|"Components + IDs"| RAGIntegratedGenerator

    %% Class styling
    class FunctionCallSyllabusGenerator,SyllabusBuilder,RAGIntegratedGenerator {
        fill:#e3f2fd
        stroke:#1976d2
    }
    class FunctionCallParser {
        fill:#fff3e0
        stroke:#f57c00
    }
    class ComponentRetrievalPipeline,SyllabusComponentStore {
        fill:#f3e5f5
        stroke:#7b1fa2
    }
```

## Description

This class diagram shows the core architecture components of the function calling system:

### **Primary Components:**

- **FunctionCallSyllabusGenerator**: Main orchestrator that coordinates T5 model, parsing, and syllabus building
- **SyllabusBuilder**: Execution engine that validates and executes function calls to construct valid JSON
- **FunctionCallParser**: Sophisticated parser with error recovery for processing T5-generated function calls

### **RAG Integration:**

- **RAGIntegratedGenerator**: Combines function calling with component retrieval for database-ready output
- **ComponentRetrievalPipeline**: Manages semantic search and component filtering
- **SyllabusComponentStore**: Vector database interface for educational component storage and retrieval

### **Key Innovation:**

The architecture separates concerns effectively:
- **T5 Model**: Semantic educational content generation
- **Parser**: Syntax recovery and validation
- **Builder**: Educational validation and JSON construction
- **RAG**: Component retrieval with database IDs