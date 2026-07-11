import json, csv
from collections import defaultdict

IN  = "extractions.jsonl"
OUT = "yield_benefit_estimates.csv"

LABEL = {
 "head_ct_syncope":"Head CT in syncope",
 "head_ct_minor_injury":"Head CT in minor head injury",
 "ctpa_low_risk_pe":"CTPA for suspected PE",
 "ct_cardiac_arrest":"CT after cardiac arrest",
 "recurrent_ct_renal_colic":"CT for renal colic / stones",
 "ct_nonspecific_abdo_pain":"CT for abdominal pain",
 "incidentaloma_surveillance":"Incidental findings on CT",
 "whole_body_screening":"Whole-body CT screening",
}
ORDER = ["head_ct_syncope","head_ct_minor_injury","ctpa_low_risk_pe","ct_cardiac_arrest",
         "incidentaloma_surveillance","ct_nonspecific_abdo_pain","recurrent_ct_renal_colic","whole_body_screening"]

# estimates removed on manual validation, with the reason for each
DROP_PMIDS = {
    "30054114": "42% figure is coronary angiography, not CT",
    "34083228": "misindexed to syncope; actually head CT in hepatic encephalopathy / AMS",
    "35169500": "effect size does not match its supporting quote",
}
def drop_reason(pmid, e):
    if pmid in DROP_PMIDS:
        return DROP_PMIDS[pmid]
    if pmid == "41552157" and e.get("measure") == "number_needed_to_scan":
        return "number-needed-to-scan was computed by the model, not stated in the abstract"
    return None

rows = [json.loads(l) for l in open(IN)]
raw = sum(len(r.get("estimates", [])) for r in rows)

cur, dropped = [], []
for r in rows:
    for e in r.get("estimates", []):
        reason = drop_reason(r["pmid"], e)
        if reason:
            dropped.append((r["pmid"], e.get("measure", ""), e.get("effect_size", ""), reason))
            continue
        cur.append({
            "indication_label": LABEL.get(r["indication"], r["indication"]),
            "measure": e.get("measure", ""), "effect_size": e.get("effect_size", ""),
            "outcome_measure": e.get("outcome_measure", ""), "population": e.get("population", ""),
            "year": r["year"], "pmid": r["pmid"], "supporting_quote": e.get("supporting_quote", ""),
            "_ord": ORDER.index(r["indication"]) if r["indication"] in ORDER else 99,
        })

cur.sort(key=lambda x: (x["_ord"], x["pmid"]))
fields = ["indication_label", "measure", "effect_size", "outcome_measure", "population", "year", "pmid", "supporting_quote"]
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    w.writeheader(); w.writerows(cur)

print(f"Raw estimates : {raw}")
print(f"Dropped       : {len(dropped)}")
for pmid, m, eff, reason in dropped:
    print(f"  - PMID {pmid} [{m}] {eff[:38]}  ->  {reason}")
print(f"Curated       : {len(cur)}  (written to {OUT})")
print("Per-indication:")
by = defaultdict(int)
for c in cur:
    by[c["indication_label"]] += 1
for k in ORDER:
    print(f"  {LABEL[k]:<32} {by[LABEL[k]]}")