Semantic NLP system for automated verification of machine safety regulations
===================================

## Project Overview

- This project analyzes the conformity of a machine product sheet with regulatory requirements extracted from a directive.
- Requirements are extracted using pattern matching on article identifiers, and simple rules are applied to identify their type and approximate category.
- Product sheets are transformed into structured facts (e.g., CE marking, emergency stop, instruction languages, risk evaluation).
- Semantic comparison uses Sentence Transformers (PyTorch) to match product facts to requirements, with top-k retrieval for relevance.
- Each requirement is classified as:
  - **BLOQUANT** – requirement not satisfied  
  - **MAJEUR** – partially satisfied  
  - **AMBIGU** – insufficient information  
- A global conformity score summarizes the audit results.
- For more details see DECISIONS.md

## Running the Analysis

- Execute the analysis via `notebooks/audit.ipynb` (interactive) or `scripts/audit.py` (script-based).  
- The scripts perform extraction, fact transformation, semantic comparison, classification, and scoring.

## Project Structure

- `notebooks/` – audit notebook  
- `scripts/` – execution scripts  
- `lib/` – text processing and similarity utilities  

## Environment Setup

1. Open a terminal and navigate to the project folder:
   cd exercise

2. Create and activate a conda environment with Python 3.10.11:
   conda create -n audit python=3.10.11 -y
   conda activate audit

3. Install required packages:
   pip install -r requirements.txt

---

## Notes

- ...
