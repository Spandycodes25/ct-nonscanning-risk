import os, csv, time
from datetime import date
from Bio import Entrez

Entrez.email = "your-email@example.com"
Entrez.api_key = os.environ.get("NCBI_API_KEY")
SEARCH_DATE = date.today().isoformat()

CT = '("computed tomography"[tiab] OR "CT scan"[tiab] OR "CT imaging"[tiab])'

QUERIES = [
    ("overuse_clean", "CT overuse / inappropriate / low-value (appropriateness removed)",
    f'{CT} AND ("overutilization"[tiab] OR "overuse"[tiab] OR "inappropriate"[tiab] OR "low-value"[tiab] OR "unnecessary"[tiab] OR "Choosing Wisely"[tiab]) '
    'NOT ("overuse injury"[tiab] OR "overuse injuries"[tiab] OR tendinopathy[tiab] OR "stress fracture"[tiab] OR veterinary[tiab] OR canine[tiab] OR feline[tiab])'),
    ("overuse_mesh", "MeSH: CT AND Medical Overuse / Unnecessary Procedures",
     '"Tomography, X-Ray Computed"[Mesh] AND ("Medical Overuse"[Mesh] OR "Unnecessary Procedures"[Mesh])'),
    ("appropriateness", "CT appropriateness / appropriate use (shown separately)",
    f'{CT} AND ("appropriateness"[tiab] OR "appropriate use"[tiab] OR "appropriateness criteria"[tiab]) '
    'NOT ("overuse injury"[tiab] OR "overuse injuries"[tiab] OR tendinopathy[tiab] OR "stress fracture"[tiab] OR veterinary[tiab] OR canine[tiab] OR feline[tiab])'),
    ("incidental", "CT incidental findings / incidentaloma / overdiagnosis",
     f'{CT} AND ("incidental finding"[tiab] OR "incidental findings"[tiab] OR "incidentaloma"[tiab] OR "overdiagnosis"[tiab])'),
    ("cumulative_dose", "CT cumulative / recurrent / repeated dose",
     f'{CT} AND ("cumulative radiation"[tiab] OR "cumulative dose"[tiab] OR "cumulative effective dose"[tiab] OR "recurrent CT"[tiab] OR "repeated CT"[tiab])'),
    ("yield_test", "CT diagnostic yield as a TEST (CT-guided biopsy/procedure removed)",
     f'{CT} AND ("diagnostic yield"[tiab] OR "low yield"[tiab] OR "number needed to scan"[tiab] OR "number needed to image"[tiab]) '
     'NOT ("CT-guided"[tiab] OR "CT guided"[tiab] OR biopsy[tiab] OR "core needle"[tiab] OR "fine needle"[tiab] OR aspiration[tiab])'),
    ("benefit_named_clean", "CT net/marginal/incremental benefit (AI/radiomics removed)",
     f'{CT} AND ("net clinical benefit"[tiab] OR "net benefit"[tiab] OR "marginal benefit"[tiab] OR "incremental benefit"[tiab]) '
     'NOT (radiomics[tiab] OR "deep learning"[tiab] OR "machine learning"[tiab] OR "neural network"[tiab] OR "artificial intelligence"[tiab] OR nomogram[tiab])'),
]

def get_count(q):
    h = Entrez.esearch(db="pubmed", term=q, retmax=0)
    r = Entrez.read(h); h.close()
    return int(r["Count"])

def titles(q, n):
    h = Entrez.esearch(db="pubmed", term=q, retmax=n, sort="relevance")
    ids = Entrez.read(h)["IdList"]; h.close()
    if not ids: return []
    time.sleep(0.34)
    h = Entrez.esummary(db="pubmed", id=",".join(ids))
    s = Entrez.read(h); h.close()
    return [(x["Id"], x.get("PubDate", "")[:4], x.get("Title", "[no title]")) for x in s]

rows = []
print(f"{'count':>7} | category            | label")
print("-" * 92)
for cat, label, q in QUERIES:
    n = get_count(q)
    rows.append({"category": cat, "label": label, "query": q, "count": n, "search_date": SEARCH_DATE})
    print(f"{n:>7} | {cat:<19} | {label}")
    time.sleep(0.34)

with open("s23_landscape_counts_refined.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["category", "label", "query", "count", "search_date"])
    w.writeheader(); w.writerows(rows)
print("-" * 92)
print(f"Saved s23_landscape_counts_refined.csv  (search date {SEARCH_DATE})")

# Verify the two buckets that define the benefit-quantification gap
for cat in ["benefit_named_clean", "yield_test"]:
    q = next(r["query"] for r in rows if r["category"] == cat)
    print("\n" + "=" * 92)
    print(f"VERIFY titles: {cat}")
    print("=" * 92)
    for pmid, year, title in titles(q, 15):
        print(f"[{year}] {title}  (PMID {pmid})")
    time.sleep(0.34)
