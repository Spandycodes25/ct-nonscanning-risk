import os, json, time
from datetime import date
from collections import Counter
from Bio import Entrez, Medline

Entrez.email = "your-email@example.com
Entrez.api_key = os.environ.get("NCBI_API_KEY")
SEARCH_DATE = date.today().isoformat()

CORPORA = {
    "A_radiation":
        '("computed tomography"[tiab] OR "CT scan"[tiab]) AND ('
        '"radiation risk"[tiab] OR "radiation-induced cancer"[tiab] '
        'OR "radiation induced cancer"[tiab] OR "lifetime attributable risk"[tiab] '
        'OR "carcinogenic risk"[tiab])',
    "B_nonscanning":
        '(("computed tomography"[tiab] OR "CT scan"[tiab]) AND ('
        '"delayed diagnosis"[tiab] OR "diagnostic delay"[tiab] OR "missed diagnosis"[tiab])) '
        'OR ("time to CT"[tiab] OR "door-to-CT"[tiab] OR "door to CT"[tiab] '
        'OR "time to computed tomography"[tiab] OR "delayed CT scan"[tiab])',
}

RETMAX = 600    # cap per side
BATCH = 200     # efetch batch size

STOP = {"Humans", "Animals", "Female", "Male", "Adult", "Aged", "Aged, 80 and over",
        "Middle Aged", "Young Adult", "Adolescent", "Child", "Child, Preschool",
        "Infant", "Infant, Newborn", "Retrospective Studies", "Prospective Studies",
        "Cohort Studies", "Follow-Up Studies", "Reproducibility of Results",
        "Cross-Sectional Studies", "Case-Control Studies"}

def clean_mesh(mh):
    return mh.split("/")[0].replace("*", "").strip()

def fetch_pmids(query, retmax):
    h = Entrez.esearch(db="pubmed", term=query, retmax=retmax, sort="relevance")
    ids = Entrez.read(h)["IdList"]; h.close()
    return ids

def fetch_records(pmids):
    out = []
    for i in range(0, len(pmids), BATCH):
        chunk = pmids[i:i + BATCH]
        h = Entrez.efetch(db="pubmed", id=",".join(chunk),
                          rettype="medline", retmode="text")
        for rec in Medline.parse(h):
            mesh = [clean_mesh(m) for m in rec.get("MH", [])]
            mesh = [m for m in mesh if m and m not in STOP]
            out.append({"pmid": rec.get("PMID", ""),
                        "year": rec.get("DP", "")[:4],
                        "mesh": mesh})
        h.close()
        time.sleep(0.4)
    return out

data = {}
for side, query in CORPORA.items():
    pmids = fetch_pmids(query, RETMAX)
    time.sleep(0.4)
    recs = fetch_records(pmids)
    data[side] = recs
    with_mesh = [r for r in recs if r["mesh"]]
    terms = Counter(t for r in recs for t in r["mesh"])
    print(f"\n=== {side} ===")
    print(f"  fetched: {len(recs)} records ({len(with_mesh)} MeSH-indexed)")
    print(f"  unique MeSH terms: {len(terms)}")
    print("  top 20 MeSH:")
    for term, c in terms.most_common(20):
        print(f"    {c:>4}  {term}")

with open("mesh_corpus.json", "w") as f:
    json.dump({"search_date": SEARCH_DATE, "corpora": CORPORA, "data": data}, f, indent=2)
print(f"\nSaved mesh_corpus.json  (search date {SEARCH_DATE})")
