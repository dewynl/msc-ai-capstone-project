# Educational Syllabus Generation Data Model - Visual Diagrams

## Overview
This document provides visual representations of the data model using Mermaid diagrams.

## 1. Template-Based User Experience Flow

```mermaid
flowchart TB
    Start[🚀 User starts syllabus creation]

    subgraph TemplateSelection["📋 Template Selection"]
        Choice{I want to create a...}
        Choice --> Uni[📚 University Course]
        Choice --> Corp[🏢 Corporate Training]
        Choice --> Prof[🛠️ Professional Workshop]
        Choice --> Cert[📜 Certification Prep]
    end

    subgraph UniForm["🎓 University Template"]
        U1[Subject Area<br/>CS, Math, Biology...]
        U2[Academic Level<br/>Freshman, Graduate...]
        U3[Term Format<br/>Semester, Quarter...]
        U4[Course Type<br/>Core, Elective...]
    end

    subgraph CorpForm["💼 Corporate Template"]
        C1[Business Skill<br/>Leadership, Excel, Communication...]
        C2[Employee Level<br/>New hire, Manager, Executive...]
        C3[Training Format<br/>Half-day, Workshop series...]
        C4[Business Goal<br/>Efficiency, Compliance, Skills...]
    end

    subgraph ProfForm["🔧 Professional Template"]
        P1[Skill Domain<br/>Design, Development, Management...]
        P2[Experience Level<br/>Beginner, Practitioner, Expert...]
        P3[Workshop Format<br/>1-day, Multi-day, Bootcamp...]
        P4[Outcome Type<br/>Certification, Portfolio, Skills...]
    end

    subgraph CertForm["🎯 Certification Template"]
        E1[Certification Body<br/>AWS, PMP, Google...]
        E2[Current Level<br/>No experience, Some knowledge...]
        E3[Study Timeline<br/>4 weeks, 3 months, 6 months...]
        E4[Exam Focus<br/>Practical, Theoretical, Mixed...]
    end

    subgraph NeuralProcessing["🧠 Neural Architecture Processing"]
        ContextClassification[Template context classification]
        StandardsCompliance[Standards compliance validation]
        ContentGeneration[Context-aware content generation]
    end

    subgraph StandardizedOutput["📄 Generated Syllabus"]
        StandardFormat[IEEE LOM compliant structure]
        ContextAdapted[Context-appropriate content]
        QualityValidated[Standards validated output]
    end

    Start --> TemplateSelection
    Uni --> UniForm
    Corp --> CorpForm
    Prof --> ProfForm
    Cert --> CertForm

    UniForm --> NeuralProcessing
    CorpForm --> NeuralProcessing
    ProfForm --> NeuralProcessing
    CertForm --> NeuralProcessing

    NeuralProcessing --> StandardizedOutput

    style TemplateSelection fill:#e3f2fd
    style UniForm fill:#f3e5f5
    style CorpForm fill:#e8f5e8
    style ProfForm fill:#fff3e0
    style CertForm fill:#fce4ec
    style NeuralProcessing fill:#f1f8e9
    style StandardizedOutput fill:#c8e6c9
```

### Template Examples:

**University Template (4 clicks):**
1. "📚 University Course" → 2. "Computer Science" → 3. "Undergraduate" → 4. "Machine Learning"

**Corporate Template (4 clicks):**
1. "🏢 Corporate Training" → 2. "Technical Skills" → 3. "Intermediate Level" → 4. "Data Analysis with Excel"

**Result: Complete syllabus generated from minimal, context-appropriate inputs!**

## 2. Template-Specific Input Models

### 2a. Core Template Classes

```mermaid
classDiagram
    class TemplateBase {
        <<abstract>>
        +str identifier
        +TemplateType template_type
        +validate()
        +to_standard_format()
    }

    class UniversityTemplate {
        +SubjectArea subject_area
        +AcademicLevel academic_level
        +TermFormat term_format
        +CourseType course_type
        +Optional~int~ credit_hours
        +List~str~ prerequisites
    }

    class CorporateTemplate {
        +BusinessSkill business_skill
        +EmployeeLevel employee_level
        +TrainingFormat training_format
        +BusinessGoal business_goal
        +DepartmentType department
        +Optional~str~ industry_context
    }

    class ProfessionalTemplate {
        +SkillDomain skill_domain
        +ExperienceLevel experience_level
        +WorkshopFormat workshop_format
        +OutcomeType outcome_type
        +Optional~CertificationBody~ cert_prep
        +Optional~str~ portfolio_focus
    }

    class CertificationTemplate {
        +CertificationBody cert_body
        +CurrentLevel current_level
        +StudyTimeline study_timeline
        +ExamFocus exam_focus
        +Optional~str~ prior_attempts
        +Optional~List~str~~ weak_areas
    }

    class StandardizedInput {
        +General general
        +Educational educational
        +List~LearningObjective~ learning_objectives
        +DeliveryContext delivery_context
        +TargetAudience target_audience
    }

    class General {
        +str identifier
        +str title
        +str language
        +str description
        +List~str~ keywords
        +str coverage
    }

    class Educational {
        +str interactivity_type
        +List~str~ learning_resource_type
        +str interactivity_level
        +str semantic_density
        +List~str~ intended_end_user_role
        +str context
        +str typical_age_range
        +str difficulty
        +str typical_learning_time
    }

    class LearningObjective {
        +str objective
        +BloomLevel bloom_level
        +KnowledgeDimension knowledge_dimension
    }

    class DeliveryContext {
        +OrganizationType organization_type
        +DeliveryMode delivery_mode
        +Duration duration
        +List~str~ constraints
    }

    class TargetAudience {
        +List~str~ prerequisite_competencies
        +List~str~ entry_skills
        +Optional~List~str~~ professional_context
        +Optional~str~ academic_level
    }


    TemplateBase <|-- UniversityTemplate
    TemplateBase <|-- CorporateTemplate
    TemplateBase <|-- ProfessionalTemplate
    TemplateBase <|-- CertificationTemplate

    UniversityTemplate --> StandardizedInput : converts to
    CorporateTemplate --> StandardizedInput : converts to
    ProfessionalTemplate --> StandardizedInput : converts to
    CertificationTemplate --> StandardizedInput : converts to

    StandardizedInput *-- General
    StandardizedInput *-- Educational
    StandardizedInput *-- "1..*" LearningObjective
    StandardizedInput *-- DeliveryContext
    StandardizedInput *-- TargetAudience
```

### 2b. Supporting Data Types

```mermaid
classDiagram
    class Duration {
        +int weeks
        +int hours_per_week
        +int total_hours
    }

    class TemplateType {
        <<enumeration>>
        UNIVERSITY
        CORPORATE
        PROFESSIONAL
        CERTIFICATION
    }

    class BloomLevel {
        <<enumeration>>
        REMEMBER
        UNDERSTAND
        APPLY
        ANALYZE
        EVALUATE
        CREATE
    }

    class KnowledgeDimension {
        <<enumeration>>
        FACTUAL
        CONCEPTUAL
        PROCEDURAL
        METACOGNITIVE
    }

    class OrganizationType {
        <<enumeration>>
        UNIVERSITY
        CORPORATE
        TRAINING_INSTITUTE
        CERTIFICATION_PROVIDER
        ONLINE_PLATFORM
    }

    class DeliveryMode {
        <<enumeration>>
        IN_PERSON
        ONLINE
        HYBRID
        SELF_PACED
        INSTRUCTOR_LED
    }
```

### 2c. Template-Specific Enumerations

```mermaid
classDiagram
    class SubjectArea {
        <<enumeration>>
        COMPUTER_SCIENCE
        MATHEMATICS
        BIOLOGY
        PHYSICS
        CHEMISTRY
        ENGINEERING
        BUSINESS
        HUMANITIES
        SOCIAL_SCIENCES
        ARTS
    }

    class AcademicLevel {
        <<enumeration>>
        FRESHMAN
        SOPHOMORE
        JUNIOR
        SENIOR
        GRADUATE
        DOCTORAL
    }

    class BusinessSkill {
        <<enumeration>>
        LEADERSHIP
        COMMUNICATION
        PROJECT_MANAGEMENT
        DATA_ANALYSIS
        EXCEL
        PRESENTATION
        NEGOTIATION
        TECHNICAL_WRITING
    }

    class EmployeeLevel {
        <<enumeration>>
        NEW_HIRE
        JUNIOR
        INTERMEDIATE
        SENIOR
        MANAGER
        EXECUTIVE
    }

    class CertificationBody {
        <<enumeration>>
        AWS
        MICROSOFT
        GOOGLE
        PMP
        CISCO
        COMPTIA
        ADOBE
        SALESFORCE
    }
```

## 3. Context-Specific Processing Rules

```mermaid
flowchart TD
    subgraph Templates["📝 Template Inputs"]
        Uni[University Template]
        Corp[Corporate Template]
        Prof[Professional Template]
        Cert[Certification Template]
    end

    subgraph NeuralComponents["🧠 Neural Architecture Components"]
        TemplateEncoder[Template-Context Encoder<br/>- Context classification<br/>- Template type identification<br/>- Input standardization]

        ComplianceController[Standards Compliance Controller<br/>- IEEE LOM validation<br/>- QTI 3.0 assessment format<br/>- WCAG accessibility checks]

        ContentGenerator[Context-Aware Content Generator<br/>- Template-specific generation<br/>- Educational content creation<br/>- Assessment design]
    end

    subgraph StandardOutput["📋 Standardized Internal Format"]
        IEEE[IEEE LOM Structure]
        QTI[QTI Assessment Format]
        Metadata[Rich Metadata]
    end

    Uni --> TemplateEncoder
    Corp --> TemplateEncoder
    Prof --> TemplateEncoder
    Cert --> TemplateEncoder

    TemplateEncoder --> ComplianceController
    ComplianceController --> ContentGenerator
    ContentGenerator --> StandardOutput

    style Templates fill:#e3f2fd
    style NeuralComponents fill:#f1f8e9
    style StandardOutput fill:#e8f5e8
```

## 4. Template-Based Input Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as Template UI
    participant Validator as Input Validator
    participant NeuralArch as Neural Architecture
    participant Generator as Syllabus Generator

    User->>UI: Select "🏢 Corporate Training"
    UI->>UI: Load corporate-specific form

    User->>UI: Complete form inputs
    Note over UI: - Training topic<br/>- Target audience<br/>- Duration<br/>- Learning objectives

    UI->>Validator: Validate template inputs
    Validator->>Validator: Check required fields
    Validator->>NeuralArch: Send validated template data

    NeuralArch->>NeuralArch: Context classification
    NeuralArch->>NeuralArch: Standards compliance processing
    NeuralArch->>Generator: Generate complete syllabus
    Generator-->>User: Return publication-ready syllabus
```

## 5. Original Input Data Model Structure
        +General general
        +Educational educational
        +List~LearningObjective~ learning_objectives
        +DeliveryContext delivery_context
        +TargetAudience target_audience
    }

    class General {
        +str identifier
        +str title
        +str language
        +str description
        +List~str~ keywords
        +str coverage
    }

    class Educational {
        +str interactivity_type
        +List~str~ learning_resource_type
        +str interactivity_level
        +str semantic_density
        +List~str~ intended_end_user_role
        +str context
        +str typical_age_range
        +str difficulty
        +str typical_learning_time
    }

    class LearningObjective {
        +str objective
        +BloomLevel bloom_level
        +KnowledgeDimension knowledge_dimension
    }

    class DeliveryContext {
        +OrganizationType organization_type
        +DeliveryMode delivery_mode
        +Duration duration
        +List~str~ constraints
    }

    class TargetAudience {
        +List~str~ prerequisite_competencies
        +List~str~ entry_skills
        +Optional~List~str~~ professional_context
        +Optional~str~ academic_level
    }

    EducationalProgramInput *-- General
    EducationalProgramInput *-- Educational
    EducationalProgramInput *-- "1..*" LearningObjective
    EducationalProgramInput *-- DeliveryContext
    EducationalProgramInput *-- TargetAudience
```

## 3. Output Data Model Structure

```mermaid
classDiagram
    class SyllabusOutput {
        +CourseInformation course_information
        +LearningDesign learning_design
        +List~ContentModule~ content_modules
        +AssessmentPlan assessment_plan
        +EducationalMetadata educational_metadata
        +ContextExtensions context_extensions
    }

    class CourseInformation {
        +str title
        +str identifier
        +str description
        +Optional~float~ credits
        +Duration duration
        +Optional~Schedule~ schedule
    }

    class LearningDesign {
        +List~LearningOutcome~ learning_outcomes
        +List~str~ prerequisite_knowledge
        +OrderedList~str~ learning_progression
    }

    class ContentModule {
        +str module_id
        +str title
        +Duration duration
        +List~str~ learning_objectives
        +List~Topic~ topics
        +List~Assessment~ assessments
    }

    class AssessmentPlan {
        +str assessment_strategy
        +List~Assessment~ assessments
        +GradingScheme grading_scheme
    }

    class EducationalMetadata {
        +Dict bloom_distribution
        +List~float~ cognitive_load_progression
        +AccessibilityCompliance accessibility_compliance
        +Interoperability interoperability
    }

    class AccessibilityCompliance {
        +WCAGLevel wcag_level
        +bool screen_reader_compatible
        +bool keyboard_navigation
        +bool color_contrast_compliant
        +bool alternative_text_provided
        +List~str~ accessibility_features
        +str compliance_notes
    }

    class WCAGLevel {
        <<enumeration>>
        A
        AA
        AAA
    }

    class Interoperability {
        +List~str~ supported_standards
        +bool scorm_compatible
        +bool xapi_compatible
        +bool qti_compatible
        +str export_formats
        +Dict metadata_mappings
    }

    class GradingScheme {
        +GradingType grading_type
        +List~GradeComponent~ grade_components
        +float passing_threshold
        +bool curved_grading
        +str grade_scale
        +Optional~str~ late_policy
        +Optional~str~ makeup_policy
    }

    class GradingType {
        <<enumeration>>
        POINTS_BASED
        PERCENTAGE_BASED
        LETTER_GRADES
        PASS_FAIL
        COMPETENCY_BASED
        WEIGHTED_CATEGORIES
    }

    class GradeComponent {
        +str component_name
        +float weight_percentage
        +int total_points
        +bool drop_lowest
        +str description
    }

    SyllabusOutput *-- CourseInformation
    SyllabusOutput *-- LearningDesign
    SyllabusOutput *-- "1..*" ContentModule
    SyllabusOutput *-- AssessmentPlan
    SyllabusOutput *-- EducationalMetadata
    SyllabusOutput *-- ContextExtensions
```

## 4. Learning Taxonomy Integration

```mermaid
graph TD
    subgraph "Bloom's Taxonomy (Cognitive)"
        BT[Learning Objectives]
        BT --> R[Remember]
        BT --> U[Understand]
        BT --> AP[Apply]
        BT --> AN[Analyze]
        BT --> E[Evaluate]
        BT --> C[Create]
    end

    subgraph "Knowledge Dimensions"
        KD[Knowledge Types]
        KD --> F[Factual]
        KD --> CO[Conceptual]
        KD --> P[Procedural]
        KD --> M[Metacognitive]
    end

    subgraph "Gagné's Learning Types"
        GL[Learning Outcomes]
        GL --> VI[Verbal Information]
        GL --> IS[Intellectual Skills]
        GL --> CS[Cognitive Strategies]
        GL --> MS[Motor Skills]
        GL --> AT[Attitudes]
    end

    R & F --> VI
    U & CO --> IS
    AP & P --> CS
    AN & M --> CS
    E & M --> AT
    C & M --> IS
```

## 5. Standards Compliance Flow

```mermaid
flowchart LR
    subgraph Standards["📋 Educational Standards"]
        IEEE[IEEE LOM<br/>Metadata Structure]
        QTI[IMS QTI 3.0<br/>Assessment Format]
        CEDS[CEDS<br/>Data Elements]
        DC[Dublin Core<br/>Discovery Metadata]
        WCAG[WCAG 2.1<br/>Accessibility]
        SCORM[SCORM/xAPI<br/>Tracking]
    end

    subgraph DataModel["🗄️ Our Data Model"]
        Input[Input Schema]
        Output[Output Schema]
        Meta[Metadata Layer]
    end

    IEEE --> Input
    IEEE --> Output
    QTI --> Output
    CEDS --> Input
    DC --> Meta
    WCAG --> Output
    SCORM --> Meta
```

## 6. Context-Specific Extensions

```mermaid
graph TB
    Base[Base Syllabus Model]

    Base --> Academic[Academic Extension]
    Academic --> AD[Department Info]
    Academic --> AP[Program Requirements]
    Academic --> AC[Academic Calendar]
    Academic --> CH[Contact Hours]

    Base --> Corporate[Corporate Extension]
    Corporate --> BO[Business Objectives]
    Corporate --> ROI[ROI Metrics]
    Corporate --> CF[Competency Framework]
    Corporate --> RA[Role Applications]

    Base --> Certification[Certification Extension]
    Certification --> CB[Certifying Body]
    Certification --> CEU[CE Units]
    Certification --> RR[Renewal Requirements]
    Certification --> IS[Industry Standards]
```

## 7. Assessment Model (QTI 3.0 Compliant)

```mermaid
classDiagram
    class Assessment {
        +str identifier
        +str title
        +str instructions
        +Optional~Duration~ time_limit
        +int attempts_allowed
        +FeedbackType feedback_type
        +bool adaptive
    }

    class AssessmentType {
        <<enumeration>>
        FORMATIVE
        SUMMATIVE
        DIAGNOSTIC
    }

    class AssessmentFormat {
        <<enumeration>>
        QUIZ
        ASSIGNMENT
        PROJECT
        EXAM
        PEER_REVIEW
    }

    class Rubric {
        +List~Criterion~ criteria
    }

    class Criterion {
        +str criterion
        +List~Level~ levels
    }

    class Level {
        +str level
        +float points
        +str description
    }

    Assessment --> AssessmentType
    Assessment --> AssessmentFormat
    Assessment *-- Rubric
    Rubric *-- "1..*" Criterion
    Criterion *-- "3..5" Level
```

## 8. Data Processing Pipeline

**Validation Approach**: The system uses rule-based validators that apply established educational standards (IEEE LOM, Bloom's taxonomy, QTI 3.0, WCAG 2.1) rather than learned quality patterns. This ensures transparency, educational defensibility, and alignment with federal requirements for accountable AI systems in education.

```mermaid
sequenceDiagram
    participant User
    participant Input as Input Validator (Rule-Based)
    participant AI as AI Model
    participant Standards as Standards Validator (Rule-Based)
    participant Output as Output Generator

    User->>Input: Provide course specifications
    Input->>Input: Apply IEEE LOM validation rules
    Input->>Input: Apply Bloom's taxonomy progression rules
    Input->>AI: Send validated input

    AI->>AI: Process with educational components
    AI->>AI: Generate syllabus content
    AI->>Standards: Send draft syllabus

    Standards->>Standards: Apply QTI 3.0 compliance rules
    Standards->>Standards: Apply WCAG 2.1 accessibility rules
    Standards->>Standards: Apply educational coherence rules
    Standards->>Output: Send validated content

    Output->>Output: Apply context extensions
    Output->>Output: Generate final format
    Output->>User: Return complete syllabus
```
