import os, csv, time
from datetime import date
from Bio import Entrez

Entrez.email = "your-email@example.com"
Entrez.api_key = os.environ.get("NCBI_API_KEY")
SEARCH_DATE = date.today().isoformat()

OPTICS = (' NOT (spectrometer[tiab] OR spectral[tiab] OR fluorescence[tiab] '
          'OR microscopy[tiab] OR multiplexing[tiab])')

QUERIES = [
    ("A", "named", "radiation risk (named concept)",
     '("computed tomography"[tiab] OR "CT scan"[tiab]) AND ("radiation risk"[tiab] '
     'OR "radiation-induced cancer"[tiab] OR "radiation induced cancer"[tiab] '
     'OR "lifetime attributable risk"[tiab] OR "carcinogenic risk"[tiab])'),
    ("A", "mesh", "Neoplasms, Radiation-Induced (indexed MeSH concept)",
     '"Tomography, X-Ray Computed"[Mesh] AND "Neoplasms, Radiation-Induced"[Mesh]'),
    ("B", "named", "risk of NOT scanning (named concept, optics removed)",
     '("computed tomography"[tiab] OR "CT scan"[tiab]) AND ("risk of not scanning"[tiab] '
     'OR "not scanning"[tiab] OR "non-scanning"[tiab] OR "withholding CT"[tiab] '
     'OR "withholding imaging"[tiab] OR "deferred CT"[tiab] OR "forgoing CT"[tiab] '
     'OR "forgoing imaging"[tiab])' + OPTICS),
    ("B", "operational", "delay-to-scan (time-to-CT / door-to-CT, clean)",
     '("time to CT"[tiab] OR "time-to-CT"[tiab] OR "door-to-CT"[tiab] '
     'OR "door to CT"[tiab] OR "time to computed tomography"[tiab] '
     'OR "delayed CT scan"[tiab] OR "delay in CT"[tiab]) '
     'NOT ("delayed phase"[tiab] OR "delayed-phase"[tiab] OR "delayed enhancement"[tiab] '
     'OR "delayed contrast"[tiab] OR "time-resolved"[tiab])'),
    ("B", "proxy", "delayed/missed diagnosis co-mentioning CT (off-concept proxy)",
     '("computed tomography"[tiab] OR "CT scan"[tiab]) AND ("delayed diagnosis"[tiab] '
     'OR "diagnostic delay"[tiab] OR "missed diagnosis"[tiab])'),
]

def get_count(q):
    h = Entrez.esearch(db="pubmed", term=q, retmax=0)
    r = Entrez.read(h); h.close()
    return int(r["Count"])

rows = []
print(f"{'count':>7} | side | bucket      | label")
print("-" * 92)
for side, bucket, label, q in QUERIES:
    n = get_count(q)
    rows.append({"side": side, "bucket": bucket, "label": label,
                 "query": q, "count": n, "search_date": SEARCH_DATE})
    print(f"{n:>7} |  {side}   | {bucket:<11} | {label}")
    time.sleep(0.34)

with open("bibliometric_counts_final.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["side", "bucket", "label", "query", "count", "search_date"])
    w.writeheader(); w.writerows(rows)

print("-" * 92)
print(f"Saved bibliometric_counts_final.csv  (search date {SEARCH_DATE})")
