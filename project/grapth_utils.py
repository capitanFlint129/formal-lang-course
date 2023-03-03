import cfpq_data
import networkx as nx


def get_graph_by_name(name: str) -> nx.Graph:
    """
    Loads graph from cfpq_data package by name
    """
    path = cfpq_data.download(name)
    return cfpq_data.graph_from_csv(path)


def get_number_of_nodes(graph: nx.Graph) -> int:
    """
    Returns the number of nodes in the graph
    """
    return graph.number_of_nodes()


def get_number_of_edges(graph: nx.Graph) -> int:
    """
    Returns the number of edges in the graph
    """
    return graph.number_of_edges()


def get_labels(graph: nx.Graph) -> list[str]:
    """
    Returns labels of the graph
    """
    labels = list(set([label for _, _, label in graph.edges(data="label")]))
    return labels


def get_graph_info(graph: nx.Graph) -> dict:
    """
    Returns dict with an info about the given graph
    """
    return {
        "number_of_nodes": get_number_of_nodes(graph),
        "number_of_edges": get_number_of_edges(graph),
        "labels": get_labels(graph),
    }


def create_two_cycles_graph(n: int, m: int, labels: tuple[str, str]) -> nx.MultiDiGraph:
    """
    Returns a graph with two cycles connected by one node. With labeled edges.

    Parameters
    ----------
    n :
        The number of nodes in the first cycle without a common node.

    m :
        The number of nodes in the second cycle without a common node.

    labels:
        Labels that will be used to mark the edges of the graph.

    Returns
    -------
    graph :
        A graph with two cycles connected by one node.
    """
    return cfpq_data.labeled_two_cycles_graph(n, m, labels=labels)


def save_graph_to_dot(graph: nx.Graph, path: str) -> None:
    """
    Saves networkx graph to file in dot format

    Parameters
    ----------
    graph :
      The given graph
    path :
      Path to file where dot representation of graph must be saved

    """
    pydot_graph = nx.nx_pydot.to_pydot(graph)
    pydot_graph.write_raw(path)


def create_two_cycles_graph_and_save(n, m, labels, path):
    graph = create_two_cycles_graph(n, m, labels)
    save_graph_to_dot(graph, path)
