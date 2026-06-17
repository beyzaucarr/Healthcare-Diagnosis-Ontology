"""
Healthcare Diagnosis Ontology v4
LLM Integration — Natural Language to SPARQL

Translates clinical questions into executable SPARQL queries using the
Claude API (claude-sonnet-4-6), then runs them against healthcare-v4.ttl.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 llm_integration_v4.py

Requirements:
    pip install rdflib requests
"""

import os
import re
import sys
import json
import textwrap
import requests
from rdflib import Graph, Namespace, RDF, RDFS

# ── Config ──────────────────────────────────────────────────────────────────
BASE     = "http://www.semanticweb.org/beyza/ontologies/2026/healthcare#"
TTL_PATH = "healthcare-v4.ttl"
API_URL  = "https://api.anthropic.com/v1/messages"
MODEL    = "claude-sonnet-4-6"
HDO      = Namespace(BASE)

SPARQL_PREFIX = f"""\
PREFIX hdo:  <{BASE}>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>

"""

# ── System prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = f"""\
You are a SPARQL 1.1 expert for the Healthcare Diagnosis Ontology v4.

NAMESPACE
  Ontology URI : http://www.semanticweb.org/beyza/ontologies/2026/healthcare
  Prefix       : hdo:  <{BASE}>

CLASSES (11)
  Patient, Disease, Symptom, Treatment, DiagnosticTest,
  ClinicalAlert, RiskAssessment, PatientObservation,
  DiagnosticRecommendation, ClinicalRule, Diagnosis

OBJECT PROPERTIES
  hdo:hasSymptom          Disease  → Symptom
  hdo:hasTreatment        Disease  → Treatment
  hdo:reportsSymptom      Patient  → Symptom
  hdo:possibleDiagnosis   Patient  → Disease          [inferred via property chain]
  hdo:requiresTest        Patient  → DiagnosticTest
  hdo:triggersAlert       Patient  → ClinicalAlert
  hdo:hasRecommendation   Patient  → DiagnosticRecommendation
  hdo:hasRiskAssessment   Patient  → RiskAssessment
  hdo:basedOnObservation  Patient  → PatientObservation

DATA PROPERTIES
  hdo:hasSymptomDuration   Patient       xsd:integer   (days, min 1)
  hdo:hasFeverStatus       Patient       xsd:string    ("Yes" | "No")
  hdo:hasRiskLevel         Patient       xsd:string    ("Low" | "Medium" | "High")
  hdo:hasAge               Patient       xsd:integer   (0–130)
  hdo:hasGender            Patient       xsd:string    ("Male" | "Female" | "Other")
  hdo:hasAlertMessage      ClinicalAlert xsd:string
  hdo:hasDOID              Disease       xsd:string
  hdo:hasDescription       Disease       xsd:string
  hdo:hasCategory          Disease       xsd:string

DISEASE CATEGORIES (10)
  Infectious, Respiratory, Metabolic, Cardiovascular, Neurological,
  Autoimmune, Hematological, Surgical, Renal, Musculoskeletal

PATIENTS (20)
  Ali, Ayse, Mehmet, Zeynep, Burak, Elif, Hasan, Selin, Murat, Fatma,
  Kemal, Nilufer, Tarik, Derya, Cemil, Pinar, Volkan, Aysun, Orhan, Gulsah

DISEASES (50 — sample)
  Infectious : Influenza, COVID19, Tuberculosis, Pneumonia, Dengue, Malaria,
               Cholera, Chickenpox, Typhoid, Hepatitis, Measles, Mumps,
               Rabies, Leptospirosis, Schistosomiasis
  Respiratory: Asthma, Bronchitis, COPD, PulmonaryFibrosis, SleepApnea
  Metabolic  : Diabetes, Hypothyroidism, Hyperthyroidism, Gout, Obesity
  Cardiovascular: Hypertension, HeartFailure, CoronaryArteryDisease, Stroke, Arrhythmia
  Neurological: Migraine, Alzheimer, Epilepsy, Parkinson, MultipleSclerosis, Meningitis
  Autoimmune : RheumatoidArthritis, Lupus, Psoriasis, CeliacDisease, Sarcoidosis
  Hematological: Anemia, Leukemia, Hemophilia
  Surgical   : Appendicitis, GallstoneDisease, KidneyStones, HerniatedDisc
  Renal      : KidneyDisease
  Musculoskeletal: Osteoporosis

SWRL RULE (simulated in SPARQL via FILTER)
  Patient(?p) AND hasSymptomDuration(?p, ?d) AND ?d > 13 AND hasFeverStatus(?p,"Yes")
  → requiresTest(?p, SputumTest)

OUTPUT RULES
  - Return ONLY the SPARQL SELECT query. No markdown fences, no explanation.
  - Do NOT include PREFIX declarations (they are added automatically).
  - Always use rdfs:label for human-readable output where available.
  - Use FILTER for numeric/string comparisons.
  - Use COUNT + GROUP BY for aggregation questions.
  - Use DISTINCT when duplicate rows are likely.
"""

# ── Demo questions ───────────────────────────────────────────────────────────
DEMO_QUESTIONS = [
    # Basic retrieval
    "Which patients have a high risk level?",
    "What treatments are available for Tuberculosis?",
    "What diagnostic test is assigned to each patient?",
    "Which patients have triggered a clinical alert? Show the alert message.",
    "What is the age, gender, and risk level of each patient?",
    # Reasoning
    "Which patients share at least one symptom with COVID-19?",
    "Which patients meet the SWRL rule conditions (symptom duration over 13 days and fever Yes)?",
    "Which high-risk patients are over 50 years old?",
    # Aggregation
    "How many symptoms does each disease have? Order by count descending.",
    "How many diseases are there in each clinical category?",
    "What is the average symptom duration per risk level?",
    "Which diseases have the Fatigue symptom?",
    # Advanced
    "Which Neurological diseases exist in the ontology?",
    "Which female patients have a high risk level?",
    "Which patients have been symptomatic for more than 30 days?",
]


# ── Core functions ────────────────────────────────────────────────────────────

def load_graph(path: str) -> Graph:
    """Load the healthcare ontology from Turtle file."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Ontology file not found: {path}\n"
            "Make sure healthcare-v4.ttl is in the current directory."
        )
    g = Graph()
    g.parse(path, format="turtle")
    g.bind("hdo", HDO)
    return g


def call_claude(question: str, api_key: str) -> str:
    """Send question to Claude API and return generated SPARQL query."""
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    body = {
        "model": MODEL,
        "max_tokens": 1024,
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": f"Translate this clinical question to SPARQL:\n{question}"}
        ],
    }
    resp = requests.post(API_URL, headers=headers, json=body, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"API error {resp.status_code}: {resp.text[:300]}")
    data = resp.json()
    raw = data["content"][0]["text"].strip()
    # Strip any markdown fences the model might add despite instructions
    raw = re.sub(r"```sparql\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```\s*", "", raw)
    raw = raw.strip()
    # Prepend standard prefixes
    return SPARQL_PREFIX + raw


def execute_sparql(g: Graph, sparql: str):
    """Execute a SPARQL query against the graph. Returns (rows, error)."""
    try:
        result = g.query(sparql)
        rows = list(result)
        return rows, result.vars, None
    except Exception as exc:
        return [], [], str(exc)


def format_results(rows, vars_, limit: int = 15) -> str:
    """Format SPARQL result rows as a readable table."""
    if not rows:
        return "  (no results)"
    # Header
    col_names = [str(v) for v in vars_] if vars_ else []
    lines = []
    if col_names:
        lines.append("  " + " | ".join(f"{c:<22}" for c in col_names))
        lines.append("  " + "-" * max(60, len(lines[0])))
    for row in rows[:limit]:
        vals = []
        for v in row:
            if v is None:
                vals.append("—")
            else:
                s = str(v)
                # Shorten URIs to local name
                if "#" in s:
                    s = s.split("#")[-1]
                vals.append(s[:22])
        lines.append("  " + " | ".join(f"{v:<22}" for v in vals))
    if len(rows) > limit:
        lines.append(f"  ... ({len(rows) - limit} more rows)")
    return "\n".join(lines)


def print_separator(title: str = ""):
    width = 70
    if title:
        pad = (width - len(title) - 2) // 2
        print(f"\n{'─'*pad} {title} {'─'*pad}")
    else:
        print("─" * width)


# ── Interactive mode ──────────────────────────────────────────────────────────

def interactive_mode(g: Graph, api_key: str):
    """Interactive REPL for asking natural language clinical questions."""
    print("\n" + "=" * 70)
    print("  Healthcare Diagnosis Ontology v4 — Interactive Query Mode")
    print("  Type a clinical question in English, or 'quit' to exit.")
    print("=" * 70)
    while True:
        try:
            question = input("\n  Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Exiting.")
            break
        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            print("  Goodbye.")
            break
        try:
            sparql = call_claude(question, api_key)
            print(f"\n  Generated SPARQL:")
            for line in sparql.strip().split("\n"):
                print(f"    {line}")
            rows, vars_, err = execute_sparql(g, sparql)
            if err:
                print(f"\n  ⚠ Query error: {err}")
            else:
                print(f"\n  Results ({len(rows)} rows):")
                print(format_results(rows, vars_))
        except Exception as exc:
            print(f"\n  ⚠ Error: {exc}")


# ── Demo mode ─────────────────────────────────────────────────────────────────

def demo_mode(g: Graph, api_key: str):
    """Run all 15 demo questions and print results."""
    print("\n" + "=" * 70)
    print("  Healthcare Diagnosis Ontology v4 — LLM Integration Demo")
    print(f"  Ontology: {TTL_PATH}  |  Triples: {len(g)}  |  Model: {MODEL}")
    print("=" * 70)

    passed = 0
    failed = 0

    for i, question in enumerate(DEMO_QUESTIONS, 1):
        print_separator(f"Q{i:02d}")
        print(f"  Question : {question}")

        try:
            sparql = call_claude(question, api_key)
            # Show only the meaningful SELECT ... WHERE part for brevity
            body_lines = [
                ln for ln in sparql.split("\n")
                if ln.strip() and not ln.startswith("PREFIX")
            ]
            print(f"  SPARQL   :")
            for ln in body_lines[:12]:
                print(f"    {ln}")
            if len(body_lines) > 12:
                print(f"    ... ({len(body_lines)-12} more lines)")

            rows, vars_, err = execute_sparql(g, sparql)
            if err:
                print(f"  ⚠ Error  : {err}")
                failed += 1
            else:
                print(f"  Results  : {len(rows)} rows")
                print(format_results(rows, vars_, limit=8))
                passed += 1

        except Exception as exc:
            print(f"  ⚠ API Error: {exc}")
            failed += 1

    print_separator()
    print(f"\n  Summary: {passed} passed, {failed} failed / {len(DEMO_QUESTIONS)} total")
    print_separator()


# ── Offline demo (no API key) ─────────────────────────────────────────────────

OFFLINE_QUERIES = {
    "Which patients have a high risk level?": """\
SELECT ?patientLabel ?age ?gender ?feverStatus
WHERE {
  ?p rdf:type hdo:Patient .
  ?p rdfs:label ?patientLabel .
  ?p hdo:hasRiskLevel "High" .
  ?p hdo:hasAge ?age .
  ?p hdo:hasGender ?gender .
  ?p hdo:hasFeverStatus ?feverStatus .
}
ORDER BY DESC(?age)""",

    "What treatments are available for Tuberculosis?": """\
SELECT ?treatmentLabel
WHERE {
  hdo:Tuberculosis hdo:hasTreatment ?t .
  ?t rdfs:label ?treatmentLabel .
}""",

    "Which patients meet the SWRL rule conditions (symptom duration over 13 days and fever Yes)?": """\
SELECT ?patientLabel ?duration ?feverStatus ?riskLevel
WHERE {
  ?p rdf:type hdo:Patient .
  ?p rdfs:label ?patientLabel .
  ?p hdo:hasSymptomDuration ?duration .
  ?p hdo:hasFeverStatus ?feverStatus .
  ?p hdo:hasRiskLevel ?riskLevel .
  FILTER (?duration > 13 && ?feverStatus = "Yes")
}
ORDER BY DESC(?duration)""",

    "How many symptoms does each disease have? Order by count descending.": """\
SELECT ?diseaseLabel (COUNT(?s) AS ?symptomCount)
WHERE {
  ?d rdf:type hdo:Disease .
  ?d rdfs:label ?diseaseLabel .
  ?d hdo:hasSymptom ?s .
}
GROUP BY ?diseaseLabel
ORDER BY DESC(?symptomCount)""",

    "How many diseases are there in each clinical category?": """\
SELECT ?category (COUNT(?d) AS ?diseaseCount)
WHERE {
  ?d rdf:type hdo:Disease .
  ?d hdo:hasCategory ?category .
}
GROUP BY ?category
ORDER BY DESC(?diseaseCount)""",
}


def offline_demo(g: Graph):
    """Run key queries without the Claude API — for testing and demonstration."""
    print("\n" + "=" * 70)
    print("  Healthcare Diagnosis Ontology v4 — Offline Demo (no API key)")
    print(f"  Ontology: {TTL_PATH}  |  Triples: {len(g)}")
    print("=" * 70)

    for i, (question, sparql_body) in enumerate(OFFLINE_QUERIES.items(), 1):
        print_separator(f"Q{i:02d}")
        print(f"  Question : {question}")
        full_sparql = SPARQL_PREFIX + sparql_body
        rows, vars_, err = execute_sparql(g, full_sparql)
        if err:
            print(f"  ⚠ Error  : {err}")
        else:
            print(f"  Results  : {len(rows)} rows")
            print(format_results(rows, vars_, limit=10))

    print_separator()
    print(f"\n  Offline demo complete — {len(OFFLINE_QUERIES)} queries executed.")
    print_separator()


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    print("Healthcare Diagnosis Ontology v4 — LLM Integration")
    print(f"Loading {TTL_PATH}...")

    try:
        g = load_graph(TTL_PATH)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    from rdflib import RDF, Namespace
    HDO_NS = Namespace(BASE)
    n_diseases  = len(list(g.subjects(RDF.type, HDO_NS.Disease)))
    n_patients  = len(list(g.subjects(RDF.type, HDO_NS.Patient)))
    n_symptoms  = len(list(g.subjects(RDF.type, HDO_NS.Symptom)))
    print(f"Loaded {len(g)} triples — "
          f"{n_diseases} diseases, {n_patients} patients, {n_symptoms} symptoms\n")

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()

    if not api_key:
        print("⚠  ANTHROPIC_API_KEY not set.")
        print("   Running offline demo with pre-defined queries.\n")
        offline_demo(g)
        print("\nTo enable full LLM translation, run:")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        print("  python3 llm_integration_v4.py\n")
        return

    # Choose mode from command-line arg
    mode = sys.argv[1] if len(sys.argv) > 1 else "demo"
    if mode == "interactive":
        interactive_mode(g, api_key)
    else:
        demo_mode(g, api_key)


if __name__ == "__main__":
    main()
