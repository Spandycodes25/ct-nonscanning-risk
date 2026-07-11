import os, csv, time
from datetime import date
from Bio import Entrez
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

Entrez.email = "your-email@example.com"
Entrez.api_key = os.environ.get("NCBI_API_KEY")
SEARCH_DATE = date.today().isoformat()

CT = '("computed tomography"[tiab] OR "CT scan"[tiab] OR "CT imaging"[tiab])'
YEARS = list(range(2000, 2026))   # 2026 is partial, excluded

CONCEPTS = {
    "Overuse / low-value / appropriateness":
        f'{CT} AND ("overutilization"[tiab] OR "overuse"[tiab] OR "inappropriate"[tiab] OR "low-value"[tiab] '
        'OR "unnecessary"[tiab] OR "appropriateness"[tiab] OR "Choosing Wisely"[tiab]) '
        'NOT ("overuse injury"[tiab] OR "overuse injuries"[tiab] OR tendinopathy[tiab] OR veterinary[tiab] OR canine[tiab] OR feline[tiab])',
    "Incidental findings / overdiagnosis":
        f'{CT} AND ("incidental finding"[tiab] OR "incidental findings"[tiab] OR "incidentaloma"[tiab] OR "overdiagnosis"[tiab])',
    "Cumulative / recurrent dose":
        f'{CT} AND ("cumulative radiation"[tiab] OR "cumulative dose"[tiab] OR "cumulative effective dose"[tiab] OR "recurrent CT"[tiab] OR "repeated CT"[tiab])',
    "Benefit / yield quantification":
        f'{CT} AND ("diagnostic yield"[tiab] OR "low yield"[tiab] OR "number needed to scan"[tiab] '
        'OR "number needed to image"[tiab] OR "net clinical benefit"[tiab] OR "net benefit"[tiab] '
        'OR "marginal benefit"[tiab] OR "incremental benefit"[tiab]) '
        'NOT (radiomics[tiab] OR "deep learning"[tiab] OR "machine learning"[tiab] OR "neural network"[tiab] '
        'OR "artificial intelligence"[tiab] OR nomogram[tiab] OR "CT-guided"[tiab] OR biopsy[tiab])',
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
    print(f"{y}: " + " | ".join(f"{name.split('/')[0].strip()[:12]}={series[name][-1]}" for name in CONCEPTS))

with open("s23_trends_by_year.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["year"] + list(CONCEPTS.keys()) + ["search_date"])
    for i, y in enumerate(YEARS):
        w.writerow([y] + [series[name][i] for name in CONCEPTS] + [SEARCH_DATE])

styles = {
    "Overuse / low-value / appropriateness": ("#c0392b", "-", "o"),
    "Incidental findings / overdiagnosis":   ("#e67e22", "-", "s"),
    "Cumulative / recurrent dose":           ("#7b241c", "-", "D"),
    "Benefit / yield quantification":        ("#2471a3", "--", "^"),
}
plt.figure(figsize=(11, 6.5))
for name in CONCEPTS:
    c, ls, mk = styles[name]
    plt.plot(YEARS, series[name], color=c, linestyle=ls, marker=mk,
             markersize=4, linewidth=2, label=name)
plt.xlabel("Year of publication")
plt.ylabel("PubMed articles (title/abstract)")
plt.title("Publication trends: CT overuse/harm concepts vs benefit/yield quantification\n"
          f"(PubMed, search date {SEARCH_DATE})", fontsize=12)
plt.legend(frameon=False, fontsize=9)
plt.grid(alpha=0.25)
plt.tight_layout()
plt.savefig("s23_trends_by_year.png", dpi=220, bbox_inches="tight")
plt.savefig("s23_trends_by_year.svg", bbox_inches="tight")
print(f"\nSaved s23_trends_by_year.csv / .png / .svg  (search date {SEARCH_DATE})")
