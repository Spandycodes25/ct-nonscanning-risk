# Quantifying the risk of not performing CT

Analysis code, derived data, and prototype tools for the paper *The risk of not performing or delaying a CT scan, quantified* (Surdas and Rehani).

The paper looks at how unevenly the two sides of the CT justification question are represented in the literature. The radiation risk of scanning is quantified in a large body of work, while the risk of not scanning is barely counted at all. It then extracts source-traceable estimates of the harm of delay and of diagnostic yield across seven acute conditions and eight lower-yield indications, places each on a benefit-to-harm spectrum, and reports how much usable evidence exists to place it.

This repository reproduces the numbers, tables, and figures in the paper starting from PubMed identifiers. It does not include any article text (see Data).

## Repository layout

The work runs across several numbered folders. The bibliometric folders count the literature, the extraction folders pull estimates from abstracts, the dose folder builds the risk model, and the rest hold the figures and the prototype tools.

Analysis:

- `01-bibliometric/` : the asymmetry analysis. Concept counts in PubMed by year (`01_counts.py`, `02_spotcheck.py`, `03_counts_final.py`), MeSH counts and the co-occurrence network (`04_fetch_mesh.py`, `05_mesh_network.py`, `06_mesh_network_v2.py`), and trends and citation context (`07_trends.py`, `08_citations.py`). `test_query.py` is a query sanity check.
- `05-s23-landscape/` : the lower-yield landscape for Scenarios 2 and 3. Counts and refined concept volumes (`01_counts.py`, `02_spotcheck.py`, `03_counts_refined.py`, `06_concept_volumes.py`), MeSH and network (`04_fetch_mesh.py`, `05_network.py`), trends (`07_trends.py`), and the landscape figure (`08_landscape_figure.py`).
- `02-extraction/` : Scenario 1 (acute conditions) extraction. Corpus build and model runs (`01_build_corpus.py`, `02_extract_test.py`, `03_extract_sample.py`, `04_extract_all.py`, `05_topup_corpus.py`), then quote-grounding validation and aggregation (`06_validate.py`, `07_aggregate.py`). `extractor.py` holds the schema, prompt, and model call.
- `06-s23-extraction/` : Scenarios 2 and 3 (lower-yield) extraction. Same shape: corpus build and runs (`01_build_corpus.py` through `04_topup_corpus.py`), then curation (`05_curate.py`).
- `07-s23-cumulative-dose/` : the radiation-risk model and benefit-to-harm ratio (`01_parameters.py`, `02_model.py`, `03_figures.py`).
- `04-temporal/` : the time-criticality figures for the acute conditions (`fig1_appendicitis_stroke.py`, `fig2_mesenteric_aortic.py`, `fig3_time_criticality.py`, `params.py`).

Prototype decision-support tools (React components described in the paper):

- `03-dashboard/Comparative_Risk_Dashboard.jsx` : the Scenario-1 comparative-risk tool
- `08-s23-full-spectrum-ct-dashboard/Full_Spectrum_CT_Dashboard.jsx` : the full-spectrum tool
- `06-Patient_and_Clinician_Facing/Understanding_Your_Scan.jsx` and `09-scan_needed_or_not_dashboard/Do_We_Need_This_Scan.jsx` : the audience-separated shared-decision tool, patient and clinician views
- `10-evidence-density-map/Evidence_Confidence_Checker.jsx` : the evidence-confidence checker

## Requirements

- Python 3.11 or later, with the packages in `requirements.txt` (Biopython, pandas, numpy, matplotlib, requests, pytrends)
- Ollama with the qwen2.5 7B model, used only for the extraction steps:

  ```
  ollama pull qwen2.5
  ```

  Ollama has to be running before any extraction script. On CPU the extraction is slow but works; a GPU is faster and not required.
- Node.js with a React toolchain (for example Vite) to run the `.jsx` tools

## Setup

NCBI asks for a contact email on every E-utilities request. Keep yours out of the code and set it in the environment instead:

```
export ENTREZ_EMAIL="you@example.com"
pip install -r requirements.txt
```

## Running

Run the folders in this order, and the scripts inside each folder in their numeric order:

1. `01-bibliometric/` : the asymmetry counts, MeSH, and citation context.
2. `05-s23-landscape/` : the lower-yield landscape.
3. `02-extraction/` : acute-condition extraction (Ollama running).
4. `06-s23-extraction/` : lower-yield extraction (Ollama running).
5. `07-s23-cumulative-dose/` : the risk model and the benefit-to-harm ratio.
6. `04-temporal/` : the time-criticality figure; the figure scripts inside the bibliometric, landscape, and dose folders produce the others.

Each stage writes its counts and extracted estimates as CSVs. The extraction runs entirely on your machine; no abstract text leaves the workstation.

## Prototype tools

The components under `03-`, `06-`, `08-`, `09-`, and `10-` are standalone React files. To view one, drop it into a React project (for example a Vite app) and import it, or open it in any React sandbox. They compute in the browser and need no server. Figure 3 in the paper is a screenshot of the comparative-risk tool.

## Data

The two corpora were each searched once: the acute set on 3 June 2026 and the lower-yield set on 10 June 2026. PubMed changes daily, so rerunning the searches will not reproduce the exact counts; the frozen identifier lists will.

Abstracts belong to their publishers and are not redistributed here. Each estimate is given as its PMID, the value extracted from it, and the short verbatim quotation that supports the value. That is enough to trace and check every figure without copying the source text.

## Citing

Please cite both the paper and this archive:

- Surdas S, Rehani MM. The risk of not performing or delaying a CT scan, quantified. Br J Radiol. 2026.
- Surdas S, Rehani MM. Analysis code and data for 'The risk of not performing or delaying a CT scan, quantified' [data set]. Zenodo; 2026. doi:10.5281/zenodo.21315038.

## License

The code is released under the MIT License (see `LICENSE`). The derived data is released under Creative Commons Attribution 4.0 (CC BY 4.0).
