from collections import defaultdict
from typing import Iterable
import math

from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, Symbol, State
from pyformlang.cfg import Variable
from scipy.sparse import dok_matrix, csr_matrix

from project.recursive_finite_state_machines import RecursiveFiniteAutomaton


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


def get_boolean_decomposition_of_rfa(
    rfa: RecursiveFiniteAutomaton,
    states_orders_fa: dict[Variable, dict[State, int]],
) -> dict[Variable, dict[str, dok_matrix]]:
    """
    Creates boolean decomposition of recursive finite automata
    """
    return {
        sym: get_boolean_decomposition_of_fa(fa, states_orders_fa[sym])
        for sym, fa in rfa.symbol_to_fa.items()
    }


def get_fa_from_boolean_decomposition(
    boolean_decomposition: dict[Symbol, dok_matrix],
    start_states: Iterable[int],
    final_states: Iterable[int],
) -> NondeterministicFiniteAutomaton:
    """
    Creates finite automata from boolean decomposition, start states and final states
    """
    result_fa = NondeterministicFiniteAutomaton()
    if len(boolean_decomposition) == 0:
        return result_fa
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
