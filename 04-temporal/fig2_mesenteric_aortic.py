"""Task 4 - Figure 2: high-lethality vascular conditions (mesenteric ischemia; aortic dissection)."""
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
MES, MES2, AOR, GRID = "#8172B2", "#B07FD0", "#B8943B", "#E6E6E6"

fig = plt.figure(figsize=(11, 4.4))
gs = gridspec.GridSpec(1, 2, wspace=0.40)

# --- A: mesenteric mortality vs time (data anchors) ---
axM = fig.add_subplot(gs[0])
ax_, ay_ = zip(*P.MES_COHORT_A)
bx_, by_ = zip(*P.MES_COHORT_B)
axM.plot(ax_, ay_, "-o", color=MES, lw=2, ms=7, label=f"\u226424 h vs >24 h surgery ({P.MES_COHORT_A_SRC[1]})")
axM.plot(bx_, by_, "-s", color=MES2, lw=2, ms=7, label=f"dx-to-op 10 h vs 37 h ({P.MES_COHORT_B_SRC[1]})")
axM.set_ylim(40, 100)
axM.set_xlabel("Time to definitive treatment (hours)")
axM.set_ylabel("Mortality (%)")
axM.set_title("A \u00b7 Mesenteric ischemia: mortality vs delay", loc="left")
axM.legend(fontsize=8, frameon=False, loc="lower right")
axM.grid(True, color=GRID, lw=0.7)
c = P.MES_DELAY_AOR
axM.text(0.0, -0.34,
         "DATA anchors (two cohorts). Delay also raised\n"
         f"mortality: consult >24 h aOR {c['consult >24h']}, op >6 h aOR {c['operation >6h']}\n"
         f"({P.MES_DELAY_SRC[1]}). Lethal even with prompt care.",
         transform=axM.transAxes, fontsize=8, color="#666", va="top")

# --- B: aortic cumulative mortality (literature band) ---
axA = fig.add_subplot(gs[1])
lo_r, hi_r = P.AORTIC_MORT_PER_H
ta = np.linspace(0, 48, 300)
axA.fill_between(ta, np.clip(lo_r * ta, 0, 100), np.clip(hi_r * ta, 0, 100),
                 color=AOR, alpha=0.25, label=f"{lo_r:g}\u2013{hi_r:g}%/h range")
axA.plot(ta, P.AORTIC_MORT_MID * ta, color=AOR, lw=2.4, label=f"~{P.AORTIC_MORT_MID:g}%/h midpoint")
y48 = P.AORTIC_MORT_MID * 48
axA.scatter([48], [y48], color=AOR, s=30, zorder=5)
axA.annotate(f"~{y48:.0f}% by 48 h", (48, y48), textcoords="offset points",
             xytext=(-6, 6), fontsize=9, color="#444", ha="right")
axA.set_xlabel("Hours from symptom onset (untreated type-A)")
axA.set_ylabel("Cumulative mortality (%)")
axA.set_title("B \u00b7 Aortic dissection: ~1\u20132% mortality/hour", loc="left")
axA.legend(fontsize=8, frameon=False, loc="upper left")
axA.grid(True, color=GRID, lw=0.7)
axA.text(0.0, -0.34,
         f"LIT constant ({P.AORTIC_MORT_SRC[1]}) \u2014 not from our\n"
         "abstract extraction; aortic delay-harm was absent\nfrom the yield (see Coverage & gaps).",
         transform=axA.transAxes, fontsize=8, color="#666", va="top")

fig.suptitle("Harm-accrual curves \u00b7 high-lethality vascular conditions", fontsize=13, fontweight="bold", y=1.02)
fig.savefig("fig2_mesenteric_aortic.png", bbox_inches="tight", dpi=200)
print("saved fig2_mesenteric_aortic.png")