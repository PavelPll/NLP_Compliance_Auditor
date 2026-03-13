import sys
sys.path.insert(0, "../")

from lib.extractor import extract_requirements
from lib.analyzer import analyze_product
from lib.comparator import compare
from lib.report import generate_report

# READ documents
def load_file(path):

    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
regulation_text = load_file("../data/regulation.txt")
product_text = load_file("../data/product.txt")

# Regulations EXTRACTION
requirements = extract_requirements(regulation_text)
print("Regulation")
for r in requirements:
    print(r["id"], r["category"])
print()

# Description parsing
product = analyze_product(product_text)
print("Product:")
print(product)

# Comparison and final report
findings = compare(requirements, product)
generate_report(findings)