from functools import reduce
from typing import Optional, Iterable, Union

import networkx as nx
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
    EpsilonNFA,
    Symbol,
    State,
    Epsilon,
)
from pyformlang.regular_expression import Regex


class RFA:
    """
    Alternative RFA implementation using EpsilonNFA
    """

    def __init__(self, start_non_terminal: str = "S"):
        # self.nfa = Regex(start_non_terminal).to_epsilon_nfa()
        self.nfa = EpsilonNFA()
        state0 = State("0")
        state1 = State("1")
        self.nfa.add_start_state(state0)
        self.nfa.add_final_state(state1)
        self.nfa.add_transition(state0, Symbol(start_non_terminal), state1)
        self.state_to_non_terminals = {
            state: {start_non_terminal}
            for state in self.nfa.start_states | self.nfa.final_states
        }
        self.start_non_terminal = start_non_terminal

    def set_starts(self, states, state_to_non_terminals) -> "RFA":
        """
        Set new start vertices and non-terminals for them
        """
        res = RFA(self.start_non_terminal)
        res.nfa = self.nfa.copy()
        res.nfa.start_states.clear()
        for state in states:
            res.nfa.add_start_state(state)
        res.state_to_non_terminals = {
            state: set(map(lambda el: Symbol(el), state_to_non_terminals[state.value]))
            for state in self.nfa.start_states
        }
        return res

    def set_finals(self, states, state_to_non_terminals) -> "RFA":
        """
        Set new final vertices and non-terminals for them
        """
        res = RFA(self.start_non_terminal)
        res.nfa = self.nfa.copy()
        res.nfa.final_states.clear()
        for state in states:
            res.nfa.add_final_state(state)
        res.state_to_non_terminals = {
            state: set(map(lambda el: Symbol(el), state_to_non_terminals[state.value]))
            for state in self.nfa.final_states
        }
        return res

    def add_start(self, state, non_terminals) -> "RFA":
        """
        Add start state and set non-terminals
        """
        res = RFA(self.start_non_terminal)
        res.nfa = self.nfa.copy()
        res.nfa.add_start_state(state)
        res.state_to_non_terminals[State(state)] = set(
            map(lambda el: Symbol(el), non_terminals)
        )
        return res

    def add_final(self, state, non_terminals) -> "RFA":
        """
        Add final state and set non-terminals
        """
        res = RFA(self.start_non_terminal)
        res.nfa = self.nfa.copy()
        res.nfa.add_final_state(state)
        res.state_to_non_terminals[State(state)] = set(
            map(lambda el: Symbol(el), non_terminals)
        )
        return res

    def concat(self, other: Union["RFA", EpsilonNFA]) -> "RFA":
        """
        Concat RFA with other automata
        """
        res = RFA(self.start_non_terminal)
        res.state_to_non_terminals = {
            state: set(non_terminals)
            for state, non_terminals in self.state_to_non_terminals.items()
        }
        new_nfa = self.nfa.copy()
        if isinstance(other, EpsilonNFA):
            fa2 = other
            new_states = {state: State(str(state.value) + "_2") for state in fa2.states}
            new_finals = [new_states[st] for st in fa2.final_states]
            for final in new_nfa.final_states:
                for start in fa2.start_states:
                    new_nfa.add_transition(final, Epsilon(), new_states[start])
            new_nfa.final_states.clear()
            for src, label, dst in fa2:
                new_nfa.add_transition(new_states[src], label, new_states[dst])
            for final in new_finals:
                new_nfa.add_final_state(final)
            for final in fa2.final_states:
                res.state_to_non_terminals[new_states[final]] = {res.start_non_terminal}
        elif isinstance(other, RFA):
            fa2 = other.nfa
            new_states = {state: State(str(state.value) + "_2") for state in fa2.states}
            new_finals = [new_states[st] for st in fa2.final_states]
            for final in new_nfa.final_states:
                for start in fa2.start_states:
                    new_nfa.add_transition(final, Epsilon(), new_states[start])
            new_nfa.final_states.clear()
            for src, label, dst in fa2:
                if label == other.start_non_terminal:
                    label = str(other.start_non_terminal) + "_2"
                new_nfa.add_transition(new_states[src], label, new_states[dst])
            for final in new_finals:
                new_nfa.add_final_state(final)
            for start in new_nfa.start_states:
                if self.start_non_terminal in self.state_to_non_terminals[start]:
                    res.state_to_non_terminals[start].add(res.start_non_terminal)
            for final in fa2.final_states:
                res.state_to_non_terminals[new_states[final]] = {res.start_non_terminal}
        res.nfa = new_nfa
        return res

    def rev_concat(self, other: EpsilonNFA) -> "RFA":
        """
        Concat RFA with nfa in reversed case
        """
        res = RFA(str(self.start_non_terminal) + "_2")
        res.state_to_non_terminals = {
            state: set(non_terminals)
            for state, non_terminals in self.state_to_non_terminals.items()
        }
        for final in res.nfa.final_states:
            res.state_to_non_terminals[final] = {res.start_non_terminal}
        new_nfa = self.nfa.copy()
        fa2 = other
        new_states = {state: State(str(state.value) + "_2") for state in fa2.states}
        new_starts = [new_states[st] for st in fa2.start_states]
        for start in new_nfa.start_states:
            for final in fa2.final_states:
                new_nfa.add_transition(new_states[final], Epsilon(), start)
        new_nfa.start_states.clear()
        for src, label, dst in fa2:
            new_nfa.add_transition(new_states[src], label, new_states[dst])
        for start in new_starts:
            new_nfa.add_start_state(start)
        for start in fa2.start_states:
            res.state_to_non_terminals[new_states[start]] = {res.start_non_terminal}
        res.nfa = new_nfa
        return res

    def union(self, other: Union["RFA", EpsilonNFA]) -> "RFA":
        """
        Union RFA with other automata
        """
        res = RFA(self.start_non_terminal)
        res.state_to_non_terminals = {
            state: set(non_terminals)
            for state, non_terminals in self.state_to_non_terminals.items()
        }
        new_nfa = self.nfa.copy()
        if isinstance(other, EpsilonNFA):
            fa2 = other
            new_states = {state: State(str(state.value) + "_2") for state in fa2.states}
            for start1 in new_nfa.start_states:
                for start2 in fa2.start_states:
                    new_nfa.add_transition(start1, Epsilon(), new_states[start2])
            for src, label, dst in fa2:
                new_nfa.add_transition(new_states[src], label, new_states[dst])
            for final in fa2.final_states:
                new_nfa.add_final_state(new_states[final])
                res.state_to_non_terminals[new_states[final]] = {res.start_non_terminal}
        elif isinstance(other, RFA):
            fa2 = other.nfa
            new_states = {state: State(str(state.value) + "_2") for state in fa2.states}
            for start1 in new_nfa.start_states:
                for start2 in fa2.start_states:
                    new_nfa.add_transition(start1, Epsilon(), new_states[start2])
            for src, label, dst in fa2:
                new_nfa.add_transition(new_states[src], label, new_states[dst])
            for final in fa2.final_states:
                new_nfa.add_final_state(new_states[final])
            for final in fa2.final_states:
                res.state_to_non_terminals[new_states[final]] = {res.start_non_terminal}
            for state, non_terminals in other.state_to_non_terminals.items():
                res.state_to_non_terminals[new_states[state]] = non_terminals
        # res.nfa = new_nfa.minimize()
        res.nfa = new_nfa
        return res

    def kleene_star(self) -> "RFA":
        """
        Get kleene star for RFA
        """
        res = RFA(self.start_non_terminal)
        res.nfa = self.nfa.copy()
        for final in self.nfa.final_states:
            if self.start_non_terminal in self.state_to_non_terminals[final]:
                for start in self.nfa.start_states:
                    if self.start_non_terminal in self.state_to_non_terminals[start]:
                        self.nfa.add_transition(final, Epsilon(), start)
        return res

    def intersect(self, other: EpsilonNFA):
        # Not implemented because we skipped the task of implementing RFA intersection through tensors
        raise NotImplementedError()

    def to_rsm(self):
        raise NotImplementedError()

    def non_terminals(self) -> set[Symbol]:
        """
        Get RFA non-terminal
        """
        return reduce(
            lambda cur, el: cur.add(el), self.state_to_non_terminals.values(), set()
        )


def automatas_concat(
    fa1: Union[EpsilonNFA, RFA], fa2: Union[EpsilonNFA, RFA]
) -> Union[EpsilonNFA, RFA]:
    """
    Concat automatas
    """
    if isinstance(fa1, RFA):
        return fa1.concat(fa2)
    if isinstance(fa2, RFA):
        return fa2.rev_concat(fa1)
    return fa1.concatenate(fa2).minimize()


def automatas_union(
    fa1: Union[EpsilonNFA, RFA], fa2: Union[EpsilonNFA, RFA]
) -> Union[EpsilonNFA, RFA]:
    """
    Union automatas
    """
    if isinstance(fa1, RFA):
        return fa1.union(fa2)
    if isinstance(fa2, RFA):
        return fa2.union(fa1)
    return fa1.union(fa2).minimize()


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
