import json, math, random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from collections import Counter, defaultdict
from itertools import combinations
from matplotlib.lines import Line2D

TOPK = 28
MIN_EDGE = 4
A_COLOR = "#c0392b"
B_COLOR = "#2471a3"
SHARED_COLOR = "#7f8c8d"
RING = "#b9770e"   # gold ring for non-scanning concept terms
CONCEPT = {"Delayed Diagnosis", "Missed Diagnosis", "Diagnostic Errors", "Early Diagnosis"}

with open("mesh_corpus.json") as f:
    blob = json.load(f)
data, search_date = blob["data"], blob["search_date"]

edge_w = Counter()
node_side = defaultdict(lambda: {"A": 0, "B": 0})
for side_key, recs in data.items():
    s = "A" if side_key.startswith("A") else "B"
    for r in recs:
        terms = sorted(set(r["mesh"]))
        for t in terms:
            node_side[t][s] += 1
        for u, v in combinations(terms, 2):
            edge_w[(u, v)] += 1

by_A = sorted(node_side, key=lambda t: node_side[t]["A"], reverse=True)[:TOPK]
by_B = sorted(node_side, key=lambda t: node_side[t]["B"], reverse=True)[:TOPK]
nodes = set(by_A) | set(by_B)

def color_for(t):
    a, b = node_side[t]["A"], node_side[t]["B"]
    tot = a + b
    f = a / tot if tot else 0
    return A_COLOR if f >= 0.65 else B_COLOR if f <= 0.35 else SHARED_COLOR

G = nx.Graph()
for t in nodes:
    G.add_node(t, size=node_side[t]["A"] + node_side[t]["B"], color=color_for(t))
for (u, v), w in edge_w.items():
    if u in nodes and v in nodes and w >= MIN_EDGE:
        G.add_edge(u, v, weight=w)
G.remove_nodes_from(list(nx.isolates(G)))

A_nodes = [n for n in G if G.nodes[n]["color"] == A_COLOR]
B_nodes = [n for n in G if G.nodes[n]["color"] == B_COLOR]
GA, GB = G.subgraph(A_nodes), G.subgraph(B_nodes)
print(f"Drawn: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
print(f"Side A: {GA.number_of_nodes()} nodes | density {nx.density(GA):.3f} | "
      f"{nx.number_connected_components(GA)} component(s)")
print(f"Side B: {GB.number_of_nodes()} nodes | density {nx.density(GB):.3f} | "
      f"{nx.number_connected_components(GB)} component(s)")
print("\nSide B fragments:")
for i, comp in enumerate(sorted(nx.connected_components(GB), key=len, reverse=True), 1):
    print(f"  [{i}] " + ", ".join(sorted(comp)))

random.seed(42)
init = {}
for n in G:
    c = G.nodes[n]["color"]
    x = -1.0 if c == A_COLOR else 1.0 if c == B_COLOR else 0.0
    init[n] = (x + random.uniform(-0.25, 0.25), random.uniform(-1, 1))
bridge = "Tomography, X-Ray Computed"
fixed = None
if bridge in G:
    init[bridge] = (0.0, 0.0)
    fixed = [bridge]
pos = nx.spring_layout(G, pos=init, fixed=fixed, k=1.5, seed=42,
                       weight="weight", iterations=300)

fig, ax = plt.subplots(figsize=(17, 12))
sizes = {n: 40 + math.sqrt(G.nodes[n]["size"]) * 60 for n in G}
widths = [0.2 + 0.11 * G[u][v]["weight"] for u, v in G.edges()]
nx.draw_networkx_edges(G, pos, width=widths, edge_color="#dce0e2", alpha=0.7, ax=ax)
nx.draw_networkx_nodes(G, pos, node_size=[sizes[n] for n in G],
                       node_color=[G.nodes[n]["color"] for n in G],
                       alpha=0.93, linewidths=0.6, edgecolors="white", ax=ax)
for n in G:
    if n in CONCEPT:
        x, y = pos[n]
        ax.scatter([x], [y], s=sizes[n] + 300, facecolors="none",
                   edgecolors=RING, linewidths=2.4, zorder=5)
label_pos = {n: (x, y + 0.045) for n, (x, y) in pos.items()}
nx.draw_networkx_labels(G, label_pos, font_size=6.5, font_color="#1b2631", ax=ax)

legend = [
    Line2D([0],[0], marker="o", color="w", markerfacecolor=A_COLOR, markersize=11, label="Radiation-risk literature (1 connected cluster)"),
    Line2D([0],[0], marker="o", color="w", markerfacecolor=B_COLOR, markersize=11, label="Non-scanning-adjacent literature (fragmented)"),
    Line2D([0],[0], marker="o", color="w", markerfacecolor=SHARED_COLOR, markersize=11, label="Shared modality / setting terms"),
    Line2D([0],[0], marker="o", color="w", markerfacecolor="none", markeredgecolor=RING, markeredgewidth=2.2, markersize=12, label="'Risk of not scanning' concept terms"),
]
ax.legend(handles=legend, loc="upper left", fontsize=11, frameon=False)
ax.set_title("MeSH co-occurrence: CT radiation risk vs. the risk of not scanning\n"
             f"(PubMed, search date {search_date}; node size = article frequency)", fontsize=13)
ax.axis("off")
plt.tight_layout()
plt.savefig("mesh_network_v2.png", dpi=220, bbox_inches="tight")
plt.savefig("mesh_network_v2.svg", bbox_inches="tight")
print("\nSaved mesh_network_v2.png and mesh_network_v2.svg")