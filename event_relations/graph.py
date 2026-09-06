"""Graph analysis preserving concept IDs and parallel relation edges."""

from collections import Counter, deque
from .evaluation import INVALID, normalize, prediction, records


def build_graph(data, labels="reference", k=2, seed=None, hops=2):
    if labels not in ("reference", "selected"):
        raise ValueError("labels must be reference or selected")
    if type(k) is not int or k < 0 or type(hops) is not int or hops < 0:
        raise ValueError("k and hops must be nonnegative integers")
    nodes, edges = {}, set()
    invalid, self_loops = 0, 0
    for gold, row in records(data):
        rel = gold if labels == "reference" else prediction(row, "selected")
        if rel == INVALID:
            invalid += 1
            continue
        a, b = row["start"]["@id"], row["end"]["@id"]
        if a == b:
            self_loops += 1
            continue
        nodes[a], nodes[b] = row["start"]["label"], row["end"]["label"]
        edges.add((a, b, rel))
    # Define k-core on an undirected simple projection, restoring all labelled
    # directed edges afterwards. Parallel labels do not inflate core degree.
    neighbors = {n: set() for n in nodes}
    for a, b, _ in edges:
        neighbors[a].add(b)
        neighbors[b].add(a)
    active = set(nodes)
    queue = deque(n for n in nodes if len(neighbors[n]) < k)
    while queue:
        n = queue.popleft()
        if n not in active:
            continue
        active.remove(n)
        for other in neighbors[n]:
            neighbors[other].discard(n)
            if other in active and len(neighbors[other]) < k:
                queue.append(other)
    if seed is not None and seed not in active:
        raise ValueError("Selected seed is not in the k-core")
    if not active:
        included, seed = set(), None
    else:
        seed = seed or min(active, key=lambda n: (-len(neighbors[n]), n))
        included, frontier = {seed}, {seed}
        for _ in range(hops):
            frontier = {b for a in frontier for b in neighbors[a] if b in active} - included
            included |= frontier
    chosen = sorted((a, b, r) for a, b, r in edges if a in included and b in included)
    degree = Counter(x for a, b, _ in chosen for x in (a, b))
    return dict(label_source=labels, k=k, hops=hops, seed=seed,
                core_nodes=len(active), invalid_predictions_excluded=invalid,
                self_loops_excluded=self_loops,
                nodes=[dict(id=n, label=nodes[n], degree=degree[n]) for n in sorted(included)],
                edges=[dict(source=a, target=b, relation=r) for a, b, r in chosen])


def render_html(graph):
    """Optional Pyvis export. Escape data-derived labels and tooltip text."""
    from html import escape
    from pyvis.network import Network
    net = Network(height="800px", width="100%", directed=True, cdn_resources="in_line")
    colors = {"Causes": "#b91c1c", "HasSubevent": "#2563eb", "HasFirstSubevent": "#15803d", "HasLastSubevent": "#7e22ce"}
    for node in graph["nodes"]:
        net.add_node(escape(node["id"]), label=escape(node["label"]), title=escape(node["id"]), value=node["degree"])
    for edge in graph["edges"]:
        net.add_edge(escape(edge["source"]), escape(edge["target"]), label=edge["relation"], color=colors[edge["relation"]])
    return net.generate_html()
