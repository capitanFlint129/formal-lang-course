import re
from collections import defaultdict
from typing import AbstractSet

from pyformlang.cfg import CFG, Variable, Terminal
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.regular_expression import Regex

from project.automata import get_deterministic_automata_from_regex
from project.weak_chomsky_normal_form import read_grammar_from_file


class RecursiveFiniteAutomaton:
    """
    Represents a recursive FA

    Parameters
    ----------
    start_symbol :
        The start symbol
    symbol_to_fa :
        Dictionary of variables and automatas for each variable
    """

    def __init__(
        self,
        start_symbol: Variable,
        symbol_to_fa: dict[Variable, NondeterministicFiniteAutomaton],
    ):
        self.start_symbol = start_symbol
        self.symbol_to_fa = symbol_to_fa

    def minimize(self) -> "RecursiveFiniteAutomaton":
        """
        Minimize the current RFA

        Returns
        ----------
        rfa :
            RFA with minimized DFA for each variable
        """
        self.symbol_to_fa = {
            var: fa.minimize() for var, fa in self.symbol_to_fa.items()
        }
        return self

    @classmethod
    def from_ecfg(cls, ecfg) -> "RecursiveFiniteAutomaton":
        """
        Transforms context free grammar to extended context free grammar

        Parameters
        ----------
        ecfg :
            Extended contex free grammar object

        Returns
        -------
        rfa :
            A recursive finite automaton representation
        """
        return ecfg.to_recursive_fa()

    @classmethod
    def from_text_ecfg(cls, text: str) -> "RecursiveFiniteAutomaton":
        """
        Reads an extended context free grammar from a text representation and transforms it to rfa

        Parameters
        ----------
        text : str
            The text of transform
        start_symbol : str, optional
            The start symbol, S by default

        Returns
        -------
        rfa :
            A recursive finite automaton representation
        """
        return ECFG.from_text(text).to_recursive_fa()

    @classmethod
    def from_file_ecfg(cls, path: str) -> "RecursiveFiniteAutomaton":
        """
        Reads an extended context free grammar from a file and transforms it to rfa

        Parameters
        ----------
        path :
            Path to file

        Returns
        -------
        rfa :
            A recursive finite automaton representation
        """
        return ECFG.from_file(path).to_recursive_fa()


class ECFG:
    """
    A class representing an extended context free grammar

    Parameters
    ----------
    variables :
        The variables of the ECFG
    terminals :
        The terminals of the ECFG
    start_symbol :
        The start symbol
    productions :
        The productions of the ECFG
    """

    def __init__(
        self,
        variables: AbstractSet[Variable] = None,
        terminals: AbstractSet[Terminal] = None,
        start_symbol: Variable = None,
        productions: dict[Variable, Regex] = None,
    ):
        self.variables = variables
        self.terminals = terminals
        self.start_symbol = start_symbol
        self.productions = productions

    def to_recursive_fa(self) -> RecursiveFiniteAutomaton:
        """
        Returns recursive finite automaton representation of ecfg

        Returns
        -------
        rfa :
            A recursive finite automaton representation
        """
        return RecursiveFiniteAutomaton(
            self.start_symbol,
            {
                head: get_deterministic_automata_from_regex(body)
                for head, body in self.productions.items()
            },
        )

    @classmethod
    def from_cfg(cls, cfg: CFG) -> "ECFG":
        """
        Transforms context free grammar to extended context free grammar

        Parameters
        ----------
        cfg :
            Contex free grammar object

        Returns
        -------
        ecfg :
            An extended context free grammar
        """
        ecfg_productions = defaultdict(list)
        for production in cfg.productions:
            ecfg_productions[production.head.value].extend(production.body)
        for var in cfg.variables:
            if not isinstance(var, Terminal) and var.value not in ecfg_productions:
                ecfg_productions[var.value].append("$")
        ecfg = ECFG(
            variables=cfg.variables,
            terminals=cfg.terminals,
            start_symbol=cfg.start_symbol,
            productions={
                head: Regex(" | ".join([re.escape(var.value) for var in body]))
                for head, body in ecfg_productions.items()
            },
        )
        return ecfg

    @classmethod
    def from_text_cfg(cls, text: str, start_symbol: Variable = Variable("S")) -> "ECFG":
        """
        Read a context free grammar from a text and transforms
        it to extended context free grammar

        Parameters
        ----------
        text : str
            The text of transform
        start_symbol : str, optional
            The start symbol, S by default

        Returns
        -------
        ecfg :
            An extended context free grammar
        """
        return cls.from_cfg(CFG.from_text(text, start_symbol))

    @classmethod
    def from_file_cfg(cls, path) -> "ECFG":
        """
        Reads extended context free grammar from file with text representation of cfg

        Parameters
        ----------
        path :
            Path to file

        Returns
        ----------
        ecfg:
            Extended context free grammar read from file
        """
        return cls.from_cfg(read_grammar_from_file(path))

    @classmethod
    def from_text(cls, text, start_symbol=Variable("S")) -> "ECFG":
        """
        Read an extended context free grammar from a text.
        The text contains one rule per line.
        The structure of a production is:
        head -> <regex>
        A variable (or non-terminal) begins by a capital letter.
        A terminal begins by a non-capital character
        Terminals and Variables are separated by spaces.
        An epsilon symbol can be represented by epsilon, $, ε, ϵ or Є.

        Parameters
        ----------
        text : str
            The text of transform
        start_symbol : str, optional
            The start symbol, S by default

        Returns
        -------
        ecfg :
            An extended context free grammar
        """
        variables = set()
        productions = dict()
        terminals = set()
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            cls._read_line(line, productions, terminals, variables)
        return cls(
            variables=variables,
            terminals=terminals,
            productions=productions,
            start_symbol=start_symbol,
        )

    @classmethod
    def _read_line(cls, line, productions, terminals, variables):
        head_s, body_s = line.split("->")
        head_text = head_s.strip()
        head = Variable(head_text)
        body_text = body_s.strip()
        body = Regex(body_text)
        variables.add(head)
        regex_cfg = body.to_cfg()
        terminals.update([t for t in regex_cfg.terminals if str.islower(t.value[0])])
        productions[head] = body

    @classmethod
    def from_file(cls, path) -> "ECFG":
        """
        Reads extended context free grammar from file

        Parameters
        ----------
        path :
            Path to file with text representation of grammar

        Returns
        ----------
        ecfg:
            Extended context free grammar read from file
        """
        with open(path, "r") as inf:
            return cls.from_text(inf.read())
