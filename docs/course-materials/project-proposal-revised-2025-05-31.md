# MSc Artificial Intelligence Project Proposal

## Project Title
Developing a Custom Neural Network Architecture for Automated Course Syllabus Generation from Structured Educational Inputs

## Significance/Contribution to the Discipline/Research Problem

Course syllabus creation is a labour-intensive process requiring domain expertise and pedagogical knowledge (Parkes and Harris, 2002). While large language models can generate text, they often lack the structure and educational coherence required for quality syllabi. Current approaches typically rely on templates or require extensive human intervention.

The significance of this research lies in addressing a clear gap in automated educational content creation:

**Technical Innovation:** Adapting proven neural language architectures with specialised educational components and constraints, including curriculum learning mechanisms and pedagogical structure encoders, to optimise structured educational content generation beyond general-purpose language models (Vaswani et al., 2017)

**Practical Application:** Reducing educator workload while maintaining pedagogical quality aligned with established educational taxonomies (Anderson et al., 2001)

**Domain Advancement:** Contributing to the emerging field of AI in education through custom machine learning solutions for content structuring (Wang et al., 2018)

**Knowledge Transfer:** Demonstrating how domain-specific constraints can be incorporated into neural network design using curriculum learning approaches (Bengio et al., 2009)

## Research Question

"How can a custom machine learning model effectively generate structured, coherent course syllabi from specific educational inputs including course descriptions, learning objectives, and problem statements?"

## Aims and Objectives

### Primary Aim
To adapt and evaluate existing neural language architectures with custom educational components to generate educationally sound, structurally coherent course syllabi from well-defined input context.

### Objectives

**Data Collection and Preprocessing**
- Collect 500+ high-quality course syllabi from diverse educational domains
- Achieve 80% automated preprocessing accuracy with manual validation pipeline during the data preprocessing phase
- Create standardised dataset with consistent metadata formatting

**Educational Architecture Adaptation**
- Adapt existing transformer architectures with custom educational layers and constraints
- Develop domain-specific fine-tuning strategies and educational word embeddings achieving 10% improvement over generic embeddings on educational terminology
- Implement curriculum learning mechanisms and pedagogical structure encoders
- Complete initial model validation with baseline performance metrics

**Model Training and Optimisation**
- Train the model to achieve strong performance on standard NLP metrics for text generation quality
- Implement iterative refinement process reducing training loss by 20% through hyperparameter optimisation
- Develop domain classification capability with 85%+ accuracy across different subject areas
- Conduct extensive hyperparameter tuning and model validation

**Evaluation and Demonstration**
- Create comprehensive evaluation framework measuring technical performance and educational quality
- Conduct case studies demonstrating practical application across 3 different educational domains
- Achieve expert reviewer ratings of 7/10+ for educational coherence and pedagogical appropriateness
- Perform comparative analysis with existing educational content generation approaches

## Key Literature Related to the Project

### Natural Language Generation
Recent advancements in sequence-to-sequence modelling and attention mechanisms have revolutionised natural language generation capabilities (Vaswani et al., 2017). Domain adaptation of transformer architectures has become standard practice in specialised NLP applications. Gururangan et al. (2020) demonstrate that continued pretraining of language models on domain-specific corpora consistently leads to performance gains, with their multi-phase adaptive pretraining approach showing that custom domain adaptations are both effective and widely adopted. Lin et al. (2022) establish a taxonomy for transformer variations that explicitly includes "architectural modification" as a primary category for enhancing model performance, validating that custom architectural components are recognised approaches in the field.

Attention layers will be adapted for educational content hierarchy, with position-aware attention prioritising learning objective sequences and maintaining pedagogical flow throughout generated syllabi. Neural question generation for reading comprehension has demonstrated how AI can create structured educational content (Du et al., 2017).

### Educational Content Development
Taxonomies of educational objectives provide frameworks for structuring learning materials (Anderson et al., 2001). Output layers will encode Bloom's taxonomy levels to ensure generated content maintains pedagogical progression from knowledge recall through synthesis and evaluation. Research on syllabus design has identified key structural and functional elements that must be preserved in automated generation (Parkes and Harris, 2002). Recent work in automating question generation from educational text shows promising results but requires further development (Bhowmick et al., 2023).

### Custom Neural Architectures
Curriculum learning approaches have shown that neural networks can be trained more effectively through structured learning progressions (Bengio et al., 2009). Training will follow curriculum learning principles, starting with simple syllabus structures before progressing to complex interdisciplinary content, ensuring the model learns educational foundations before advanced content organisation. Domain-specific models like QG-Net demonstrate how custom architectures can outperform general models for educational content generation (Wang et al., 2018).

## Methodology/Development Strategy/Research Design

This research employs a design science research framework combining quantitative model development with qualitative educational assessment, particularly suitable for developing novel AI solutions in educational contexts where both technical performance and pedagogical effectiveness must be evaluated.

### Research Strategy
The study follows an iterative development methodology with three integrated phases:

**Phase 1: Exploratory Analysis** - Systematic examination of syllabus structure and patterns across disciplines through content analysis to inform model design requirements

**Phase 2: Quantitative Development** - Iterative adaptation of existing transformer architectures with custom educational components incorporating curriculum learning principles and domain-specific constraints

**Phase 3: Mixed-Method Evaluation** - Performance assessment using standard NLP metrics (ROUGE, BERTScore) combined with educational quality measures based on established pedagogical frameworks (Bloom's taxonomy, SOLO taxonomy)

### Implementation Methods
The technical implementation will utilise transfer learning principles, adapting pre-trained transformer models (such as T5 or BERT variants) with custom educational components. This approach leverages the linguistic capabilities of established models while incorporating domain-specific constraints through architectural modifications including pedagogical attention mechanisms, curriculum learning schedulers, and educational taxonomy encoders.

**Data Access Strategy:** Primary data will be sourced from publicly available repositories (Open Syllabus Project API, MIT OpenCourseWare). If institutional barriers limit access, synthetic syllabus generation using advanced LLMs will serve as a legitimate backup approach, following established practices in AI research for training data augmentation.

**Educational Quality Assessment:** Structured evaluation against established educational frameworks and comparison with exemplar syllabi from reputable institutions, ensuring pedagogical appropriateness and coherence

## Ethical Considerations and Risk Assessment

### Ethical Framework
This research adheres to principles of ethical AI development and educational research. All educational content will be properly attributed with appropriate permissions sought for syllabus data. The research complies with relevant data protection regulations and institutional policies. Strategies will be implemented to identify and address potential biases in training data, with generated content evaluated against established educational standards to ensure pedagogical appropriateness.

### Key Risk Mitigation Strategies

| Risk Category | Risk Description | Mitigation Strategy |
|---------------|------------------|-------------------|
| **Data Availability** | Limited access to sufficient high-quality educational content data | Develop relationships with educational repositories; prepare multiple data acquisition pathways; implement data augmentation techniques |
| **Methodological Challenges** | Challenges in effectively adapting general language models to educational domain constraints | Build upon proven adaptation techniques from educational NLP research; consult with educational experts throughout development; implement iterative design approach with regular validation against educational benchmarks |
| **Domain Adaptability** | Limited generalisability across different educational domains | Develop domain classification mechanisms; ensure diversity in training data; consider domain-specific fine-tuning |
| **Resource Constraints** | Computational and time limitations for model development and training | Optimise model architecture; develop efficient training protocols; utilise cloud computing resources when necessary |
| **Evaluation Complexity** | Challenges in objective assessment of educational quality | Develop comprehensive evaluation framework combining quantitative metrics and qualitative expert assessment |
| **Technical Integration** | Difficulties in implementing theoretical approaches in practical systems | Maintain focus on real-world applicability; regularly test preliminary implementations |

## Description of Artefact(s) That Will Be Created

**Custom Neural Network Model and Training Pipeline:** Complete machine learning solution including specialised architecture for syllabus generation, trained model weights, inference pipeline, and domain classification capabilities.

**Processed Educational Dataset and Documentation:** Structured collection of annotated syllabi with metadata, classification information, comprehensive dataset documentation, and usage guidelines for future research.

**Evaluation Framework and Assessment Tools:** Technical evaluation scripts, educational quality assessment protocols, comparative analysis tools, and methodological frameworks for measuring both technical performance and pedagogical effectiveness.

**Interactive Demonstration System and Technical Documentation:** Web interface for generating syllabi from user inputs, visualisation of model operations, export functionality for practical use, comprehensive architecture description, implementation details, training methodology, and usage guidelines.

## Timeline of Proposed Activities

| Phase | Activities | Duration | Weeks |
|-------|------------|----------|-------|
| Planning & Literature Review | Initial research, requirements analysis, research design finalisation | 4 weeks | 1-4 |
| Data Collection | Gather syllabi from multiple sources, create permissions framework | 6 weeks | 5-10 |
| Data Preprocessing | Standardise formats, annotate structure, create datasets | 4 weeks | 9-12 |
| Educational Architecture Adaptation | Adapt transformer models with educational constraints, implement curriculum learning | 6 weeks | 11-16 |
| Training & Optimisation | Training, hyperparameter tuning, performance optimisation, extensive validation | 5 weeks | 17-21 |
| Evaluation | Technical evaluation, educational quality assessment, case studies, comparative analysis | 5 weeks | 22-26 |
| Documentation & Presentation | Technical documentation, dissertation writing, presentation preparation | 6 weeks | 27-32 |

**Working Schedule:**
- 3 days per week dedicated to project
- Weekly progress reviews
- Bi-weekly supervisor meetings

## References

Anderson, L.W., Krathwohl, D.R., Airasian, P.W., Cruikshank, K.A., Mayer, R.E., Pintrich, P.R., Raths, J. and Wittrock, M.C. (2001) *A taxonomy for learning, teaching, and assessing: A revision of Bloom's taxonomy of educational objectives*. New York: Longman.

Bengio, Y., Louradour, J., Collobert, R. and Weston, J. (2009) 'Curriculum learning', *Proceedings of the 26th Annual International Conference on Machine Learning*, pp. 41-48.

Bhowmick, A.K., Jagmohan, A., Vempaty, A., Dey, P., Hall, L., Hartman, J., Kokku, R. and Maheshwari, H. (2023) 'Automating Question Generation from Educational Text', *SGAI Conference*.

Du, X., Shao, J. and Cardie, C. (2017) 'Learning to Ask: Neural Question Generation for Reading Comprehension', *Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics*.

Gururangan, S., Marasović, A., Swayamdipta, S., Lo, K., Beltagy, I., Downey, D. and Smith, N.A. (2020) 'Don't stop pretraining: Adapt language models to domains and tasks', *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics*, pp. 8342-8360.

Lin, T., Wang, Y., Liu, X. and Qiu, X. (2022) 'A survey of transformers', *AI Open*, 3, pp. 111-132.

Parkes, J. and Harris, M.B. (2002) 'The purposes of a syllabus', *College Teaching*, 50(2), pp. 55-61.

Srivastava, M. and Goodman, N.D. (2021) 'Question Generation for Adaptive Education', *Proceedings of the 14th International Conference on Educational Data Mining*.

Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A.N., Kaiser, Ł. and Polosukhin, I. (2017) 'Attention is all you need', *Advances in Neural Information Processing Systems*, 30.

Wang, Z., Lan, A.S., Nie, W., Waters, A.E., Grimaldi, P.J. and Baraniuk, R. (2018) 'QG-Net: A Data-Driven Question Generation Model for Educational Content', *Proceedings of the 5th ACM Conference on Learning*. 