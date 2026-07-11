"""Task 4 - Figure 1: hours-scale harm accrual (appendicitis perforation; stroke reperfusion benefit)."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import params as P

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.labelsize": 11, "figure.dpi": 110,
})
APP, STR, GRID = "#C44E52", "#4C72B0", "#E6E6E6"

fig = plt.figure(figsize=(11, 4.4))
gs = gridspec.GridSpec(1, 2, wspace=0.40)

# --- A: appendicitis perforation odds vs hours ---
axA = fig.add_subplot(gs[0])
t = np.linspace(0, 72, 400)
orc = P.APP_PERF_OR_PER_H ** t
axA.plot(t, orc, color=APP, lw=2.4)
for h in (12, 24, 48):
    y = P.APP_PERF_OR_PER_H ** h
    axA.scatter([h], [y], color=APP, zorder=5, s=28)
    axA.annotate(f"{h} h\n{y:.2f}\u00d7", (h, y), textcoords="offset points",
                 xytext=(6, -4), fontsize=9, color="#444")
axA.axhline(1, color="#999", lw=0.8, ls=":")
axA.set_xlabel("Hours from ED triage to incision")
axA.set_ylabel("Perforation odds (relative to t = 0)")
axA.set_title("A \u00b7 Appendicitis: perforation odds vs delay", loc="left")
axA.grid(True, color=GRID, lw=0.7)
axA.text(0.0, -0.34,
         f"Model: odds(t) = {P.APP_PERF_OR_PER_H}$^{{t}}$  ({P.APP_PERF_OR_SRC[0]}, {P.APP_PERF_OR_SRC[1]}).\n"
         "Other studies report perforation OR 3.1\u20137.8 for\nlonger delays \u2014 same direction, different cohorts.",
         transform=axA.transAxes, fontsize=8, color="#666", va="top")

# --- B: stroke reperfusion benefit vs time ---
axB = fig.add_subplot(gs[1])
rt = np.array(sorted(P.STROKE_REPERF_RD))
rd = np.array([P.STROKE_REPERF_RD[k] for k in rt], float)
coef = np.polyfit(rt, rd, 1)                       # linear decay through the 3 reported points
xs = np.linspace(2.5, 8, 200)
axB.plot(xs, np.clip(np.polyval(coef, xs), 0, None), color=STR, lw=2.0, ls="--", alpha=0.8)
axB.scatter(rt, rd, color=STR, s=55, zorder=5)
for x, y in zip(rt, rd):
    axB.annotate(f"+{y:.1f}%", (x, y), textcoords="offset points", xytext=(6, 6), fontsize=9, color="#444")
xz = -coef[1] / coef[0]
axB.axhline(0, color="#999", lw=0.8, ls=":")
axB.annotate(f"benefit reaches 0\nby ~{xz:.1f} h", (xz, 0), textcoords="offset points",
             xytext=(-4, 12), fontsize=9, color="#444", ha="right")
axB.set_xlabel("Time to reperfusion (hours)")
axB.set_ylabel("Absolute gain in good outcome\n(mRS 0\u20132, vs no reperfusion)")
axB.set_title("B \u00b7 Stroke: reperfusion benefit vs time", loc="left")
axB.grid(True, color=GRID, lw=0.7)
axB.text(0.0, -0.34,
         f"{P.STROKE_REPERF_SRC[0]}: risk differences at 3/4/6 h ({P.STROKE_REPERF_SRC[1]}).\n"
         f"Untreated large-vessel stroke loses ~{P.STROKE_NEURONS_PER_MIN/1e6:.1f}M\n"
         f"neurons/min ({P.STROKE_NEURONS_SRC[1]}).",
         transform=axB.transAxes, fontsize=8, color="#666", va="top")

fig.suptitle("Harm-accrual curves \u00b7 hours-scale conditions", fontsize=13, fontweight="bold", y=1.02)
fig.savefig("fig1_appendicitis_stroke.png", bbox_inches="tight", dpi=200)
print("saved fig1_appendicitis_stroke.png")
print(f"stroke benefit reaches 0 at t = {xz:.2f} h (slope {coef[0]:.2f} %/h)")