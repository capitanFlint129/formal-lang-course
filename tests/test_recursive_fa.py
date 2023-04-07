from pyformlang.cfg import CFG
from pyformlang.finite_automaton import State, Symbol, NondeterministicFiniteAutomaton

from project.recursive_finite_state_machines import (
    RecursiveFiniteAutomaton,
    ECFG,
    Variable,
)
from project.weak_chomsky_normal_form import read_grammar_from_file


def test_ecfg_from_cfg():
    cfg = CFG.from_text(
        """
        S -> NP VP
        S -> PUNC
        PUNC -> . | !
        VP -> V NP
        V -> buys | touches | sees
        NP -> georges | jacques | leo | Det N
        Det -> a | an | the
        N -> gorilla | dog | carrots
        U -> $
        """
    )
    ecfg = ECFG.from_cfg(cfg)
    assert ecfg.variables == cfg.variables
    assert ecfg.start_symbol == cfg.start_symbol
    assert ecfg.terminals == cfg.terminals
    assert len(ecfg.productions) == len(cfg.variables)
    assert all([var in ecfg.productions for var in cfg.variables])
    for production in cfg.productions:
        for symbol in production.body:
            assert ecfg.productions[production.head].accepts([symbol.value])


def test_ecfg_from_text_cfg():
    text = """
        S -> NP VP
        S -> PUNC
        PUNC -> . | !
        VP -> V NP
        V -> buys | touches | sees
        NP -> georges | jacques | leo | Det N
        Det -> a | an | the
        N -> gorilla | dog | carrots
        U -> $
        """
    cfg = CFG.from_text(text)
    ecfg = ECFG.from_text_cfg(text)
    assert ecfg.variables == cfg.variables
    assert ecfg.start_symbol == cfg.start_symbol
    assert ecfg.terminals == cfg.terminals
    assert len(ecfg.productions) == len(cfg.variables)
    assert all([var in ecfg.productions for var in cfg.variables])
    for production in cfg.productions:
        for symbol in production.body:
            assert ecfg.productions[production.head].accepts([symbol.value])


def test_ecfg_from_file_cfg():
    path = "tests/data/cfg_grammar"
    cfg = read_grammar_from_file(path)
    ecfg = ECFG.from_file_cfg(path)
    assert ecfg.variables == cfg.variables
    assert ecfg.start_symbol == cfg.start_symbol
    assert ecfg.terminals == cfg.terminals
    assert len(ecfg.productions) == len(cfg.variables)
    assert all([var in ecfg.productions for var in cfg.variables])
    for production in cfg.productions:
        for symbol in production.body:
            assert ecfg.productions[production.head].accepts([symbol.value])


def test_ecfg_from_text():
    cfg = CFG.from_text(
        """
        S -> NP VP
        VP -> V NP
        V -> buys | touches | sees
        NP -> georges | jacques | leo | Det N
        Det -> a | an | the
        N -> gorilla | dog | carrots
        U -> $
        """
    )
    ecfg = ECFG.from_text(
        """
        S -> NP VP
        VP -> V NP
        V -> buys | touches | sees
        NP -> georges | jacques | leo | Det N
        Det -> a | an | the
        N -> gorilla | dog | carrots
        U -> $
        """
    )
    assert ecfg.variables == cfg.variables
    assert ecfg.start_symbol == cfg.start_symbol
    assert ecfg.terminals == cfg.terminals
    assert len(ecfg.productions) == len(cfg.variables)
    assert all([var in ecfg.productions for var in cfg.variables])
    for production in cfg.productions:
        assert ecfg.productions[production.head].accepts(
            [sym.value for sym in production.body]
        )


def test_ecfg_from_file():
    text = """
        S -> NP VP
        VP -> V NP
        V -> buys | touches | sees
        NP -> georges | jacques | leo | Det N
        Det -> a | an | the
        N -> gorilla | dog | carrots
        U -> $
        """
    cfg = CFG.from_text(text)
    path = "tests/data/ecfg_grammar"
    ecfg = ECFG.from_file(path)
    assert ecfg.variables == cfg.variables
    assert ecfg.start_symbol == cfg.start_symbol
    assert ecfg.terminals == cfg.terminals
    assert len(ecfg.productions) == len(cfg.variables)
    assert all([var in ecfg.productions for var in cfg.variables])
    for production in cfg.productions:
        assert ecfg.productions[production.head].accepts(
            [sym.value for sym in production.body]
        )


def test_to_recursive_fa():
    ecfg = ECFG.from_text(
        """
        S -> a S b | a b
        """
    )
    result_rfa = ecfg.to_recursive_fa()
    states = [State(i) for i in range(4)]
    symbols = {s: Symbol(s) for s in "abS"}
    fa = NondeterministicFiniteAutomaton()
    fa.add_start_state(states[0])
    fa.add_final_state(states[3])
    fa.add_transitions(
        [
            [states[0], symbols["a"], states[1]],
            [states[1], symbols["S"], states[2]],
            [states[1], symbols["b"], states[3]],
            [states[2], symbols["b"], states[3]],
        ]
    )
    expected_rfa = RecursiveFiniteAutomaton(Variable("S"), {Variable("S"): fa})
    assert expected_rfa.start_symbol == result_rfa.start_symbol
    for var, fa in result_rfa.symbol_to_fa.items():
        assert expected_rfa.symbol_to_fa[var].is_equivalent_to(fa)
