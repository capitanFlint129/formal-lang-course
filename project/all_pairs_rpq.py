from typing import Optional

from pyformlang.regular_expression import Regex
from scipy.sparse import kron
import networkx as nx

from project import automata
from project.boolean_decomposition import *


def finite_automata_intersection(
    fa1: NondeterministicFiniteAutomaton,
    fa2: NondeterministicFiniteAutomaton,
    states_order_fa_1: Optional[dict[State, int]] = None,
    states_order_fa_2: Optional[dict[State, int]] = None,
) -> NondeterministicFiniteAutomaton:
    """
    Builds intersection of two finite automata through the tensor product

    Parameters
    ----------
    fa1, fa2 :
        Input finite automatas
    states_order_fa_1, states_order_fa_2 :
        Dictionaries with indexes of states

    Returns
    ----------
    result_fa:
        Intersection of given finite automatas
    """
    if states_order_fa_1 is None:
        states_order_fa_1 = enumerate_states(fa1)
    if states_order_fa_2 is None:
        states_order_fa_2 = enumerate_states(fa2)
    fa1_boolean_decomposition = get_boolean_decomposition_of_fa(fa1, states_order_fa_1)
    fa2_boolean_decomposition = get_boolean_decomposition_of_fa(fa2, states_order_fa_2)
    result_boolean_decomposition = dict()
    for symbol in fa1.symbols:
        if symbol.value in set([s.value for s in fa2.symbols]):
            result_boolean_decomposition[symbol.value] = dok_matrix(
                kron(
                    fa1_boolean_decomposition[symbol.value],
                    fa2_boolean_decomposition[symbol.value],
                )
            )
    result_fa = get_fa_from_boolean_decomposition(
        result_boolean_decomposition,
        [
            states_order_fa_1[state1] * len(fa2.states) + states_order_fa_2[state2]
            for state1 in fa1.start_states
            for state2 in fa2.start_states
        ],
        [
            states_order_fa_1[state1] * len(fa2.states) + states_order_fa_2[state2]
            for state1 in fa1.final_states
            for state2 in fa2.final_states
        ],
    )
    return result_fa


def regular_query_to_graph(
    query: Regex,
    graph: nx.Graph,
    start_states: Iterable[int],
    final_states: Iterable[int],
) -> list[tuple]:
    """
    Executes regular query to the given graph with given start and end vertices

    Parameters
    ----------
    query :
        Regular expression of query
    graph :
        The graph on which the request is executed
    start_states :
        Graph vertices that interpreted as start
    final_states :
        Graph vertices that interpreted as final

    Returns
    ----------
    result :
        List of pairs from the given start and final states that are connected by a path
        that forms a word from the language specified by the regular expression of query
    """
    query_fa = automata.get_deterministic_automata_from_regex(query)
    graph_fa = automata.get_nondeterministic_automata_from_graph(
        graph, start_states, final_states
    )
    states_order_query_fa = enumerate_states(query_fa)
    states_order_graph_fa = enumerate_states(graph_fa)
    intersection = finite_automata_intersection(
        query_fa, graph_fa, states_order_query_fa, states_order_graph_fa
    )

    intersection_states_order = enumerate_states(intersection)
    intersection_boolean_decomposition = get_boolean_decomposition_of_fa(
        intersection, intersection_states_order
    )
    transitive_closure = get_transitive_closure_of_boolean_decomposition(
        intersection_boolean_decomposition
    )

    result = []
    for start_state in intersection.start_states:
        for final_state in intersection.final_states:
            if transitive_closure[
                intersection_states_order[start_state],
                intersection_states_order[final_state],
            ]:
                result.append(
                    (
                        start_state.value % len(graph_fa.states),
                        final_state.value % len(graph_fa.states),
                    )
                )
    return result


def enumerate_states(fa: NondeterministicFiniteAutomaton) -> dict[State, int]:
    return {state: i for i, state in enumerate(fa.states)}
