## Choix techniques

### Extraction des exigences

Le texte réglementaire est structuré par articles (Art.X.X).
Une extraction par regex permet d’identifier pour chaque exigence :

- identifiant de l’article (ex : Art.7.1)
- texte complet de l’exigence
- catégorie thématique (sécurité, conformité, documentation, gestion des risques…)

Exemple d’articles extraits :
Art.4.1 – securite  
Art.4.2 – general  
Art.5.1 – conformite  
Art.5.2 – conformite  
Art.6.1 – securite  
Art.6.2 – securite  
Art.7.1 – documentation  
Art.7.2 – documentation  
Art.8.1 – risk_management  
Art.8.2 – risk_management  
Art.9.1 – general

### Analyse de la fiche produit

La fiche est transformée en faits normalisés :  
- manufacturer
- address
- ce_marking
- emergency_stop
- emergency_norm
- risk_scope
- ce_declaration
- machine_category
- manual_languages
- original_language_manual
- notified_body
- schemas_status

### Comparaison sémantique

Sentence Transformers (PyTorch) génère embeddings et calcule similarité cosinus.  

Top-k retrieval identifie les faits pertinents pour chaque exigence (J’ai implémenté deux versions).

Les règles déterministes sont appliquées avant la comparaison sémantique pour attraper des cas évidents, comme la notice en langue d’origine absente ou schémas en cours de finalisation.
SEE rule_based_checks() in comparator.py.

### Classification des écarts

- BLOQUANT : exigence non respectée  
- MAJEUR : conformité partielle  
- AMBIGU : info insuffisante  

Détection d’ambiguïté : "NON RENSEIGNE", "EN COURS", "EN FINALISATION", "A VERIFIER", "NON PRÉCISE".  
SEE detect_ambiguity() in comparator.py.

### Score de conformité

transformer les résultats qualitatifs en "un système" de pénalité numérique
penalty = 3 * BLOQUANT + 2 * MAJEUR + 1 * AMBIGU
SEE compute_score(findings) in report.py
---

## Ecarts et cas ambigus

### Art.7.1 – Notice d’instructions

Directive : Art.7.1 - Notice d'instructions
Chaque machine doit etre accompagnee d'une notice redigee dans la langue
officielle de chaque Etat membre dans lequel la machine est mise sur le
marche. La version dans la langue d'origine du fabricant doit egalement etre
fournie.

Fiche produit : "Marches vises : France, Allemagne, Espagne"
"Notice d'instructions : PRESENTE en francais et en allemand" "Version notice langue d'origine (anglais) : NON INCLUSE dans la livraison standard"

Analyse :
    - absence de notice en espagnol pour le marché espagnol
    - absence de la version dans la langue d'origine du fabricant (anglais)

BLOQUANT  
notice non fournie dans toutes les langues requises (Art.7.1)

### Art.8.1 – Evaluation des risques

Directive : le fabricant doit réaliser une évaluation des risques couvrant
l’ensemble du cycle de vie de la machine.

Fiche produit : "Evaluation des risques : REALISEE - phase d'utilisation (ref EVR-TX900-2024)"

Analyse : la fiche indique que l’évaluation des risques a été réalisée uniquement pour la phase d’utilisation de la machine. La directive exige une couverture de l’ensemble du cycle de vie (conception, installation, utilisation, maintenance, etc.).
MAJEUR  
évaluation des risques limitée à la phase d’utilisation (Art.8.1)

### Art.4.2 – Dossier technique

Directive : le dossier technique doit inclure notamment
les schémas des circuits de commande (Art.4.2.b).
Fiche produit : "Schemas electriques : PRESENTS (ref SCH-ELEC-TX900)"
"Schemas des circuits de commande CN : EN COURS DE FINALISATION"

Analyse : les schémas électriques sont indiqués comme présents,
mais les schémas des circuits de commande CN sont signalés
comme en cours de finalisation. La disponibilité complète des schémas exigés par l'article
4.2.b n'est donc pas certaine.

AMBIGU  
schémas des circuits de commande non finalisés (Art.4.2.b)

---

## Points potentiellement ambigus

selon l'article 9.1, Pour les machines classees a risque eleve (categorie III ou IV), l'intervention d'un organisme notifie est obligatoire avant mise sur le
marche.

Fiche produit :
"Numero organisme notifie : NON RENSEIGNE"  
"Certificat examen CE de type : NON FOURNI"
"Categorie machine : risque standard (non classe categorie III ou IV)"

Analyse :
La fiche produit indique que la machine est classee comme "risque standard".
Dans ce cas, l'absence d'organisme notifie et de certificat d'examen CE de type est probablement normale (?). Cependant, la classification de la machine n'est pas verifiable
avec les informations disponibles.

Conclusion :
pas d'ecart detecte, mais classification a confirmer.
---

## Limites

Approche basée sur similarité sémantique + heuristiques.  
Un LLM pourrait améliorer :  
- interprétation des obligations  
- relations entre articles  
- explications détaillées  

Méthode actuelle : reproductible et explicable.
Limitations connues : score normalisé seulement sur les écarts détectés, certains faits construits à partir de texte peuvent masquer des non-conformités partielles (ex : langues manquantes, phase de cycle de vie incomplète).
