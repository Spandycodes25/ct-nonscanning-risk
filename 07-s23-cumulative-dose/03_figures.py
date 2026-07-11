import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("cumulative_model.csv")

SCAN_ORDER = ["Head CT", "Chest CT (routine)", "CTPA (suspected PE)",
              "Abdomen/pelvis CT (single-phase)", "Abdomen/pelvis CT (multiphase)"]
SCAN_COLORS = {
    "Head CT": "#4C9F70",
    "Chest CT (routine)": "#E0A030",
    "CTPA (suspected PE)": "#D9694A",
    "Abdomen/pelvis CT (single-phase)": "#3D6B9E",
    "Abdomen/pelvis CT (multiphase)": "#8E4B9E",
}
AGE_COLORS = {20: "#C0392B", 40: "#E0A030", 60: "#3D6B9E"}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False})

# Figure 1: cumulative effective dose vs number of scans (dose is age/sex-independent)
fig, ax = plt.subplots(figsize=(8, 5))
sub = df[(df.age == 40) & (df.sex == "F")]
for scan in SCAN_ORDER:
    d = sub[sub.scan == scan]
    ax.plot(d.n_scans, d.cum_dose_mSv, color=SCAN_COLORS[scan], lw=2, label=scan)
ax.axhline(100, ls="--", color="#888888", lw=1.2)
ax.text(30, 103, "100 mSv", ha="right", va="bottom", color="#666666", fontsize=9)
ax.set_xlabel("Number of CT examinations")
ax.set_ylabel("Cumulative effective dose (mSv)")
ax.set_title("Cumulative radiation dose accrues with repeat CT", fontsize=12, weight="bold")
ax.set_xlim(1, 30); ax.set_ylim(0, None)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
ax.grid(axis="y", alpha=0.25)
fig.tight_layout(); fig.savefig("fig1_cumulative_dose.png", dpi=150); plt.close(fig)

# Figure 2: cumulative added cancer risk vs N, by scan type, age 40 (woman | man)
fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharey=True)
for ax, sex, title in zip(axes, ("F", "M"), ("40-year-old woman", "40-year-old man")):
    sub = df[(df.age == 40) & (df.sex == sex)]
    for scan in SCAN_ORDER:
        d = sub[sub.scan == scan]
        ax.plot(d.n_scans, d.cum_LAR_pct, color=SCAN_COLORS[scan], lw=2, label=scan)
    ax.axhline(1.0, ls="--", color="#888888", lw=1.2)
    ax.text(30, 1.03, "1%", ha="right", va="bottom", color="#666666", fontsize=9)
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("Number of CT examinations")
    ax.set_xlim(1, 30); ax.set_ylim(0, None)
    ax.grid(axis="y", alpha=0.25)
axes[0].set_ylabel("Cumulative added cancer risk (%)")
axes[1].legend(fontsize=8, frameon=False, loc="upper left")
fig.suptitle("Cumulative added cancer risk by scan type and number of scans",
             fontsize=12, weight="bold")
fig.tight_layout(); fig.savefig("fig2_risk_by_scan.png", dpi=150); plt.close(fig)

# Figure 3: age/sex modulation for the two abdomen-pelvis indications
fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharey=True)
panels = [("Abdomen/pelvis CT (single-phase)",
           "Single-phase abdomen/pelvis\n(e.g. renal colic, abdominal pain)"),
          ("Abdomen/pelvis CT (multiphase)",
           "Multiphase abdomen/pelvis\n(overuse variant)")]
for ax, (scan, title) in zip(axes, panels):
    for age in (20, 40, 60):
        for sex, ls in (("F", "-"), ("M", "--")):
            d = df[(df.scan == scan) & (df.age == age) & (df.sex == sex)]
            ax.plot(d.n_scans, d.cum_LAR_pct, color=AGE_COLORS[age], ls=ls, lw=1.8,
                    label=f"age {age} {sex}")
    ax.axhline(1.0, ls=":", color="#888888", lw=1.2)
    ax.text(30, 1.03, "1%", ha="right", va="bottom", color="#666666", fontsize=9)
    ax.set_title(title, fontsize=10.5)
    ax.set_xlabel("Number of CT examinations")
    ax.set_xlim(1, 30); ax.set_ylim(0, None)
    ax.grid(axis="y", alpha=0.25)
axes[0].set_ylabel("Cumulative added cancer risk (%)")
axes[0].legend(fontsize=8, frameon=False, loc="upper left")
fig.suptitle("How age and sex shift the risk of recurrent abdominal CT",
             fontsize=12, weight="bold")
fig.tight_layout(); fig.savefig("fig3_age_sex_abdomen.png", dpi=150); plt.close(fig)

print("Wrote: fig1_cumulative_dose.png, fig2_risk_by_scan.png, fig3_age_sex_abdomen.png")