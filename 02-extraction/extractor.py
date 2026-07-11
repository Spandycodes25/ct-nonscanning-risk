# extractor.py — reusable non-scanning-harm extraction engine (local qwen2.5 via Ollama)
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
    "imaging (especially CT), diagnosis, or treatment, from biomedical abstracts.\n\n"
    "Record an estimate only when the abstract states an explicit quantitative value tied to "
    "delay / withholding / missed diagnosis AND a worse outcome. If there is no such estimate, "
    "set contains_estimate to false and estimates to [].\n\n"
    "Rules for each estimate:\n"
    "- effect_size: copy the ACTUAL numeric result(s) verbatim, with units, percentages, and "
    "confidence intervals. When two groups are compared, include BOTH values "
    "(e.g., '1.6% (early) vs 43.2% (delayed)' or 'RR 3.31 (95% CI 2.03-5.38)'). "
    "NEVER put a label like 'relative_risk' or 'percentage' in this field; it must contain numbers.\n"
    "- measure_type: the statistic the abstract actually uses. odds_ratio for OR or common odds "
    "ratio (cOR); hazard_ratio for HR; relative_risk for RR; percentage or absolute_rate for a plain "
    "rate/proportion; per_unit_time_rate for a per-hour/per-minute figure; mean_difference; else other.\n"
    "- outcome_measure: a short plain-English name (e.g., 'in-hospital mortality', '90-day mRS', "
    "'perforation rate').\n"
    "- what_was_delayed: imaging/CT, diagnosis, or treatment.\n"
    "- supporting_quote: the exact sentence(s) from the abstract containing the number(s).\n"
    "- Use an empty string for any detail not stated. Do NOT invent numbers.\n\n"
    "The diagnostic accuracy of CT (sensitivity/specificity) or radiation dose alone is NOT a "
    "non-scanning-harm estimate.\n\n"
    "Example done right: abstract says 'mortality was 1.6% with early diagnosis and 43.2% with "
    "delayed diagnosis' -> effect_size = '1.6% (early) vs 43.2% (delayed)', measure_type = 'percentage'."
)

def extract(rec):
    """Structured extraction for one corpus record (dict with condition/title/abstract)."""
    user_text = (f"Condition (search tag): {rec['condition']}\n\n"
                 f"Title: {rec['title']}\n\nAbstract:\n{rec['abstract']}")
    resp = ollama.chat(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": user_text}],
        format=SCHEMA,
        options={"temperature": 0, "num_ctx": 8192},
    )
    return json.loads(resp["message"]["content"])