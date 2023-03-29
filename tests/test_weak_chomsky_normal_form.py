from pyformlang.cfg import CFG

from project.weak_chomsky_normal_form import read_grammar_from_file


def test_transform_to_weak_normal_form():
    pass


def test_read_grammar():
    expected = CFG.from_text(
        """
        S -> NP VP PUNC
        PUNC -> . | !
        VP -> V NP
        V -> buys | touches | sees
        NP -> georges | jacques | leo | Det N
        Det -> a | an | the
        N -> gorilla | dog | carrots"""
    )
    result = read_grammar_from_file("data/cfg_grammar")
    assert result.productions == expected.productions
    assert result.start_symbol == expected.start_symbol
    assert result.terminals == expected.terminals
    assert result.variables == expected.variables
