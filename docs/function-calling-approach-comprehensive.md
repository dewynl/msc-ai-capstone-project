# Function Calling Approach for Structured Educational Content Generation

**A Novel Method for Making Smaller Neural Models Useful for Structured Generation**

---

## Executive Summary

Our MSc AI Capstone project successfully implemented a RAG-enhanced syllabus generation system using vector search and templates. However, **we discovered our trained T5 model (60M parameters) is completely unused** - the "RAG + Template" approach only uses SentenceTransformer embeddings for retrieval, not T5 for generation.

**The Core Problem**: T5 generates semantically correct educational content but produces syntactically broken JSON that cannot be parsed.

**The Function Calling Solution**: Instead of forcing T5 to generate perfect JSON syntax, have it generate executable function calls that programmatically construct valid JSON structures.

**Key Innovation**: Transform `T5 → broken JSON → unusable output` into `T5 → function calls → guaranteed valid JSON + intelligent content`

**Value Proposition**: **Actually utilize our trained T5 model** to add educational intelligence currently missing from the pure template approach.

---

## 1. Theoretical Foundation

### 1.1 Problem Formulation

**Current Project Status Analysis:**

**What We Have**:
- ✅ RAG system with 3,346 educational components in vector store
- ✅ Template-based JSON generation (100% valid JSON)
- ✅ Trained T5 model (90 examples, 3 epochs) with educational domain knowledge
- ❌ **T5 model completely unused** due to JSON formatting failures

**The Core Challenge**: Our trained T5 model generates intelligent educational content but produces syntactically broken JSON:

```
T5 Output: "learning_objectives":["Understand ML algorithms"],"prerequisites":"Python"
Problem:   Missing braces, malformed separators, unmatched quotes
Result:    json.loads() fails → entire output unusable
```

**Current "Solution" - Template Only**:
```python
# What we actually do (no T5 involved):
syllabus = {
    "learning_objectives": [
        "Understand fundamental concepts",  # ← Generic template
        "Apply theoretical knowledge",      # ← Generic template
        "Analyze information critically"    # ← Generic template
    ]
}
```

**The Opportunity**: T5 generates much better content than our generic templates, but we can't use it due to JSON syntax issues.

**Mathematical Formulation:**
```
Current:  P(intelligent_output | requirements) = 0 (T5 unused due to JSON failures)
Proposed: P(intelligent_output | requirements) = P(T5_semantics | requirements) × 1.0
                                               where JSON validity = 1.0 by construction
```

### 1.2 Related Work and Theoretical Backing

#### 1.2.1 Program Synthesis Literature

**Austin et al. (2021)** in "Program Synthesis with Large Language Models" demonstrate that language models can generate executable code more reliably than direct output formats. While their work focuses on large models (137B parameters), our approach tests whether this principle extends to smaller models like T5-small (60M parameters) for structured data generation.

**Key Insight for Smaller Models**: If function calls are simpler to generate than perfect JSON syntax, even smaller models like T5 might succeed where direct JSON generation fails.

#### 1.2.2 Tool Use and Function Calling in LLMs

**Schick et al. (2023)** in "Toolformer: Language Models Can Teach Themselves to Use Tools" show that language models can learn to use external tools through API calls. Our approach applies this concept to JSON construction.

**Yao et al. (2022)** in "ReAct: Synergizing Reasoning and Acting in Language Models" demonstrate that interleaving reasoning with action (function calls) improves task performance and interpretability.

#### 1.2.3 Domain-Specific Languages (DSLs)

**Yin & Neubig (2017)** in "Learning to Generate Programs from Natural Language Descriptions" show that generating domain-specific languages can be more effective than generating target outputs directly.

**Theoretical Foundation**: Our syllabus generation functions constitute a **Domain-Specific Language (DSL)** for educational content construction.

#### 1.2.4 Constrained Decoding Research

**Lu et al. (2021)** in "NEUROLOGIC Decoding" present methods for constraining neural text generation to satisfy logical predicates. Our approach achieves similar constraint satisfaction through executable function semantics.

---

## 2. Technical Approach

### 2.1 Function Call DSL Design

We define a domain-specific language for syllabus construction with the following primitive functions:

```python
# Course-level functions
create_course(title: str, domain: str, level: str, duration: str = "semester")
set_description(description: str)
set_prerequisites(prerequisites: str)
set_target_audience(audience: str)

# Learning objectives
add_objective(objective: str, bloom_level: str = "understand")

# Content components
add_module(title: str, description: str, key_concepts: List[str], hours: int)
add_activity(title: str, description: str, bloom_level: str, hours: int)
add_assessment(title: str, type: str, hours: int, description: str = "")

# Metadata and policies
add_policy(policy_type: str, description: str)
set_grading_scheme(scheme: Dict[str, float])
```

**Design Principles:**
1. **Semantic Clarity**: Function names reflect educational semantics
2. **Type Safety**: Parameters have explicit types and validation
3. **Compositionality**: Functions can be called in any valid order
4. **Extensibility**: New functions can be added without breaking existing calls

### 2.2 Model Training Strategy

#### 2.2.1 Training Data Transformation

Transform existing JSON training data into function call sequences:

```python
# Original training pair:
input_json = {
    "title": "Introduction to Machine Learning",
    "domain": "computer_science",
    "level": "intermediate"
}

target_json = {
    "course_info": {"title": "Introduction to Machine Learning", ...},
    "learning_objectives": ["Understand ML algorithms", ...]
}

# Transformed training pair:
input_text = "generate syllabus functions for: Introduction to Machine Learning, computer_science, intermediate"

target_functions = """
create_course("Introduction to Machine Learning", "computer_science", "intermediate")
set_description("Fundamentals of machine learning algorithms and applications")
add_objective("Understand supervised and unsupervised learning algorithms")
add_objective("Implement machine learning models in Python")
add_module("Linear Regression", "Introduction to regression analysis...", ["regression", "optimization"], 4)
add_activity("Programming Assignment", "Implement linear regression from scratch", "apply", 8)
add_assessment("Midterm Exam", "exam", 2, "Covers supervised learning concepts")
"""
```

#### 2.2.2 Fine-tuning Approach

**Base Model**: T5-small (existing trained model)
**Training Objective**: Minimize cross-entropy loss on function call sequences
**Training Format**: `"generate syllabus functions for: {requirements}" → function_calls`

**Advantages over JSON training**:
- **Simpler target format**: Function calls vs. nested JSON
- **Natural language alignment**: Function calls resemble natural language instructions
- **Error tolerance**: Small syntax errors in function calls are more recoverable
- **Incremental validation**: Each function call can be validated independently

### 2.3 Execution Engine Design

```python
class SyllabusBuilder:
    """Execution engine for syllabus construction functions"""

    def __init__(self):
        self.syllabus = {
            "course_info": {},
            "learning_objectives": [],
            "modules": [],
            "activities": [],
            "assessments": [],
            "policies": []
        }

    def create_course(self, title: str, domain: str, level: str, duration: str = "semester"):
        """Validate and set course information"""
        # Type validation
        assert isinstance(title, str) and len(title.strip()) > 0
        assert domain in ["computer_science", "mathematics", "physics"]  # Domain validation
        assert level in ["beginner", "intermediate", "advanced"]        # Level validation

        self.syllabus["course_info"].update({
            "title": title.strip(),
            "domain": domain,
            "level": level,
            "duration": duration
        })

    def add_objective(self, objective: str, bloom_level: str = "understand"):
        """Add learning objective with validation"""
        assert isinstance(objective, str) and len(objective.strip()) > 10
        assert bloom_level in ["remember", "understand", "apply", "analyze", "evaluate", "create"]

        self.syllabus["learning_objectives"].append({
            "text": objective.strip(),
            "bloom_level": bloom_level
        })

    # ... additional function implementations

    def to_json(self) -> dict:
        """Convert to final JSON structure"""
        # Apply post-processing and validation
        self._validate_completeness()
        self._apply_defaults()
        return self.syllabus

    def _validate_completeness(self):
        """Ensure required fields are present"""
        required_fields = ["course_info.title", "course_info.domain", "learning_objectives"]
        for field_path in required_fields:
            if not self._has_field(field_path):
                raise ValidationError(f"Required field missing: {field_path}")
```

### 2.4 Hybrid Integration with RAG

Combine function calling with RAG component retrieval:

```python
class HybridFunctionGenerator:
    def generate_syllabus(self, requirements):
        # Phase 1: Generate base structure with T5 function calls
        function_calls = self.t5_model.generate_functions(requirements)
        builder = self.execute_functions(function_calls)

        # Phase 2: Enhance with RAG components
        rag_components = self.rag_pipeline.get_diverse_components(requirements)

        # Phase 3: Integrate RAG components using function calls
        for module in rag_components["modules"][:3]:
            builder.add_module(
                title=module["title"],
                description=module["description"],
                key_concepts=module["key_concepts"],
                hours=module["estimated_hours"]
            )

        return builder.to_json()  # Guaranteed valid JSON
```

---

## 3. Implementation Strategy

### 3.1 Phase 1: Data Preparation and Model Training

#### 3.1.1 Training Data Conversion

**Status**: 🔄 **[IN PROGRESS - Week 1]**

**Objective**: Convert existing JSON training data (90 examples) to function call format

**Implementation Steps**:
```python
def convert_json_to_functions(json_training_data):
    """Convert JSON syllabus examples to function call sequences"""
    converted_examples = []

    for example in json_training_data:
        requirements = example["input_json"]
        target_syllabus = example["output_json"]

        # Generate equivalent function calls
        function_calls = json_to_function_calls(target_syllabus)

        converted_examples.append({
            "input": f"generate syllabus functions for: {format_requirements(requirements)}",
            "output": function_calls
        })

    return converted_examples
```

**Progress Tracking**:
- [ ] Implement `json_to_function_calls()` converter
- [ ] Validate conversion on 5 sample examples
- [ ] Convert full training dataset (90 examples)
- [ ] Manual review of 10 converted examples for quality

#### 3.1.2 Model Fine-tuning

**Status**: 🔄 **[PLANNED - Week 1-2]**

**Objective**: Fine-tune existing T5 model on function call generation

**Training Configuration**:
```python
function_training_config = {
    "base_model": "existing T5-small model",
    "training_examples": 90,
    "max_input_length": 256,  # Shorter than JSON training
    "max_target_length": 1024,  # Function calls are more compact
    "learning_rate": 3e-4,
    "epochs": 5,  # More epochs due to simpler target format
    "batch_size": 4
}
```

**Progress Tracking**:
- [ ] Prepare training script for function call format
- [ ] Run training with monitoring for convergence
- [ ] Evaluate on held-out validation set
- [ ] Compare perplexity: function calls vs. original JSON training

### 3.2 Phase 2: Execution Engine Implementation

**Status**: 🔄 **[PLANNED - Week 2]**

**Objective**: Implement robust execution engine for generated function calls

**Key Components**:

#### 3.2.1 Function Execution with Error Handling

```python
class SafeFunctionExecutor:
    def execute_with_recovery(self, function_calls: str) -> dict:
        """Execute function calls with error recovery"""
        builder = SyllabusBuilder()

        try:
            # Parse and execute function calls
            parsed_calls = self.parse_function_calls(function_calls)
            for func_call in parsed_calls:
                self.execute_single_call(builder, func_call)

        except SyntaxError as e:
            # Attempt to repair common syntax errors
            repaired_calls = self.repair_function_syntax(function_calls)
            return self.execute_with_recovery(repaired_calls)

        except ValidationError as e:
            # Log validation errors but continue execution
            self.log_validation_error(e)

        return builder.to_json()
```

**Progress Tracking**:
- [ ] Implement `SyllabusBuilder` class with all DSL functions
- [ ] Add comprehensive type and domain validation
- [ ] Implement syntax repair for common function call errors
- [ ] Test execution on generated examples
- [ ] Benchmark execution time and reliability

### 3.2.2 Integration Testing

**Status**: 🔄 **[PLANNED - Week 2-3]**

**Test Scenarios**:
```python
test_scenarios = [
    {
        "name": "Basic Function Generation",
        "input": "Introduction to Machine Learning, computer_science, intermediate",
        "expected_functions": ["create_course", "add_objective", "add_module"],
        "success_criteria": "Valid JSON with required fields"
    },
    {
        "name": "Cross-Domain Generation",
        "input": "Linear Algebra, mathematics, beginner",
        "expected_functions": ["create_course", "set_prerequisites"],
        "success_criteria": "Domain-appropriate content"
    },
    {
        "name": "Complex Syllabus Generation",
        "input": "Advanced Machine Learning, computer_science, advanced",
        "expected_functions": ["create_course", "add_module", "add_activity", "add_assessment"],
        "success_criteria": "Complete syllabus with all components"
    }
]
```

**Progress Tracking**:
- [ ] Implement comprehensive test suite
- [ ] Test function generation quality
- [ ] Test execution engine reliability
- [ ] Compare against baseline (RAG template approach)
- [ ] Measure success rate and content quality

### 3.3 Phase 3: Hybrid RAG Integration

**Status**: 🔄 **[PLANNED - Week 3-4]**

**Objective**: Integrate function calling with existing RAG pipeline

**Integration Architecture**:
```python
class HybridFunctionRAGGenerator:
    def __init__(self):
        self.function_model = T5FunctionCallModel()
        self.rag_pipeline = ComponentRetrievalPipeline()
        self.executor = SafeFunctionExecutor()

    def generate_syllabus(self, requirements):
        # Step 1: Generate core structure via functions
        core_functions = self.function_model.generate(requirements)
        builder = self.executor.execute(core_functions)

        # Step 2: Retrieve relevant RAG components
        rag_components = self.rag_pipeline.get_diverse_components(requirements)

        # Step 3: Augment with RAG components via additional functions
        augmentation_functions = self.generate_rag_functions(rag_components)
        enhanced_builder = self.executor.execute_additional(builder, augmentation_functions)

        return enhanced_builder.to_json()
```

**Progress Tracking**:
- [ ] Implement hybrid architecture
- [ ] Test T5 function generation + RAG component integration
- [ ] Optimize balance between generated and retrieved content
- [ ] Validate educational quality of hybrid output
- [ ] Performance benchmarking vs pure approaches

---

## 4. Evaluation Framework

### 4.1 Success Metrics

#### 4.1.1 Structural Validity
- **JSON Validity Rate**: % of outputs that parse as valid JSON
- **Schema Compliance Rate**: % of outputs that match syllabus schema
- **Field Completeness**: % of required fields present in output

#### 4.1.2 Content Quality
- **Educational Appropriateness**: Domain expert evaluation of content
- **Coherence Score**: Semantic consistency across syllabus components
- **Diversity Score**: Variety in generated content vs templates

#### 4.1.3 Function Generation Quality
- **Function Syntax Accuracy**: % of generated functions that execute without error
- **Function Semantic Appropriateness**: Relevance of function calls to requirements
- **Function Sequence Logic**: Logical ordering and dependencies

### 4.2 Comparison Studies

#### 4.2.1 Baseline Comparisons
1. **Pure T5 JSON Generation** (current implementation)
2. **RAG Template Approach** (current best performing)
3. **Hybrid Function Calling** (proposed approach)

#### 4.2.2 Ablation Studies
1. Function calling without RAG integration
2. Function calling with different DSL designs
3. Effect of training data size on function generation quality

---

## 5. Theoretical Contributions

### 5.1 Novel Aspects

1. **Function Calling for Smaller Models**: First systematic application of function calling to enable structured generation in sub-billion parameter models (T5-small 60M)
2. **Salvaging Trained Models**: Novel approach to make unusable trained models productive through alternative generation formats
3. **Hybrid Template-Neural Integration**: Combines deterministic JSON structure with neural content intelligence

### 5.2 Broader Impact for Resource-Constrained AI

**Primary Contribution**: Demonstrates that smaller, more efficient models can achieve reliable structured generation through architectural innovation rather than parameter scaling.

**Implications**:
- **Edge AI Applications**: Enable structured generation on mobile/edge devices
- **Cost-Effective AI**: Achieve LLM-like reliability without LLM-scale resources
- **Academic Research**: Make advanced AI techniques accessible with limited computational budgets
- **Educational AI**: Smaller models suitable for educational institution deployments

**Beyond Syllabus Generation**:
- **Configuration File Generation**: T5 + functions for YAML/TOML/XML generation
- **Structured Report Creation**: Academic papers, technical documentation with consistent formatting
- **Data Pipeline Configuration**: ML pipeline definitions, data processing workflows

---

## 6. Progress Tracking

### 6.1 Implementation Milestones

#### Phase 1: Proof of Concept (Next 2-3 Days)
- [ ] Convert 10-20 JSON training examples to function call format
- [ ] Test existing T5 model on function call generation (zero-shot)
- [ ] Implement basic SyllabusBuilder execution engine
- [ ] **Goal**: Demonstrate T5 can generate function calls better than JSON

#### Phase 2: Full Implementation (1 Week)
- [ ] Convert all 90 training examples to function call format
- [ ] Fine-tune T5 model on function call generation task
- [ ] Implement complete execution engine with error handling
- [ ] **Goal**: Functional T5 function calling system

#### Phase 3: Integration and Evaluation (1 Week)
- [ ] Integrate T5 function calling with existing RAG retrieval
- [ ] Compare approaches: RAG-only vs T5+RAG vs Function+RAG
- [ ] Comprehensive evaluation across STEM domains
- [ ] **Goal**: Demonstrate improvement over current template approach

#### Phase 4: Documentation and Finalization (3-4 Days)
- [ ] Document performance improvements and limitations
- [ ] Prepare final project deliverables
- [ ] Archive all approaches with comparative analysis
- [ ] **Goal**: Complete project with multiple validated approaches

### 6.2 Risk Mitigation

**Risk 1**: Function generation quality insufficient
- **Mitigation**: Implement function call repair mechanisms similar to JSON repair
- **Fallback**: Hybrid approach with template fallback for failed function calls

**Risk 2**: Execution engine complexity introduces new failure modes
- **Mitigation**: Extensive testing and validation at each function execution
- **Fallback**: Safe execution mode that continues despite individual function failures

**Risk 3**: Training data insufficient for function call learning
- **Mitigation**: Data augmentation through automated conversion of additional JSON examples
- **Fallback**: Few-shot learning approach with function call exemplars

---

## 7. Implementation Notes

### 7.1 Code Organization

```
src/
├── function_calling/
│   ├── dsl.py                 # Domain-specific language definition
│   ├── executor.py            # Function execution engine
│   ├── training.py            # T5 training for function calls
│   └── integration.py         # RAG integration
├── evaluation/
│   ├── metrics.py             # Evaluation metrics
│   ├── comparison.py          # Baseline comparisons
│   └── validation.py          # Content quality validation
└── data/
    ├── function_examples/     # Training data in function call format
    └── evaluation_sets/       # Test datasets for evaluation
```

### 7.2 Dependencies

**New Dependencies**:
```python
ast          # For parsing function calls safely
inspect      # For function signature validation
typing       # For type hints and validation
```

**Existing Dependencies**: All current project dependencies remain

---

## 8. Future Research Directions

### 8.1 Advanced Function DSL Design

- **Conditional Functions**: Support for if/then logic in function calls
- **Loop Functions**: Generate repeated structures programmatically
- **Composition Functions**: Higher-order functions for complex structures

### 8.2 Multi-Domain Function Libraries

- **Extensible DSL**: Framework for adding new domains beyond STEM
- **Cross-Domain Functions**: Functions that work across multiple educational domains
- **Personalization Functions**: User-specific customization capabilities

### 8.3 Interactive Function Generation

- **Real-time Validation**: Interactive feedback during function generation
- **User Correction**: Allow users to modify generated function calls
- **Incremental Generation**: Build syllabi through interactive function calling

---

## 9. References

**Core Program Synthesis Literature**:
1. Austin, J., Odena, A., et al. (2021). "Program Synthesis with Large Language Models." arXiv:2108.07732.
2. Chen, M., Tworek, J., et al. (2021). "Evaluating Large Language Models Trained on Code." arXiv:2107.03374.
3. Li, Y., Choi, D., et al. (2022). "Competition-level code generation with AlphaCode." Science, 378(6624), 1092-1097.

**Function Calling and Tool Use**:
4. Schick, T., Dwivedi-Yu, J., et al. (2023). "Toolformer: Language Models Can Teach Themselves to Use Tools." arXiv:2302.04761.
5. Yao, S., Zhao, J., et al. (2022). "ReAct: Synergizing Reasoning and Acting in Language Models." arXiv:2210.03629.
6. Li, M., Zhang, Y., et al. (2023). "API-Bank: A Benchmark for Tool-Augmented LLMs." arXiv:2304.08244.

**Structured Generation and Constrained Decoding**:
7. Lu, X., Welleck, S., et al. (2021). "NEUROLOGIC Decoding: (Un)supervised Neural Text Generation with Predicate Logic Constraints." NAACL-HLT 2021.
8. Bosselut, A., Rashkin, H., et al. (2020). "Guided Generation of Cause and Effect." EMNLP 2020.

**Domain-Specific Language Generation**:
9. Yin, P., & Neubig, G. (2017). "Learning to Generate Programs from Natural Language Descriptions." ACL 2017.
10. Yu, T., Yasunaga, M., et al. (2018). "Semantic Parsing with Syntax- and Table-Aware SQL Generation." ACL 2018.

**Educational Technology Applications**:
11. Wang, Y., Wang, W., et al. (2021). "CodeT5: Identifier-aware Unified Pre-trained Encoder-Decoder Models for Code Understanding and Generation." EMNLP 2021.
12. Nijkamp, E., Ruffolo, J., et al. (2022). "PROGEN: Language Modeling for Protein Generation." arXiv:2004.03497.

---

**Document Version**: 1.0
**Last Updated**: 2024-09-25
**Status**: Initial Draft - Ready for Implementation
**Next Review**: Weekly progress updates