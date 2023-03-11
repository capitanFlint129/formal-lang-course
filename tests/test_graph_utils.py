import networkx as nx

from project import grapth_utils


def test_get_graph_info():
    graph = grapth_utils.get_graph_by_name("gzip")
    assert grapth_utils.get_number_of_nodes(graph) == 2687
    assert grapth_utils.get_number_of_edges(graph) == 2293
    assert set(grapth_utils.get_labels(graph)) == {"a", "d"}


def test_two_cycle_graph():
    graph = grapth_utils.create_two_cycles_graph(
        9,
        4,
        (
            "a",
            "b",
        ),
    )
    assert graph.number_of_nodes() == 14
    assert graph.number_of_edges() == 15
    assert set(grapth_utils.get_labels(graph)) == {"a", "b"}

    filename = "two_cycles_graph.dot"
    grapth_utils.save_graph_to_dot(graph, filename)
    graph_from_file = nx.drawing.nx_pydot.read_dot(filename)
    nx.utils.graphs_equal(graph, graph_from_file)
