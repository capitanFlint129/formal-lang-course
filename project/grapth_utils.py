import cfpq_data
import networkx as nx


def get_graph_by_name(name):
    path = cfpq_data.download(name)
    return cfpq_data.graph_from_csv(path)


def get_number_of_nodes(graph):
    return graph.number_of_nodes()


def get_number_of_edges(graph):
    return graph.number_of_edges()


def get_labels(graph):
    labels = list(set([label for _, _, label in graph.edges(data="label")]))
    return labels


def create_two_cycles_graph(n, m, labels):
    return cfpq_data.labeled_two_cycles_graph(n, m, labels=labels)


def save_graph_to_dot(graph, path):
    pydot_graph = nx.nx_pydot.to_pydot(graph)
    pydot_graph.write_raw(path)
