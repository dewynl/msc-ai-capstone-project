# MSc Artificial Intelligence Project Proposal

## Project Title

Developing a Custom Neural Network Architecture for Automated Course Syllabus Generation from Structured Educational Inputs

## Significance/Contribution to the Discipline/Research Problem

Course syllabus creation is a labor-intensive process requiring domain expertise and pedagogical knowledge (Parkes and Harris, 2002). While large language models can generate text, they often lack the structure and educational coherence required for quality syllabi. Current approaches typically rely on templates or require extensive human intervention.

The significance of this research lies in addressing a clear gap in automated educational content creation:

1. **Technical Innovation**: Developing specialized neural architectures optimized for structured educational content rather than relying on general-purpose language models (Vaswani et al., 2017)
2. **Practical Application**: Reducing educator workload while maintaining pedagogical quality aligned with established educational taxonomies (Anderson et al., 2001)
3. **Domain Advancement**: Contributing to the emerging field of AI in education through custom machine learning solutions for question generation and content structuring (Wang et al., 2018)
4. **Knowledge Transfer**: Demonstrating how domain-specific constraints can be incorporated into neural network design using curriculum learning approaches (Bengio et al., 2009)

## Research Question

"How can a custom machine learning model effectively generate structured, coherent course syllabi from specific educational inputs including course descriptions, learning objectives, and problem statements?"

## Aims and Objectives

### Primary Aim

To develop and evaluate a custom machine learning model capable of generating educationally sound, structurally coherent course syllabi from well-defined input context.

### Objectives

1. **Data Collection and Preprocessing** (Weeks 5-12)
2. 
    - Collect 500+ high-quality course syllabi from diverse educational domains within 8 weeks
    - Achieve 80% automated preprocessing accuracy with manual validation pipeline during the data preprocessing phase
    - Create standardized dataset with consistent metadata formatting
3. **Custom Neural Architecture Development** (Weeks 13-18)
4. 
    - Design and implement a novel neural network architecture optimized for educational content structure within 6 weeks
    - Develop domain-specific word embeddings achieving 10% improvement over generic embeddings on educational terminology
    - Complete initial model validation with baseline performance metrics
5. **Model Training and Optimization** (Weeks 19-24)
6. 
    - Train the model to achieve ROUGE-L scores of 0.4+ and BERTScore of 0.6+ on held-out test data within 6 weeks
    - Implement iterative refinement process reducing training loss by 20% through hyperparameter optimization
    - Develop domain classification capability with 85%+ accuracy across different subject areas
7. **Evaluation and Demonstration** (Weeks 25-28)
8. 
    - Create comprehensive evaluation framework measuring technical performance and educational quality within 4 weeks
    - Conduct case studies demonstrating practical application across 3 different educational domains
    - Achieve expert reviewer ratings of 7/10+ for educational coherence and pedagogical appropriateness

## Key Literature Related to the Project

### Natural Language Generation

- Recent advancements in sequence-to-sequence modeling and attention mechanisms have revolutionized natural language generation capabilities (Vaswani et al., 2017)
- Neural question generation for reading comprehension has demonstrated how AI can create structured educational content (Du et al., 2017)

### Educational Content Development

- Taxonomies of educational objectives provide frameworks for structuring learning materials (Anderson et al., 2001)
- Research on syllabus design has identified key structural and functional elements that must be preserved in automated generation (Parkes and Harris, 2002)
- Recent work in automating question generation from educational text shows promising results but requires further development (Bhowmick et al., 2023)
- Question generation for adaptive education demonstrates the potential for AI to create personalized learning materials (Srivastava and Goodman, 2021)

### Custom Neural Architectures

- Curriculum learning approaches have shown that neural networks can be trained more effectively through structured learning progressions (Bengio et al., 2009)
- Domain-specific models like QG-Net demonstrate how custom architectures can outperform general models for educational content generation (Wang et al., 2018)

## Methodology/Development Strategy/Research Design

This research will employ a mixed methods approach combining quantitative and qualitative methodologies within a design science research framework. This approach is particularly suitable for developing novel AI solutions in educational contexts where both technical performance and pedagogical effectiveness must be evaluated (Wang et al., 2018).

### Research Philosophy

The study adopts a pragmatic epistemological stance, recognizing that both objective measurements of model performance and subjective evaluations of educational quality are essential to fully address the research question. This pragmatism allows for methodological pluralism in examining how machine learning models can effectively generate educational content.

### Research Approach

The research follows an iterative and incremental approach characterized by:

1. **Mixed Methods Design**: An exploratory sequential design will be employed, where qualitative analysis of educational content structure will inform the quantitative development of the neural network architecture, followed by both quantitative and qualitative evaluation methods.
2. **Design Science Research**: The study adheres to design science principles by focusing on creating an innovative technological artifact (the neural network model) while ensuring rigor through systematic development and evaluation methods.
3. **Theoretical Framework**: The research is situated within educational content development theories (Anderson et al., 2001) and natural language processing paradigms (Vaswani et al., 2017), with particular attention to structural pedagogy principles and sequence-to-sequence learning approaches.

### Research Strategy

The overall strategy encompasses four key phases:

- **Exploratory Phase**: Analysis of existing educational syllabi structure and content patterns to inform model design requirements, following established frameworks for educational content analysis (Parkes and Harris, 2002).
- **Development Phase**: Iterative design and implementation of the custom neural network architecture based on findings from the exploratory phase, incorporating curriculum learning principles (Bengio et al., 2009).
- **Evaluation Phase**: Multi-faceted assessment using both technical metrics and educational quality evaluations, drawing on approaches from educational question generation evaluation (Srivastava and Goodman, 2021).
- **Refinement Phase**: Model optimization based on evaluation results to enhance both performance and educational value.

### Data Collection and Analysis Methods

Multiple data collection and analysis methods will be employed:

- **Content Analysis**: Systematic examination of syllabus structure and patterns across disciplines
- **Machine Learning**: Development and training of neural network models using approaches demonstrated in educational content generation (Du et al., 2017)
- **Performance Metrics**: Quantitative evaluation using standard NLP metrics
- **Expert Review**: Qualitative assessment by educational specialists
- **Comparative Analysis**: Evaluation against human-created syllabi (Bhowmick et al., 2023)

The integration of these methods will provide a comprehensive understanding of both the technical capabilities of the model and its practical value in educational contexts.

## Ethical Considerations and Risk Assessment

### Ethical Considerations

This research adheres to principles of ethical AI development and educational research:

- **Data Ethics**: All educational content used will be properly attributed, with appropriate permissions sought for syllabus data. The research will comply with relevant data protection regulations and institutional policies.
- **Bias Mitigation**: Strategies will be implemented to identify and address potential biases in training data that could affect the educational content generated by the model.
- **Educational Standards**: Generated content will be evaluated against established educational standards to ensure pedagogical appropriateness.
- **Human Oversight**: The research design maintains human review in the content generation pipeline, recognizing that AI-generated educational materials require expert validation.

| Risk Category | Description | Potential Impact | Mitigation Strategy |
| --- | --- | --- | --- |
| **Data Availability** | Limited access to sufficient high-quality educational content data | Could restrict model training and affect output quality | Develop relationships with educational repositories; Prepare multiple data acquisition pathways; Implement data augmentation techniques |
| **Methodological Challenges** | Difficulty in capturing educational structure in machine learning models | May result in models that generate technically correct but pedagogically weak content | Consult with educational experts throughout development; Implement iterative design approach with regular evaluation |
| **Domain Adaptability** | Limited generalizability across different educational domains | Model may perform inconsistently across disciplines | Develop domain classification mechanisms; Ensure diversity in training data; Consider domain-specific fine-tuning |
| **Resource Constraints** | Computational and time limitations for model development and training | Could impact model complexity and training depth | Optimize model architecture; Develop efficient training protocols; Utilize cloud computing resources when necessary |
| **Evaluation Complexity** | Challenges in objective assessment of educational quality | May make it difficult to conclusively demonstrate improvements | Develop comprehensive evaluation framework combining quantitative metrics and qualitative expert assessment |
| **Technical Integration** | Difficulties in implementing theoretical approaches in practical systems | Could limit practical application of research findings | Maintain focus on real-world applicability; Regularly test preliminary implementations |

This comprehensive risk assessment demonstrates awareness of potential challenges and a strategic approach to addressing them. Regular reassessment of risks will be conducted throughout the project lifecycle, with mitigation strategies adjusted as needed.

## Description of Artefact(s) That Will Be Created

### 1. Custom Neural Network Model and Training Pipeline

Complete machine learning solution including specialized architecture for syllabus generation, trained model weights, inference pipeline, and domain classification capabilities.

### 2. Processed Educational Dataset and Documentation

Structured collection of annotated syllabi with metadata, classification information, comprehensive dataset documentation, and usage guidelines for future research.

### 3. Evaluation Framework and Assessment Tools

Technical evaluation scripts, educational quality assessment protocols, comparative analysis tools, and methodological frameworks for measuring both technical performance and pedagogical effectiveness.

### 4. Interactive Demonstration System and Technical Documentation

Web interface for generating syllabi from user inputs, visualization of model operations, export functionality for practical use, comprehensive architecture description, implementation details, training methodology, and usage guidelines.

| Phase | Activities | Duration | Weeks |
| --- | --- | --- | --- |
| Planning & Literature Review | Initial research, requirements analysis, research design finalization | 4 weeks | 1-4 |
| **Data Collection** | Gather syllabi from multiple sources, create permissions framework | 4 weeks | 5-8 |
| **Data Preprocessing** | Standardize formats, annotate structure, create datasets | 4 weeks | 9-12 |
| **Model Development** | Architecture design, implementation, initial validation | 6 weeks | 13-18 |
| **Training & Optimization** | Training, hyperparameter tuning, performance optimization | 6 weeks | 19-24 |
| **Evaluation** | Technical evaluation, educational quality assessment, case studies | 4 weeks | 25-28 |
| **Documentation & Presentation** | Technical documentation, dissertation writing, presentation preparation | 4 weeks | 29-32 |

## Working Schedule

- 3 days per week dedicated to project
- Weekly progress reviews
- Bi-weekly supervisor meetings

## References

Anderson, L.W., Krathwohl, D.R., Airasian, P.W., Cruikshank, K.A., Mayer, R.E., Pintrich, P.R., Raths, J. and Wittrock, M.C. (2001) *A taxonomy for learning, teaching, and assessing: A revision of Bloom's taxonomy of educational objectives*. New York: Longman.

Bengio, Y., Louradour, J., Collobert, R. and Weston, J. (2009) 'Curriculum learning', *Proceedings of the 26th Annual International Conference on Machine Learning*, pp. 41-48.

Bhowmick, A.K., Jagmohan, A., Vempaty, A., Dey, P., Hall, L., Hartman, J., Kokku, R. and Maheshwari, H. (2023) 'Automating Question Generation from Educational Text', *SGAI Conference*.

Du, X., Shao, J. and Cardie, C. (2017) 'Learning to Ask: Neural Question Generation for Reading Comprehension', *Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics*.

Parkes, J. and Harris, M.B. (2002) 'The purposes of a syllabus', *College Teaching*, 50(2), pp. 55-61.

Srivastava, M. and Goodman, N.D. (2021) 'Question Generation for Adaptive Education', *Proceedings of the 14th International Conference on Educational Data Mining*.

Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A.N., Kaiser, Ł. and Polosukhin, I. (2017) 'Attention is all you need', *Advances in Neural Information Processing Systems*, 30.

Wang, Z., Lan, A.S., Nie, W., Waters, A.E., Grimaldi, P.J. and Baraniuk, R. (2018) 'QG-Net: A Data-Driven Question Generation Model for Educational Content', *Proceedings of the 5th ACM Conference on Learning.*