from pyformlang.cfg import CFG, Variable

from project.cfpq import matrix
from project.graph_utils import create_two_cycles_graph


def test_get_reachable_pairs_matrix():
    grammar = CFG.from_text(
        """
        S -> A B
        S -> A S1
        S1 -> S B
        A -> a
        B -> b
        """
    )
    graph = create_two_cycles_graph(2, 1, ["a", "b"])
    result = matrix.get_reachable_pairs(graph, grammar)
    expected = {
        (0, Variable("A"), 1),
        (0, Variable("B"), 3),
        (0, Variable("S"), 0),
        (0, Variable("S"), 3),
        (0, Variable("S1"), 0),
        (0, Variable("S1"), 3),
        (1, Variable("S"), 0),
        (1, Variable("A"), 2),
        (1, Variable("S"), 3),
        (1, Variable("S1"), 0),
        (1, Variable("S1"), 3),
        (2, Variable("A"), 0),
        (2, Variable("S1"), 0),
        (2, Variable("S"), 3),
        (2, Variable("S1"), 3),
        (2, Variable("S"), 0),
        (3, Variable("B"), 0),
    }
    assert result == expected


def test_cf_query_to_graph_matrix():
    grammar = CFG.from_text(
        """
        S -> A B
        S -> A S1
        S1 -> S B
        A -> a
        B -> b
        """
    )
    graph = create_two_cycles_graph(2, 1, ["a", "b"])
    result = matrix.cf_query_to_graph(
        grammar,
        graph,
        Variable("S"),
        [0, 1],
        [2, 3],
    )
    expected = {(0, 3), (1, 3)}
    assert result == expected
