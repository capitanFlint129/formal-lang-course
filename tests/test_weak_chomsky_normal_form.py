from pyformlang.cfg import CFG, Terminal, Epsilon

from project.weak_chomsky_normal_form import (
    transform_to_weak_normal_form,
    read_grammar_from_file,
)


def test_transform_to_weak_normal_form():
    grammar = CFG.from_text(
        """
        S -> NP VP PUNC
        PUNC -> . | !
        VP -> V NP
        V -> buys | touches | sees
        NP -> georges | jacques | leo | Det N
        Det -> a | an | the
        N -> gorilla | dog | carrots
        U -> $
        """
    )
    assert not grammar.is_normal_form()
    grammar_in_weak_normal_form = transform_to_weak_normal_form(grammar)
    assert not grammar.is_normal_form()
    assert grammar_in_weak_normal_form.start_symbol == grammar.start_symbol
    assert grammar_in_weak_normal_form.terminals == grammar.terminals

    for production in grammar_in_weak_normal_form.productions:
        assert not isinstance(production.head, Terminal)
        if len(production.body) == 2:
            assert not isinstance(production.body[0], Terminal)
            assert not isinstance(production.body[1], Terminal)
        elif len(production.body) == 1:
            assert isinstance(production.body[0], Terminal) or isinstance(
                production.body[0], Epsilon
            )
        else:
            raise AssertionError()


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
    result = read_grammar_from_file("tests/data/cfg_grammar")
    assert result.productions == expected.productions
    assert result.start_symbol == expected.start_symbol
    assert result.terminals == expected.terminals
    assert result.variables == expected.variables
