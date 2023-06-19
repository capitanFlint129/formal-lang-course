from typing import AbstractSet

import networkx as nx
import pydot
from pyformlang.cfg import CFG, Terminal, Epsilon

from project.weak_chomsky_normal_form import (
    transform_to_weak_normal_form,
    read_grammar_from_file,
)
from project.boolean_decomposition import *
from project.graph_utils import get_number_of_nodes
from scipy.sparse import dok_matrix


def get_reachable_pairs(
    graph: nx.Graph | str,
    cfg: CFG | str,
) -> set[tuple]:
    """
    Finds all pairs of graph vertices where first vertex is reachable from
    second vertex with path that belongs to given grammar
    regardless of the starting non-terminal

    Parameters
    ----------
    graph :
        The graph on which the request is executed or path to dot file of graph.
        If a file is passed, then the first graph is taken from it
    cfg :
        Context free grammar of query or path to file with text representation of cfg

    Returns
    ----------
    result :
        List of triples of (v, N, u) where v - source vertex, u - destination vertex
        N - non-terminal that allows reaching v from u
    """
    if isinstance(graph, str):
        graph = nx.nx_pydot.from_pydot(pydot.graph_from_dot_file(graph)[0])
    if isinstance(cfg, str):
        cfg = read_grammar_from_file(cfg)
    cfg = transform_to_weak_normal_form(cfg)

    n = get_number_of_nodes(graph)
    T = {nt: dok_matrix((n, n), dtype=bool) for nt in _get_nonterminals(cfg)}
    for i, j, x in graph.edges(data="label"):
        for production in cfg.productions:
            t = production.body[0]
            if isinstance(t, Epsilon):
                T[production.head][i, j] = True
            if isinstance(t, Terminal) and t.value == x:
                T[production.head][i, j] = True
    T_prev = T
    while True:
        T = T.copy()
        for production in cfg.productions:
            if not isinstance(production.body[0], (Epsilon, Terminal)):
                T[production.head] += T[production.body[0]] @ T[production.body[1]]
        if all((T[key] != T_prev[key]).nnz == 0 for key in T.keys() | T_prev.keys()):
            break
        T_prev = T
    result = {
        (i, nt, j)
        for nt, matrix in T.items()
        for (i, j), value in matrix.todok().items()
        if value
    }
    return result


def cf_query_to_graph(
    query: CFG,
    graph: nx.Graph,
    start_nonterminal: Variable,
    start_states: Iterable[int],
    final_states: Iterable[int],
) -> set[tuple]:
    """
    Executes context free query to the given graph using Hellings algorithm

    Parameters
    ----------
    query :
        Context free grammar of query or path to file with text representation of cfg
    graph :
        The graph on which the request is executed or path to dot file of graph.
        If a file is passed, then the first graph is taken from it
    start_nonterminal :
        Start nonterminal of query
    start_states :
        Graph vertices which interpreted as start states
    final_states :
        Graph vertices which interpreted as final states

    Returns
    ----------
    result :
        Set of pairs of vertices, where first vertex is start state and second vertex is
        final state. Second vertex is reachable from first vertex and path is
        belongs to the language with grammar from query
    """
    return {
        (src, dst)
        for src, sym, dst in get_reachable_pairs(graph, query)
        if src in start_states and sym == start_nonterminal and dst in final_states
    }


def _get_nonterminals(cfg: CFG) -> AbstractSet[Variable]:
    return {var for var in cfg.variables if var not in cfg.terminals}
