import json
from collections import defaultdict
import ollama

MODEL = "qwen2.5:7b"

SCHEMA = {
    "type": "object",
    "properties": {
        "contains_estimate": {"type": "boolean"},
        "estimates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "indication": {"type": "string"},
                    "measure": {"type": "string",
                        "description": "diagnostic_yield, positive_or_abnormal_rate, clinically_important_finding_rate, number_needed_to_scan, overdiagnosis_or_incidentaloma_rate, incidentaloma_malignancy_rate, marginal_outcome_benefit, or other"},
                    "outcome_measure": {"type": "string", "description": "plain description of what was measured"},
                    "effect_size": {"type": "string", "description": "value exactly as reported, e.g. '4.2%', '1 in 14', '0.8% had a neurosurgical lesion'"},
                    "measure_type": {"type": "string", "description": "percentage, proportion, number_needed_to_scan, rate, odds_ratio, mean_difference, or other"},
                    "population": {"type": "string", "description": "e.g. 'adults with syncope, n=1024'; empty string if not stated"},
                    "supporting_quote": {"type": "string", "description": "exact sentence/phrase from the abstract"}
                },
                "required": ["indication", "measure", "outcome_measure", "effect_size", "measure_type", "population", "supporting_quote"]
            }
        }
    },
    "required": ["contains_estimate", "estimates"]
}

SYSTEM = (
    "You extract quantitative estimates of the YIELD, BENEFIT, or OVERDIAGNOSIS of performing a CT scan "
    "in low-yield or overused settings, from one biomedical abstract.\n\n"
    "Record an estimate ONLY when the abstract gives an explicit quantitative value for one of:\n"
    "- diagnostic_yield / positive_or_abnormal_rate: the PROPORTION OF SCANS showing a positive, abnormal, "
    "or clinically important finding (e.g. 'head CT was abnormal in 4%').\n"
    "- clinically_important_finding_rate: proportion of scans with a clinically important / actionable finding.\n"
    "- number_needed_to_scan: a COUNT of scans per one positive finding (e.g. '250' or '1 in 250'), NEVER a percentage.\n"
    "- overdiagnosis_or_incidentaloma_rate: proportion of scans with an incidental finding, or the "
    "malignancy rate among incidental findings.\n"
    "- marginal_outcome_benefit: a change in management, mortality, or outcome attributable to scanning vs not.\n\n"
    "NEVER record sensitivity, specificity, positive or negative predictive value, accuracy, AUC, or a "
    "decision rule's performance as an estimate, even when written as a percentage. Those are NOT yield/benefit. "
    "If the only numbers in the abstract are accuracy / sensitivity / specificity, set contains_estimate to false.\n"
    "Copy effect sizes verbatim; never invent or reinterpret numbers. supporting_quote must be the exact "
    "sentence containing the number.\n\n"
    "Examples:\n"
    "GOOD: 'CT detected a clinically important finding in 6.2% of patients' -> measure=clinically_important_finding_rate, effect_size='6.2%'.\n"
    "GOOD: '1 in 14 scans changed management' -> measure=number_needed_to_scan, effect_size='1 in 14'.\n"
    "GOOD: 'an incidental finding was reported in 31% of scans' -> measure=overdiagnosis_or_incidentaloma_rate, effect_size='31%'.\n"
    "REJECT: 'the rule was 100% sensitive (95% CI 92-100)' -> accuracy metric, contains_estimate=false.\n"
    "REJECT: 'specificity was 48%' -> accuracy metric, not yield."
)

def extract(rec):
    resp = ollama.chat(
        model=MODEL, format=SCHEMA, options={"temperature": 0},
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content":
                f"Indication (search tag): {rec['indication']}\n\nTitle: {rec['title']}\n\nAbstract:\n{rec['abstract']}"},
        ],
    )
    return json.loads(resp["message"]["content"])

with open("corpus_abstracts.json") as f:
    records = json.load(f)["records"]

by_ind = defaultdict(list)
for r in records:
    by_ind[r["indication"]].append(r)

sample = []
for ind, recs in by_ind.items():
    n = len(recs)
    idxs = sorted(set(min(n - 1, int(n * f)) for f in (0.2, 0.5, 0.8)))
    for i in idxs:
        sample.append(recs[i])

hits = 0
for rec in sample:
    out = extract(rec)
    print("=" * 92)
    print(f"{rec['indication']}  | PMID {rec['pmid']} ({rec['year']})")
    print(f"  {rec['title'][:88]}")
    print(f"  contains_estimate: {out['contains_estimate']}  ({len(out['estimates'])} estimate(s))")
    if out["estimates"]:
        hits += 1
    for e in out["estimates"]:
        print(f"    - [{e['measure']}] {e['effect_size']}  |  {e['outcome_measure'][:64]}")
        print(f"        quote: {e['supporting_quote'][:110]}")
print("=" * 92)
print(f"Tested {len(sample)} abstracts (spread across indications); {hits} returned at least one estimate.")