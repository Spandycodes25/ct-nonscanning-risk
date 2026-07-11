"""Task 4 - Figure 3: comparative time-criticality of the non-scanning decision (log-time)."""
import matplotlib.pyplot as plt
import params as P

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 14,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 16, "axes.titleweight": "bold",
    "axes.labelsize": 15, "figure.dpi": 110,
})
STR, AOR, MES, PE, APP = "#4C72B0", "#B8943B", "#8172B2", "#55A868", "#C44E52"
DAY = 1440
pct_per_h = (P.APP_PERF_OR_PER_H - 1) * 100        # 1.02 -> +2%/h

# label, t_start (min), t_end (min), color, rate-note
bars = [
    ("Ischemic stroke",     1,       6 * 60,  STR, f"~{P.STROKE_NEURONS_PER_MIN/1e6:.1f}M neurons/min; thrombectomy window \u22646 h"),
    ("Aortic dissection",   30,      48 * 60, AOR, f"~{P.AORTIC_MORT_PER_H[0]:g}\u2013{P.AORTIC_MORT_PER_H[1]:g}% mortality / hour (untreated type-A)"),
    ("Mesenteric ischemia", 6 * 60,  24 * 60, MES, f"critical ~6\u201324 h; aOR {P.MES_DELAY_AOR['consult >24h']} if consult >24 h"),
    ("Pulmonary embolism",  6 * 60,  3 * DAY, PE,  f"delay >24 h \u2192 mortality RR {P.PE_DELAY_RR}"),
    ("Appendicitis",        12 * 60, 3 * DAY, APP, f"perforation odds +{pct_per_h:.0f}% / hour"),
]

fig, ax = plt.subplots(figsize=(11, 4.6))
for i, (lab, a, b, col, note) in enumerate(bars):
    y = len(bars) - i
    ax.plot([a, b], [y, y], color=col, lw=11, solid_capstyle="round", alpha=0.85)
    ax.text(a * 0.8, y, lab, ha="right", va="center", fontsize=14, fontweight="bold", color="#222")
    ax.text(b * 1.15, y, note, ha="left", va="center", fontsize=12, fontweight="bold", color="#555")
ax.set_xscale("log")
ax.set_xlim(0.6, 4e4)
ax.set_ylim(0.3, len(bars) + 0.8)
ax.set_yticks([])
ax.set_xticks([1, 5, 15, 60, 180, 360, 1440, 2880, 10080])
ax.set_xticklabels(["1 min", "5 min", "15 min", "1 h", "3 h", "6 h", "1 day", "2 days", "7 days"], fontsize=13)
ax.grid(True, axis="x", color="#E6E6E6", lw=0.7)
ax.spines["left"].set_visible(False)
ax.set_xlabel("Time from symptom onset (log scale)")
ax.set_title("Time-criticality of the non-scanning decision spans orders of magnitude", fontsize=13)
ax.text(0.0, -0.22,
        "Bars mark each condition's decision-critical window; rates are harm-accrual estimates from the extracted literature or\n"
        "cited constants. The cost of withholding CT is real for all five, but its time constant ranges from minutes (stroke) to days (appendicitis).",
        transform=ax.transAxes, fontsize=8.5, color="#666", va="top")
fig.savefig("fig3_time_criticality.png", bbox_inches="tight", dpi=200)
print("saved fig3_time_criticality.png")