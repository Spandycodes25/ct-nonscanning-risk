import json, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from collections import Counter, defaultdict
from itertools import combinations
from matplotlib.lines import Line2D

TOPK = 28          # top MeSH terms per side to include
MIN_EDGE = 4       # minimum co-occurrence to draw an edge
A_COLOR = "#c0392b"       # radiation-risk literature (red)
B_COLOR = "#2471a3"       # non-scanning-adjacent literature (blue)
SHARED_COLOR = "#7f8c8d"  # substantial on both sides (gray)

with open("mesh_corpus.json") as f:
    blob = json.load(f)
data = blob["data"]
search_date = blob["search_date"]

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
    total = a + b
    frac_a = a / total if total else 0
    if frac_a >= 0.65: return A_COLOR
    if frac_a <= 0.35: return B_COLOR
    return SHARED_COLOR

G = nx.Graph()
for t in nodes:
    G.add_node(t, size=node_side[t]["A"] + node_side[t]["B"], color=color_for(t))
for (u, v), w in edge_w.items():
    if u in nodes and v in nodes and w >= MIN_EDGE:
        G.add_edge(u, v, weight=w)
G.remove_nodes_from(list(nx.isolates(G)))

# quantitative companion stats
A_nodes = [n for n in G if G.nodes[n]["color"] == A_COLOR]
B_nodes = [n for n in G if G.nodes[n]["color"] == B_COLOR]
GA, GB = G.subgraph(A_nodes), G.subgraph(B_nodes)
print(f"Drawn: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
print(f"Side A subgraph: {GA.number_of_nodes()} nodes | density {nx.density(GA):.3f} "
      f"| {nx.number_connected_components(GA)} components")
print(f"Side B subgraph: {GB.number_of_nodes()} nodes | density {nx.density(GB):.3f} "
      f"| {nx.number_connected_components(GB)} components")

# draw
pos = nx.spring_layout(G, k=0.9, seed=42, weight="weight", iterations=200)
fig, ax = plt.subplots(figsize=(15, 11))
sizes = [40 + math.sqrt(G.nodes[n]["size"]) * 60 for n in G]
colors = [G.nodes[n]["color"] for n in G]
widths = [0.2 + 0.12 * G[u][v]["weight"] for u, v in G.edges()]
nx.draw_networkx_edges(G, pos, width=widths, edge_color="#d5d8dc", alpha=0.7, ax=ax)
nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color=colors,
                       alpha=0.92, linewidths=0.6, edgecolors="white", ax=ax)
nx.draw_networkx_labels(G, pos, font_size=7.5, font_color="#1b2631", ax=ax)

legend = [Line2D([0],[0], marker="o", color="w", markerfacecolor=A_COLOR, markersize=11, label="Radiation-risk literature"),
          Line2D([0],[0], marker="o", color="w", markerfacecolor=B_COLOR, markersize=11, label="Non-scanning-adjacent literature"),
          Line2D([0],[0], marker="o", color="w", markerfacecolor=SHARED_COLOR, markersize=11, label="Shared (both)")]
ax.legend(handles=legend, loc="upper left", fontsize=11, frameon=False)
ax.set_title("MeSH co-occurrence: CT radiation risk vs. the risk of not scanning\n"
             f"(PubMed, search date {search_date}; node size = article frequency)", fontsize=13)
ax.axis("off")
plt.tight_layout()
plt.savefig("mesh_network.png", dpi=200, bbox_inches="tight")
plt.savefig("mesh_network.svg", bbox_inches="tight")
print("\nSaved mesh_network.png and mesh_network.svg")