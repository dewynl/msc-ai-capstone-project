# Figure 4.5: RAG-Integrated Output with Component IDs

```mermaid
graph TD
    subgraph "Generated Syllabus Structure"
        A["📚 Course Info<br/>{title, domain, level, description}"]
        B["🎯 Learning Objectives<br/>[{text, bloom_level}]"]
        C["📖 Modules with IDs<br/>[{id: 'mod_abc123', title, description, key_concepts}]"]
        D["⚡ Activities with IDs<br/>[{id: 'act_def456', title, description, bloom_level}]"]
        E["📋 Assessments with IDs<br/>[{id: 'ass_ghi789', title, type, description}]"]
        F["📊 Metadata<br/>{generated_by, total_components, rag_count}"]
    end

    subgraph "Database References"
        G["🔗 Component IDs<br/>{module_ids: ['mod_abc123', 'mod_def456'],<br/>activity_ids: ['act_ghi789'],<br/>assessment_ids: ['ass_jkl012']}"]
    end

    subgraph "Component Details"
        H["Module: mod_abc123<br/>✅ Database Record<br/>✅ Reusable Across Syllabi<br/>✅ Live Content Updates"]
        I["Activity: act_def456<br/>✅ Database Record<br/>✅ Detailed Instructions<br/>✅ Bloom's Taxonomy Aligned"]
        J["Assessment: ass_ghi789<br/>✅ Database Record<br/>✅ Professional Quality<br/>✅ Standards Compliant"]
    end

    subgraph "Frontend Integration"
        K[Component Detail Pages]
        L[Syllabus Editor Interface]
        M[Component Substitution]
        N[Live Content Updates]
    end

    subgraph "Database Operations"
        O["CREATE syllabus_components<br/>(syllabus_id, component_id, type)"]
        P["SELECT * FROM components<br/>WHERE id IN (component_ids)"]
        Q["UPDATE component content<br/>→ Auto-updates all syllabi"]
    end

    %% Connections
    C --> H
    D --> I
    E --> J
    G --> K
    G --> L
    G --> M
    H --> N
    I --> N
    J --> N

    G --> O
    G --> P
    H --> Q
    I --> Q
    J --> Q

    %% Example JSON structure
    subgraph "Example JSON Output"
        R["```json<br/>{<br/>  'course_info': {<br/>    'title': 'Machine Learning Fundamentals',<br/>    'domain': 'computer_science',<br/>    'level': 'intermediate'<br/>  },<br/>  'modules': [<br/>    {<br/>      'id': '870b584d-b080-4132-9a2e-2ad1b00d0f43',<br/>      'title': 'Feature Engineering',<br/>      'description': '...',<br/>      'source': 'rag_retrieved'<br/>    }<br/>  ],<br/>  'database_references': {<br/>    'module_ids': ['870b584d-b080-4132-9a2e-2ad1b00d0f43'],<br/>    'activity_ids': ['27e3f58d-e2d5-4593-bfc3-7859d0ab092e']<br/>  },<br/>  'metadata': {<br/>    'rag_retrieved_components': 5,<br/>    'generated_components': 0<br/>  }<br/>}```"]
    end

    %% Source tracking
    subgraph "Source Attribution"
        S["🔗 RAG Retrieved<br/>Components with database IDs<br/>Reusable across syllabi"]
        T["✨ Generated<br/>Content without IDs<br/>Unique to this syllabus"]
    end

    C --> S
    D --> S
    E --> S
    B --> T

    style A fill:#e3f2fd
    style C fill:#e8f5e8
    style D fill:#e8f5e8
    style E fill:#e8f5e8
    style G fill:#fff3e0
    style R fill:#f3e5f5
```

## Description

This diagram illustrates the complete output structure with RAG integration and component IDs:

### **Key Output Components:**

1. **Course Info**: Basic course metadata (title, domain, level, description)
2. **Learning Objectives**: T5-generated educational objectives with Bloom's taxonomy levels
3. **Modules**: Retrieved components with actual database IDs for reusability
4. **Activities**: Educational activities with database references and difficulty levels
5. **Assessments**: Professional-quality assessments with database integration
6. **Metadata**: Generation statistics and component source tracking

### **Database Integration Features:**

- **Component IDs**: Actual UUIDs linking to database records
- **Database References**: Organized arrays of IDs for easy frontend integration
- **Source Tracking**: Clear distinction between RAG-retrieved and generated content
- **Reusability**: Components can be shared across multiple syllabi

### **Frontend Benefits:**

- **Component Detail Pages**: Direct links to detailed component information
- **Live Updates**: Component changes automatically reflect in all syllabi
- **Component Substitution**: Easy replacement of components with alternatives
- **Analytics**: Track component usage and popularity

### **Production Readiness:**

- **100% Valid JSON**: Guaranteed parseable output structure
- **Database Integration**: Ready for immediate database linking
- **Standards Compliance**: Educational quality validation throughout
- **Component Relationships**: Maintains database referential integrity

This output format enables sophisticated educational content management with component reusability, live updates, and comprehensive database integration.