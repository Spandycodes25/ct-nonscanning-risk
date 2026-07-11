import os, json, time
from collections import OrderedDict
from datetime import date
from Bio import Entrez, Medline

Entrez.email = "ssurdas@mgh.harvard.edu"
Entrez.api_key = os.environ.get("NCBI_API_KEY")
SEARCH_DATE = date.today().isoformat()

RETMAX = 100     # per indication (relevance-ranked)
BATCH = 100

INDICATIONS = {
    "head_ct_syncope":
        '("syncope"[tiab]) AND ("head CT"[tiab] OR "cranial CT"[tiab] OR "head computed tomography"[tiab] '
        'OR "brain CT"[tiab] OR "neuroimaging"[tiab]) AND ("yield"[tiab] OR "diagnostic yield"[tiab] '
        'OR "abnormal"[tiab] OR "positive"[tiab] OR "clinically important"[tiab] OR "low yield"[tiab])',

    "head_ct_minor_injury":
        '("minor head injury"[tiab] OR "mild head injury"[tiab] OR "mild traumatic brain injury"[tiab] '
        'OR "minor traumatic brain injury"[tiab] OR "minor head trauma"[tiab]) AND '
        '("computed tomography"[tiab] OR "CT scan"[tiab] OR "head CT"[tiab]) AND '
        '("clinically important"[tiab] OR "positive"[tiab] OR "yield"[tiab] OR "neurosurgical"[tiab] '
        'OR "abnormal"[tiab] OR "low yield"[tiab])',

    "ctpa_low_risk_pe":
        '("pulmonary embolism"[tiab]) AND ("CT pulmonary angiography"[tiab] OR "CTPA"[tiab] '
        'OR "CT angiography"[tiab] OR "computed tomography"[tiab]) AND ("yield"[tiab] OR "positive"[tiab] '
        'OR "low risk"[tiab] OR "low-risk"[tiab] OR "D-dimer"[tiab] OR "PERC"[tiab] OR "Wells"[tiab] '
        'OR "overuse"[tiab] OR "negative"[tiab])',

    "ct_cardiac_arrest":
        '("cardiac arrest"[tiab] OR "out-of-hospital cardiac arrest"[tiab]) AND '
        '("computed tomography"[tiab] OR "CT scan"[tiab] OR "head-to-pelvis"[tiab] OR "whole-body CT"[tiab]) '
        'AND ("yield"[tiab] OR "diagnostic yield"[tiab] OR "finding"[tiab] OR "findings"[tiab] OR "cause"[tiab])',

    "recurrent_ct_renal_colic":
        '("renal colic"[tiab] OR "nephrolithiasis"[tiab] OR "ureteral stone"[tiab] OR "kidney stone"[tiab] '
        'OR "urolithiasis"[tiab]) AND ("computed tomography"[tiab] OR "CT"[tiab]) AND ("recurrent"[tiab] '
        'OR "repeat"[tiab] OR "repeated"[tiab] OR "cumulative"[tiab] OR "yield"[tiab] OR "low yield"[tiab] OR "overuse"[tiab])',

    "ct_nonspecific_abdo_pain":
        '("abdominal pain"[tiab]) AND ("computed tomography"[tiab] OR "CT scan"[tiab] OR "abdominal CT"[tiab]) '
        'AND ("nonspecific"[tiab] OR "non-specific"[tiab] OR "recurrent"[tiab] OR "yield"[tiab] '
        'OR "low yield"[tiab] OR "diagnostic yield"[tiab] OR "management"[tiab])',

    "incidentaloma_surveillance":
        '("incidentaloma"[tiab] OR "incidental finding"[tiab] OR "incidental findings"[tiab] '
        'OR "pulmonary nodule"[tiab] OR "adrenal incidentaloma"[tiab] OR "renal incidentaloma"[tiab]) AND '
        '("computed tomography"[tiab] OR "CT"[tiab]) AND ("surveillance"[tiab] OR "follow-up"[tiab] '
        'OR "malignancy"[tiab] OR "overdiagnosis"[tiab] OR "prevalence"[tiab] OR "rate"[tiab])',

    "whole_body_screening":
        '("whole-body CT"[tiab] OR "total-body CT"[tiab] OR "whole body computed tomography"[tiab]) AND '
        '("screening"[tiab] OR "asymptomatic"[tiab] OR "self-referral"[tiab]) AND ("yield"[tiab] '
        'OR "incidental"[tiab] OR "finding"[tiab] OR "findings"[tiab] OR "abnormal"[tiab])',
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

corpus = OrderedDict()   # pmid -> record (dedupes across indications)
for ind, q in INDICATIONS.items():
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
            corpus[pmid] = {"pmid": pmid, "indication": ind, "year": r.get("DP", "")[:4],
                            "title": r.get("TI", ""), "abstract": ab}
    print(f"{ind:<28} ids={len(ids):>3}  with_abstract={n_abs:>3}")
    time.sleep(0.34)

records = list(corpus.values())
with open("corpus_abstracts.json", "w") as f:
    json.dump({"search_date": SEARCH_DATE, "indications": INDICATIONS, "records": records}, f, indent=2)

print("-" * 52)
print(f"Unique abstracts in corpus: {len(records)}")
print(f"Saved corpus_abstracts.json  (search date {SEARCH_DATE})")