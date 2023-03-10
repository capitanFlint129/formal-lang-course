from collections import defaultdict
from typing import Iterable, Optional
import math

from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, Symbol, State
from pyformlang.regular_expression import Regex
from scipy.sparse import dok_matrix, csr_matrix, kron
import networkx as nx

from project import automata


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


def get_boolean_decomposition_of_fa(
    fa: NondeterministicFiniteAutomaton,
    states_order_fa: dict[State, int],
) -> dict[str, dok_matrix]:
    """
    Creates boolean decomposition of finite automata
    """
    result = defaultdict(
        lambda: dok_matrix((len(fa.states), len(fa.states)), dtype=bool)
    )
    for src, transitions in fa.to_dict().items():
        for symbol, destinations in transitions.items():
            if isinstance(destinations, Iterable):
                for dst in destinations:
                    result[symbol.value][
                        states_order_fa[src], states_order_fa[dst]
                    ] = True
            else:
                result[symbol.value][
                    states_order_fa[src], states_order_fa[destinations]
                ] = True
    return result


def get_fa_from_boolean_decomposition(
    boolean_decomposition: dict[Symbol, dok_matrix],
    start_states: Iterable[int],
    final_states: Iterable[int],
) -> NondeterministicFiniteAutomaton:
    """
    Creates finite automata from boolean decomposition, start states and final states
    """
    result_fa = NondeterministicFiniteAutomaton()
    states_number = next(iter(boolean_decomposition.values())).shape[0]
    states = [State(i) for i in range(states_number)]
    for state_index in start_states:
        result_fa.add_start_state(states[state_index])
    for state_index in final_states:
        result_fa.add_final_state(states[state_index])
    for symbol, symbol_boolean_matrix in boolean_decomposition.items():
        symbol_object = Symbol(symbol)
        for states_pair, value in symbol_boolean_matrix.items():
            if value == True:
                src, dst = states_pair
                result_fa.add_transition(states[src], symbol_object, states[dst])
    return result_fa


def get_transitive_closure_of_boolean_decomposition(
    boolean_decomposition: dict[str, dok_matrix]
) -> csr_matrix:
    """
    Creates transitive closure from boolean decomposition of finite automata
    """
    states_number = next(iter(boolean_decomposition.values())).shape[0]
    sum_of_matrices = dok_matrix((states_number, states_number), dtype=bool)
    for matrix in boolean_decomposition.values():
        sum_of_matrices += matrix
    result_matrix = sum_of_matrices.tocsc()
    for _ in range(math.ceil(math.log2(states_number))):
        result_matrix = result_matrix + result_matrix @ result_matrix
    return result_matrix
