import os, csv, time
from datetime import date
from Bio import Entrez

Entrez.email = "your-email@example.com"
Entrez.api_key = os.environ.get("NCBI_API_KEY")
SEARCH_DATE = date.today().isoformat()

# (side, category, label, query)
QUERIES = [
    # ----- Side A: radiation risk OF CT -----
    ("A", "precise", "CT + radiation risk",
     '("computed tomography"[tiab] OR "CT scan"[tiab]) AND "radiation risk"[tiab]'),
    ("A", "precise", "CT + radiation-induced cancer",
     '("computed tomography"[tiab] OR "CT scan"[tiab]) AND ("radiation-induced cancer"[tiab] OR "radiation induced cancer"[tiab])'),
    ("A", "precise", "CT + lifetime attributable / carcinogenic risk",
     '("computed tomography"[tiab] OR "CT scan"[tiab]) AND ("lifetime attributable risk"[tiab] OR "carcinogenic risk"[tiab])'),
    ("A", "MeSH",    "MeSH: CT AND Neoplasms, Radiation-Induced",
     '"Tomography, X-Ray Computed"[Mesh] AND "Neoplasms, Radiation-Induced"[Mesh]'),
    ("A", "broad",   "CT + radiation dose + risk",
     '("computed tomography"[tiab] OR "CT scan"[tiab]) AND "radiation dose"[tiab] AND risk[tiab]'),

    # ----- Side B: risk of NOT scanning -----
    ("B", "precise", "CT + risk of not scanning / non-scanning",
     '("computed tomography"[tiab] OR "CT scan"[tiab]) AND ("risk of not scanning"[tiab] OR "not scanning"[tiab] OR "non-scanning"[tiab])'),
    ("B", "precise", "withholding / deferred / forgoing CT or imaging",
     '("computed tomography"[tiab] OR "CT scan"[tiab]) AND ("withholding CT"[tiab] OR "deferred CT"[tiab] OR "forgoing CT"[tiab] OR "withholding imaging"[tiab] OR "deferred imaging"[tiab] OR "forgoing imaging"[tiab])'),
    ("B", "precise", "delayed CT / CT delay / time to CT",
     '("delayed CT"[tiab] OR "CT delay"[tiab] OR "time to CT"[tiab] OR "delayed computed tomography"[tiab])'),
    ("B", "MeSH",    "MeSH: CT AND Delayed Diagnosis (broad proxy)",
     '"Tomography, X-Ray Computed"[Mesh] AND "Delayed Diagnosis"[Mesh]'),
    ("B", "broad",   "CT + delayed diagnosis / diagnostic delay (broad proxy)",
     '("computed tomography"[tiab] OR "CT scan"[tiab]) AND ("delayed diagnosis"[tiab] OR "diagnostic delay"[tiab])'),
    ("B", "broad",   "CT + missed diagnosis (broad proxy)",
     '("computed tomography"[tiab] OR "CT scan"[tiab]) AND "missed diagnosis"[tiab]'),
]

def get_count(q):
    h = Entrez.esearch(db="pubmed", term=q, retmax=0)
    r = Entrez.read(h); h.close()
    return int(r["Count"])

rows = []
print("  count | side | category | label")
print("-" * 78)
for side, cat, label, q in QUERIES:
    n = get_count(q)
    rows.append({"side": side, "category": cat, "label": label,
                 "query": q, "count": n, "search_date": SEARCH_DATE})
    print(f"{n:>7} |  {side}   | {cat:<7} | {label}")
    time.sleep(0.34)

with open("bibliometric_counts.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["side","category","label","query","count","search_date"])
    w.writeheader(); w.writerows(rows)

def subtotal(side, cat):
    return sum(r["count"] for r in rows if r["side"] == side and r["category"] == cat)

print("-" * 78)
print("CONCEPT-PRECISE comparison (the honest asymmetry):")
print(f"  Side A precise total: {subtotal('A','precise')}")
print(f"  Side B precise total: {subtotal('B','precise')}")
print("MeSH concept presence:")
print(f"  Side A  Neoplasms, Radiation-Induced : {subtotal('A','MeSH')}   (a dedicated indexed concept)")
print(f"  Side B  Delayed Diagnosis [proxy]    : {subtotal('B','MeSH')}   (no MeSH term exists for 'non-scanning risk')")
print(f"\nSaved to bibliometric_counts.csv  (search date {SEARCH_DATE})")