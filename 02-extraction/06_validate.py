import json, re, random
random.seed(7)

with open("corpus_abstracts.json") as f:
    abstracts = {r["pmid"]: r["abstract"] for r in json.load(f)["records"]}

rows = [json.loads(l) for l in open("extractions.jsonl") if l.strip()]

def norm(s):
    return re.sub(r"\s+", " ", (s or "").lower()).strip()

items = []
for r in rows:
    ab = norm(abstracts.get(r["pmid"], ""))
    for e in r.get("estimates", []):
        q = norm(e.get("supporting_quote", ""))
        grounded = bool(q) and q in ab
        items.append({"pmid": r["pmid"], "condition": r["condition"],
                      "outcome": e.get("outcome_measure", ""), "effect": e.get("effect_size", ""),
                      "mtype": e.get("measure_type", ""), "quote": e.get("supporting_quote", ""),
                      "grounded": grounded})

n = len(items)
g = sum(it["grounded"] for it in items)
print(f"Total estimates: {n}")
print(f"Grounded (quote found verbatim in abstract): {g}/{n} = {100*g/n:.0f}%")
print(f"Ungrounded (need manual check): {n - g}\n")

ung = [it for it in items if not it["grounded"]]
if ung:
    print("=== UNGROUNDED ESTIMATES — verify each ===")
    for it in ung:
        print(f"[{it['condition']}] PMID {it['pmid']} | {it['outcome']} = {it['effect']} [{it['mtype']}]")
        print(f"   quote: \"{it['quote']}\"\n")

print("=== RANDOM SAMPLE (grounded) — spot-check faithfulness ===")
gs = [it for it in items if it["grounded"]]
for it in random.sample(gs, min(10, len(gs))):
    print(f"[{it['condition']}] PMID {it['pmid']} | {it['outcome']} = {it['effect']} [{it['mtype']}]")
    print(f"   quote: \"{it['quote']}\"\n")