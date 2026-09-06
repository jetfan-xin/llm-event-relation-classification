from pyvis.network import Network
from collections import Counter, defaultdict, deque
import networkx as nx
import json
import numpy as np
from matplotlib import colormaps

# Load dataset (update the file path as needed)
DATA_PATH = "data/generated_relations_final.json"
with open(DATA_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)

def find_related_events(start_events):
    # Create a graph of events and relationships
    graph = defaultdict(list)
    relations = []

    # Build the graph from the dataset
    for relation, examples in data.items():
        for example in examples:
            start_event = example["start"]["label"]
            end_event = example["end"]["label"]
            graph[start_event].append((end_event, relation))
            graph[end_event].append((start_event, relation))  # Bi-directional graph
            relations.append((start_event, end_event, relation))

    # Perform BFS to find all connected events
    visited = set()
    queue = deque(start_events)
    connected_events = set(start_events)
    event_relations = set()

    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        for neighbor, relation in graph[current]:
            if neighbor not in visited:
                connected_events.add(neighbor)
                if (current, neighbor, relation) in relations:
                    event_relations.add((current, neighbor, relation))
                elif (neighbor, current, relation) in relations:
                    event_relations.add((neighbor, current, relation))
                queue.append(neighbor)

    return connected_events, event_relations

def extract_k_core(all_relations, k):
    # Build a networkx graph
    G = nx.DiGraph()
    for start, end, relation in all_relations:
        G.add_edge(start, end, relation=relation)

    # Extract the K-core subgraph
    k_core_subgraph = nx.k_core(G, k=k)

    # Extract nodes and edges from the K-core subgraph
    edges_set = set()
    core_nodes = list(k_core_subgraph.nodes())
    for rel in data.keys():
        for example in data[rel]:
            if example["start"]["label"] in core_nodes and example["end"]["label"] in core_nodes:
                edges_set.add((example["start"]["label"], example["end"]["label"], rel))
    core_edges = [
        (start, end, k_core_subgraph[start][end]["relation"])
        for start, end in k_core_subgraph.edges()
    ]

    if set(core_edges) <= edges_set:
        print(
            "Different: The edges in k_core_subgraph are a subset of the edges associated with the corresponding nodes in the original graph, because there can be multiple relationships between the same pair of start and end nodes.")

    # print(set(core_edges)^edges_set)

    return core_nodes, list(edges_set)

def find_most_common_events(number):
    # Combine start and end event counts
    event_counter = Counter()

    for relation, examples in data.items():
        for example in examples:
            start_event = example["start"]["label"]
            end_event = example["end"]["label"]
            event_counter[start_event] += 1
            event_counter[end_event] += 1

    # Find the top number most common events
    top_events = event_counter.most_common(number)
    return [elem[0] for elem in top_events]

def filter_top_nodes_by_degree(core_nodes, core_edges, percentile=10):
    # Build a graph to calculate degree
    G = nx.MultiDiGraph()

    for start, end, relation in core_edges:
        G.add_edge(start, end, relation=relation)

    # Calculate degrees and identify the top percentile
    node_degrees = dict(G.degree(core_nodes))
    if not node_degrees:
        print("No degrees found. Returning empty lists.")
        return [], G

    degree_threshold = np.percentile(list(node_degrees.values()), percentile)
    # print(degree_threshold)

    # Filter nodes based on the degree threshold
    top_nodes = [node for node, degree in node_degrees.items() if degree >= degree_threshold]

    #print(f"Top nodes based on degree (percentile={percentile}): {top_nodes}")

    return top_nodes, G

def depth_limited_direct_bfs(graph, start_nodes, depth_limit):
    """
    Explore nodes and edges reachable from start_nodes within the depth_limit.
    """
    included_nodes = set(start_nodes)
    included_edges = set()

    undirected_G = graph.to_undirected()
    print("start nodes: ", len(start_nodes))
    print("depth limit: ", depth_limit)
    for start in start_nodes:
        if start not in graph:
            continue

        # Explore neighbors up to depth_limit
        for neighbor, path in nx.single_source_shortest_path(undirected_G, start, cutoff=depth_limit).items():
            for node_on_path in path:
                included_nodes.add(node_on_path)

        for start in included_nodes:
            for end in included_nodes:
                if graph.has_edge(start, end):
                    edge_data = graph.get_edge_data(start, end)
                    for edge_type in edge_data.values():
                        included_edges.add((start, end, edge_type["relation"]))

    return included_nodes, included_edges,

def plot_filtered_network(top_nodes, graph, max_distance, title, data):
    G = nx.MultiDiGraph()

    # Filter top nodes to only include those present in the subgraph
    filtered_top_nodes = [node for node in top_nodes if node in graph]
    if not filtered_top_nodes:
        print("No filtered top nodes found in the largest WCC. Exiting.")
        return

    # Compute the longest shortest path (diameter) in the WCC
    try:
        longest_path_length = nx.diameter(graph.to_undirected())
    except nx.NetworkXError:
        print("Unable to compute diameter (disconnected graph). Exiting.")
        return

    depth_limit = int(max_distance * longest_path_length)

    # Directly explore nodes and edges within depth limit from top_nodes
    included_nodes, included_edges = depth_limited_direct_bfs(graph, filtered_top_nodes, depth_limit)

    for start, end, relation in list(included_edges):
        G.add_edge(start, end, relation=relation)

    print("included_nodes:", len(included_nodes))
    if not included_nodes:
        print("No nodes found within depth limit. Exiting.")
        return

    # Calculate node degrees within the subgraph
    degree_dict = dict(G.degree(included_nodes))

    # Normalize node sizes based on degree (min size 15, max size 50)
    print(degree_dict)
    max_degree = max(degree_dict.values()) if degree_dict else 1
    min_degree = min(degree_dict.values()) if degree_dict else 0
    size_range = 75 - 10  # Node size range (15 to 50)

    node_sizes = {
        node: 10 + ((degree - min_degree) / (max_degree - min_degree)) * size_range
        if max_degree > min_degree else 15
        for node, degree in degree_dict.items()
    }

    # Calculate prediction accuracy for each node
    node_accuracy = {node: {"correct": 0, "total": 0} for node in included_nodes}

    for start, end, relation in included_edges:
        for rel in data.keys():
            for example in data[rel]:
                if example["start"]["label"] == start and example["end"]["label"] == end:
                    predicted_relation = example.get("final_relation", {}).get("Relation", "Unknown")
                    node_accuracy[start]["total"] += 1
                    node_accuracy[end]["total"] += 1
                    if predicted_relation[3:] == rel:
                        node_accuracy[start]["correct"] += 1
                        node_accuracy[end]["correct"] += 1
    # Calculate accuracy and assign color based on accuracy
    cmap = colormaps["cividis"]  # Updated colormap retrieval
    def get_color(accuracy):
        r, g, b, _ = cmap(accuracy)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    node_colors = {
        node: get_color(node_accuracy[node]["correct"] / node_accuracy[node]["total"])
        if node_accuracy[node]["total"] > 0 else "white"  # Default gray for no predictions
        for node in included_nodes
    }

    # Relationship color mapping
    relation_colors = {
        "Causes": "red",
        "HasSubevent": "blue",
        "HasFirstSubevent": "green",
        "HasLastSubevent": "purple",
        "Unknown": "gray"
    }

    # Create pyvis network
    net = Network(height="1500px", width="1500px", directed=True, notebook=False)

    # Add nodes with sizes proportional to their degree
    for node in included_nodes:
        degree = degree_dict.get(node, 0)
        size = node_sizes.get(node, 15)
        color = node_colors.get(node, "#B0B0B0")  # Default gray if no color
        net.add_node(
            node,
            # label=f"{node}\nDegree: {degree}",  # Tooltip includes degree information
            label=f"{node}",  # Tooltip includes degree information
            color=color,
            shape="dot",
            size=size,
            font={"size": 25, "color": "black"}
        )

    # Add edges with color-coded relations and smooth curves
    for start, end, relation in included_edges:
        for rel in data.keys():
            for example in data[rel]:
                if example["start"]["label"] == start and example["end"]["label"] == end:
                    predicted_relation = example.get("final_relation", {}).get("Relation", "/r/Unknown")[3:]
        color = relation_colors.get(predicted_relation, "black")
        print(color)
        # net.add_edge(start, end, label=relation, color=color, smooth={"enabled": True})
        net.add_edge(start, end, color=color, width=2, smooth={"enabled": True})

    # Set global style options for better visualization
    net.set_options('''
    var options = {
      "nodes": {
        "borderWidth": 2,
        "color": {
          "border": "#2B7CE9",
          "background": "#D2E5FF",
          "highlight": {
            "border": "#FFA000",
            "background": "#FFFACD"
          },
          "hover": {
            "border": "#A52A2A",
            "background": "#FFD700"
          }
        },
        "font": {
          "color": "#343434",
          "size": 14,
          "face": "arial"
        }
      },
      "edges": {
        "color": {
          "color": "#848484",
          "highlight": "#FF6347",
          "hover": "#00CED1"
        },
        "smooth": {
          "enabled": true,
          "type": "dynamic"
        }
      },
      "interaction": {
        "tooltipDelay": 200,
        "hover": true
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -20000,
          "springLength": 50,
          "springConstant": 0.5
        },
        "minVelocity": 0.75
      }
    }
    ''')

    # Save and display the network
    net.show(f"{title}.html", notebook=False)


# Step 1: Find the most common event
start_events = find_most_common_events(number=1)
print(start_events)
# Step 2: Find all connected events and relations
all_events, all_relations = find_related_events(start_events)

# Step 3: Extract K-core subgraph (e.g., k=2)
k = 2
core_nodes, core_edges = extract_k_core(all_relations, k)

# Step 4: Filter and get nodes with top 1% degree
top_nodes, core_graph = filter_top_nodes_by_degree(core_nodes, core_edges, percentile=99)
# Step 5: Plot filtered network with 10% depth limit
plot_filtered_network(top_nodes, core_graph, max_distance=0.1, title="Filtered Semantic Network", data=data)
