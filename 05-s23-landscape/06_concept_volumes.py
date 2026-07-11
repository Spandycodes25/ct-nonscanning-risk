import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATE = "2026-06-10"

# (label, count, side, MeSH-indexed)  — from the refined counts + corpus totals
ROWS = [
    ("Overuse / inappropriate / appropriateness", 7189, "harm", True),
    ("Incidental findings / overdiagnosis",       3391, "harm", True),
    ("Diagnostic yield (CT as a test)",            992, "benefit", False),
    ("Cumulative / recurrent radiation dose",      938, "harm", False),
    ("MeSH: Medical Overuse / Unnecessary Procedures", 805, "harm", True),
    ("Net / marginal benefit of scanning (named)", 154, "benefit", False),
]
ROWS = sorted(ROWS, key=lambda r: r[1])  # ascending -> longest on top in barh

labels = [r[0] for r in ROWS]
counts = [r[1] for r in ROWS]
colors = ["#c0392b" if r[2] == "harm" else "#2471a3" for r in ROWS]
y = list(range(len(ROWS)))

fig, ax = plt.subplots(figsize=(11, 5.6))
ax.barh(y, counts, color=colors, edgecolor="white")
ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=10)
for yi, r in zip(y, ROWS):
    tag = "  (MeSH-indexed)" if r[3] else ""
    ax.text(r[1] + 90, yi, f"{r[1]:,}{tag}", va="center", fontsize=9, color="#555")

ax.set_xlabel(f"PubMed articles (title/abstract; search date {DATE})")
ax.set_title("CT overuse/harm is quantified and indexed; the benefit/yield of scanning is not\n"
             "harm/overuse side (red) vs benefit/yield side (blue)", fontsize=12)
ax.set_xlim(0, max(counts) * 1.20)
ax.text(0.98, 0.06,
        "Corpus totals:  overuse/harm 11,220   vs   benefit/yield 1,216   (~9:1)",
        transform=ax.transAxes, ha="right", fontsize=10, style="italic",
        bbox=dict(boxstyle="round", fc="#f3efe7", ec="#cccccc"))
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
plt.tight_layout()
plt.savefig("s23_concept_volumes.png", dpi=220, bbox_inches="tight")
plt.savefig("s23_concept_volumes.svg", bbox_inches="tight")
print("Saved s23_concept_volumes.png / .svg")