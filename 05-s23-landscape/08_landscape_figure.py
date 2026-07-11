import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

counts, search_date = {}, ""
with open("s23_landscape_counts_refined.csv") as f:
    for row in csv.DictReader(f):
        counts[row["category"]] = int(row["count"])
        search_date = row["search_date"]
g = lambda k: counts.get(k, 0)

# Rehani regrouping: pool named overuse + MeSH overuse into one bar;
# appropriateness pulled out and shown separately (neutral, not summed)
overuse_pooled = g("overuse_clean") + g("overuse_mesh")
harm = [
    ("Overuse / inappropriate use", overuse_pooled),
    ("Incidental findings / overdiagnosis", g("incidental")),
    ("Cumulative / recurrent radiation dose", g("cumulative_dose")),
]
benefit = [
    ("Diagnostic yield (as a test)", g("yield_test")),
    ("Net / marginal benefit", g("benefit_named_clean")),
]
neutral = [("Appropriateness (shown separately)", g("appropriateness"))]

harm_total = sum(v for _, v in harm)
benefit_total = sum(v for _, v in benefit)
ratio = harm_total / benefit_total if benefit_total else float("inf")

HARM, BEN, NEU = "#c0392b", "#2471a3", "#7f8c8d"
rows = ([(l, v, HARM) for l, v in harm]
        + [(l, v, NEU) for l, v in neutral]
        + [(l, v, BEN) for l, v in benefit])
rows.sort(key=lambda r: r[1])           # largest ends at the top
labels = [r[0] for r in rows]; vals = [r[1] for r in rows]; colors = [r[2] for r in rows]

plt.rcParams.update({"font.size": 16})
fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.barh(labels, vals, color=colors, edgecolor="white", height=0.68)
ax.bar_label(bars, labels=[f"{v:,}" for v in vals], padding=5, fontsize=15)
ax.set_xlim(0, max(vals) * 1.18)
ax.set_xlabel("PubMed articles (title/abstract, with MeSH where indexed)", fontsize=16)
ax.tick_params(axis="y", labelsize=16)
ax.set_title("How often CT overuse and harm are quantified, versus the benefit of scanning\n"
             f"(PubMed, search date {search_date})", fontsize=18, pad=14)

summary = (f"Overuse and harm: {harm_total:,}\n"
           f"Benefit and yield: {benefit_total:,}\n"
           f"about {ratio:.0f} to 1")
ax.text(0.985, 0.04, summary, transform=ax.transAxes, ha="right", va="bottom",
        fontsize=15, bbox=dict(boxstyle="round,pad=0.5", fc="#f7f7f7", ec="#cccccc"))
ax.legend(handles=[Patch(facecolor=HARM, label="Overuse / harm of scanning"),
                   Patch(facecolor=BEN,  label="Benefit / yield of scanning"),
                   Patch(facecolor=NEU,  label="Appropriateness (not summed)")],
          loc="lower right", bbox_to_anchor=(0.985, 0.30), fontsize=14, frameon=False)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
plt.tight_layout()
plt.savefig("s23_concept_volumes.png", dpi=220, bbox_inches="tight")
plt.savefig("s23_concept_volumes.svg", bbox_inches="tight")

print("Bars:")
for l, v in harm + neutral + benefit:
    print(f"  {v:>7,}  {l}")
print(f"\nOveruse/harm total : {harm_total:,}")
print(f"Benefit/yield total: {benefit_total:,}")
print(f"Ratio              : about {ratio:.1f} to 1")
print("Saved s23_concept_volumes.png and .svg")