import os, json, time
from datetime import date
from Bio import Entrez, Medline

Entrez.email = "ssurdas@mgh.harvard.edu"
Entrez.api_key = os.environ.get("NCBI_API_KEY")
SEARCH_DATE = date.today().isoformat()

RETMAX = 90
BATCH = 100

TOPUP = {
    "recurrent_ct_renal_colic":
        '("nephrolithiasis"[tiab] OR "renal colic"[tiab] OR "ureteral stone"[tiab] OR "urolithiasis"[tiab] '
        'OR "kidney stone"[tiab] OR "ureteric colic"[tiab]) AND ("computed tomography"[tiab] OR "CT"[tiab]) AND '
        '("number of CT"[tiab] OR "repeat imaging"[tiab] OR "recurrent stone"[tiab] OR "cumulative"[tiab] '
        'OR "diagnostic yield"[tiab] OR "changed management"[tiab] OR "change in management"[tiab] OR "low-dose"[tiab]) '
        'NOT (Case Reports[pt])',
    "ct_nonspecific_abdo_pain":
        '("abdominal pain"[tiab]) AND ("computed tomography"[tiab] OR "abdominal CT"[tiab] OR "CT scan"[tiab]) AND '
        '("diagnostic yield"[tiab] OR "changed management"[tiab] OR "change in management"[tiab] '
        'OR "clinically significant"[tiab] OR "low yield"[tiab] OR "negative CT"[tiab] OR "nonspecific"[tiab]) '
        'NOT (Case Reports[pt])',
    "whole_body_screening":
        '("whole-body CT"[tiab] OR "total-body CT"[tiab] OR "whole body computed tomography"[tiab]) AND '
        '("screening"[tiab] OR "asymptomatic"[tiab] OR "self-referral"[tiab] OR "self referral"[tiab]) AND '
        '("finding"[tiab] OR "findings"[tiab] OR "yield"[tiab] OR "prevalence"[tiab] OR "abnormal"[tiab]) '
        'NOT (Case Reports[pt])',
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
        recs.extend(list(Medline.parse(h))); h.close()
        time.sleep(0.4)
    return recs

with open("corpus_abstracts.json") as f:
    blob = json.load(f)
records = blob["records"]
existing = {r["pmid"] for r in records}
print(f"Existing corpus: {len(records)} records.")

added = {}
for ind, q in TOPUP.items():
    ids = esearch_ids(q, RETMAX); time.sleep(0.34)
    recs = fetch_medline(ids)
    n_new = 0
    for r in recs:
        pmid, ab = r.get("PMID", ""), r.get("AB", "")
        if not pmid or not ab or pmid in existing:
            continue
        existing.add(pmid); n_new += 1
        records.append({"pmid": pmid, "indication": ind, "year": r.get("DP", "")[:4],
                        "title": r.get("TI", ""), "abstract": ab})
    added[ind] = n_new
    print(f"{ind:<28} ids={len(ids):>3}  new_added={n_new:>3}")
    time.sleep(0.34)

blob["records"] = records
blob["topup_date"] = SEARCH_DATE
blob.setdefault("topup_queries", {}).update(TOPUP)
with open("corpus_abstracts.json", "w") as f:
    json.dump(blob, f, indent=2)

print("-" * 52)
print(f"Total new added: {sum(added.values())}")
print(f"Corpus now: {len(records)} records.  Saved corpus_abstracts.json")