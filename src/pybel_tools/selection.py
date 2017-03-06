"""

This module contains functions to help select data from networks

"""
import logging
import os
from collections import defaultdict
from itertools import combinations

from pybel import BELGraph, to_pickle
from pybel.constants import ANNOTATIONS
from .summary import count_annotation_instances
from .utils import check_has_annotation

log = logging.getLogger(__name__)


def group_subgraphs(graph, annotation):
    """Groups the nodes that occur in edges by the given annotation

    :param graph: A BEL graph
    :type graph: pybel.BELGraph
    :param annotation: An annotation to use to group edges
    :type annotation: str
    :return: dict of sets of BELGraph nodes
    """
    result = defaultdict(set)

    for u, v, d in graph.edges_iter(data=True):

        if not check_has_annotation(d, annotation):
            continue

        result[d[ANNOTATIONS][annotation]].add(u)
        result[d[ANNOTATIONS][annotation]].add(v)

    return result


def get_subgraph_by_annotation(graph, annotation, value):
    """Builds a new subgraph induced over all edges whose annotations match the given key and value

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param annotation: An annotation
    :type annotation: str
    :param value: The value for the annotation
    :type value: str
    :rtype: BELGraph
    """
    bg = BELGraph()

    for u, v, key, attr_dict in graph.edges_iter(keys=True, data=True):
        if not check_has_annotation(attr_dict, annotation):
            continue

        if attr_dict[ANNOTATIONS][annotation] == value:

            if u not in bg:
                bg.add_node(u, graph.node[u])

            if v not in bg:
                bg.add_node(v, graph.node[v])

            bg.add_edge(u, v, key=key, attr_dict=attr_dict)

    return bg


def subgraphs_to_pickles(graph, annotation, directory):
    """Groups the given graph into subgraphs by the given annotation with :func:`group_subgraphs` and outputs them
    as gpickle files to the given directory with :func:`pybel.to_pickle`

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param annotation: An annotation to split by. Suggestion: 'Subgraph'
    :type annotation: str
    :param directory: A directory to output the pickles
    """
    c = count_annotation_instances(graph, annotation)

    for value in c:
        sg = get_subgraph_by_annotation(graph, annotation, value)
        sg.document.update(graph.document)

        file_name = '{}_{}.gpickle'.format(annotation, value.replace(' ', '_'))
        path = os.path.join(directory, file_name)
        to_pickle(sg, path)


def get_triangles(graph, node):
    """Yields all triangles pointed by the given node

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param node: The source node
    :type node: tuple
    """
    for a, b in combinations(graph.edge[node], 2):
        if graph.edge[a][b]:
            yield a, b
        if graph.edge[b][a]:
            yield b, a


def filter_graph(graph, expand_nodes=None, remove_nodes=None, **kwargs):
    """Queries graph's edges with multiple filters

    Order of operations:
    1. Match by annotations
    2. Add nodes
    3. Remove nodes

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param expand_nodes: Add the neighborhoods around all of these nodes
    :type expand_nodes: list
    :param remove_nodes: Remove these nodes and all of their in/out edges
    :type remove_nodes: list
    :param kwargs: Annotation filters (match all with :func:`pybel.utils.subdict_matches`)
    :type kwargs: dict
    :return: A BEL Graph
    :rtype: BELGraph
    """

    expand_nodes = [] if expand_nodes is None else expand_nodes
    remove_nodes = [] if remove_nodes is None else remove_nodes

    result_graph = BELGraph()

    for u, v, k, d in graph.edges_iter(keys=True, data=True, **{ANNOTATIONS: kwargs}):
        result_graph.add_edge(u, v, key=k, attr_dict=d)

    for node in result_graph.nodes_iter():
        result_graph.node[node] = graph.node[node]

    for node in expand_nodes:
        expand_graph_around_node(result_graph, graph, node)

    for node in remove_nodes:
        if node not in result_graph:
            log.warning('%s is not in graph %s', node, graph.name)
            continue

        result_graph.remove_node(node)

    return result_graph


def expand_graph_around_node(graph, query_graph, node):
    """Expands around the neighborhoods of the given nodes in the result graph by looking at the original_graph,
    in place.

    :param graph: The graph to add stuff to
    :type graph: pybel.BELGraph
    :param query_graph: The graph containing the stuff to add
    :type query_graph: pybel.BELGraph
    :param node: A node tuples from the query graph
    :type node: tuple
    """
    if node not in query_graph:
        raise ValueError('{} not in graph {}'.format(node, graph.name))

    if node not in graph:
        graph.add_node(node, attr_dict=query_graph.node[node])

    skip_predecessors = set()
    for predecessor in query_graph.predecessors_iter(node):
        if predecessor in graph:
            skip_predecessors.add(predecessor)
            continue
        graph.add_node(predecessor, attr_dict=query_graph.node[node])

    for predecessor, _, k, d in query_graph.in_edges_iter(node, data=True, keys=True):
        if predecessor in skip_predecessors:
            continue

        if k < 0:
            graph.add_edge(predecessor, node, key=k, attr_dict=d)
        else:
            graph.add_edge(predecessor, node, attr_dict=d)

    skip_successors = set()
    for successor in query_graph.successors_iter(node):
        if successor in graph:
            skip_successors.add(successor)
            continue
        graph.add_node(successor, attr_dict=query_graph.node[node])

    for _, successor, k, d in query_graph.out_edges_iter(node, data=True, keys=True):
        if successor in skip_successors:
            continue

        if k < 0:
            graph.add_edge(node, successor, key=k, attr_dict=d)
        else:
            graph.add_edge(node, successor, attr_dict=d)
