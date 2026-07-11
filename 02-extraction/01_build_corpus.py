import os, json, time
from collections import OrderedDict
from datetime import date
from Bio import Entrez, Medline

Entrez.email = "your-email@example.com"
Entrez.api_key = os.environ.get("NCBI_API_KEY")
SEARCH_DATE = date.today().isoformat()

RETMAX = 60     # per condition (relevance-ranked); tune later
BATCH = 100

CONDITIONS = {
    "appendicitis":
        '("appendicitis"[tiab]) AND ("perforation"[tiab] OR "delayed diagnosis"[tiab] '
        'OR "diagnostic delay"[tiab] OR "time to"[tiab]) AND (rate[tiab] OR risk[tiab] '
        'OR "odds ratio"[tiab] OR outcome*[tiab] OR hours[tiab])',
    "ischemic_stroke":
        '("ischemic stroke"[tiab] OR "acute stroke"[tiab]) AND ("time to treatment"[tiab] '
        'OR "onset to treatment"[tiab] OR "door-to-needle"[tiab] OR "treatment delay"[tiab]) '
        'AND (outcome*[tiab] OR mortality[tiab] OR mRS[tiab] OR disability[tiab])',
    "subarachnoid_hemorrhage":
        '("subarachnoid hemorrhage"[tiab] OR "subarachnoid haemorrhage"[tiab]) AND '
        '("misdiagnosis"[tiab] OR "missed diagnosis"[tiab] OR "delayed diagnosis"[tiab] '
        'OR "rebleeding"[tiab]) AND (rate[tiab] OR risk[tiab] OR mortality[tiab] OR outcome*[tiab])',
    "pulmonary_embolism":
        '("pulmonary embolism"[tiab]) AND ("delayed diagnosis"[tiab] OR "diagnostic delay"[tiab] '
        'OR "delayed treatment"[tiab]) AND (mortality[tiab] OR death[tiab] OR outcome*[tiab] '
        'OR prognosis[tiab])',
    "aortic_dissection":
        '("aortic dissection"[tiab]) AND ("delayed diagnosis"[tiab] OR "diagnostic delay"[tiab] '
        'OR "misdiagnosis"[tiab]) AND (mortality[tiab] OR death[tiab] OR outcome*[tiab])',
    "mesenteric_ischemia":
        '("mesenteric ischemia"[tiab] OR "mesenteric ischaemia"[tiab]) AND ("delayed diagnosis"[tiab] '
        'OR "diagnostic delay"[tiab] OR "time to"[tiab]) AND (mortality[tiab] OR death[tiab] '
        'OR outcome*[tiab] OR survival[tiab])',
    "major_trauma":
        '("polytrauma"[tiab] OR "major trauma"[tiab] OR "multiple trauma"[tiab]) AND '
        '("time to CT"[tiab] OR "whole-body CT"[tiab] OR "time to computed tomography"[tiab]) '
        'AND (mortality[tiab] OR survival[tiab] OR outcome*[tiab])',
}

def esearch_ids(q, retmax):
    h = Entrez.esearch(db="pubmed", term=q, retmax=retmax, sort="relevance")
    ids = Entrez.read(h)["IdList"]; h.close()
    return ids

def fetch_medline(pmids):
    recs = []
    for i in range(0, len(pmids), BATCH):
        chunk = pmids[i:i + BATCH]
        h = Entrez.efetch(db="pubmed", id=",".join(chunk), rettype="medline", retmode="text")
        recs.extend(list(Medline.parse(h)))
        h.close()
        time.sleep(0.4)
    return recs

corpus = OrderedDict()   # pmid -> record (dedupes across conditions)
for cond, q in CONDITIONS.items():
    ids = esearch_ids(q, RETMAX)
    time.sleep(0.34)
    recs = fetch_medline(ids)
    n_abs = 0
    for r in recs:
        pmid, ab = r.get("PMID", ""), r.get("AB", "")
        if not pmid or not ab:
            continue
        n_abs += 1
        if pmid not in corpus:
            corpus[pmid] = {"pmid": pmid, "condition": cond, "year": r.get("DP", "")[:4],
                            "title": r.get("TI", ""), "abstract": ab}
    print(f"{cond:<26} ids={len(ids):>3}  with_abstract={n_abs:>3}")
    time.sleep(0.34)

records = list(corpus.values())
with open("corpus_abstracts.json", "w") as f:
    json.dump({"search_date": SEARCH_DATE, "conditions": CONDITIONS, "records": records}, f, indent=2)

print("-" * 50)
print(f"Unique abstracts in corpus: {len(records)}")
print(f"Saved corpus_abstracts.json  (search date {SEARCH_DATE})")
