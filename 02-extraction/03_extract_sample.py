import json, time
from collections import defaultdict
from extractor import extract

PER_CONDITION = 2   # sample size per condition for this quality check

with open("corpus_abstracts.json") as f:
    records = json.load(f)["records"]

by_cond = defaultdict(list)
for r in records:
    if len(by_cond[r["condition"]]) < PER_CONDITION:
        by_cond[r["condition"]].append(r)
sample = [r for rs in by_cond.values() for r in rs]

print(f"Extracting from {len(sample)} abstracts ({PER_CONDITION} per condition)...\n")
for rec in sample:
    data = extract(rec)
    print("=" * 90)
    print(f"PMID {rec['pmid']} | {rec['condition']} ({rec['year']}) | estimate={data['contains_estimate']}")
    print(f"  {rec['title']}")
    for e in data["estimates"]:
        print(f"   - {e['outcome_measure']}: {e['effect_size']}  [{e['measure_type']}]  "
              f"(delayed: {e['what_was_delayed']}; cmp: {e['comparison'] or '-'})")
        print(f"     quote: \"{e['supporting_quote']}\"")
    time.sleep(0.2)
print("=" * 90)