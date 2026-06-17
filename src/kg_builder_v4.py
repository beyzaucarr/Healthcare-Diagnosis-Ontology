"""
Healthcare Diagnosis Knowledge Graph Builder — v4
50 diseases | 20 patients | 103 symptoms | 99 treatments | 1,925 triples
Usage: python3 kg_builder_v4.py
"""
from rdflib import Graph, Namespace, RDF, RDFS

BASE = "http://www.semanticweb.org/beyza/ontologies/2026/healthcare#"
HDO  = Namespace(BASE)
TTL  = "healthcare-v4.ttl"

P = f"""PREFIX hdo: <{BASE}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""

QUERIES = {
    "Q1  Disease → Symptoms": P + """
SELECT ?diseaseLabel ?symptomLabel
WHERE { ?d rdf:type hdo:Disease . ?d rdfs:label ?diseaseLabel .
        ?d hdo:hasSymptom ?s . ?s rdfs:label ?symptomLabel . }
ORDER BY ?diseaseLabel""",

    "Q2  Patient → Reported Symptoms": P + """
SELECT ?patientLabel ?symptomLabel
WHERE { ?p rdf:type hdo:Patient . ?p rdfs:label ?patientLabel .
        ?p hdo:reportsSymptom ?s . ?s rdfs:label ?symptomLabel . }
ORDER BY ?patientLabel""",

    "Q3  Patient → Required Test": P + """
SELECT ?patientLabel ?testLabel
WHERE { ?p rdf:type hdo:Patient . ?p rdfs:label ?patientLabel .
        ?p hdo:requiresTest ?t . ?t rdfs:label ?testLabel . }
ORDER BY ?patientLabel""",

    "Q4  Patient → Clinical Alert + Message": P + """
SELECT ?patientLabel ?alertLabel ?message
WHERE { ?p rdf:type hdo:Patient . ?p rdfs:label ?patientLabel .
        ?p hdo:triggersAlert ?a . ?a rdfs:label ?alertLabel .
        ?a hdo:hasAlertMessage ?message . }
ORDER BY ?patientLabel""",

    "Q5  Patient Full Clinical Profile": P + """
SELECT ?patientLabel ?age ?gender ?riskLevel ?feverStatus ?duration
WHERE { ?p rdf:type hdo:Patient . ?p rdfs:label ?patientLabel .
        ?p hdo:hasAge ?age . ?p hdo:hasGender ?gender .
        ?p hdo:hasRiskLevel ?riskLevel . ?p hdo:hasFeverStatus ?feverStatus .
        ?p hdo:hasSymptomDuration ?duration . }
ORDER BY DESC(?duration)""",

    "Q6  Disease → Treatments": P + """
SELECT ?diseaseLabel ?treatmentLabel
WHERE { ?d rdf:type hdo:Disease . ?d rdfs:label ?diseaseLabel .
        ?d hdo:hasTreatment ?t . ?t rdfs:label ?treatmentLabel . }
ORDER BY ?diseaseLabel""",

    "Q7  Disease DOID + Category": P + """
SELECT ?diseaseLabel ?doid ?category
WHERE { ?d rdf:type hdo:Disease . ?d rdfs:label ?diseaseLabel .
        ?d hdo:hasDOID ?doid . ?d hdo:hasCategory ?category . }
ORDER BY ?category ?diseaseLabel""",

    "Q8  Patient → Recommendations": P + """
SELECT ?patientLabel ?recLabel
WHERE { ?p rdf:type hdo:Patient . ?p rdfs:label ?patientLabel .
        ?p hdo:hasRecommendation ?r . ?r rdfs:label ?recLabel . }
ORDER BY ?patientLabel""",

    "Q9  Patients sharing TB symptoms": P + """
SELECT DISTINCT ?patientLabel ?sharedSymptom
WHERE { hdo:Tuberculosis hdo:hasSymptom ?sym . ?sym rdfs:label ?sharedSymptom .
        ?p rdf:type hdo:Patient . ?p rdfs:label ?patientLabel .
        ?p hdo:reportsSymptom ?sym . }
ORDER BY ?patientLabel""",

    "Q10 SWRL rule match (duration>13 AND fever=Yes)": P + """
SELECT ?patientLabel ?duration ?feverStatus ?riskLevel ?age
WHERE { ?p rdf:type hdo:Patient . ?p rdfs:label ?patientLabel .
        ?p hdo:hasSymptomDuration ?duration . ?p hdo:hasFeverStatus ?feverStatus .
        ?p hdo:hasRiskLevel ?riskLevel . ?p hdo:hasAge ?age .
        FILTER (?duration > 13 && ?feverStatus = "Yes") }
ORDER BY DESC(?duration)""",

    "Q11 High risk + age > 50": P + """
SELECT ?patientLabel ?age ?riskLevel ?testLabel
WHERE { ?p rdf:type hdo:Patient . ?p rdfs:label ?patientLabel .
        ?p hdo:hasAge ?age . ?p hdo:hasRiskLevel ?riskLevel .
        ?p hdo:requiresTest ?t . ?t rdfs:label ?testLabel .
        FILTER (?age > 50 && ?riskLevel = "High") }
ORDER BY DESC(?age)""",

    "Q12 Symptom count per disease (AGG)": P + """
SELECT ?diseaseLabel (COUNT(?s) AS ?symptomCount)
WHERE { ?d rdf:type hdo:Disease . ?d rdfs:label ?diseaseLabel .
        ?d hdo:hasSymptom ?s . }
GROUP BY ?diseaseLabel ORDER BY DESC(?symptomCount)""",

    "Q13 Disease count per category (AGG)": P + """
SELECT ?category (COUNT(?d) AS ?diseaseCount)
WHERE { ?d rdf:type hdo:Disease . ?d hdo:hasCategory ?category . }
GROUP BY ?category ORDER BY DESC(?diseaseCount)""",

    "Q14 Patient count per risk level (AGG)": P + """
SELECT ?riskLevel (COUNT(?p) AS ?patientCount)
WHERE { ?p rdf:type hdo:Patient . ?p hdo:hasRiskLevel ?riskLevel . }
GROUP BY ?riskLevel ORDER BY DESC(?patientCount)""",

    "Q15 Avg symptom duration per risk level (AGG)": P + """
SELECT ?riskLevel (AVG(?d) AS ?avgDuration)
WHERE { ?p rdf:type hdo:Patient . ?p hdo:hasRiskLevel ?riskLevel .
        ?p hdo:hasSymptomDuration ?d . }
GROUP BY ?riskLevel ORDER BY DESC(?avgDuration)""",

    "Q16 Diseases sharing Fatigue symptom": P + """
SELECT ?diseaseLabel ?category
WHERE { ?d rdf:type hdo:Disease . ?d rdfs:label ?diseaseLabel .
        ?d hdo:hasCategory ?category .
        ?d hdo:hasSymptom ?s . ?s rdfs:label "Fatigue" . }
ORDER BY ?category""",

    "Q17 Infectious diseases with >5 symptoms (AGG)": P + """
SELECT ?diseaseLabel (COUNT(?s) AS ?n)
WHERE { ?d rdf:type hdo:Disease . ?d rdfs:label ?diseaseLabel .
        ?d hdo:hasCategory "Infectious" . ?d hdo:hasSymptom ?s . }
GROUP BY ?diseaseLabel HAVING (COUNT(?s) > 5) ORDER BY DESC(?n)""",

    "Q18 Female patients with High risk": P + """
SELECT ?patientLabel ?age ?feverStatus ?duration
WHERE { ?p rdf:type hdo:Patient . ?p rdfs:label ?patientLabel .
        ?p hdo:hasGender "Female" . ?p hdo:hasRiskLevel "High" .
        ?p hdo:hasAge ?age . ?p hdo:hasFeverStatus ?feverStatus .
        ?p hdo:hasSymptomDuration ?duration . }
ORDER BY DESC(?age)""",

    "Q19 Patients symptomatic > 30 days": P + """
SELECT ?patientLabel ?duration ?riskLevel ?testLabel
WHERE { ?p rdf:type hdo:Patient . ?p rdfs:label ?patientLabel .
        ?p hdo:hasSymptomDuration ?duration . ?p hdo:hasRiskLevel ?riskLevel .
        ?p hdo:requiresTest ?t . ?t rdfs:label ?testLabel .
        FILTER (?duration > 30) }
ORDER BY DESC(?duration)""",

    "Q20 Cardiovascular diseases + treatments": P + """
SELECT ?diseaseLabel ?treatmentLabel
WHERE { ?d rdf:type hdo:Disease . ?d rdfs:label ?diseaseLabel .
        ?d hdo:hasCategory "Cardiovascular" .
        ?d hdo:hasTreatment ?t . ?t rdfs:label ?treatmentLabel . }
ORDER BY ?diseaseLabel""",
}


def load_graph(path: str) -> Graph:
    g = Graph()
    g.parse(path, format="turtle")
    g.bind("hdo", HDO)
    return g


def stats(g: Graph):
    classes = [HDO.Disease, HDO.Symptom, HDO.Treatment, HDO.Patient,
               HDO.DiagnosticTest, HDO.ClinicalAlert, HDO.DiagnosticRecommendation]
    labels  = ["Diseases","Symptoms","Treatments","Patients","Tests","Alerts","Recommendations"]
    print(f"\n{'='*60}")
    print(f"  Knowledge Graph Statistics")
    print(f"{'='*60}")
    print(f"  Total triples : {len(g)}")
    for cls, lbl in zip(classes, labels):
        print(f"  {lbl:<18}: {len(list(g.subjects(RDF.type, cls)))}")


def run_all(g: Graph):
    summary = []
    for title, query in QUERIES.items():
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
        try:
            rows = list(g.query(query))
            if not rows:
                print("  (no results)")
            else:
                if g.query(query).vars:
                    print("  " + " | ".join(str(v) for v in g.query(query).vars))
                    print("  " + "-"*56)
                for row in rows[:15]:
                    vals = [str(v).split("#")[-1][:35] if v else "" for v in row]
                    print("  " + " | ".join(vals))
                if len(rows) > 15:
                    print(f"  ... ({len(rows)-15} more rows)")
            summary.append((title, len(rows), "OK"))
        except Exception as e:
            print(f"  ERROR: {e}")
            summary.append((title, 0, str(e)))

    print(f"\n{'='*60}")
    print("  SUMMARY — All Queries")
    print(f"{'='*60}")
    ok = sum(1 for _,_,s in summary if s=="OK")
    for t, c, s in summary:
        mark = "✓" if s=="OK" else "✗"
        print(f"  {mark} {t}: {c} rows")
    print(f"\n  {ok}/{len(summary)} queries passed")


if __name__ == "__main__":
    print("Healthcare KG Builder v4")
    g = load_graph(TTL)
    stats(g)
    run_all(g)
    out = "healthcare-kg-v4.ttl"
    g.serialize(out, format="turtle")
    print(f"\n  Serialized → {out}")
