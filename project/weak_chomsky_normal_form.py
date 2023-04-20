from pyformlang.cfg import CFG


def transform_to_weak_normal_form(grammar: CFG) -> CFG:
    """
    Returns new grammar in weak Chomsky normal form

    Parameters
    ----------
    grammar :
        Grammar to transform

    Returns
    ----------
    cfg:
        New grammar in weak Chomsky normal form
    """
    grammar = grammar.eliminate_unit_productions().remove_useless_symbols()
    new_productions = grammar._get_productions_with_only_single_terminals()
    new_productions = grammar._decompose_productions(new_productions)
    cfg = CFG(start_symbol=grammar._start_symbol, productions=set(new_productions))
    return cfg


def read_grammar_from_file(path: str) -> CFG:
    """
    Reads context free grammar from file

    Parameters
    ----------
    path :
        Path to file with text representation of grammar

    Returns
    ----------
    cfg:
        Context free grammar read from file
    """
    with open(path, "r") as inf:
        return CFG.from_text(inf.read())
