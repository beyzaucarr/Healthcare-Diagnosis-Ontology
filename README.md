# Healthcare Diagnosis Ontology v4

> An OWL 2 knowledge graph for clinical decision support — 50 diseases, 20 patients, 1,925 RDF triples.

---

## Team

| Name | Student ID | University | Email |
|---|---|---|---|
| Beyza Ucar | 220316060 | Manisa Celal Bayar University | beyza@mcbu.edu.tr |

---

## Project Summary

| Metric | Value |
|---|---|
| Total RDF Triples | 1,925 |
| Diseases | 50 |
| Symptoms | 103 |
| Treatments | 99 |
| Patients | 20 |
| Diagnostic Tests | 25 |
| Clinical Alerts | 12 |
| OWL Classes | 11 |
| Object Properties | 9 |
| Data Properties | 9 |
| SPARQL Queries | 20 (all passing) |
| SHACL Shapes | 7 (Conforms: True) |
| Disease Categories | 10 |

---

## Repository Structure

```
Healthcare-Diagnosis-Ontology/
│
├── ontology/
│   └── healthcare-v4.ttl              # Main OWL 2 ontology (Turtle format)
│
├── data/
│   └── diseases50.csv                 # 50-disease dataset (DOID references)
│
├── queries/
│   └── sparql-v4.rq                   # 20 SPARQL queries (basic, reasoning, aggregation)
│
├── validation/
│   └── shacl-v4.ttl                   # 7 SHACL constraint shapes
│
├── src/
│   ├── kg_builder_v4.py               # RDFLib KG builder + all 20 SPARQL queries
│   └── llm_integration_v4.py          # Claude API NL→SPARQL pipeline
│
├── docs/
│   └── widoco-docs/
│       └── index.html                 # WIDOCO-style ontology documentation
│
├── report/
│   ├── report-final.pdf               # Project report (PDF — for submission)
│   └── report-final.docx              # Project report (Word)
│
├── presentation/
│   └── presentation-final.pptx        # 11-slide presentation
│
└── README.md
```

---

## Dataset

Primary source: **Human Disease Ontology (DOID)**
> Schriml, L. M., et al. (2022). Human Disease Ontology 2022 update. *Nucleic Acids Research*, 50(D1), D1305–D1310. https://doi.org/10.1093/nar/gkab1063

### Disease Categories

| Category | Count | Example Diseases |
|---|---|---|
| Infectious | 15 | Influenza, COVID-19, Tuberculosis, Dengue, Malaria, Cholera ... |
| Neurological | 6 | Migraine, Alzheimer, Epilepsy, Parkinson, MultipleSclerosis, Meningitis |
| Autoimmune | 5 | RheumatoidArthritis, Lupus, Psoriasis, CeliacDisease, Sarcoidosis |
| Cardiovascular | 5 | Hypertension, HeartFailure, CoronaryArteryDisease, Stroke, Arrhythmia |
| Metabolic | 5 | Diabetes, Hypothyroidism, Hyperthyroidism, Gout, Obesity |
| Respiratory | 5 | Asthma, Bronchitis, COPD, PulmonaryFibrosis, SleepApnea |
| Hematological | 3 | Anemia, Leukemia, Hemophilia |
| Surgical | 4 | Appendicitis, GallstoneDisease, KidneyStones, HerniatedDisc |
| Renal | 1 | KidneyDisease |
| Musculoskeletal | 1 | Osteoporosis |

---

## Installation & Setup

### Requirements

```bash
pip install rdflib pyshacl requests
```

### Run Knowledge Graph Builder (all 20 SPARQL queries)

```bash
cd src/
python3 kg_builder_v4.py
```

Expected output: 20/20 queries passing, triple count printed, KG serialized.

### Run SHACL Validation

```bash
python3 - << 'PYEOF'
import pyshacl
from rdflib import Graph

data_g = Graph().parse("ontology/healthcare-v4.ttl", format="turtle")
shacl_g = Graph().parse("validation/shacl-v4.ttl", format="turtle")
conforms, _, text = pyshacl.validate(
    data_g, shacl_graph=shacl_g, inference="rdfs", abort_on_first=False
)
print("Conforms:", conforms)   # → True
PYEOF
```

### Run LLM Integration (requires API key)

```bash
export ANTHROPIC_API_KEY=sk-ant-...

# Demo mode — runs 15 preset questions
python3 src/llm_integration_v4.py

# Interactive mode — ask your own questions
python3 src/llm_integration_v4.py interactive
```

Without an API key, the script automatically runs an **offline demo** with 5 pre-defined queries against the local knowledge graph — no internet required.

---

## Core Ontology Design

### Namespace

```
Base URI : http://www.semanticweb.org/beyza/ontologies/2026/healthcare
Prefix   : hdo:  <http://www.semanticweb.org/beyza/ontologies/2026/healthcare#>
```

### Key Inference — OWL 2 Property Chain Axiom

```
reportsSymptom ∘ inverse(hasSymptom) ⊑ possibleDiagnosis
```

If a patient reports symptom S **and** a disease has symptom S → the OWL reasoner (HermiT) automatically infers that disease as a **possible diagnosis**. No manual assertion required.

### SWRL Clinical Rule

```
Patient(?p) ∧ hasSymptomDuration(?p, ?d) ∧ swrlb:greaterThan(?d, 13)
           ∧ hasFeverStatus(?p, "Yes")
           → requiresTest(?p, SputumTest)
```

Fires for: **Ali** (14 days, fever Yes) and **Selin** (45 days, fever Yes).

---

## SPARQL Query Examples

### Q10 — SWRL Rule Simulation

```sparql
PREFIX hdo: <http://www.semanticweb.org/beyza/ontologies/2026/healthcare#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?patientLabel ?duration ?feverStatus ?riskLevel
WHERE {
  ?p rdf:type hdo:Patient .
  ?p rdfs:label ?patientLabel .
  ?p hdo:hasSymptomDuration ?duration .
  ?p hdo:hasFeverStatus ?feverStatus .
  ?p hdo:hasRiskLevel ?riskLevel .
  FILTER (?duration > 13 && ?feverStatus = "Yes")
}
ORDER BY DESC(?duration)
```

Result: Ali (14 d, Medium), Selin (45 d, Medium), Gulsah (35 d, High)

### Q13 — Disease Count per Category

```sparql
SELECT ?category (COUNT(?d) AS ?diseaseCount)
WHERE {
  ?d rdf:type hdo:Disease .
  ?d hdo:hasCategory ?category .
}
GROUP BY ?category
ORDER BY DESC(?diseaseCount)
```

---

## SHACL Validation Summary

| Shape | Target | Key Constraints |
|---|---|---|
| PatientShape | Patient | 8 constraints: min 1 symptom; riskLevel ∈ {Low,Medium,High}; feverStatus ∈ {Yes,No}; age 0–130; gender ∈ {Male,Female,Other}; min 1 test; min 1 recommendation |
| DiseaseShape | Disease | 5 constraints: 2–10 symptoms; min 1 treatment; exactly 1 DOID; valid category |
| ClinicalAlertShape | ClinicalAlert | alert message ≥ 10 chars |
| DiagnosticTestShape | DiagnosticTest | must have rdfs:label |
| DiagnosticRecommendationShape | DiagnosticRecommendation | must have rdfs:label |
| SymptomShape | Symptom | must have rdfs:label |
| TreatmentShape | Treatment | must have rdfs:label |

**Validation result: Conforms: True — zero violations across 1,925 triples** ✅

---

## LLM Integration

### Architecture (3-stage pipeline)

```
Natural Language Question
        ↓
Claude API (claude-sonnet-4-6)
  — Schema-constrained system prompt
  — 50 diseases, 20 patients, all properties listed
        ↓
SPARQL Query
        ↓
RDFLib Execution against healthcare-v4.ttl
        ↓
Structured Result
```

### Hallucination Mitigation

- System prompt explicitly lists all 50 disease names, 20 patient names, valid categories and property names
- Generated SPARQL is immediately validated by RDFLib execution
- Schema-anchored generation prevents fabrication of non-existent entities

---

## Tools Used

| Tool | Purpose |
|---|---|
| Protégé 5.6 | Ontology editing, HermiT OWL 2 reasoning, SWRL rules (SWRLTab) |
| HermiT Reasoner | OWL 2 DL property chain evaluation |
| RDFLib 7.x | KG construction, SPARQL execution, TTL serialization |
| pyshacl | SHACL constraint validation |
| Disease Ontology (DOID) | Reference disease dataset |
| Claude API (claude-sonnet-4-6) | NL→SPARQL translation |

---

## Research Reference

This project integrates architectural components from:

> Real-Time Health Analytics Using Ontology-Driven Complex Event Processing and LLM Reasoning: A Tuberculosis Case Study

Adapted components: ontology-driven healthcare modelling, SWRL-based clinical reasoning, RDF semantic representation, SPARQL querying, diagnostic recommendation modelling, clinical alert reasoning.

---

## Links

- **GitHub Repository:** https://github.com/beyzaucarr/Healthcare-Diagnosis-Ontology
- **WIDOCO Documentation:** https://beyzaucarr.github.io/Healthcare-Diagnosis-Ontology/
- **Report (PDF):** report/report-final.pdf

---

## License

Academic project — Manisa Celal Bayar University, Department of Computer Engineering, 2025–2026.
