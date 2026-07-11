import json, os, time
from extractor import extract

IN = "corpus_abstracts.json"
OUT = "extractions.jsonl"

with open(IN) as f:
    records = json.load(f)["records"]

# resume: skip PMIDs already written
done = set()
if os.path.exists(OUT):
    with open(OUT) as f:
        for line in f:
            try:
                done.add(json.loads(line)["pmid"])
            except Exception:
                pass

todo = [r for r in records if r["pmid"] not in done]
print(f"{len(records)} total | {len(done)} already done | {len(todo)} to process\n")

with open(OUT, "a") as out:
    for i, rec in enumerate(todo, 1):
        try:
            data = extract(rec)
            err = ""
        except Exception as e:
            data, err = {"contains_estimate": False, "estimates": []}, str(e)
        row = {"pmid": rec["pmid"], "condition": rec["condition"], "year": rec["year"],
               "title": rec["title"],
               "contains_estimate": data.get("contains_estimate", False),
               "estimates": data.get("estimates", []), "error": err}
        out.write(json.dumps(row) + "\n")
        out.flush()
        print(f"[{i}/{len(todo)}] {rec['pmid']} {rec['condition']:<22} "
              f"estimate={row['contains_estimate']} ({len(row['estimates'])})"
              + (f"  ERR: {err}" if err else ""))

print(f"\nDone. Wrote extractions to {OUT}")