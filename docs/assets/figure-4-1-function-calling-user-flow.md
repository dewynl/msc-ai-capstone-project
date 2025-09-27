# Figure 4.1: Function Calling User Experience Flow

```mermaid
graph TD
    A[User Input:<br/>Course Requirements] --> B[T5 Model:<br/>Generate Function Calls]
    B --> C{Function Call<br/>Parsing}
    C -->|Success| D[SyllabusBuilder:<br/>Execute Functions]
    C -->|Syntax Error| E[Error Recovery:<br/>Repair & Retry]
    E --> D
    D --> F[RAG Integration:<br/>Retrieve Components]
    F --> G[Component Assembly:<br/>Add Database IDs]
    G --> H[Validation:<br/>Educational Standards]
    H --> I[Final JSON Output:<br/>Complete Syllabus]

    %% User interaction path
    A -.->|"title: 'ML Course'<br/>domain: 'computer_science'<br/>level: 'intermediate'"| B

    %% Function call examples
    B -.->|"create_course('ML Course', 'CS', 'intermediate')<br/>add_objective('Understand algorithms')<br/>add_module('Linear Regression', ...)"| C

    %% Error recovery examples
    E -.->|"Fix missing quotes<br/>Repair malformed parameters<br/>Apply intelligent defaults"| D

    %% Component integration
    F -.->|"Module IDs: [mod_123, mod_456]<br/>Activity IDs: [act_789]<br/>Assessment IDs: [ass_321]"| G

    %% Final output
    I -.->|"100% Valid JSON<br/>Database-Ready<br/>Component IDs Included"| J[Frontend Ready]

    style A fill:#e1f5fe
    style B fill:#fff3e0
    style D fill:#f3e5f5
    style I fill:#e8f5e8
    style J fill:#fff9c4
```

## Description

This diagram illustrates the complete user experience flow for the function calling architecture:

1. **User Input**: Simple course requirements (title, domain, level)
2. **T5 Generation**: Model generates educational function calls instead of JSON
3. **Parsing & Recovery**: Sophisticated error handling with intelligent repair
4. **Function Execution**: SyllabusBuilder executes validated function calls
5. **RAG Integration**: Retrieves relevant educational components with database IDs
6. **Component Assembly**: Integrates components maintaining database relationships
7. **Validation**: Applies educational standards and coherence checking
8. **Output**: Guaranteed valid JSON ready for frontend consumption

**Key Innovation**: Separates semantic generation (T5's strength) from structural precision (programmatic construction).