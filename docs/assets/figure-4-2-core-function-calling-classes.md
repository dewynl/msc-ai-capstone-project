# Figure 4.2: Core Function Calling Architecture Classes

```mermaid
classDiagram
    class T5FunctionCallGenerator {
        +model: T5ForConditionalGeneration
        +tokenizer: T5Tokenizer
        +generate_function_calls(requirements)
    }

    class FunctionCallParser {
        +parse_t5_output(t5_output)
        -_extract_field(text, field_name)
        -_extract_objectives(text)
        -_extract_modules(text)
        -_convert_to_function_calls(t5_output)
        -_create_fallback_calls(t5_output)
    }

    class SyllabusBuilder {
        +course_info: Dict
        +learning_objectives: List
        +modules: List
        +activities: List
        +assessments: List
        +set_info(title, domain, level, duration, description)
        +add_objective(objective)
        +add_module(title, estimated_hours, description, key_concepts)
        +add_activity(title, bloom_level, estimated_hours, description)
        +add_assessment(title, assessment_type, estimated_hours, description)
        +build() Dict
        +to_json() str
    }

    class FunctionCallSyllabusGenerator {
        +t5_generator: T5FunctionCallGenerator
        +parser: FunctionCallParser
        +generate_syllabus(requirements)
    }

    class RAGIntegratedSyllabusBuilder {
        +rag_pipeline: ComponentRetrievalPipeline
        +add_module_by_query(query, estimated_hours)
        +add_activity_by_query(query, bloom_level, estimated_hours)
        +add_assessment_by_query(query, assessment_type, estimated_hours)
    }

    class RAGIntegratedGenerator {
        +rag_pipeline: ComponentRetrievalPipeline
        +generate_syllabus_with_ids(requirements)
    }

    class ComponentRetrievalPipeline {
        +vector_store: SyllabusComponentStore
        +retrieve_components(requirements, k_per_type)
    }

    class SyllabusComponentStore {
        +collection: ChromaDB
        +encoder: SentenceTransformer
        +search_similar(query, k)
    }

    %% Relationships
    FunctionCallSyllabusGenerator --> T5FunctionCallGenerator : uses
    FunctionCallSyllabusGenerator --> FunctionCallParser : uses
    RAGIntegratedSyllabusBuilder --|> SyllabusBuilder : extends
    RAGIntegratedSyllabusBuilder --> ComponentRetrievalPipeline : queries
    RAGIntegratedGenerator --> RAGIntegratedSyllabusBuilder : creates
    RAGIntegratedGenerator --> ComponentRetrievalPipeline : uses
    ComponentRetrievalPipeline --> SyllabusComponentStore : queries

    %% Class styling
    class T5FunctionCallGenerator,FunctionCallSyllabusGenerator {
        fill:#e3f2fd
        stroke:#1976d2
    }
    class FunctionCallParser {
        fill:#fff3e0
        stroke:#f57c00
    }
    class SyllabusBuilder,RAGIntegratedSyllabusBuilder {
        fill:#f3e5f5
        stroke:#7b1fa2
    }
    class RAGIntegratedGenerator,ComponentRetrievalPipeline,SyllabusComponentStore {
        fill:#e8f5e9
        stroke:#388e3c
    }
```

## Description

This class diagram shows the **actual** core architecture components as implemented:

### **T5 Generation Layer:**
- **T5FunctionCallGenerator**: Loads T5 model and generates text output from requirements
- **FunctionCallParser**: Intelligent parser that extracts information from any T5 output format and constructs valid function calls

### **Builder Layer:**
- **SyllabusBuilder**: Core builder with methods to construct syllabus (set_info, add_objective, add_module, add_activity, add_assessment, build)
- **RAGIntegratedSyllabusBuilder**: Extends SyllabusBuilder to add RAG-enhanced methods (add_module_by_query, etc.)

### **Orchestration Layer:**
- **FunctionCallSyllabusGenerator**: Combines T5 generation + parsing to produce syllabi
- **RAGIntegratedGenerator**: High-level interface that creates RAGIntegratedSyllabusBuilder instances

### **RAG Layer:**
- **ComponentRetrievalPipeline**: Manages vector database queries for component retrieval
- **SyllabusComponentStore**: ChromaDB interface with SentenceTransformer embeddings

### **Key Architecture Points:**
- Parser is format-agnostic - handles any T5 output
- SyllabusBuilder has simple, clear methods (no validation methods shown because they don't exist)
- RAG is integrated through inheritance (RAGIntegratedSyllabusBuilder extends SyllabusBuilder)
- Functions query RAG during execution, not as a separate step
