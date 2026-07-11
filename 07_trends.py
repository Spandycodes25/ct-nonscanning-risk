import os, csv, time
from datetime import date
from Bio import Entrez
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

Entrez.email = "your-email@example.com"
Entrez.api_key = os.environ.get("NCBI_API_KEY")
SEARCH_DATE = date.today().isoformat()

YEARS = list(range(2000, 2026))   # 2026 is partial, excluded

CONCEPTS = {
    "Radiation risk (named)":
        '("computed tomography"[tiab] OR "CT scan"[tiab]) AND ("radiation risk"[tiab] '
        'OR "radiation-induced cancer"[tiab] OR "radiation induced cancer"[tiab] '
        'OR "lifetime attributable risk"[tiab] OR "carcinogenic risk"[tiab])',
    "Delay-to-scan (time-to-CT)":
        '("time to CT"[tiab] OR "time-to-CT"[tiab] OR "door-to-CT"[tiab] '
        'OR "door to CT"[tiab] OR "time to computed tomography"[tiab] '
        'OR "delayed CT scan"[tiab] OR "delay in CT"[tiab]) '
        'NOT ("delayed phase"[tiab] OR "delayed-phase"[tiab] OR "delayed enhancement"[tiab] '
        'OR "delayed contrast"[tiab] OR "time-resolved"[tiab])',
    "Risk of NOT scanning (named concept)":
        '("computed tomography"[tiab] OR "CT scan"[tiab]) AND ("risk of not scanning"[tiab] '
        'OR "not scanning"[tiab] OR "non-scanning"[tiab] OR "withholding CT"[tiab] '
        'OR "withholding imaging"[tiab] OR "deferred CT"[tiab] OR "forgoing CT"[tiab] '
        'OR "forgoing imaging"[tiab]) NOT (spectrometer[tiab] OR spectral[tiab] '
        'OR fluorescence[tiab] OR microscopy[tiab] OR multiplexing[tiab])',
}

def count(q):
    h = Entrez.esearch(db="pubmed", term=q, retmax=0)
    r = Entrez.read(h); h.close()
    return int(r["Count"])

series = {name: [] for name in CONCEPTS}
for y in YEARS:
    for name, base in CONCEPTS.items():
        n = count(f'({base}) AND ("{y}"[dp])')
        series[name].append(n)
        time.sleep(0.2)
    print(f"{y}: " + " | ".join(f"{name.split('(')[0].strip()}={series[name][-1]}"
                                for name in CONCEPTS))

with open("trends_by_year.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["year"] + list(CONCEPTS.keys()) + ["search_date"])
    for i, y in enumerate(YEARS):
        w.writerow([y] + [series[name][i] for name in CONCEPTS] + [SEARCH_DATE])

styles = {
    "Radiation risk (named)": ("#c0392b", "-", "o"),
    "Delay-to-scan (time-to-CT)": ("#2471a3", "-", "s"),
    "Risk of NOT scanning (named concept)": ("#b9770e", "--", "^"),
}
plt.figure(figsize=(11, 6.5))
for name in CONCEPTS:
    c, ls, mk = styles[name]
    plt.plot(YEARS, series[name], color=c, linestyle=ls, marker=mk,
             markersize=4, linewidth=2, label=name)
plt.xlabel("Year of publication")
plt.ylabel("PubMed articles (title/abstract)")
plt.title("Publication trends: CT radiation risk vs. the risk of not scanning\n"
          f"(PubMed, search date {SEARCH_DATE})", fontsize=12)
plt.legend(frameon=False, fontsize=9)
plt.grid(alpha=0.25)
plt.tight_layout()
plt.savefig("trends_by_year.png", dpi=220, bbox_inches="tight")
plt.savefig("trends_by_year.svg", bbox_inches="tight")
print(f"\nSaved trends_by_year.csv / .png / .svg  (search date {SEARCH_DATE})")
