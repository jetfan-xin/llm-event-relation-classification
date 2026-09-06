import networkx as nx
import matplotlib.pyplot as plt

# Define the list of concept pairs and their relations
concept_pairs = [
    ("unexpected knock", "leads to", "interruption"),
    ("neighbor", "returns", "package"),
    ("package", "delivered to", "neighbor"),
    ("interruption", "causes", "brief chat"),
    ("chat", "about", "weather"),
    ("chat", "leads to", "clock check"),
    ("clock check", "reveals", "running late"),
    ("running late", "causes", "rushing out"),
    ("rushing out", "results in", "forgetting lunch"),
    ("lunch", "left on", "counter"),
    ("forgotten lunch", "leads to", "cafe visit"),
    ("cafe visit", "results in", "discovering new cafe"),
    ("new cafe", "located near", "office"),
    ("cafe visit", "leads to", "meeting old friend"),
    ("old friend", "reconnects with", "Sarah"),
    ("reconnecting", "leads to", "impromptu lunch"),
    ("impromptu lunch", "involves", "catching up"),
    ("catching up", "leads to", "business conversation"),
    ("business conversation", "sparks", "new idea"),
    ("new idea", "could shape", "career"),
    ("unexpected knock", "causes", "change of schedule"),
    ("running late", "affects", "morning routine"),
    ("rushing out", "results in", "unintended discovery"),
    ("forgetting lunch", "causes", "new opportunity"),
    ("business conversation", "inspires", "career shift")
]

G = nx.DiGraph()

for source, relation, target in concept_pairs:
    G.add_edge(source, target, label=relation)

plt.figure(figsize=(12, 10))
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, node_color="skyblue", node_size=1500, font_size=10, font_weight="bold", arrowsize=15)

edge_labels = {(source, target): relation for source, relation, target in concept_pairs}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red", font_size=8)

plt.title("Causal Event Graph of Related Concepts")
plt.show()
