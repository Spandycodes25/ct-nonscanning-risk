import os, time
from Bio import Entrez

Entrez.email = "your-email@example.com"
Entrez.api_key = os.environ.get("NCBI_API_KEY")

CT = '("computed tomography"[tiab] OR "CT scan"[tiab] OR "CT imaging"[tiab])'

SPOTCHECKS = {
    "marginal_benefit -- net/marginal/incremental clinical benefit (n~515, KEY inverse-gap)":
        f'{CT} AND ("net clinical benefit"[tiab] OR "net benefit"[tiab] OR "marginal benefit"[tiab] OR "incremental benefit"[tiab])',
    "yield -- diagnostic yield / low yield / NNS (n~1694, benefit measure)":
        f'{CT} AND ("diagnostic yield"[tiab] OR "low yield"[tiab] OR "number needed to scan"[tiab] OR "number needed to image"[tiab] OR "incremental yield"[tiab])',
    "overuse -- overuse / inappropriate / low-value / unnecessary (n~6792, headline)":
        f'{CT} AND ("overutilization"[tiab] OR "overuse"[tiab] OR "inappropriate"[tiab] OR "low-value"[tiab] OR "unnecessary"[tiab])',
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
