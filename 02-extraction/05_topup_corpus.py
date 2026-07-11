import os, json, time
from datetime import date
from Bio import Entrez, Medline

Entrez.email = "your-email@example.com"
Entrez.api_key = os.environ.get("NCBI_API_KEY")

RETMAX = 50
BATCH = 100

# outcome-focused queries that exclude narrative reviews/management overviews
TOPUP = {
    "subarachnoid_hemorrhage":
        '("subarachnoid hemorrhage"[tiab] OR "subarachnoid haemorrhage"[tiab]) AND '
        '("misdiagnosis"[tiab] OR "missed diagnosis"[tiab] OR "delayed diagnosis"[tiab] OR '
        '"rebleeding"[tiab] OR "rebleed"[tiab] OR "case fatality"[tiab]) AND '
        '(mortality[tiab] OR rate[tiab] OR incidence[tiab] OR risk[tiab] OR "odds ratio"[tiab]) '
        'NOT (review[ti] OR management[ti] OR overview[ti] OR update[ti])',
    "aortic_dissection":
        '("aortic dissection"[tiab]) AND ("delayed diagnosis"[tiab] OR "diagnostic delay"[tiab] OR '
        'misdiagnosis[tiab] OR "time to diagnosis"[tiab] OR missed[tiab]) AND '
        '(mortality[tiab] OR death[tiab] OR survival[tiab] OR "per hour"[tiab] OR rate[tiab]) '
        'NOT (review[ti] OR management[ti])',
    "mesenteric_ischemia":
        '("mesenteric ischemia"[tiab] OR "mesenteric ischaemia"[tiab]) AND (delayed[tiab] OR '
        '"diagnostic delay"[tiab] OR "time to"[tiab]) AND (mortality[tiab] OR death[tiab] OR '
        'survival[tiab] OR rate[tiab]) NOT (review[ti] OR management[ti])',
}

with open("corpus_abstracts.json") as f:
    blob = json.load(f)
records = blob["records"]
existing = {r["pmid"] for r in records}

def esearch_ids(q, retmax):
    h = Entrez.esearch(db="pubmed", term=q, retmax=retmax, sort="relevance")
    ids = Entrez.read(h)["IdList"]; h.close()
    return ids

def fetch_medline(pmids):
    out = []
    for i in range(0, len(pmids), BATCH):
        h = Entrez.efetch(db="pubmed", id=",".join(pmids[i:i + BATCH]),
                          rettype="medline", retmode="text")
        out.extend(list(Medline.parse(h))); h.close(); time.sleep(0.4)
    return out

added_total = 0
for cond, q in TOPUP.items():
    ids = esearch_ids(q, RETMAX)
    time.sleep(0.34)
    new_ids = [i for i in ids if i not in existing]
    recs = fetch_medline(new_ids) if new_ids else []
    added = 0
    for r in recs:
        pmid, ab = r.get("PMID", ""), r.get("AB", "")
        if not pmid or not ab or pmid in existing:
            continue
        records.append({"pmid": pmid, "condition": cond, "year": r.get("DP", "")[:4],
                        "title": r.get("TI", ""), "abstract": ab})
        existing.add(pmid); added += 1
    added_total += added
    print(f"{cond:<24} query_hits={len(ids):>3}  new_added={added:>3}")
    time.sleep(0.34)

blob["records"] = records
blob["topup_date"] = date.today().isoformat()
with open("corpus_abstracts.json", "w") as f:
    json.dump(blob, f, indent=2)

print("-" * 50)
print(f"Added {added_total} new abstracts. Corpus now {len(records)} records.")
