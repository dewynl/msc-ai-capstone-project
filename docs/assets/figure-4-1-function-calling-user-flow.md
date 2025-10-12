# Figure 4.1: Function Calling User Experience Flow

```mermaid
graph TD
    A[User Input:<br/>Course Requirements] --> B[T5 Model:<br/>Generate Text Output]
    B --> C[Intelligent Parser:<br/>Extract Information]
    C --> D[Construct Valid<br/>Function Calls]
    D --> E[Execute Functions]
    E --> F[Build JSON Structure]
    F --> G[Complete Syllabus]

    %% RAG is embedded in function execution
    E -.->|"Functions query RAG<br/>during execution"| RAG[RAG Component<br/>Retrieval]
    RAG -.->|"Retrieved components"| E

    %% User interaction path
    A -.->|"Title, Domain, Level"| B

    %% T5 output (flexible format)
    B -.->|"May be functions,<br/>JSON, or mixed"| C

    %% Parser extracts info
    C -.->|"Extract fields<br/>using regex patterns"| D

    %% Final output
    F -.->|"100% Valid JSON"| G

    style A fill:#e1f5fe
    style B fill:#fff3e0
    style C fill:#ffe0b2
    style D fill:#ffe0b2
    style E fill:#f3e5f5
    style RAG fill:#fff3e0
    style F fill:#e8f5e8
    style G fill:#fff9c4
```

## Description

This diagram illustrates the complete user experience flow for the function calling architecture:

1. **User Input**: Simple course requirements (title, domain, level)
2. **T5 Generation**: Model generates text (may be function calls, JSON-like, or mixed format)
3. **Intelligent Parser**: Extracts information using regex patterns (handles any T5 output format)
4. **Function Construction**: Builds valid function calls from extracted information
5. **Function Execution**: SyllabusBuilder executes guaranteed-valid function calls (RAG queries during execution)
6. **Build JSON**: Assembles final JSON structure from executed functions
7. **Output**: Guaranteed valid JSON syllabus

**Key Innovation**: Parser is format-agnostic - T5 can output ANY format (functions, JSON, text) and parser extracts the information and constructs valid function calls. This separates semantic generation (T5's strength) from structural precision (programmatic construction).