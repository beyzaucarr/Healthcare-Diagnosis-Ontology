# Healthcare Diagnosis Ontology

# Specification Document (Version 2)

---

# 1. Domain Description

This ontology models a simplified healthcare diagnosis domain. It captures semantic relationships between patients, symptoms, diseases, diagnostic tests, clinical alerts, and healthcare observations in order to support automated clinical reasoning and diagnosis-related inference.

The ontology was extended in Phase 2 with SWRL-based clinical reasoning inspired by ontology-driven healthcare decision support system (DSS) architectures.

---

# 2. Scope and Objectives

## Scope

The ontology focuses on:

- Representing symptoms reported by patients
- Linking diseases to their associated symptoms
- Modeling patient observations and risk-related information
- Inferring possible diagnoses and diagnostic test requirements
- Supporting semantic querying using SPARQL
- Supporting rule-based reasoning using SWRL

---

## Objectives

- Provide a structured semantic representation of healthcare knowledge
- Enable logical inference using OWL and SWRL reasoning
- Support diagnosis suggestions based on patient-reported symptoms
- Enable automated inference of diagnostic recommendations
- Provide a foundation for ontology-driven healthcare DSS systems

---

# 3. Core Concepts and Relationships

## Classes

### Existing Classes
- Patient: Represents individuals receiving medical attention
- Disease: Represents medical conditions
- Symptom: Represents observable patient conditions
- Treatment: Represents medical interventions
- Diagnosis: Represents inferred disease identification

### Newly Added Classes (v2)
- ClinicalRule: Represents clinical reasoning rules
- DiagnosticTest: Represents medical diagnostic tests
- RiskAssessment: Represents patient risk evaluations
- ClinicalAlert: Represents healthcare-related alerts
- PatientObservation: Represents structured patient observations
- DiagnosticRecommendation: Represents recommendation entities

---

## Object Properties

### Existing Object Properties
- reportsSymptom (Patient → Symptom)
- hasSymptom (Disease → Symptom)
- hasTreatment (Disease → Treatment)
- possibleDiagnosis (Patient → Disease)

### Newly Added Object Properties (v2)
- requiresTest (Patient → DiagnosticTest)
- hasRiskAssessment (Patient → RiskAssessment)
- triggersAlert (Patient → ClinicalAlert)
- basedOnObservation (Patient → PatientObservation)
- hasRecommendation (Patient → DiagnosticRecommendation)

---

## Data Properties (v2)

- hasSymptomDuration (Patient → integer)
- hasFeverStatus (Patient → string)
- hasRiskLevel (Patient → string)
- hasAlertMessage (ClinicalAlert → string)

---

# 4. Inference Model

## OWL Property Chain Reasoning

The ontology defines the following property chain axiom:

reportsSymptom ∘ inverse(hasSymptom) ⊑ possibleDiagnosis

This enables the system to infer a possible diagnosis when a patient reports symptoms associated with a disease.

---

## SWRL-Based Clinical Reasoning (v2)

The ontology was extended with SWRL-based reasoning rules.

Example SWRL rule:

```text
Patient(?p) ^
hasSymptomDuration(?p, ?d) ^
swrlb:greaterThan(?d, 13)
-> requiresTest(?p, SputumTest)
5. Competency Questions

The ontology is designed to answer the following questions:

Which diseases can be inferred from a patient’s reported symptoms?
Which patients are likely to have a specific disease?
What symptoms are associated with a given disease?
Can the system automatically infer diagnostic test requirements?
Which patients require diagnostic testing?
6. Intended Use Cases
Clinical decision support (simplified)
Educational demonstration of ontology reasoning
Semantic healthcare modeling
Automated diagnosis inference
Rule-based healthcare reasoning
7. Design Considerations
Uses OWL object properties for semantic relationships
Employs property-chain reasoning for diagnosis inference
Uses SWRL rules for clinical reasoning
Designed for explainable logical inference
Keeps the ontology extensible and modular
8. Changes from Version 1 to Version 2
Newly Added Features
Added SWRL-based clinical reasoning
Added DiagnosticTest, ClinicalAlert, RiskAssessment, and PatientObservation classes
Added patient observation data properties
Added automated diagnostic test inference
Added RDF-compatible healthcare modeling
9. Limitations
No probabilistic reasoning
Limited disease and symptom coverage
No real-time streaming implementation
No deployed GraphDB backend
No LLM-based reasoning implementation
10. Future Work

Future versions may include:

Expanded disease coverage
Additional SWRL clinical rules
GraphDB deployment
CEP integration
LLM-based explanation generation
Integration of real-world healthcare datasets