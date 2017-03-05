"""

This module contains functions useful throughout PyBEL Tools

"""

from collections import Counter

from pybel.constants import ANNOTATIONS, FUNCTION, PATHOLOGY


def count_defaultdict(d):
    """Takes a defaultdict(list) and applys a counter to each list

    :param d: A dictionary of lists
    :type d: defaultdict(list)
    :return: A dictionary of {key: Counter(values)}
    :rtype: dict
    """
    return {k: Counter(v) for k, v in d.items()}


def count_dict_values(dict_of_counters):
    """Counts the number of elements in each value (can be list, Counter, etc)

    :param d: A dictionary of lists
    :type d: defaultdict(list)
    :rtype: dict
    """
    return {k: len(v) for k, v in dict_of_counters.items()}


def _check_has_data(d, sd, key):
    return sd in d and key in d[sd]


def check_has_annotation(d, key):
    """Checks that ANNOTATION is included in the data dictionary and that the key is also present

    :param d: The data dictionary from a BELGraph's edge
    :param key: An annotation key
    :return: If the annotation key is present in the current data dictionary
    :rtype: bool

    For example, it might be useful to print all edges that are annotated with 'Subgraph':

    >>> from pybel import BELGraph
    >>> graph = BELGraph()
    >>> ...
    >>> for u, v, data in graph.edges_iter(data=True):
    >>>     if not check_has_annotation(data, 'Subgraph')
    >>>         continue
    >>>     print(u, v, data)
    """
    return _check_has_data(d, ANNOTATIONS, key)


def keep_node(graph, node, super_nodes=None):
    """A default function for filtering out unwanted nodes in an analysis.

    This function returns false for nodes that have PATHOLOGY or are on a pre-defined blacklist. This can be most
    easily used with :py:func:`functools.partial`:

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param node: The node to check if it should be kepy
    :type node: tuple
    :param super_nodes: A list of nodes to automatically throw out
    :type super_nodes: list of tuples
    :return: Should the node be kept?
    :rtype: bool


    >>> from functools import partial
    >>> from pybel.constants import GENE
    >>> from pybel_tools.utils import keep_node
    >>> cool_filter = partial(keep_node, super_nodes={(GENE, 'HGNC', 'APP')})
    """

    if graph.node[node][FUNCTION] == PATHOLOGY:
        return False

    if super_nodes and node in super_nodes:
        return False

    return True
