from pyformlang.cfg import CFG, Variable

from project.grapth_utils import create_two_cycles_graph
from project.hellings_algorithm import get_reachable_pairs_hellings, cf_query_to_graph


def test_get_reachable_pairs_hellings():
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
    result = get_reachable_pairs_hellings(graph, grammar)
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


def test_cf_query_to_graph():
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
    result = cf_query_to_graph(
        grammar,
        graph,
        Variable("S"),
        [0, 1],
        [2, 3],
    )
    expected = {(0, 3), (1, 3)}
    assert result == expected
