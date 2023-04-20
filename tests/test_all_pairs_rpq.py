from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State, Symbol
from pyformlang.regular_expression import Regex

from project import all_pairs_rpq, automata, grapth_utils


def test_finite_automata_intersection():
    symbols = {symbol: Symbol(symbol) for symbol in "ab"}

    states1 = [State(0), State(1), State(2)]
    fa1 = NondeterministicFiniteAutomaton()
    fa1.add_start_state(states1[2])
    fa1.add_final_state(states1[2])
    fa1.add_transitions(
        [
            (states1[0], symbols["b"], states1[0]),
            (states1[0], symbols["a"], states1[1]),
            (states1[1], symbols["a"], states1[1]),
            (states1[1], symbols["b"], states1[2]),
            (states1[2], symbols["b"], states1[0]),
            (states1[2], symbols["a"], states1[1]),
        ]
    )

    states2 = [State(0), State(1)]
    fa2 = NondeterministicFiniteAutomaton()
    fa2.add_start_state(states1[0])
    fa2.add_final_state(states1[0])
    fa2.add_transitions(
        [
            (states2[0], symbols["a"], states2[0]),
            (states2[0], symbols["b"], states2[1]),
            (states2[1], symbols["a"], states2[1]),
            (states2[1], symbols["b"], states2[0]),
        ]
    )

    expected = fa1.get_intersection(fa2)
    result = all_pairs_rpq.finite_automata_intersection(fa1, fa2)
    assert expected.is_equivalent_to(result)

    expected = fa1.get_intersection(fa1)
    result = all_pairs_rpq.finite_automata_intersection(fa1, fa1)
    assert expected.is_equivalent_to(result)

    fa2 = NondeterministicFiniteAutomaton()
    expected = fa1.get_intersection(fa2)
    result = all_pairs_rpq.finite_automata_intersection(fa1, fa2)
    assert expected.is_equivalent_to(result)


def test_finite_automata_intersection_regex_and_graph():
    graph = grapth_utils.create_two_cycles_graph(
        3,
        3,
        (
            "a",
            "b",
        ),
    )
    start_states = [0, 1, 2]
    final_states = [4, 5, 6]
    query = Regex("a* b*")
    query_fa = automata.get_deterministic_automata_from_regex(query)
    graph_fa = automata.get_nondeterministic_automata_from_graph(
        graph, start_states, final_states
    )

    result = all_pairs_rpq.finite_automata_intersection(query_fa, graph_fa)

    expected = query_fa.get_intersection(graph_fa)
    assert result.is_equivalent_to(expected)


def test_regular_query_to_graph():
    graph = grapth_utils.create_two_cycles_graph(
        3,
        3,
        (
            "a",
            "b",
        ),
    )
    start_states = [0, 1, 2]
    final_states = [4, 5, 6]
    query = Regex("a* b*")

    result = all_pairs_rpq.regular_query_to_graph(
        query, graph, start_states, final_states
    )
    expected = [
        (start_state, final_state)
        for start_state in start_states
        for final_state in final_states
    ]
    assert set(result) == set(expected)

    query = Regex("a*")
    result = all_pairs_rpq.regular_query_to_graph(
        query, graph, start_states, final_states
    )
    expected = []
    assert result == expected

    query = Regex("b*")
    result = all_pairs_rpq.regular_query_to_graph(
        query, graph, start_states, final_states
    )
    expected = [(0, 4), (0, 5), (0, 6)]
    assert result == expected

    query = Regex("a a b")
    result = all_pairs_rpq.regular_query_to_graph(
        query, graph, start_states, final_states
    )
    expected = [(2, 4)]
    assert result == expected
