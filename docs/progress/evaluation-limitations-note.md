# Section 6.5: Limitations Discussion - Draft Text

**For inclusion in your Evaluation chapter when you write it**

---

## 6.5 Limitations and Discussion

This research demonstrates significant technical achievements in automated educational content generation through the function calling architecture, achieving 100% structural validity whilst maintaining 85% neural model contribution. However, several limitations warrant acknowledgment and discussion for comprehensive evaluation transparency.

### 6.5.1 Educational Quality Assessment Constraints

This research employs automated rule-based validation rather than human expert review for educational quality assessment. While expert review would provide additional validation of pedagogical appropriateness and contextual suitability, the automated approach offers several methodological advantages that align with contemporary educational AI requirements:

**Advantages of Rule-Based Validation:**

1. **Transparency and Reproducibility**: Automated validation enables systematic, repeatable assessment through explicit reference to established educational frameworks (Bloom's taxonomy, IEEE LOM metadata standards). This transparency supports independent verification and research reproducibility essential for academic research validation.

2. **Scalability and Consistency**: Rule-based approaches maintain consistent validation standards across all generated content without variability introduced by subjective human judgment. This consistency enables large-scale systematic evaluation whilst ensuring uniform application of educational standards.

3. **Educational Defensibility**: Automated validation aligns with federal guidance emphasising transparent, accountable AI systems in educational contexts (U.S. Department of Education, 2023). Educational stakeholders can understand and verify system decisions through reference to recognised educational frameworks rather than relying on opaque expert opinions.

4. **Integration with System Architecture**: Rule-based validation integrates directly into the execution engine, providing real-time quality assurance during content generation rather than requiring post-generation review. This architectural integration ensures pedagogical appropriateness throughout the generation process.

**Limitations Acknowledged:**

Despite these advantages, the absence of human expert review introduces specific limitations:

- **Qualitative Pedagogical Insights**: Automated validation cannot assess nuanced pedagogical appropriateness that experienced educators might identify through professional judgment. Contextual suitability, cultural sensitivity, and institutional fit require human evaluation beyond rule-based frameworks.

- **Edge Case Detection**: Rule-based systems may fail to identify subtle educational quality issues that fall outside explicit validation criteria. Human experts can recognise problematic patterns and contextual inappropriateness through experience and tacit pedagogical knowledge.

- **Stakeholder Acceptance**: Educational practitioners may perceive expert-reviewed content as more trustworthy than exclusively machine-validated materials, potentially affecting system adoption despite technical validity.

**Future Work Implications:**

Future research should incorporate human expert validation to complement automated assessment, combining the consistency and transparency of rule-based validation with the qualitative insights provided by experienced educational professionals. This hybrid evaluation approach would provide comprehensive assessment whilst maintaining the methodological advantages demonstrated in this research.

### 6.5.2 STEM Domain Focus and Generalizability

The research focuses exclusively on STEM domains (Computer Science, Mathematics, Physics, Engineering), enabling sophisticated domain-specific validation rules but limiting immediate applicability to humanities and social science disciplines. This domain restriction represents a deliberate methodological choice (see Annex A.6.1 for detailed rationale) that prioritises validation quality over breadth of coverage.

**Implications for Generalizability:**

The function calling architecture remains extensible to additional domains through expanded function calling DSL definitions and domain-specific validation modules. However, humanities domains may require fundamentally different validation approaches that accommodate subjective content evaluation criteria and diverse pedagogical traditions.

### 6.5.3 Synthetic Data Limitations

Whilst synthetic training data ensures privacy protection and quality consistency, it may not fully capture institutional diversity, formatting variations, and unconventional pedagogical approaches present in real-world educational syllabi. The controlled nature of synthetic data limits the model's exposure to edge cases and authentic educational diversity.

### 6.5.4 Temporal and Deployment Constraints

The research timeframe limits the scope of longitudinal evaluation of generated content effectiveness in actual educational settings. Real-world deployment testing with educational practitioners remains beyond the scope of this academic project, restricting assessment to technical performance metrics and automated educational quality validation rather than empirical educational effectiveness measurement.

---

## Summary: Methodological Positioning

This research deliberately prioritises **transparent, reproducible automated validation** over expert review, aligning with contemporary requirements for explainable educational AI systems. The rule-based validation approach provides systematic, verifiable quality assurance whilst acknowledging the complementary value of human expert judgment in comprehensive educational content evaluation.

The limitations discussed represent opportunities for future research extension rather than fundamental weaknesses in the methodological approach demonstrated.
