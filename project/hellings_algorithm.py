import networkx as nx
import pydot
from pyformlang.cfg import CFG, Terminal, Epsilon

from project.boolean_decomposition import *
from project.weak_chomsky_normal_form import (
    transform_to_weak_normal_form,
    read_grammar_from_file,
)


def get_reachable_pairs_hellings(
    graph: nx.Graph | str,
    cfg: CFG | str,
) -> set[tuple]:
    """
    Executes context free query to the given graph

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
    result = set()
    for production in cfg.productions:
        t = production.body[0]
        if isinstance(t, Epsilon):
            result |= {(v, production.head, v) for v in graph.nodes}
        if isinstance(t, Terminal):
            result |= {
                (u, production.head, v)
                for u, v, label in graph.edges(data="label")
                if label == t.value
            }

    m = result.copy()
    while m:
        v, ni, u = m.pop()
        for v_hat, nj in [(ut, nt) for ut, nt, vt in result if vt == v]:
            for nk in [p.head for p in cfg.productions if p.body == [nj, ni]]:
                new_triple = (v_hat, nk, u)
                if new_triple not in result:
                    m.add(new_triple)
                    result.add(new_triple)
        for v_hat, nj in [(vt, nt) for ut, nt, vt in result if ut == u]:
            for nk in [p.head for p in cfg.productions if p.body == [ni, nj]]:
                new_triple = (v, nk, v_hat)
                if (v_hat, nk, u) not in result:
                    m.add(new_triple)
                    result.add(new_triple)
    return result


def cf_query_to_graph(
    query: CFG,
    graph: nx.Graph,
    start_nonterminal: Variable,
    start_states: Iterable[int],
    final_states: Iterable[int],
) -> set[tuple]:
    return {
        (src, dst)
        for src, sym, dst in get_reachable_pairs_hellings(graph, query)
        if src in start_states and sym == start_nonterminal and dst in final_states
    }
