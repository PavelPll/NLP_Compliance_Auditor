def compute_score(findings):
    # turn qualitative results into a numerical penalty system
    # not finished 100%, 1st version to be modified

    weights = {
        "BLOQUANT": 3, # Product cannot be marketed
        "MAJEUR": 2, # Must be corrected
        "AMBIGU": 1 # Needs clarification
    }

    total_requirements = len(findings) # probably not the best choise

    penalty = 0
    for f in findings:
        severity = f["severity"]
        if severity in weights:
            penalty += weights[severity]
        else:
            penalty += 0  # optional, could skip this line

    # normalize the penalty only based on detected issues
    # other requirements which are fully compliant, this is not reflected
    max_penalty = total_requirements * 3 # 3 is worst-case penalty per requirement
    # normalize the penalty only based on the full set of requirements
    # max_penalty = number_of_requirements * 3 # for next version

    score = 1 - (penalty / max_penalty)

    # prevent negative score
    return max(score, 0)


def generate_report(findings):

    bloquant = [f for f in findings if f["severity"] == "BLOQUANT"]
    majeur = [f for f in findings if f["severity"] == "MAJEUR"]
    ambigu = [f for f in findings if f["severity"] == "AMBIGU"]

    if len(bloquant) > 0:
        status = "NON CONFORME"
    else:
        status = "CONFORME"

    print()
    print("RAPPORT D'AUDIT - TX-900-CE-2024")
    print()

    print("Statut :", status)
    score = compute_score(findings) 
    print("Compliance score:", round(score * 100, 1), "%")
    print()

    print("BLOQUANT :", len(bloquant))
    print("MAJEUR :", len(majeur))
    print("AMBIGU :", len(ambigu))
    print()

    print("ECARTS BLOQUANTS :")
    for f in bloquant:
        print("[{}] {}".format(f["requirement_id"], f["justification"]))
    print()

    print("CAS AMBIGUS :")
    for f in ambigu:
        print("[{}] {}".format(f["requirement_id"], f["justification"]))
    print()

    print("ECARTS MAJEURS :")
    for f in majeur:
        print("[{}] {}".format(f["requirement_id"], f["justification"]))
    print()