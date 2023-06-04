from typing import Optional, Iterable

import networkx as nx
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
)
from pyformlang.regular_expression import Regex


def get_deterministic_automata_from_regex(regex: Regex) -> DeterministicFiniteAutomaton:
    """
    Transforms the regular expression into a minimum DFA

    Parameters
    ----------
    regex :
        An input regex

    Returns
    ----------
    dfa :
        A minimum DFA equivalent to the regex

    Examples
    --------

    >>> regex = Regex("abc|d")
    >>> get_deterministic_automata_from_regex(regex)

    """
    nfa = regex.to_epsilon_nfa()
    dfa_minimum = nfa.minimize()
    return dfa_minimum


def get_nondeterministic_automata_from_graph(
    graph: nx.Graph,
    start_states: Optional[Iterable] = None,
    final_states: Optional[Iterable] = None,
) -> NondeterministicFiniteAutomaton:
    """
    Transforms the networkx graph into a NFA

    Parameters
    ----------
    graph :
        The graph representation of the automaton
    start_states :
        States to be marked as start
    final_states :
        States to be marked as final

    Returns
    -------
    nfa :
        A epsilon nondeterministic finite automaton read from the graph


    Examples
    --------

    >>> from project import graph_utils
    >>> graph = graph_utils.create_two_cycles_graph(5, 3, ("a", "b",))
    >>> get_nondeterministic_automata_from_graph(graph, [1, 2, 3], [4, 5])

    """
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
