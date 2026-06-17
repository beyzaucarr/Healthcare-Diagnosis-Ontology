# Healthcare Diagnosis Ontology v4

# Specification Document (Version 4)

---

## 1. Domain Description

The Healthcare Diagnosis Ontology (HDO) v4 models a healthcare diagnosis and clinical decision support domain using Semantic Web technologies. It represents relationships between patients, symptoms, diseases, treatments, diagnostic tests, clinical alerts, risk-related clinical data, diagnostic recommendations, and patient observations.

The ontology is designed to support explainable clinical reasoning rather than black-box prediction. It uses OWL 2 DL for formal modeling, an OWL property chain axiom for possible diagnosis inference, SWRL-style clinical rule logic for diagnostic test assignment, SPARQL 1.1 for semantic querying, SHACL for data quality validation, and an LLM-based natural language interface for translating user questions into SPARQL queries.

Version 4 extends the earlier simplified diagnosis ontology into a larger, reproducible knowledge graph containing 50 diseases, 103 symptoms, 99 treatments, 20 patients, 25 diagnostic tests, 12 clinical alerts, 12 diagnostic recommendations, and 1,925 RDF triples.

---

## 2. Scope and Objectives

### 2.1 Scope

The ontology focuses on:

- Representing patient profiles and reported symptoms
- Linking diseases to their associated symptoms, treatments, DOID identifiers, descriptions, and clinical categories
- Inferring possible diagnoses from symptom overlap using OWL property-chain reasoning
- Representing diagnostic tests, clinical alerts, risk information, patient observations, and diagnostic recommendations
- Supporting clinical rule logic using SWRL-style conditions
- Querying the knowledge graph using SPARQL
- Validating data quality using SHACL shapes
- Supporting natural language access through an LLM-based NL-to-SPARQL workflow
- Providing ontology documentation through WIDOCO and reproducible project files through GitHub

### 2.2 Objectives

The main objectives of HDO v4 are:

1. To provide a structured semantic representation of healthcare diagnosis knowledge.
2. To model 50 diseases and their symptoms, treatments, identifiers, descriptions, and categories.
3. To represent 20 patient individuals with age, gender, fever status, risk level, symptom duration, reported symptoms, alerts, tests, and recommendations.
4. To enable possible diagnosis inference using OWL property-chain reasoning.
5. To support rule-based diagnostic test assignment using SWRL-style clinical conditions.
6. To provide a set of SPARQL queries that answer the competency questions of the ontology.
7. To validate the consistency and completeness of the knowledge graph using SHACL.
8. To integrate an LLM-based natural language interface that generates SPARQL queries while grounding answers in the knowledge graph.
9. To support reproducibility through source code, RDF/Turtle files, SHACL files, SPARQL queries, documentation, and a public GitHub repository.

---

## 3. Core Concepts and Relationships

## 3.1 Classes

HDO v4 defines 11 main OWL classes.

| Class | Description |
|---|---|
| `Patient` | Represents an individual receiving medical attention. Patients have demographic and clinical profile data and report symptoms. |
| `Disease` | Represents a medical condition associated with symptoms, treatments, DOID identifiers, descriptions, and categories. |
| `Symptom` | Represents an observable clinical condition reported by a patient or associated with a disease. |
| `Treatment` | Represents a medical intervention applicable to a disease. |
| `Diagnosis` | Represents a diagnosis-related concept, especially inferred possible diagnosis relationships. |
| `DiagnosticTest` | Represents a medical diagnostic test assigned to a patient. |
| `RiskAssessment` | Represents patient risk-related evaluation. |
| `ClinicalAlert` | Represents a clinical warning or alert triggered for a patient. |
| `PatientObservation` | Represents structured clinical observation information. |
| `DiagnosticRecommendation` | Represents a recommended clinical action, test, or referral. |
| `ClinicalRule` | Represents rule-based clinical reasoning logic. |

---

## 3.2 Object Properties

| Object Property | Domain | Range | Purpose |
|---|---|---|---|
| `reportsSymptom` | `Patient` | `Symptom` | Links a patient to symptoms they report. |
| `hasSymptom` | `Disease` | `Symptom` | Links a disease to its characteristic symptoms. |
| `hasTreatment` | `Disease` | `Treatment` | Links a disease to applicable treatments. |
| `possibleDiagnosis` | `Patient` | `Disease` | Represents possible diseases inferred for a patient. |
| `requiresTest` | `Patient` | `DiagnosticTest` | Links a patient to a required diagnostic test. |
| `triggersAlert` | `Patient` | `ClinicalAlert` | Links a patient to a triggered clinical alert. |
| `hasRecommendation` | `Patient` | `DiagnosticRecommendation` | Links a patient to a diagnostic or clinical recommendation. |
| `hasRiskAssessment` | `Patient` | `RiskAssessment` | Links a patient to a risk assessment entity. |
| `basedOnObservation` | `Patient` | `PatientObservation` | Links a patient to a structured observation. |

---

## 3.3 Data Properties

| Data Property | Domain | Range / Expected Value | Purpose |
|---|---|---|---|
| `hasAge` | `Patient` | `xsd:integer` | Stores the patient age. |
| `hasGender` | `Patient` | `"Male"`, `"Female"`, or `"Other"` | Stores the patient gender. |
| `hasRiskLevel` | `Patient` | `"Low"`, `"Medium"`, or `"High"` | Stores the patient clinical risk level. |
| `hasFeverStatus` | `Patient` | `"Yes"` or `"No"` | Indicates whether the patient has fever. |
| `hasSymptomDuration` | `Patient` | `xsd:integer` | Stores symptom duration in days. |
| `hasAlertMessage` | `ClinicalAlert` | `xsd:string` | Stores the textual alert message. |
| `hasDOID` | `Disease` | `xsd:string` | Stores the Disease Ontology identifier. |
| `hasDescription` | `Disease` | `xsd:string` | Stores a textual disease description. |
| `hasCategory` | `Disease` | `xsd:string` | Stores the disease category. |

---

## 4. Inference Model

## 4.1 OWL Property Chain Reasoning

The main diagnosis inference mechanism is the following OWL property chain axiom:

```text
reportsSymptom o inverse(hasSymptom) subPropertyOf possibleDiagnosis
```

Meaning:

```text
If a patient reports a symptom,
and a disease has the same symptom,
then that disease can be inferred as a possible diagnosis for the patient.
```

Example:

```text
Ali reportsSymptom Cough.
Tuberculosis hasSymptom Cough.
Therefore, Ali possibleDiagnosis Tuberculosis.
```

This inference is explainable because the inferred diagnosis can be traced back to the shared symptom relationship.

---

## 4.2 SWRL-Style Clinical Rule Logic

HDO v4 also includes rule-based clinical decision support. The main clinical rule used in the project is:

```text
Patient(?p) ^
hasSymptomDuration(?p, ?d) ^
swrlb:greaterThan(?d, 13) ^
hasFeverStatus(?p, "Yes")
→ requiresTest(?p, SputumTest)
```

Meaning:

```text
If a patient has symptoms for more than 13 days
and the patient has fever,
then the patient requires a Sputum Test.
```

In the RDFLib execution environment, this logic can also be simulated using SPARQL `FILTER` conditions because RDFLib does not natively execute SWRL rules.

---

## 5. Knowledge Graph Construction

The knowledge graph is serialized in RDF/Turtle format as:

```text
healthcare-v4.ttl
```

The graph contains:

| Metric | Value |
|---|---:|
| RDF triples | 1,925 |
| Diseases | 50 |
| Symptoms | 103 |
| Treatments | 99 |
| Patients | 20 |
| Diagnostic tests | 25 |
| Clinical alerts | 12 |
| Diagnostic recommendations | 12 |
| Disease categories | 10 |
| OWL classes | 11 |
| Object properties | 9 |
| Data properties | 9 |

The knowledge graph is generated and queried using RDFLib through:

```text
kg_builder_v4.py
```

Representative RDF/Turtle example:

```turtle
hdo:Ali rdf:type hdo:Patient ;
    rdfs:label "Ali" ;
    hdo:hasAge "35"^^xsd:integer ;
    hdo:hasGender "Male" ;
    hdo:hasRiskLevel "Medium" ;
    hdo:hasFeverStatus "Yes" ;
    hdo:hasSymptomDuration "14"^^xsd:integer ;
    hdo:reportsSymptom hdo:Cough, hdo:Fever, hdo:NightSweats ;
    hdo:requiresTest hdo:SputumTest ;
    hdo:triggersAlert hdo:TBAlert .
```

---

## 6. Data Acquisition

The disease component of the ontology is based on disease concepts and identifiers from the Human Disease Ontology (DOID). The project uses 50 selected diseases organized into 10 clinical categories:

- Infectious
- Respiratory
- Metabolic
- Cardiovascular
- Neurological
- Autoimmune
- Hematological
- Surgical
- Renal
- Musculoskeletal

The project dataset is represented as:

```text
diseases50.csv
```

The preprocessing and modeling process includes:

1. Selecting relevant diseases and assigning DOID identifiers.
2. Adding disease descriptions and clinical categories.
3. Associating diseases with symptoms and treatments.
4. Normalizing entity names for RDF-compatible identifiers.
5. Creating patient examples with demographic and clinical profile data.
6. Transforming the structured data into RDF triples.
7. Validating the resulting RDF graph with SHACL.

---

## 7. Competency Questions

The ontology is designed to answer the following competency questions:

1. Which diseases can be inferred as possible diagnoses from a patient's reported symptoms?
2. Which patients share symptoms with a specific disease?
3. What symptoms are associated with a given disease?
4. Which patients require a diagnostic test, and which test is assigned?
5. Which patients have triggered a clinical alert, and what is the alert message?
6. What treatments are available for a given disease?
7. How many symptoms does each disease have, and how do diseases rank by symptom count?
8. Which diseases belong to a given clinical category?
9. Which patients meet the SWRL-style rule conditions for extended symptomatic fever?
10. Which elderly high-risk patients require advanced diagnostic testing?

---

## 8. SPARQL Query Support

HDO v4 includes 20 SPARQL queries stored in:

```text
sparql-v4.rq
```

The queries are grouped into three categories.

### 8.1 Basic Retrieval Queries

Examples include:

- Disease to symptoms
- Patient to reported symptoms
- Patient to required diagnostic test
- Patient to triggered clinical alert and alert message
- Patient full clinical profile
- Disease to treatments
- Disease DOID and category
- Patient to diagnostic recommendations

### 8.2 Reasoning-Oriented Queries

Examples include:

- Patients sharing symptoms with Tuberculosis
- Patients matching the SWRL-style rule condition
- High-risk patients over age 50
- Diseases sharing symptom patterns with patient reports

### 8.3 Aggregation Queries

Examples include:

- Symptom count per disease
- Disease count per category
- Average symptom duration per risk level
- Patient count by fever status
- Treatment count per disease

---

## 9. SHACL Validation

The knowledge graph is validated using SHACL shapes stored in:

```text
shacl-v4.ttl
```

The SHACL validation layer checks data quality constraints such as:

- Required patient properties
- Correct datatypes for age and symptom duration
- Valid value ranges for age and symptom duration
- Valid categorical values for gender, fever status, and risk level
- Required labels for important entities
- Disease identifiers and category completeness
- Alert message completeness

Validation result:

```text
Conforms: True
```

This means the knowledge graph satisfies the defined SHACL constraints.

---

## 10. LLM Integration

HDO v4 includes an LLM integration layer implemented in:

```text
llm_integration_v4.py
```

The LLM workflow is:

```text
User natural language question
        ↓
Prompt with ontology schema and allowed properties
        ↓
LLM generates SPARQL SELECT query
        ↓
SPARQL query is executed against healthcare-v4.ttl using RDFLib
        ↓
Results are returned from the knowledge graph
```

The integration is designed to reduce hallucinations by:

- Providing the LLM with the ontology namespace, classes, object properties, data properties, patient names, disease categories, and example disease names
- Requiring the LLM to return only SPARQL SELECT queries
- Executing the query against the RDF knowledge graph
- Using the graph as the source of truth
- Returning only results grounded in the ontology data
- Providing an offline demo mode when the API key is unavailable

The LLM is not treated as the source of medical truth. It functions only as a natural language interface to the structured knowledge graph.

---

## 11. Intended Use Cases

HDO v4 can be used for:

- Educational demonstration of ontology engineering and Semantic Web technologies
- Explainable clinical decision support prototypes
- Semantic healthcare knowledge modeling
- OWL property-chain reasoning demonstration
- SWRL-style clinical rule demonstration
- SPARQL-based healthcare data exploration
- SHACL-based data quality validation
- LLM-grounded natural language querying over a knowledge graph

---

## 12. Design Considerations

The main design decisions are:

1. `Disease`, `Patient`, `Symptom`, `Treatment`, `DiagnosticTest`, and alert-related concepts are modeled as classes because they represent categories of entities.
2. Individual diseases, symptoms, treatments, and patients are modeled as named individuals in the ABox.
3. `reportsSymptom` and `hasSymptom` are separated because one describes patient observations and the other describes disease definitions.
4. `possibleDiagnosis` is inferred rather than manually asserted where possible, improving explainability and reducing manual inconsistency.
5. Data properties are used only for literal values such as age, gender, fever status, risk level, duration, identifiers, and descriptions.
6. Object properties are used for semantic relationships between ontology individuals.
7. SHACL is used for closed-world validation, complementing OWL's open-world reasoning.
8. LLM integration is limited to query generation and does not replace ontology reasoning or structured data validation.
9. The ontology keeps the model extensible by avoiding overly restrictive disjointness axioms at this stage.

---

## 13. Changes from Version 2 to Version 4

Version 4 introduces major extensions compared with Version 2.

### Newly Added or Expanded Features

- Expanded the disease dataset from a small demonstration set to 50 diseases.
- Increased symptom coverage to 103 symptom individuals.
- Increased treatment coverage to 99 treatment individuals.
- Added 20 patient individuals with structured clinical profiles.
- Added 25 diagnostic tests.
- Added 12 clinical alerts and 12 diagnostic recommendations.
- Organized diseases into 10 clinical categories.
- Added DOID identifiers and disease descriptions.
- Added 20 SPARQL queries.
- Added 7 SHACL validation shapes.
- Added LLM-based natural language to SPARQL integration.
- Added WIDOCO ontology documentation.
- Added public GitHub repository organization for reproducibility.
- Added report, presentation, demo transcript, source code, ontology files, validation files, and query files.

### Improved Technical Capabilities

- More complete knowledge graph construction using RDFLib
- More extensive query coverage
- Explicit validation workflow
- Stronger documentation and reproducibility
- More explainable architecture combining OWL, SWRL-style rules, SHACL, SPARQL, and LLMs

---

## 14. Limitations

The current version has the following limitations:

- The ontology is an educational clinical decision support prototype, not a real medical diagnosis system.
- Patient data is manually authored and does not represent real patient records.
- Disease-symptom relationships are simplified and do not include probabilistic weighting.
- The system does not calculate disease likelihood scores.
- RDFLib does not execute SWRL rules natively, so SWRL-style conditions may be demonstrated using SPARQL filters in Python.
- Some inferred relationships may require a reasoner such as HermiT or materialized inference output.
- The LLM interface depends on prompt quality and API availability.
- The ontology does not include real-time clinical data streams.
- The current model does not include detailed medication dosage, contraindication, or treatment plan logic.

---

## 15. Future Work

Future versions may include:

- Integration with larger biomedical ontologies and external linked data sources
- GraphDB or Fuseki deployment with persistent SPARQL endpoint support
- Exporting materialized inferred triples from a reasoner
- Additional SWRL clinical rules
- Disease likelihood scoring based on weighted symptoms
- More detailed patient history and clinical observation modeling
- Support for multilingual natural language questions
- Integration with FHIR-compatible healthcare data
- More advanced SHACL validation reports
- Web-based user interface for SPARQL and LLM interaction
- Expanded WIDOCO documentation with diagrams and more usage examples

---

## 16. Repository and Documentation

The final project repository contains ontology files, source code, SPARQL queries, SHACL validation files, dataset samples, documentation, report, and presentation materials.

```text
GitHub Repository:
https://github.com/beyzaucarr/Healthcare-Diagnosis-Ontology

WIDOCO Documentation:
https://beyzaucarr.github.io/Healthcare-Diagnosis-Ontology/widoco-docs/
```

Recommended repository location for this specification file:

```text
docs/specification-v4.md
```
