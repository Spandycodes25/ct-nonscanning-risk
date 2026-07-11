import json, re, csv
from collections import Counter

with open("corpus_abstracts.json") as f:
    abstracts = {r["pmid"]: r["abstract"] for r in json.load(f)["records"]}

rows = [json.loads(l) for l in open("extractions.jsonl") if l.strip()]

def norm(s):
    return re.sub(r"\s+", " ", (s or "").lower()).strip()

def is_logistics(e):
    o = norm(e.get("outcome_measure", ""))
    return "time to ct" in o or "time to computed tomography" in o

out_rows = []
for r in rows:
    ab = norm(abstracts.get(r["pmid"], ""))
    for e in r.get("estimates", []):
        q = norm(e.get("supporting_quote", ""))
        grounded = bool(q) and q in ab
        flags = []
        if not grounded: flags.append("ungrounded")
        if is_logistics(e): flags.append("logistics_time_to_ct")
        out_rows.append({
            "condition": r["condition"], "pmid": r["pmid"], "year": r["year"],
            "outcome_measure": e.get("outcome_measure", ""),
            "effect_size": e.get("effect_size", ""),
            "measure_type": e.get("measure_type", ""),
            "comparison": e.get("comparison", ""),
            "population": e.get("population", ""),
            "follow_up": e.get("follow_up", ""),
            "what_was_delayed": e.get("what_was_delayed", ""),
            "grounded": grounded,
            "review_flag": "|".join(flags),
            "supporting_quote": e.get("supporting_quote", ""),
            "title": r["title"],
        })

cols = ["condition", "pmid", "year", "outcome_measure", "effect_size", "measure_type",
        "comparison", "population", "follow_up", "what_was_delayed", "grounded",
        "review_flag", "supporting_quote", "title"]
with open("harm_estimates_candidate.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader(); w.writerows(out_rows)

print(f"Total estimates: {len(out_rows)}")
print(f"Grounded: {sum(r['grounded'] for r in out_rows)}/{len(out_rows)}")
print(f"Auto-flagged (ungrounded or logistics): {sum(1 for r in out_rows if r['review_flag'])}\n")
print("Per condition:")
for c, n in Counter(r["condition"] for r in out_rows).items():
    print(f"  {c:<24} {n}")
print("\nWrote harm_estimates_candidate.csv")