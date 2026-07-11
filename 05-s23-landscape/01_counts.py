import os, csv, time
from datetime import date
from Bio import Entrez

Entrez.email = "your-email@example.com"
Entrez.api_key = os.environ.get("NCBI_API_KEY")
SEARCH_DATE = date.today().isoformat()

CT = '("computed tomography"[tiab] OR "CT scan"[tiab] OR "CT imaging"[tiab])'

# (category, label, query)
QUERIES = [
    # ----- Overuse / low-value (the "may not help" side) -----
    ("overuse", "CT + overuse / inappropriate / low-value / unnecessary",
     f'{CT} AND ("overutilization"[tiab] OR "overuse"[tiab] OR "inappropriate"[tiab] OR "low-value"[tiab] OR "unnecessary"[tiab])'),
    ("overuse", "CT + appropriateness / Choosing Wisely",
     f'{CT} AND ("appropriateness"[tiab] OR "appropriate use"[tiab] OR "Choosing Wisely"[tiab])'),

    # ----- Diagnostic yield (the empirical marginal-benefit measure) -----
    ("yield", "CT + diagnostic yield / low yield / number-needed-to-scan",
     f'{CT} AND ("diagnostic yield"[tiab] OR "low yield"[tiab] OR "number needed to scan"[tiab] OR "number needed to image"[tiab] OR "incremental yield"[tiab])'),

    # ----- Incidental findings / overdiagnosis (harm of scanning beyond radiation) -----
    ("incidental", "CT + incidental findings / incidentaloma / overdiagnosis",
     f'{CT} AND ("incidental finding"[tiab] OR "incidental findings"[tiab] OR "incidentaloma"[tiab] OR "overdiagnosis"[tiab])'),

    # ----- Cumulative / recurrent radiation dose (the S2 radiation-accrual side) -----
    ("cumulative_dose", "CT + cumulative / recurrent / repeated dose",
     f'{CT} AND ("cumulative radiation"[tiab] OR "cumulative dose"[tiab] OR "cumulative effective dose"[tiab] OR "recurrent CT"[tiab] OR "repeated CT"[tiab] OR "repeat CT imaging"[tiab])'),

    # ----- Net / marginal benefit quantified (the inverse-gap bucket) -----
    ("marginal_benefit", "CT + net / marginal / incremental clinical benefit",
     f'{CT} AND ("net clinical benefit"[tiab] OR "net benefit"[tiab] OR "marginal benefit"[tiab] OR "incremental benefit"[tiab])'),

    # ----- MeSH-indexed concepts (the crystallization contrast vs S1) -----
    ("MeSH", "MeSH: CT AND Medical Overuse",
     '"Tomography, X-Ray Computed"[Mesh] AND "Medical Overuse"[Mesh]'),
    ("MeSH", "MeSH: CT AND Incidental Findings",
     '"Tomography, X-Ray Computed"[Mesh] AND "Incidental Findings"[Mesh]'),
    ("MeSH", "MeSH: CT AND Unnecessary Procedures",
     '"Tomography, X-Ray Computed"[Mesh] AND "Unnecessary Procedures"[Mesh]'),
]

def get_count(q):
    h = Entrez.esearch(db="pubmed", term=q, retmax=0)
    r = Entrez.read(h); h.close()
    return int(r["Count"])

rows = []
print("  count | category          | label")
print("-" * 88)
for cat, label, q in QUERIES:
    n = get_count(q)
    rows.append({"category": cat, "label": label, "query": q,
                 "count": n, "search_date": SEARCH_DATE})
    print(f"{n:>7} | {cat:<17} | {label}")
    time.sleep(0.34)

with open("s23_landscape_counts.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["category", "label", "query", "count", "search_date"])
    w.writeheader(); w.writerows(rows)

def subtotal(cat):
    return sum(r["count"] for r in rows if r["category"] == cat)

print("-" * 88)
print("Landscape summary (the inverse asymmetry):")
print(f"  Overuse / low-value (named)        : {subtotal('overuse')}")
print(f"  Diagnostic yield (benefit measure) : {subtotal('yield')}")
print(f"  Incidental findings / overdiagnosis: {subtotal('incidental')}")
print(f"  Cumulative / recurrent dose        : {subtotal('cumulative_dose')}")
print(f"  Net/marginal benefit quantified    : {subtotal('marginal_benefit')}  <- expected-sparse inverse gap")
print(f"  MeSH-indexed overuse concepts      : {subtotal('MeSH')}  (these terms EXIST, unlike 'non-scanning')")
print(f"\nSaved s23_landscape_counts.csv  (search date {SEARCH_DATE})")
