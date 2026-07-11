import json
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter
from itertools import combinations

with open("s23_mesh_corpus.json") as f:
    blob = json.load(f)
DATE = blob["search_date"]
A = blob["data"]["A_overuse_harm"]
B = blob["data"]["B_benefit_yield"]
nA, nB = len(A), len(B)

# organizing overuse/harm concepts to highlight (gold rings)
ANCHORS = {"Incidental Findings", "Unnecessary Procedures", "Medical Overuse",
           "Radiation Dosage", "Early Detection of Cancer", "Health Services Misuse"}

freqA = Counter(t for r in A for t in set(r["mesh"]))
freqB = Counter(t for r in B for t in set(r["mesh"]))
combined = Counter()
for t in set(freqA) | set(freqB):
    combined[t] = freqA[t] + freqB[t]

TOPN = 30
top_terms = [t for t, _ in combined.most_common(TOPN)]
tset = set(top_terms)

def side_of(t):
    if t in ANCHORS: return "anchor"
    fa, fb = freqA[t] / nA, freqB[t] / nB
    if fa >= 1.5 * fb: return "A"
    if fb >= 1.5 * fa: return "B"
    return "shared"

co = Counter()
for r in (A + B):
    present = sorted(t for t in set(r["mesh"]) if t in tset)
    for a, b in combinations(present, 2):
        co[(a, b)] += 1

MIN_EDGE = 25   # tune for legibility
G = nx.Graph()
for t in top_terms:
    G.add_node(t, side=side_of(t), size=combined[t])
for (a, b), w in co.items():
    if w >= MIN_EDGE:
        G.add_edge(a, b, weight=w)

print(f"nodes={G.number_of_nodes()} edges={G.number_of_edges()} "
      f"components={nx.number_connected_components(G)} density={nx.density(G):.3f} (MIN_EDGE={MIN_EDGE})")
print("Anchors present :", sorted(t for t in top_terms if t in ANCHORS))
print("A-distinctive   :", sorted(t for t in top_terms if side_of(t) == "A"))
print("B-distinctive   :", sorted(t for t in top_terms if side_of(t) == "B"))
print("Isolated nodes  :", [t for t in G.nodes if G.degree(t) == 0])

COL = {"A": "#c0392b", "B": "#2471a3", "shared": "#9aa0a6", "anchor": "#b9770e"}
size = {t: 150 + 9 * combined[t] ** 0.5 for t in G.nodes}
pos = nx.spring_layout(G, k=0.8, seed=42, weight="weight")

plt.figure(figsize=(15, 11))
nx.draw_networkx_edges(G, pos, width=[0.3 + 0.02 * G[u][v]["weight"] for u, v in G.edges],
                       alpha=0.22, edge_color="#888")
nx.draw_networkx_nodes(G, pos, nodelist=list(G.nodes),
                       node_color=[COL[G.nodes[t]["side"]] for t in G.nodes],
                       node_size=[size[t] for t in G.nodes],
                       edgecolors="white", linewidths=1.0)
anchors = [t for t in G.nodes if G.nodes[t]["side"] == "anchor"]
nx.draw_networkx_nodes(G, pos, nodelist=anchors, node_color="none",
                       node_size=[size[t] + 320 for t in anchors],
                       edgecolors="#b9770e", linewidths=2.6)
nx.draw_networkx_labels(G, pos, font_size=8)
plt.axis("off")
plt.title("MeSH co-occurrence — CT overuse/harm (red) vs benefit/yield (blue)\n"
          f"organizing overuse concepts ringed gold; gray = shared modality/setting (PubMed, {DATE})",
          fontsize=12)
plt.tight_layout()
plt.savefig("s23_mesh_network.png", dpi=220, bbox_inches="tight")
plt.savefig("s23_mesh_network.svg", bbox_inches="tight")
print("Saved s23_mesh_network.png / .svg")