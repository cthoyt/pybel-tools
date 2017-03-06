"""

This module contains functions useful throughout PyBEL Tools

"""
import itertools as itt
from collections import Counter, defaultdict

from pandas import DataFrame

from pybel.constants import ANNOTATIONS, FUNCTION, PATHOLOGY


def count_defaultdict(dict_of_lists):
    """Takes a dictionary and applies a counter to each list

    :param dict_of_lists: A dictionary of lists
    :type dict_of_lists: dict
    :return: A dictionary of {key: Counter(values)}
    :rtype: dict
    """
    return {k: Counter(v) for k, v in dict_of_lists.items()}


def count_dict_values(dict_of_counters):
    """Counts the number of elements in each value (can be list, Counter, etc)

    :param dict_of_counters: A dictionary of things whose lengths can be measured (lists, Counters, dicts)
    :type dict_of_counters: dict
    :return: A dictionary with the same keys as the input but the count of the length of the values
    :rtype: dict
    """
    return {k: len(v) for k, v in dict_of_counters.items()}


def _check_has_data(d, sd, key):
    return sd in d and key in d[sd]


def check_has_annotation(data, key):
    """Checks that ANNOTATION is included in the data dictionary and that the key is also present

    :param data: The data dictionary from a BELGraph's edge
    :type data: dict
    :param key: An annotation key
    :param key: str
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
    return _check_has_data(data, ANNOTATIONS, key)


def keep_node_permissive(graph, node):
    """A default node filter that is true for all nodes

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param node: The node
    :type node: tuple
    :return: True
    :rtype: bool
    """
    return True


def keep_node(graph, node, super_nodes=None):
    """A default node filter for removing unwanted nodes in an analysis.

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


def calculate_tanimoto_set_distances(dict_of_sets):
    """Returns a distance matrix keyed by the keys in the given dict. Distances are calculated
    based on pairwise tanimoto similarity of the sets contained

    :param dict_of_sets: A dict of {x: set of y}
    :type dict_of_sets: dict
    :return: A distance matrix based on the set overlap (tanimoto) score between each x
    :rtype: pandas.DataFrame
    """
    result = defaultdict(dict)

    for x, y in itt.combinations(dict_of_sets, 2):
        result[x][y] = result[y][x] = len(dict_of_sets[x] & dict_of_sets[y]) / len(dict_of_sets[x] | dict_of_sets[y])

    for x in dict_of_sets:
        result[x][x] = 1

    return DataFrame.from_dict(result)


def calculate_global_tanimoto_set_distances(dict_of_sets):
    """Calculates an alternative distance matrix based on the following equation:

    .. math:: distance(A, B)=1- \|A \cup B\| / \| \cup_{s \in S} s\|

    :param dict_of_sets: A dict of {x: set of y}
    :type dict_of_sets: dict
    :return: A distance matrix based on the
    :rtype: pandas.DataFrame
    """
    universe = set(itt.chain.from_iterable(dict_of_sets.values()))
    universe_size = len(universe)

    result = defaultdict(dict)

    for x, y in itt.combinations(dict_of_sets, 2):
        result[x][y] = result[y][x] = 1 - len(dict_of_sets[x] | dict_of_sets[y]) / universe_size

    for x in dict_of_sets:
        result[x][x] = 1 - len(x) / len(universe)

    return DataFrame.from_dict(result)
