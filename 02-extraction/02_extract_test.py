import json
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
                    "condition": {"type": "string"},
                    "what_was_delayed": {"type": "string"},
                    "outcome_measure": {"type": "string"},
                    "effect_size": {"type": "string"},
                    "measure_type": {"type": "string"},
                    "comparison": {"type": "string"},
                    "population": {"type": "string"},
                    "follow_up": {"type": "string"},
                    "supporting_quote": {"type": "string"}
                },
                "required": ["condition", "what_was_delayed", "outcome_measure", "effect_size",
                             "measure_type", "comparison", "population", "follow_up", "supporting_quote"]
            }
        }
    },
    "required": ["contains_estimate", "estimates"]
}

SYSTEM = (
    "You extract quantitative estimates of the harm of NOT performing, delaying, or withholding "
    "imaging (especially CT), diagnosis, or treatment from biomedical abstracts. Only record an "
    "estimate when the abstract gives an explicit quantitative value (a rate, percentage, ratio, or "
    "per-unit-time figure) tied to delay / withholding / missed diagnosis AND a worse outcome. "
    "Do NOT invent numbers; copy each effect size verbatim from the abstract. The diagnostic accuracy "
    "of CT (sensitivity/specificity) or radiation dose alone is NOT a non-scanning-harm estimate. "
    "If the abstract has no such estimate, set contains_estimate to false and estimates to []. "
    "Fill every field; use an empty string when a detail is not stated. measure_type must be one of: "
    "absolute_rate, percentage, odds_ratio, hazard_ratio, relative_risk, per_unit_time_rate, "
    "mean_difference, other."
)

with open("corpus_abstracts.json") as f:
    records = json.load(f)["records"]

rec = records[0]
print(f"TEST ON: PMID {rec['pmid']}  ({rec['condition']}, {rec['year']})")
print(f"Title: {rec['title']}\n")
print("Abstract:")
print(rec["abstract"])
print("\n--- EXTRACTION ---")

user_text = (f"Condition (search tag): {rec['condition']}\n\n"
             f"Title: {rec['title']}\n\nAbstract:\n{rec['abstract']}")

resp = ollama.chat(
    model=MODEL,
    messages=[{"role": "system", "content": SYSTEM},
              {"role": "user", "content": user_text}],
    format=SCHEMA,
    options={"temperature": 0, "num_ctx": 8192},
)

data = json.loads(resp["message"]["content"])
print(json.dumps(data, indent=2))