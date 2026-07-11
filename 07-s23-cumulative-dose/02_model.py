import importlib.util
import pathlib
import pandas as pd

# 01_parameters.py starts with a digit, so load it via importlib rather than a plain import.
_spec = importlib.util.spec_from_file_location(
    "params", pathlib.Path(__file__).parent / "01_parameters.py")
params = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(params)
SCAN_DOSE_mSv = params.SCAN_DOSE_mSv
PER_SCAN_LAR_one_in = params.PER_SCAN_LAR_one_in
AGES = params.AGES
SEXES = params.SEXES

# Model (linear no-threshold, LNT):
#   cumulative effective dose = N * per-scan dose
#   cumulative LAR            = N * per-scan LAR     (per-scan LAR = 1 / "1 in X")
# The linear form is the LNT-additive estimate. For N up to a few dozen and per-scan risks this
# small it stays within a fraction of a percent of the independent-trials form 1-(1-p)^N.

N_MAX = 30

rows = []
for scan, dose in SCAN_DOSE_mSv.items():
    for sex in SEXES:
        for age in AGES:
            one_in = PER_SCAN_LAR_one_in[scan][sex][age]
            p = 1.0 / one_in
            for n in range(1, N_MAX + 1):
                rows.append({
                    "scan": scan, "sex": sex, "age": age, "n_scans": n,
                    "cum_dose_mSv": round(n * dose, 1),
                    "cum_LAR": n * p,
                    "cum_LAR_pct": round(n * p * 100, 3),
                    "cum_LAR_one_in": round(one_in / n),
                })

df = pd.DataFrame(rows)
df.to_csv("cumulative_model.csv", index=False)
print(f"Wrote cumulative_model.csv  ({len(df)} rows: "
      f"{len(SCAN_DOSE_mSv)} scans x {len(SEXES)} sexes x {len(AGES)} ages x {N_MAX} counts)")

# Milestone 1: scans to reach 100 mSv cumulative effective dose (age/sex-independent)
print("\nScans to reach 100 mSv cumulative effective dose:")
for scan, dose in SCAN_DOSE_mSv.items():
    print(f"  {scan:<38} {100 / dose:5.1f} scans   ({dose} mSv each)")

# Milestone 2: scans to reach a 1% (1-in-100) cumulative added cancer risk, by age/sex
THRESH = 0.01
print(f"\nScans to reach a {THRESH * 100:.0f}% cumulative added cancer risk (1 in 100):")
print(f"  {'scan':<38} {'20F':>6} {'40F':>6} {'60F':>6} {'20M':>6} {'40M':>6} {'60M':>6}")
for scan in SCAN_DOSE_mSv:
    cells = [THRESH * PER_SCAN_LAR_one_in[scan][s][a] for s in ("F", "M") for a in AGES]
    print(f"  {scan:<38} " + " ".join(f"{v:6.1f}" for v in cells))