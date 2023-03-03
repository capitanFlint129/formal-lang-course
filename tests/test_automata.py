from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    State,
    Symbol,
    NondeterministicFiniteAutomaton,
)

from project import automata, grapth_utils


def test_get_deterministic_automata_from_regex_one_symbol():
    states = [State(0), State(1)]
    symbol = Symbol("a")

    regex = Regex("a")
    minimal_dfa = DeterministicFiniteAutomaton()
    minimal_dfa.add_start_state(states[0])
    minimal_dfa.add_final_state(states[1])
    minimal_dfa.add_transition(states[0], symbol, states[1])

    dfa = automata.get_deterministic_automata_from_regex(regex)
    assert dfa.is_equivalent_to(minimal_dfa)


def test_get_deterministic_automata_from_regex_one_word():
    states = [State(0), State(1), State(2), State(3), State(4)]
    symbols = {symbol: Symbol(symbol) for symbol in "abc!"}

    regex = Regex("a b c !")
    minimal_dfa = DeterministicFiniteAutomaton()
    minimal_dfa.add_start_state(states[0])
    minimal_dfa.add_final_state(states[4])
    minimal_dfa.add_transitions(
        [
            (states[0], symbols["a"], states[1]),
            (states[1], symbols["b"], states[2]),
            (states[2], symbols["c"], states[3]),
            (states[3], symbols["!"], states[4]),
        ]
    )

    dfa = automata.get_deterministic_automata_from_regex(regex)
    assert dfa.is_equivalent_to(minimal_dfa)


def test_get_deterministic_automata_from_regex_empty_string():
    regex = Regex("")
    minimal_dfa = DeterministicFiniteAutomaton()

    dfa = automata.get_deterministic_automata_from_regex(regex)
    assert dfa.is_equivalent_to(minimal_dfa)


def test_get_deterministic_automata_from_regex_epsilon():
    regex = Regex("$")
    state = State(0)
    minimal_dfa = DeterministicFiniteAutomaton()
    minimal_dfa.add_start_state(state)
    minimal_dfa.add_final_state(state)

    dfa = automata.get_deterministic_automata_from_regex(regex)
    assert dfa.is_equivalent_to(minimal_dfa)


def test_get_deterministic_automata_from_regex_epsilon():
    regex = Regex("$")
    state = State(0)
    minimal_dfa = DeterministicFiniteAutomaton()
    minimal_dfa.add_start_state(state)
    minimal_dfa.add_final_state(state)

    dfa = automata.get_deterministic_automata_from_regex(regex)
    assert dfa.is_equivalent_to(minimal_dfa)


def test_get_deterministic_automata_from_regex_kleene_star():
    regex = Regex("a*")

    minimal_dfa = DeterministicFiniteAutomaton()
    state = State(0)
    minimal_dfa.add_start_state(state)
    minimal_dfa.add_final_state(state)
    symb_a = Symbol("a")
    minimal_dfa.add_transition(state, symb_a, state)

    dfa = automata.get_deterministic_automata_from_regex(regex)
    assert dfa.is_equivalent_to(minimal_dfa)


def test_get_deterministic_automata_from_regex_kleene_star_two_symbols():
    regex = Regex("a b*")
    symbols = {symbol: Symbol(symbol) for symbol in "ab"}

    minimal_dfa = DeterministicFiniteAutomaton()
    states = [State(0), State(1)]
    minimal_dfa.add_start_state(states[0])
    minimal_dfa.add_final_state(states[1])
    minimal_dfa.add_transition(states[0], symbols["a"], states[1])
    minimal_dfa.add_transition(states[1], symbols["b"], states[1])

    dfa = automata.get_deterministic_automata_from_regex(regex)
    assert dfa.is_equivalent_to(minimal_dfa)


def test_get_deterministic_automata_from_regex_union():
    regex = Regex("a+b")
    symbols = {symbol: Symbol(symbol) for symbol in "ab"}

    minimal_dfa = DeterministicFiniteAutomaton()
    states = [State(0), State(1)]
    minimal_dfa.add_start_state(states[0])
    minimal_dfa.add_final_state(states[1])
    minimal_dfa.add_transition(states[0], symbols["a"], states[1])
    minimal_dfa.add_transition(states[0], symbols["b"], states[1])

    dfa = automata.get_deterministic_automata_from_regex(regex)
    assert dfa.is_equivalent_to(minimal_dfa)


def test_get_deterministic_automata_from_regex_star_and_union():
    regex = Regex("a+b*")
    symbols = {symbol: Symbol(symbol) for symbol in "ab"}

    minimal_dfa = DeterministicFiniteAutomaton()
    states = [State(0), State(1), State(2)]
    minimal_dfa.add_start_state(states[0])
    minimal_dfa.add_final_state(states[0])
    minimal_dfa.add_final_state(states[1])
    minimal_dfa.add_final_state(states[2])
    minimal_dfa.add_transition(states[0], symbols["b"], states[1])
    minimal_dfa.add_transition(states[1], symbols["b"], states[1])
    minimal_dfa.add_transition(states[0], symbols["a"], states[2])

    dfa = automata.get_deterministic_automata_from_regex(regex)
    assert dfa.is_equivalent_to(minimal_dfa)


def test_get_nondeterministic_automata_from_two_cycles_generated_graph():
    graph = grapth_utils.create_two_cycles_graph(5, 3, ["a", "b"])

    nfa = NondeterministicFiniteAutomaton()
    states = [State(i) for i in range(9)]
    symbols = {symbol: Symbol(symbol) for symbol in "ab"}

    nfa.add_transitions([(states[i], symbols["a"], states[i + 1]) for i in range(5)])
    nfa.add_transition(states[5], symbols["a"], states[0])

    nfa.add_transitions([(states[i], symbols["b"], states[i + 1]) for i in range(6, 8)])
    nfa.add_transition(states[8], symbols["b"], states[0])
    nfa.add_transition(states[0], symbols["b"], states[6])

    for state in states:
        nfa.add_start_state(state)
        nfa.add_final_state(state)

    assert automata.get_nondeterministic_automata_from_graph(graph).is_equivalent_to(
        nfa
    )


def test_get_nondeterministic_automata_from_two_cycles_generated_graph_with_final_and_start_states():
    graph = grapth_utils.create_two_cycles_graph(5, 3, ["a", "b"])

    nfa = NondeterministicFiniteAutomaton()
    states = [State(i) for i in range(9)]
    symbols = {symbol: Symbol(symbol) for symbol in "ab"}

    nfa.add_transitions([(states[i], symbols["a"], states[i + 1]) for i in range(5)])
    nfa.add_transition(states[5], symbols["a"], states[0])

    nfa.add_transitions([(states[i], symbols["b"], states[i + 1]) for i in range(6, 8)])
    nfa.add_transition(states[8], symbols["b"], states[0])
    nfa.add_transition(states[0], symbols["b"], states[6])

    start_states = [0, 1, 2]
    final_states = [2, 6, 7, 4]
    for state in start_states:
        nfa.add_start_state(states[state])
    for state in final_states:
        nfa.add_final_state(states[state])

    assert automata.get_nondeterministic_automata_from_graph(
        graph, start_states, final_states
    ).is_equivalent_to(nfa)
