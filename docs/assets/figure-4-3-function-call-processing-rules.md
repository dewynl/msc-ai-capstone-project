# Figure 4.3: Intelligent Parser Architecture

```mermaid
graph TD
    A[T5 Generated Text<br/>Any Format] --> B[Intelligent Parser]

    B --> C{Format Check}
    C -->|Already Functions| D[Return As-Is]
    C -->|Other Format| E[Information Extraction]

    E --> F[Regex Pattern Matching]
    F --> G[Extract Course Fields]
    F --> H[Extract Objectives]
    F --> I[Extract Modules]

    G --> J[Construct Function Calls]
    H --> J
    I --> J

    J --> K{Extraction Success?}
    K -->|Yes| L[Valid Function Calls]
    K -->|No| M[Apply Fallback Template]

    M --> L
    D --> L

    L --> N[SyllabusBuilder Execution]
    N --> O[Build JSON Structure]
    O --> P[100% Valid Output]

    %% Annotations
    B -.->|"Handles: functions,<br/>JSON, mixed text"| E
    F -.->|"Educational defaults<br/>applied during construction"| J
    M -.->|"Basic template with<br/>reasonable defaults"| L

    style A fill:#fff3e0
    style B fill:#ffe0b2
    style E fill:#ffe0b2
    style J fill:#ffe0b2
    style L fill:#e8f5e8
    style P fill:#c8e6c9
```

## Description

This diagram shows the intelligent parser architecture that achieves 100% function call execution success:

### **Format-Agnostic Parsing**
- Parser accepts ANY T5 output format (function calls, JSON-like text, mixed content)
- No assumptions about T5's output structure
- Separates semantic generation (T5) from structural precision (parser)

### **Information Extraction**
- **Regex Pattern Matching**: Multiple patterns for each field to handle various formats
- **Field Extraction**: `_extract_field()` finds course title, domain, level, duration, description
- **List Extraction**: `_extract_objectives()` and `_extract_modules()` extract structured lists
- **Educational Defaults**: Applied during construction (Bloom's levels, hours estimates, assessment types)

### **Fallback Strategy**
- If extraction fails, parser uses basic template with reasonable defaults
- Ensures 100% execution success even with poor T5 output
- Maintains educational quality standards

### **Key Innovation**
Parser is **format-agnostic** - it extracts semantic information from ANY format and constructs valid Python function calls. This architecture allows T5 to focus on educational content generation without worrying about syntax perfection.