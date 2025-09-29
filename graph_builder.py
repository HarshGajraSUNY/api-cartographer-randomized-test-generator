# graph_builder.py
import yaml
import networkx as nx
from matplotlib import pyplot as plt


def build_dependency_graph(config_path='api_config.yaml'):
    """Builds a directed graph from the API configuration file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    graph = nx.DiGraph()
    provides_map = {}

    # Add nodes and build a map of what each node provides
    for name, details in config.items():
        graph.add_node(name, **details)
        if details.get('provides'):
            provides_map[details['provides']] = name

    # Add edges based on requirements
    for name, details in config.items():
        for required_var in details.get('requires', []):
            if required_var in provides_map:
                source_node = provides_map[required_var]
                graph.add_edge(source_node, name)

    return graph, config


if __name__ == '__main__':
    graph, config = build_dependency_graph()
    nx.draw(graph, with_labels=True)
    plt.show()  # see the graph
