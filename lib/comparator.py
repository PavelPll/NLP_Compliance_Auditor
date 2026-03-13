# Example
# data1 from regulatory requirements (from extractor.py)
# data2 from structured product data (from analyzer.py)
# data1==data2? or "arrêt d'urgence" == "emergency stop" ???

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


model = SentenceTransformer("all-MiniLM-L6-v2")


def build_product_facts(product):
    # Turn structured data into sentences that can be compared with regulations.

    facts = []

    if product["ce_marking"]:
        facts.append("la machine porte le marquage CE")
    if product["emergency_stop"]:
        facts.append("la machine possède un dispositif d'arrêt d'urgence")
    if product["emergency_norm"]:
        facts.append("le dispositif d'arrêt d'urgence est conforme EN 13850")
    if not product["original_language_manual"]:
        facts.append("la notice dans la langue d'origine du fabricant n'est pas fournie")
    # if product["risk_scope"] == "usage_only":
    #     facts.append("l'évaluation des risques couvre seulement la phase d'utilisation")
    if product["risk_scope"] == "usage_only":
        facts.append("l'évaluation des risques ne couvre pas tout le cycle de vie")
    # facts.append("la notice est disponible en français et en allemand")
    languages = product.get("manual_languages", [])
    if languages:
        facts.append(f"la notice est disponible dans les langues suivantes : {', '.join(languages)}")

    return facts


def semantic_match(requirement_text, facts):

    req_vector = model.encode([requirement_text])
    fact_vectors = model.encode(facts)

    scores = cosine_similarity(req_vector, fact_vectors)[0]

    best_index = np.argmax(scores)

    return facts[best_index], scores[best_index]

def semantic_match_RAG(requirement_text, facts, k=2):
    # Instead of returning 1 fact, it returns top-k facts.

    # req_vec = model.encode([requirement_text])
    # fact_vecs = model.encode(facts)
    req_vec = model.encode(requirement_text.lower().strip())
    fact_vecs = model.encode([f.lower().strip() for f in facts])

    scores = cosine_similarity(req_vec, fact_vecs)[0]

    idx = scores.argsort()[-k:][::-1]

    results = []

    for i in idx:
        results.append((facts[i], scores[i]))

    return results

def semantic_match_RAG_modified(requirement_text, facts, k=3):
    """
    Improved retrieval step for the RAG pipeline.
    Returns the top-k product facts most semantically similar
    to the regulatory requirement.
    """

    # Encode requirement
    req_vec = model.encode(requirement_text)

    # Encode facts
    fact_vecs = model.encode(facts)

    # Compute cosine similarity
    scores = cosine_similarity([req_vec], fact_vecs)[0]

    # Pair each fact with its score
    pairs = list(zip(facts, scores))

    # Sort by similarity
    pairs.sort(key=lambda x: x[1], reverse=True)

    # Return top-k results
    return pairs[:k]

def detect_ambiguity(text):
    # Detect uncertain or incomplete statements.
    # Ambiguity = the information exists but is unclear or incomplete, 
    # so I cannot confirm compliance.
    # Compliance = following the required rules.
    # "Schemas : EN COURS DE FINALISATION" classified as AMBIGU

    ambiguous_terms = [
        "en cours",
        "non renseigne",
        "present", # Too vague
        "complet", # Claim without evidence ?
        "finalisation",
        "a verifier",
        "non precise"
    ]

    text = text.lower()

    for term in ambiguous_terms:
        if term in text:
            return True

    return False

def classify(requirement_text, fact, score):
    # How well the product meets a regulatory requirement
    # BLOQUANT: The requirement is clearly not satisfied, 
    #   Requirement: La version dans la langue d'origine doit être fournie.
    #   Product sheet:Version notice langue d'origine (anglais) : NON INCLUSE
    # CONFORME: The requirement is satisfied.
    #    Requirement: Toute machine doit porter le marquage CE.
    #    Product sheet: Marquage CE apposé sur la machine : OUI
    # AMBIGU: The requirement might be satisfied, 
    # but the information is incomplete, unclear, or uncertain.
    #    Requirement: Le dossier technique doit contenir les schémas.
    #    Product sheet: Schemas: EN COURS DE FINALISATION
    # MAJEUR: The requirement is partially satisfied but not fully compliant
    

    if detect_ambiguity(fact):
        return "AMBIGU"

    fact_lower = fact.lower()

    if "n'est pas" in fact_lower or "non" in fact_lower:
        # Example: "la notice n'est pas fournie"
        if score > 0.45:
            return "BLOQUANT"

    if score > 0.70:
        return "CONFORME"

    if 0.50 <= score <= 0.70:
        return "MAJEUR"

    if 0.35 <= score < 0.50:
        return "AMBIGU"
    
# deterministic regulatory checks
def rule_based_checks(requirement, product):
    # Some issues should not rely on AI similarity.

    text = requirement["text"].lower()
    art = requirement["id"]

    # Art 7.1 — original language manual must exist
    # "notice langue origine absente" is always non-compliant
    if "notice" in text and "langue d'origine" in text:
        if not product["original_language_manual"]:
            return {
                "requirement_id": art,
                "severity": "BLOQUANT",
                "justification": "La notice dans la langue d'origine du fabricant n'est pas fournie"
            }

    # Art 8.1 — risk evaluation lifecycle
    if "evaluation des risques" in text:
        if product["risk_scope"] == "usage_only":
            return {
                "requirement_id": art,
                "severity": "MAJEUR",
                "justification": "L'évaluation des risques couvre seulement la phase d'utilisation"
            }

    # Art 4.2 — technical file schematics incomplete
    if "dossier technique" in text or "schemas" in text:
        if product.get("schemas_status") == "in_progress":
            return {
                "requirement_id": art,
                "severity": "AMBIGU",
                "justification": "Les schémas des circuits de commande sont en cours de finalisation"
            }

    return None

def compare(requirements, product):

    findings = []

    facts = build_product_facts(product)

    for req in requirements:

        # rule-based compliance check
        rule_result = rule_based_checks(req, product)

        if rule_result:
            # Some issues should not rely on AI similarity
            # If a rule-based violation is detected:
            # add it to findings
            # STOP processing this requirement
            # go to the next requirement
            findings.append(rule_result)
            continue

        # semantic retrieval: uncomment or or
        # fact, score = semantic_match(req["text"], facts)
        # candidates = semantic_match_RAG(req["text"], facts)
        candidates = semantic_match_RAG_modified(req["text"], facts)
        fact, score = candidates[0] # choose best fact

        # How well the product meets a regulatory requirement
        severity = classify(req["text"], fact, score)

        # record non-conformities
        if severity and severity != "CONFORME": # add .lower potentially

            finding = {
                "requirement_id": req["id"],
                "severity": severity,
                "justification": f"Correspondance semantique avec '{fact}' (score={score:.2f})"
            }

            findings.append(finding)

    return findings