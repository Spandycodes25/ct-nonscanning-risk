import json, os
import ollama

MODEL = "qwen2.5:7b"
CORPUS = "corpus_abstracts.json"
OUT = "extractions.jsonl"

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

with open(CORPUS) as f:
    records = json.load(f)["records"]

done = set()
if os.path.exists(OUT):
    with open(OUT) as f:
        for line in f:
            try:
                done.add(json.loads(line)["pmid"])
            except Exception:
                pass
print(f"{len(records)} records; {len(done)} already done; {len(records) - len(done)} to go.", flush=True)

run_est = 0
with open(OUT, "a") as out:
    for i, rec in enumerate(records, 1):
        if rec["pmid"] in done:
            continue
        try:
            res = extract(rec)
        except Exception as e:
            res = {"contains_estimate": False, "estimates": [], "error": str(e)}
        row = {"pmid": rec["pmid"], "indication": rec["indication"], "year": rec["year"],
               "title": rec["title"], **res}
        out.write(json.dumps(row) + "\n"); out.flush()
        run_est += len(res.get("estimates", []))
        if i % 20 == 0:
            print(f"  {i}/{len(records)}  (estimates so far this run: {run_est})", flush=True)

# final tally across the whole file
recs = wat = est = 0
by_ind = {}
with open(OUT) as f:
    for line in f:
        r = json.loads(line)
        recs += 1
        by_ind.setdefault(r["indication"], [0, 0])
        if r.get("contains_estimate") and r.get("estimates"):
            wat += 1; est += len(r["estimates"])
            by_ind[r["indication"]][0] += 1
            by_ind[r["indication"]][1] += len(r["estimates"])
print(f"\nTotal: {recs} abstracts processed, {wat} with >=1 estimate, {est} estimates.")
for k in sorted(by_ind):
    print(f"  {k:<28} abstracts_with_est={by_ind[k][0]:>3}  estimates={by_ind[k][1]:>3}")
print(f"Wrote {OUT}")