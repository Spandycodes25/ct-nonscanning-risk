"""
Task 4 - grounded inputs for the harm-accrual models.
Each parameter is tagged DATA (extracted in Task 2) or LIT (literature constant).
Figures import from this file, so this is the single place inputs live.
"""

# --- Appendicitis ---
APP_PERF_OR_PER_H = 1.02                      # 95% CI 1.00-1.04
APP_PERF_OR_SRC = ("DATA", "PMID 27749630", "odds of perforation per hour, ED triage -> incision")

# --- Ischemic stroke ---
STROKE_REPERF_RD = {3: 25.9, 4: 18.8, 6: 6.7}  # abs. risk diff (%) good outcome (mRS 0-2) vs no reperfusion
STROKE_REPERF_SRC = ("DATA", "PMID 26716735", "adjusted risk difference at 3/4/6 h")
STROKE_NEURONS_PER_MIN = 1.9e6
STROKE_NEURONS_SRC = ("LIT", "Saver, Stroke 2006", "neurons lost per minute, untreated large-vessel")
STROKE_DISAB_cOR_PER_H = 0.84                  # 95% CI 0.76-0.93  (narrative annotation)
STROKE_DISAB_SRC = ("DATA", "PMID 27673305", "disability cOR per 1-h delay to reperfusion")

# --- Mesenteric ischemia ---
MES_COHORT_A = [(24, 72), (30, 87)]            # (hours, mortality %)  <=24h vs >24h surgery
MES_COHORT_A_SRC = ("DATA", "PMID 16796010", "mortality, <=24h vs >24h to surgery")
MES_COHORT_B = [(10, 59), (37, 71)]            # (hours, mortality %)  dx-to-operation interval
MES_COHORT_B_SRC = ("DATA", "PMID 12200729", "mortality by dx-to-operation interval")
MES_DELAY_AOR = {"consult >24h": 9.4, "operation >6h": 3.7}
MES_DELAY_SRC = ("DATA", "PMID 19350855", "adjusted OR for mortality with delay")

# --- Aortic dissection ---
AORTIC_MORT_PER_H = (1.0, 2.0)                 # %/h range, first 48h, untreated type-A
AORTIC_MORT_MID = 1.4                          # midpoint used for the central line
AORTIC_MORT_SRC = ("LIT", "IRAD / Hirsch 2010", "cumulative mortality 1-2% per hour, first 48 h")

# --- Pulmonary embolism (comparative panel only) ---
PE_DELAY_RR = 3.31                             # 95% CI 2.03-5.38
PE_DELAY_SRC = ("DATA", "PMID 41004149", "30-day mortality RR, delay >24h")
PE_EARLY_VS_DELAYED = (1.6, 43.2)              # in-hospital mortality %, early vs delayed dx
PE_EVD_SRC = ("DATA", "PMID 32694258", "in-hospital mortality, early vs delayed dx")


if __name__ == "__main__":
    rows = [
        ("Appendicitis", "perforation OR / hour",      APP_PERF_OR_PER_H,        APP_PERF_OR_SRC),
        ("Stroke",       "good-outcome RD @3/4/6h (%)", STROKE_REPERF_RD,         STROKE_REPERF_SRC),
        ("Stroke",       "neurons lost / min",          f"{STROKE_NEURONS_PER_MIN:.2e}", STROKE_NEURONS_SRC),
        ("Stroke",       "disability cOR / hour",       STROKE_DISAB_cOR_PER_H,   STROKE_DISAB_SRC),
        ("Mesenteric",   "mortality anchors A",         MES_COHORT_A,             MES_COHORT_A_SRC),
        ("Mesenteric",   "mortality anchors B",         MES_COHORT_B,             MES_COHORT_B_SRC),
        ("Mesenteric",   "delay aOR",                   MES_DELAY_AOR,            MES_DELAY_SRC),
        ("Aortic",       "mortality %/hour (range)",    AORTIC_MORT_PER_H,        AORTIC_MORT_SRC),
        ("PE",           "delay mortality RR",          PE_DELAY_RR,              PE_DELAY_SRC),
        ("PE",           "early vs delayed mort (%)",   PE_EARLY_VS_DELAYED,      PE_EVD_SRC),
    ]
    print(f"{'Condition':<13}{'Parameter':<28}{'Value':<24}{'Tag':<6}Source")
    print("-" * 104)
    for cond, name, val, (tag, src, note) in rows:
        print(f"{cond:<13}{name:<28}{str(val):<24}{tag:<6}{src}")
    print("\nDATA = extracted in Task 2 (PMID shown).  LIT = literature constant.")