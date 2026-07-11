# 01_parameters.py
# Inputs for the cumulative-dose / lifetime-attributable-risk (LAR) model.
#
# Primary source (effective dose AND per-scan LAR of all-cancer incidence, by age and sex):
#   Smith-Bindman R, Lipson J, Marcus R, Kim KP, Mahesh M, Gould R, Berrington de Gonzalez A,
#   Miglioretti DL. "Radiation dose associated with common computed tomography examinations and
#   the associated lifetime attributable risk of cancer." Arch Intern Med 2009;169(22):2078-2086.
#     - Effective dose  = Table 2 (median).
#     - Per-scan LAR    = Table 4 (median), expressed as the number of single scans at a given
#                         age/sex expected to cause one cancer ("1 in X"). Smaller X = higher risk.
#   Underlying risk model: National Research Council, BEIR VII Phase 2 (2006).
#
# Notes:
#  - LAR is ALL cancer combined (solid + leukemia). A leukemia-specific layer would require
#    red-bone-marrow dose with the BEIR VII leukemia model and is not included here.
#  - Per-scan LAR assumes normal life expectancy; it overestimates risk for patients with
#    shortened life expectancy (e.g., many high-cumulative-dose oncology patients).
#  - Smith-Bindman found ~13-fold dose variation within a study type across institutions; the
#    Table 4 IQR (not loaded here) captures that as a dose-driven band and can be added later.

# Median effective dose per scan, mSv (Smith-Bindman 2009, Table 2)
SCAN_DOSE_mSv = {
    "Head CT":                          2.1,
    "Chest CT (routine)":               8.2,
    "CTPA (suspected PE)":              9.6,
    "Abdomen/pelvis CT (single-phase)": 16,
    "Abdomen/pelvis CT (multiphase)":   31,
}

# Per-scan LAR of all-cancer incidence (Smith-Bindman 2009, Table 4), as "1 in X".
# F = female, M = male. Age = age at exposure (years). Smaller X = higher risk.
PER_SCAN_LAR_one_in = {
    "Head CT": {
        "F": {20: 4360, 40: 8100,  60: 12250},
        "M": {20: 7350, 40: 11080, 60: 14680},
    },
    "Chest CT (routine)": {
        "F": {20: 390,  40: 720,   60: 1090},
        "M": {20: 1040, 40: 1566,  60: 2080},
    },
    "CTPA (suspected PE)": {
        "F": {20: 330,  40: 620,   60: 930},
        "M": {20: 880,  40: 1333,  60: 1770},
    },
    "Abdomen/pelvis CT (single-phase)": {
        "F": {20: 470,  40: 870,   60: 1320},
        "M": {20: 620,  40: 942,   60: 1250},
    },
    "Abdomen/pelvis CT (multiphase)": {
        "F": {20: 250,  40: 460,   60: 700},
        "M": {20: 330,  40: 498,   60: 660},
    },
}

AGES = (20, 40, 60)
SEXES = ("F", "M")

if __name__ == "__main__":
    print("Median effective dose per scan (Smith-Bindman 2009, Table 2):")
    for k, v in SCAN_DOSE_mSv.items():
        print(f"  {k:<38} {v:>4} mSv")
    print()
    print("Per-scan LAR of all-cancer incidence (Table 4), as 1-in-X (and per 100,000 scanned):")
    for scan, bysex in PER_SCAN_LAR_one_in.items():
        print(f"  {scan}:")
        for sex in SEXES:
            byage = bysex[sex]
            parts = [f"age {a}: 1/{byage[a]} ({100000 / byage[a]:.0f}/100k)" for a in AGES]
            print(f"    {sex}: " + "  |  ".join(parts))