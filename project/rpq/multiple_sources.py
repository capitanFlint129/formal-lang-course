from typing import Optional, Any, Collection

from pyformlang.regular_expression import Regex
from scipy.sparse import block_diag
import networkx as nx

from project import automata
from project.rpq.all_pairs import enumerate_states
from project.boolean_decomposition import *


def multiple_sources_reachability_with_regular_constraints(
    query_boolean_decomposition: dict[Any, dok_matrix[bool]],
    graph_boolean_decomposition: dict[Any, dok_matrix[bool]],
    graph_sources: list[int],
    query_start_states: Collection[int],
    query_final_states: Collection[int],
    for_each_vertex: Optional[bool] = False,
) -> list:
    """
    Finds all vertices of graph which reachable from sources and
    corresponds with query graph using matrix bfs algorithm

    Parameters
    ----------
    query_boolean_decomposition :
        Boolean decomposition of regular query
    graph_boolean_decomposition :
        Boolean decomposition of graph
    graph_sources :
        Start vertices of graph
    query_start_states :
        Start states of query finite automata
    query_final_states :
        Final states of query finite automata
    for_each_vertex :
        If True then return pairs of start and final vertices


    Returns
    ----------
    result :
        List of final vertices that reachable from start (if for_each_vertex is False)

        List of pairs from the given source vertices and vertices reachable from them
        (if for_each_vertex is True)
    """
    if len(graph_boolean_decomposition) == 0 or len(query_boolean_decomposition) == 0:
        return []
    graph_vertices_number = next(iter(graph_boolean_decomposition.values())).shape[0]
    query_vertices_number = next(iter(query_boolean_decomposition.values())).shape[0]
    block_diagonal_boolean_decomposition = {}
    for symbol, query_matrix in query_boolean_decomposition.items():
        if symbol in graph_boolean_decomposition:
            block_diagonal_boolean_decomposition[symbol] = block_diag(
                [
                    query_matrix,
                    graph_boolean_decomposition[symbol],
                ]
            )
    sources_order = {source: i for i, source in enumerate(graph_sources)}
    if for_each_vertex:
        M = dok_matrix(
            tuple(
                [
                    query_vertices_number * len(graph_sources),
                    query_vertices_number + graph_vertices_number,
                ]
            ),
            dtype=bool,
        )
        for source in graph_sources:
            for i in range(query_vertices_number):
                M[sources_order[source] * query_vertices_number + i, i] = True
            for state in query_start_states:
                M[
                    sources_order[source] * query_vertices_number + state,
                    query_vertices_number + source,
                ] = True
    else:
        M = dok_matrix(
            tuple(
                [query_vertices_number, query_vertices_number + graph_vertices_number]
            ),
            dtype=bool,
        )
        for i in range(query_vertices_number):
            M[i, i] = True
        for state in query_start_states:
            for source in graph_sources:
                M[state, query_vertices_number + source] = True

    result = set()
    M_new = dok_matrix(M.shape, dtype=bool)
    while True:
        for symbol, matrix in block_diagonal_boolean_decomposition.items():
            M_new += _transform_rows(M @ matrix, query_vertices_number)
        if for_each_vertex:
            for j in range(len(graph_sources)):
                result |= set(
                    [
                        (graph_sources[j], indexes_pair[1])
                        for indexes_pair, value in M_new[
                            [
                                index + j * query_vertices_number
                                for index in query_final_states
                            ],
                            query_vertices_number:,
                        ].items()
                        if indexes_pair[1] not in sources_order and value
                    ]
                )
        else:
            result |= set(
                [
                    indexes_pair[1]
                    for indexes_pair, value in M_new[
                        query_final_states, query_vertices_number:
                    ].items()
                    if indexes_pair[1] not in sources_order and value
                ]
            )
        if (M != M_new).nnz == 0:
            break
        M = M_new
    return list(result)


def _transform_rows(
    matrix: dok_matrix[bool], query_vertices_number: Optional[int] = None
) -> dok_matrix[bool]:
    """
    Swaps rows of matrix to get ones on main diagonal for each source vertex.
    The elements must be such that the leftmost square
    sub-matrix becomes identity matrix
    """
    if query_vertices_number is None:
        query_vertices_number = matrix.shape[0]

    result = matrix.tocsr()
    for j in range(0, matrix.shape[0], query_vertices_number):
        end_index = j + query_vertices_number
        i = j
        while i < end_index:
            if result[i].max() == False:
                i += 1
            else:
                index_of_first_true = result[i].argmax()
                row_index = index_of_first_true + j
                if row_index >= end_index:
                    result[i, :] = 0
                    i += 1
                elif index_of_first_true != i % query_vertices_number:
                    if (
                        result[row_index].argmax() == index_of_first_true
                        and result[row_index].max() == True
                    ):
                        result[i] += result[row_index]
                        result[row_index] = 0
                        i += 1
                    else:
                        result[i], result[row_index] = (
                            result[row_index],
                            result[i],
                        )
                else:
                    i += 1

    return result.todok()


def multiple_sources_regular_query_for_graph(
    query: Regex,
    graph: nx.Graph,
    start_states: Optional[Iterable] = None,
    final_states: Optional[Iterable] = None,
    for_each_vertex: Optional[bool] = False,
) -> list:
    """
    Executes regular query to the given graph with given start and final vertices
    using matrix bfs algorithm

    Parameters
    ----------
    query :
        Regular expression of query
    graph :
        The graph on which the request is executed
    start_states :
        Graph vertices that interpreted as start if None then all vertices are start
    final_states :
        Graph vertices that interpreted as final if None then all vertices are final
    for_each_vertex :
        If True then return pairs of start and final vertices

    Returns
    ----------
    result :
        List of final vertices that reachable from start and forms a word from the
        language specified by the regular expression of query (if for_each_vertex is False)

        List of pairs from the given start and final states that are connected by a path
        that forms a word from the language specified by the regular expression of query
        (if for_each_vertex is True)
    """

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

    result = multiple_sources_reachability_with_regular_constraints(
        query_boolean_decomposition,
        graph_boolean_decomposition,
        [states_order_graph_fa[state] for state in graph_fa.start_states],
        [states_order_query_fa[state] for state in query_fa.start_states],
        [states_order_query_fa[state] for state in query_fa.final_states],
        for_each_vertex,
    )
    if for_each_vertex:
        result = [pair for pair in result if pair[1] in set(final_states)]
    else:
        result = list(set(result).intersection(set(final_states)))
    return result
