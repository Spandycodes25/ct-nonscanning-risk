import os, time, json, statistics, urllib.request
from datetime import date
from Bio import Entrez

Entrez.email = "your-email@example.com"
Entrez.api_key = os.environ.get("NCBI_API_KEY")
SEARCH_DATE = date.today().isoformat()

SIDES = {
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
}

def get_pmids(query, retmax=1000):
    h = Entrez.esearch(db="pubmed", term=query, retmax=retmax)
    ids = Entrez.read(h)["IdList"]; h.close()
    return ids

def get_icite(id_list, batch=200):
    out = []
    for i in range(0, len(id_list), batch):
        chunk = id_list[i:i + batch]
        url = "https://icite.od.nih.gov/api/pubs?pmids=" + ",".join(chunk)
        for attempt in range(3):
            try:
                with urllib.request.urlopen(url, timeout=60) as resp:
                    payload = json.load(resp)
                out.extend(payload.get("data", []))
                break
            except Exception as e:
                if attempt == 2:
                    print(f"  (batch starting {i} failed: {e})")
                else:
                    time.sleep(2)
        time.sleep(0.5)
    return out

results = {}
for name, q in SIDES.items():
    ids = get_pmids(q)
    time.sleep(0.3)
    print(f"{name}: {len(ids)} PMIDs -> querying iCite...")
    results[name] = get_icite(ids)

def parts(recs):
    c = [r.get("citation_count") for r in recs if r.get("citation_count") is not None]
    r_ = [r.get("relative_citation_ratio") for r in recs if r.get("relative_citation_ratio") is not None]
    p = [r.get("citations_per_year") for r in recs if r.get("citations_per_year") is not None]
    return c, r_, p

names = list(SIDES.keys())
print(f"\n{'metric':<26} | {names[0]:>22} | {names[1]:>22}")
print("-" * 78)

def row(label, fn):
    vals = []
    for n in names:
        c, r_, p = parts(results[n])
        vals.append(fn(c, r_, p))
    print(f"{label:<26} | {str(vals[0]):>22} | {str(vals[1]):>22}")

row("articles w/ iCite data", lambda c, r, p: len(c))
row("total citations",        lambda c, r, p: sum(c))
row("median citations",       lambda c, r, p: round(statistics.median(c), 1) if c else 0)
row("mean citations",         lambda c, r, p: round(statistics.mean(c), 1) if c else 0)
row("median citations/year",  lambda c, r, p: round(statistics.median(p), 2) if p else 0)
row("median RCR (norm.)",     lambda c, r, p: round(statistics.median(r), 2) if r else 0)
row("% uncited",              lambda c, r, p: f"{round(100*sum(x==0 for x in c)/len(c),1)}%" if c else "-")

with open("citation_metrics.json", "w") as f:
    json.dump({"search_date": SEARCH_DATE,
               "sides": {n: [{"pmid": r.get("pmid"), "year": r.get("year"),
                              "citation_count": r.get("citation_count"),
                              "rcr": r.get("relative_citation_ratio"),
                              "citations_per_year": r.get("citations_per_year")}
                             for r in results[n]] for n in names}}, f, indent=2)
print(f"\nSaved citation_metrics.json  (search date {SEARCH_DATE})")
