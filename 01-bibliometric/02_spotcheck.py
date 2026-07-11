import os, time
from Bio import Entrez

Entrez.email = "your-email@example.com"
Entrez.api_key = os.environ.get("NCBI_API_KEY")

SPOTCHECKS = {
    "B precise -- delayed CT / CT delay / time to CT  (n~402, AMBIGUOUS)":
        '("delayed CT"[tiab] OR "CT delay"[tiab] OR "time to CT"[tiab] OR "delayed computed tomography"[tiab])',
    "B broad -- CT + delayed diagnosis / diagnostic delay  (n~1534, PROXY)":
        '("computed tomography"[tiab] OR "CT scan"[tiab]) AND ("delayed diagnosis"[tiab] OR "diagnostic delay"[tiab])',
    "B precise -- CT + risk of not scanning / non-scanning  (n~4, EXACT CONCEPT)":
        '("computed tomography"[tiab] OR "CT scan"[tiab]) AND ("risk of not scanning"[tiab] OR "not scanning"[tiab] OR "non-scanning"[tiab])',
}

def titles(query, n):
    h = Entrez.esearch(db="pubmed", term=query, retmax=n, sort="relevance")
    ids = Entrez.read(h)["IdList"]; h.close()
    if not ids:
        return []
    time.sleep(0.34)
    h = Entrez.esummary(db="pubmed", id=",".join(ids))
    summ = Entrez.read(h); h.close()
    return [(s["Id"], s.get("PubDate", "")[:4], s.get("Title", "[no title]")) for s in summ]

for label, q in SPOTCHECKS.items():
    print("\n" + "=" * 95)
    print(label)
    print("=" * 95)
    rows = titles(q, 20)
    if not rows:
        print("  (no records)")
    for pmid, year, title in rows:
        print(f"[{year}] {title}  (PMID {pmid})")
    time.sleep(0.34)
