import re

def get_requirement_nature(text):

    conditional_keywords = [
        "si",
        "le cas echeant",
        "pour les machines"
    ]
    for word in conditional_keywords:
        if word in text.lower():
            return "conditionnelle"

    return "absolue"


def detect_category(title):

    title = title.lower()

    if "securite" in title:
        return "securite"
    if "marquage" in title or "conformite" in title:
        return "conformite"
    if "notice" in title:
        return "documentation"
    if "risques" in title:
        return "risk_management"

    return "general"


def extract_requirements(text):

    # match article header (Art.4.2 - Title)
    # group 1: number, group 2: title, group 3: body until next article
    pattern = r"Art\.(\d+\.\d+)\s*-\s*(.*?)\n(.*?)(?=Art\.\d+\.\d+|\Z)"
    # . matches any single character except a newline \n
    # \d=digit \s=" "
    # [^\n]=any character except newline 
    # +=one or more
    # Z — end of string

    # Art\. match the article prefix
    # (\d+\.\d+) capture the article number
    # \s*-\s* spaces around the dash
    # (.*?) capture the article title
    # \n title line break 
    # (.*?) capture the article body
    # (?=Art\.\d+\.\d+|\Z) stop before next article

    matches = re.findall(pattern, text, re.S)

    requirements = []
    for art_id, title, body in matches:
        full_text = (title + " " + body).strip()
        category = detect_category(title)
        nature = get_requirement_nature(full_text)
        requirement = {
            "id": "Art." + art_id,
            "text": full_text,
            "category": category,
            "nature": nature
        }
        requirements.append(requirement)

    return requirements