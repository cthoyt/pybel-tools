"""

This module contains functions to help select data from networks

"""
from collections import defaultdict

from pybel import BELGraph
from pybel.constants import ANNOTATIONS
from .utils import check_has_annotation


def group_subgraphs(graph, annotation):
    """Groups the nodes that occur in edges by the given annotation

    :param graph: A BEL graph
    :type graph: BELGraph
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


def get_subgraph_by_annotation(graph, key, value):
    """Builds a new subgraph induced over all edges whose annotations match the given key and value

    :param graph: A BEL Graph
    :type graph: BELGraph
    :param key: An annotation
    :type key: str
    :param value: The value for the annotation
    :type value: str
    :rtype: BELGraph
    """
    bg = BELGraph()

    for u, v, k, d in graph.edges_iter(keys=True, data=True):
        if not check_has_annotation(d, key):
            continue

        if d[ANNOTATIONS][key] == value:

            if u not in bg:
                bg.add_node(u, graph.node[u])

            if v not in bg:
                bg.add_node(v, graph.node[v])

            bg.add_edge(u, v, key=key, attr_dict=d)

    return bg


# TODO implement
def filter_edge_properties(edges, annotations_filter=None, relation=None):
    pass


# TODO implement
def filter_node_properties(edges, function_keep=None, namespace_keep=None, function_delete=None, namespace_delete=None):
    pass
