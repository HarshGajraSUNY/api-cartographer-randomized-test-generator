# path_generator.py
import random
import itertools


def generate_valid_paths(graph, max_depth, num_paths):
    """Generates random valid paths by traversing the dependency graph."""
    paths = []
    start_nodes = [node for node, in_degree in graph.in_degree() if in_degree == 0]

    for _ in range(num_paths):
        if not start_nodes:
            continue

        visited = set()
        path = []
        current_node = random.choice(start_nodes)
        path.append(current_node)
        visited.add(current_node)

        for _ in range(max_depth - 1):
            successors = list(graph.successors(current_node))
            valid_successors = [
                s for s in successors
                if all(pred in visited for pred in graph.predecessors(s))
            ]
            if not valid_successors:
                break
            current_node = random.choice(valid_successors)
            visited.add(current_node)
            path.append(current_node)
        paths.append(path)
    return paths


def generate_invalid_paths(graph, max_depth, num_paths):
    """Generates various types of invalid paths."""
    paths = []
    all_nodes = list(graph.nodes)

    # Type 1: Wrong order
    valid_paths = generate_valid_paths(graph, max_depth, 1)
    if valid_paths and len(valid_paths[0]) > 1:
        for valid_path in valid_paths:
            shuffled_path = valid_path.copy()
            random.shuffle(shuffled_path)
            if shuffled_path != valid_path:  # Ensure it's actually different
                paths.append(shuffled_path)

    # Type 2: Missing dependency
    for _ in range(num_paths//2):
        node_with_deps = [n for n in all_nodes if graph.in_degree(n) > 0]
        if node_with_deps:
            # Start a path with a node that requires an input
            paths.append([random.choice(node_with_deps)])

    # Type 3: Permutations of all nodes (often invalid)
    for _ in range(num_paths - len(paths)):
        path_len = random.randint(2, max_depth)
        paths.append(random.sample(all_nodes, k=min(path_len, len(all_nodes))))

    return paths[:num_paths]