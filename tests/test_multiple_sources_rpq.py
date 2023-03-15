from pyformlang.finite_automaton import State

from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, Symbol
from pyformlang.regular_expression import Regex

from project import all_pairs_rpq, grapth_utils, automata

from collections import defaultdict
from typing import Iterable, Optional, Union, Any, Sized, Collection
import math

import numpy as np
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, Symbol, State
from pyformlang.regular_expression import Regex
from scipy.sparse import dok_matrix, csr_matrix, kron, block_diag, coo_matrix
import networkx as nx
import pytest
from project import automata, multiple_sources_rpq
from project.all_pairs_rpq import enumerate_states
from project.boolean_decomposition import *


@pytest.mark.parametrize(
    "for_each_vertex, query, expected",
    [
        (False, Regex("a"), [0]),
        (False, Regex("a*"), [0]),
        (False, Regex("a b"), [4]),
        (False, Regex("a* b*"), [0, 4, 5, 6]),
        (False, Regex("a b b"), [5]),
        (True, Regex("a"), [(3, 0)]),
        (True, Regex("a*"), [(3, 0), (2, 0), (1, 0)]),
        (True, Regex("a b"), [(3, 4)]),
        (True, Regex("a* b*"), [(i, j) for i in [1, 2, 3] for j in [4, 5, 6, 0]]),
        (True, Regex("a b b"), [(3, 5)]),
    ],
)
def test_multiple_sources_reachability_with_regular_constraints(
    for_each_vertex, query, expected
):
    graph = grapth_utils.create_two_cycles_graph(
        3,
        3,
        (
            "a",
            "b",
        ),
    )
    start_states = [1, 2, 3]
    final_states = [4, 5, 6]
    query_fa = automata.get_deterministic_automata_from_regex(query)
    graph_fa = automata.get_nondeterministic_automata_from_graph(
        graph, start_states, final_states
    )
    states_order_query_fa = enumerate_states(query_fa)
    states_order_graph_fa = enumerate_states(graph_fa)
    query_boolean_decomposition = get_boolean_decomposition_of_fa(
        query_fa, states_order_query_fa
    )
    graph_boolean_decomposition = get_boolean_decomposition_of_fa(
        graph_fa, states_order_graph_fa
    )
    result = (
        multiple_sources_rpq.multiple_sources_reachability_with_regular_constraints(
            query_boolean_decomposition,
            graph_boolean_decomposition,
            [states_order_graph_fa[state] for state in graph_fa.start_states],
            [states_order_query_fa[state] for state in query_fa.start_states],
            [states_order_query_fa[state] for state in query_fa.final_states],
            for_each_vertex,
        )
    )
    assert set(result) == set(expected)


@pytest.mark.parametrize(
    "for_each_vertex, query, expected",
    [
        (False, Regex("a"), []),
        (False, Regex("a*"), []),
        (False, Regex("a b"), [4]),
        (False, Regex("a* b*"), [4, 5, 6]),
        (False, Regex("a b b"), [5]),
        (True, Regex("a"), []),
        (True, Regex("a*"), []),
        (True, Regex("a b"), [(3, 4)]),
        (True, Regex("a* b*"), [(i, j) for i in [1, 2, 3] for j in [4, 5, 6]]),
        (True, Regex("a b b"), [(3, 5)]),
    ],
)
def test_multiple_sources_regular_query_for_graph(for_each_vertex, query, expected):
    graph = grapth_utils.create_two_cycles_graph(
        3,
        3,
        (
            "a",
            "b",
        ),
    )
    start_states = [1, 2, 3]
    final_states = [4, 5, 6]
    result = multiple_sources_rpq.multiple_sources_regular_query_for_graph(
        query,
        graph,
        start_states,
        final_states,
        for_each_vertex,
    )
    assert set(result) == set(expected)
