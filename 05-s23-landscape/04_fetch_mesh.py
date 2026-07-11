import os, json, time
from datetime import date
from collections import Counter
from Bio import Entrez, Medline

Entrez.email = "your-email@example.com"
Entrez.api_key = os.environ.get("NCBI_API_KEY")
SEARCH_DATE = date.today().isoformat()

CT = '("computed tomography"[tiab] OR "CT scan"[tiab] OR "CT imaging"[tiab])'

CORPORA = {
    "A_overuse_harm":
        f'{CT} AND ("overutilization"[tiab] OR "overuse"[tiab] OR "inappropriate"[tiab] OR "low-value"[tiab] '
        'OR "unnecessary"[tiab] OR "appropriateness"[tiab] OR "Choosing Wisely"[tiab] OR "incidental finding"[tiab] '
        'OR "incidental findings"[tiab] OR "incidentaloma"[tiab] OR "overdiagnosis"[tiab] OR "cumulative radiation"[tiab] '
        'OR "cumulative dose"[tiab] OR "recurrent CT"[tiab] OR "repeated CT"[tiab]) '
        'NOT ("overuse injury"[tiab] OR "overuse injuries"[tiab] OR tendinopathy[tiab] OR veterinary[tiab] OR canine[tiab] OR feline[tiab])',
    "B_benefit_yield":
        f'{CT} AND ("diagnostic yield"[tiab] OR "low yield"[tiab] OR "number needed to scan"[tiab] '
        'OR "number needed to image"[tiab] OR "net clinical benefit"[tiab] OR "net benefit"[tiab] '
        'OR "marginal benefit"[tiab] OR "incremental benefit"[tiab]) '
        'NOT (radiomics[tiab] OR "deep learning"[tiab] OR "machine learning"[tiab] OR "neural network"[tiab] '
        'OR "artificial intelligence"[tiab] OR nomogram[tiab] OR "CT-guided"[tiab] OR biopsy[tiab])',
}

BATCH = 200
MAX_IDS = 12000   # high enough to grab the entire result set per side

STOP = {"Humans","Animals","Female","Male","Adult","Aged","Aged, 80 and over",
        "Middle Aged","Young Adult","Adolescent","Child","Child, Preschool",
        "Infant","Infant, Newborn","Retrospective Studies","Prospective Studies",
        "Cohort Studies","Follow-Up Studies","Reproducibility of Results",
        "Cross-Sectional Studies","Case-Control Studies","Sensitivity and Specificity",
        "Predictive Value of Tests"}

def clean_mesh(mh):
    return mh.split("/")[0].replace("*", "").strip()

def fetch_all_pmids(query):
    h = Entrez.esearch(db="pubmed", term=query, retmax=MAX_IDS)
    r = Entrez.read(h); h.close()
    return r["IdList"], int(r["Count"])

def fetch_records(pmids):
    out = []
    for i in range(0, len(pmids), BATCH):
        chunk = pmids[i:i+BATCH]
        for attempt in range(3):
            try:
                h = Entrez.efetch(db="pubmed", id=",".join(chunk), rettype="medline", retmode="text")
                for rec in Medline.parse(h):
                    mesh = [clean_mesh(m) for m in rec.get("MH", [])]
                    mesh = [m for m in mesh if m and m not in STOP]
                    out.append({"pmid": rec.get("PMID", ""), "year": rec.get("DP", "")[:4], "mesh": mesh})
                h.close()
                break
            except Exception as e:
                if attempt == 2:
                    print(f"\n  (batch at {i} failed: {e})")
                else:
                    time.sleep(2)
        print(f"    ...fetched {min(i+BATCH, len(pmids))}/{len(pmids)}", end="\r")
        time.sleep(0.4)
    print()
    return out

data = {}
for side, query in CORPORA.items():
    pmids, total = fetch_all_pmids(query)
    print(f"\n=== {side} ===  ({total} total hits; fetching {len(pmids)})")
    time.sleep(0.4)
    recs = fetch_records(pmids)
    data[side] = recs
    with_mesh = [r for r in recs if r["mesh"]]
    terms = Counter(t for r in recs for t in r["mesh"])
    print(f"  records: {len(recs)} ({len(with_mesh)} MeSH-indexed); unique MeSH terms: {len(terms)}")
    print("  top 25 MeSH:")
    for term, c in terms.most_common(25):
        print(f"    {c:>5}  {term}")

with open("s23_mesh_corpus.json", "w") as f:
    json.dump({"search_date": SEARCH_DATE, "corpora": CORPORA, "data": data}, f, indent=2)
print(f"\nSaved s23_mesh_corpus.json  (search date {SEARCH_DATE})")
