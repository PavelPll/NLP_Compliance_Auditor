import re

def extract_field(text, pattern):
    match = re.search(pattern, text, re.I)
    if match:
        return match.group(1).strip()
    return None

def analyze_product(text):

    product = {}

    # product["manufacturer"] = "Precision Industrie SAS"
    product["manufacturer"] = extract_field(text, r"Fabricant\s*:\s*(.*)")
    # product["address"] = "Grenoble"
    product["address"] = extract_field(text, r"Adresse\s*:\s*(.*)")

    # product["ce_marking"] = "Marquage CE appose sur la machine : OUI" in text
    product["ce_marking"] = extract_field(text, r"Marquage CE appose sur la machine\s*:\s*(OUI|NON)") == "OUI"

    # product["emergency_stop"] = "Dispositif de coupure d'urgence : OUI" in text
    product["emergency_stop"] = extract_field(text, r"Dispositif de coupure d'urgence\s*:\s*(OUI|NON)") == "OUI"

    # if "EN ISO 13850" in text:
    #     product["emergency_norm"] = "EN ISO 13850"
    # else:
    #     product["emergency_norm"] = None
    emergency_norm_match = re.search(r"Certification arret urgence\s*:\s*conforme\s*(EN ISO \d+)", text, re.I)
    product["emergency_norm"] = emergency_norm_match.group(1) if emergency_norm_match else None


    # if "phase d'utilisation" in text:
    #    product["risk_scope"] = "usage_only"
    # else:
    #    product["risk_scope"] = "full"
    if re.search(r"Evaluation des risques\s*:\s*REALISEE.*phase d'utilisation", text, re.I):
        product["risk_scope"] = "usage_only"
    else:
        product["risk_scope"] = "full"

    # CE declaration presence (Art.4.2.e)
    ce_decl_match = re.search(r"Declaration CE\s*:\s*(.*)", text, re.I)
    product["ce_declaration"] = True if ce_decl_match and "SIGNEE" in ce_decl_match.group(1).upper() else False

    # Adjust risk_scope to detect full lifecycle vs usage_only (hidden compliance #1)
    risk_match = re.search(r"Evaluation des risques\s*:\s*(.*)", text, re.I)
    if risk_match:
        risk_text = risk_match.group(1).lower()
        if "phase d'utilisation" in risk_text:
            product["risk_scope"] = "usage_only"  # already partially handled
        elif "cycle de vie" in risk_text:
            product["risk_scope"] = "full"
        else:
            product["risk_scope"] = "unknown"

    # Machine category (Art.9.1)
    category_match = re.search(r"Categorie machine\s*:\s*(.*)", text, re.I)
    if category_match:
        category_text = category_match.group(1).lower()
        if "iii" in category_text or "iv" in category_text:
            product["machine_category"] = "high_risk"
        else:
            product["machine_category"] = "standard"
    else:
        product["machine_category"] = None

    # languages = []
    # if "francais" in text:
    #     languages.append("FR")
    # if "allemand" in text:
    #     languages.append("DE")
    # product["manual_languages"] = languages
    langs = re.findall(r"Notice d'instructions\s*:\s*PRESENTE en ([\w, ]+)", text, re.I)
    product["manual_languages"] = [lang.strip().upper()[:2] for lang in langs[0].split(",")] if langs else []

    product["original_language_manual"] = "NON INCLUSE" not in text

    # if "Numero organisme notifie : NON RENSEIGNE" in text:
    #    product["notified_body"] = None
    # else:
    #    product["notified_body"] = "present"
    notified_match = re.search(r"Numero organisme notifie\s*:\s*(.*)", text, re.I)
    product["notified_body"] = None if notified_match and "NON RENSEIGNE" in notified_match.group(1).upper() else notified_match.group(1)

    # This detects the ambiguity mentioned in the product sheet
    if "EN COURS" in text.lower(): # in text
        product["schemas_status"] = "in_progress"
    else:
        product["schemas_status"] = "complete"

    return product