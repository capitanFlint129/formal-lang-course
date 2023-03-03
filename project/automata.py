from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
)
from networkx import MultiDiGraph

from typing import Optional, Iterable


def get_deterministic_automata_from_regex(regex: Regex) -> DeterministicFiniteAutomaton:
    nfa = regex.to_epsilon_nfa()
    dfa_minimum = nfa.minimize()
    return dfa_minimum


def get_nondeterministic_automata_from_graph(
    graph: MultiDiGraph,
    start_states: Optional[Iterable] = None,
    final_states: Optional[Iterable] = None,
) -> NondeterministicFiniteAutomaton:
    nfa = NondeterministicFiniteAutomaton.from_networkx(graph)

    if start_states is None:
        for state in nfa.states:
            nfa.add_start_state(state)
    else:
        for state in start_states:
            nfa.add_start_state(state)

    if final_states is None:
        for state in nfa.states:
            nfa.add_final_state(state)
    else:
        for state in final_states:
            nfa.add_final_state(state)

    return nfa
