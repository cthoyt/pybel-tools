"""

These scripts are designed to assist in the analysis of errors within BEL documents
and provide some suggestions for fixes.

"""

import itertools as itt
from collections import Counter, defaultdict

import pandas as pd
from fuzzywuzzy import process, fuzz

from pybel.constants import *
from pybel.parser.parse_exceptions import MissingNamespaceNameWarning, NakedNameWarning
from .utils import check_has_annotation, keep_node_permissive


# NODE HISTOGRAMS

def count_functions(graph):
    """Counts the frequency of each function present in a graph

    :param graph: A BEL graph
    :type graph: pybel.BELGraph
    :rtype: Counter
    """
    return Counter(data[FUNCTION] for _, data in graph.nodes_iter(data=True))


def count_namespaces(graph):
    """Counts the frequency of each namespace across all nodes (that have namespaces)

    :param graph: A BEL graph
    :type graph: pybel.BELGraph
    :rtype: Counter
    """
    return Counter(data[NAMESPACE] for _, data in graph.nodes_iter(data=True) if NAMESPACE in data)


def get_names(graph, namespace):
    """Get the set of all of the names in a given namespace that are in the graph

    :param graph: A BEL graph
    :type graph: pybel.BELGraph
    :param namespace: A namespace
    :type namespace: str
    :return: A set of names belonging to the given namespace that are in the given graph
    :rtype: set of str
    """

    return {data[NAME] for _, data in graph.nodes_iter(data=True) if NAMESPACE in data and data[NAMESPACE] == namespace}


def get_unique_names(graph):
    """Get a dictionary of {namespace: set of names} present in the graph

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :return: A dictionary of {namespace: set of names}
    :rtype: dict
    """
    result = defaultdict(set)

    for node, data in graph.nodes_iter(data=True):
        if NAMESPACE in data:
            result[data[NAMESPACE]].add(data[NAME])

    return result


def has_causal_out_edges(graph, node):
    """Gets if the node has causal out edges

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param node: A node
    :type node: tuple
    :return: If the node has causal out edges
    :rtype: bool
    """
    return any(d[RELATION] in CAUSAL_RELATIONS for _, _, d in graph.out_edges_iter(node, data=True))


def has_causal_in_edges(graph, node):
    """Gets if the node has causal in edges

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param node: A node
    :type node: tuple
    :return: If the node has causal in edges
    :rtype: bool
    """
    return any(d[RELATION] in CAUSAL_RELATIONS for _, _, d in graph.in_edges_iter(node, data=True))


def get_causal_out_edges(graph, node):
    """Gets the out-edges to the given node that are causal

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param node: A node
    :type node: tuple
    :return:
    :rtype: set
    """

    return {(u, v) for u, v, d in graph.out_edges_iter(node, data=True) if d[RELATION] in CAUSAL_RELATIONS}


def get_causal_in_edges(graph, node):
    """Gets the in-edges to the given node that are causal

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param node: A node
    :type node: tuple
    :return:
    :rtype: set
    """
    return {(u, v) for u, v, d in graph.in_edges_iter(node, data=True) if d[RELATION] in CAUSAL_RELATIONS}


# TODO only count over causal edges
def get_source_abundances(graph):
    """Returns a set of all ABUNDANCE nodes that have an in-degree of 0, which likely means that it is an external
    perterbagen and is not known to have any causal origin from within the biological system.

    These nodes are useful to identify because they generally don't provide any mechanistic insight.

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :return: A set of source ABUNDANCE nodes
    :rtype: set
    """
    return {n for n, d in graph.nodes_iter(data=True) if
            d[FUNCTION] == ABUNDANCE and not has_causal_in_edges(graph, n) and has_causal_out_edges(graph, n)}


def get_central_abundances(graph):
    """Returns a set of all ABUNDANCE nodes that have both an in-degree > 0 and out-degree > 0. This means
    that they are an integral part of a pathway, since they are both produced and consumed.

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :return: A set of central ABUNDANCE nodes
    :rtype: set
    """
    result = set()

    for n, d in graph.nodes_iter(data=True):
        if d[FUNCTION] == ABUNDANCE and has_causal_in_edges(graph, n) and has_causal_out_edges(graph, n):
            result.add(n)

    return result


def get_sink_abundances(graph):
    """Returns a set of all ABUNDANCE nodes that have an causal out-degree of 0, which likely means that the knowledge
    assembly is incomplete, or there is a curation error.

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :return: A set of sink ABUNDANCE nodes
    :rtype: set
    """
    return {n for n, d in graph.nodes_iter(data=True) if
            d[FUNCTION] == ABUNDANCE and not has_causal_out_edges(graph, n) and has_causal_in_edges(graph, n)}


# EDGE HISTOGRAMS

def count_relations(graph):
    """Returns a histogram over all relationships in a graph

    :param graph: A BEL graph
    :type graph: pybel.BELGraph
    :rtype: Counter
    """
    return Counter(d[RELATION] for _, _, d in graph.edges_iter(data=True))


def get_edge_relations(graph):
    """Builds a dictionary of {node pair: set of edge types}

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :return: A dictionary of {(node, node): set of edge types}
    :rtype: dict
    """
    edge_relations = defaultdict(set)
    for u, v, d in graph.edges_iter(data=True):
        edge_relations[u, v].add(d[RELATION])
    return edge_relations


def count_unique_relations(graph):
    """Returns a histogram of the different types of relations present in a graph.

    Note: this operation only counts each type of edge once for each pair of nodes

    :param graph: A BEL graph
    :type graph: pybel.BELGraph
    :rtype: Counter
    """
    return Counter(itt.chain.from_iterable(get_edge_relations(graph).values()))


def count_annotations(graph):
    """Counts how many times each annotation is used in the graph

    :param graph: A BEL graph
    :type graph: pybel.BELGraph
    :rtype: Counter
    """
    return Counter(key for _, _, d in graph.edges_iter(data=True) if ANNOTATIONS in d for key in d[ANNOTATIONS])


def count_annotation_instances(graph, annotation):
    """Counts in how many edges each annotation appears in a graph

    :param graph: A BEL graph
    :type graph: pybel.BELGraph
    :param annotation: An annotation to count
    :type annotation: str
    :rtype: Counter
    """
    return Counter(
        d[ANNOTATIONS][annotation] for _, _, d in graph.edges_iter(data=True) if check_has_annotation(d, annotation))


def count_annotation_instances_filtered(graph, annotation, source_filter=None, target_filter=None):
    """Counts in how many edges each annotation appears in a graph, but filter out source nodes and target nodes

    See :func:`pybel_tools.utils.keep_node` for a basic filter.

    :param graph: A BEL graph
    :type graph: pybel.BELGraph
    :param annotation: An annotation to count
    :type annotation: str
    :param source_filter: a predicate (graph, node) -> bool for keeping source nodes
    :type source_filter: lambda
    :param target_filter: a predicate (graph, node) -> bool for keeping target nodes
    :type target_filter: lambda
    :rtype: Counter
    """
    source_filter = keep_node_permissive if source_filter is None else source_filter
    target_filter = keep_node_permissive if target_filter is None else target_filter

    return Counter(d[ANNOTATIONS][annotation] for u, v, d in graph.edges_iter(data=True) if
                   check_has_annotation(d, annotation) and source_filter(graph, u) and target_filter(graph, v))


def get_unique_annotations(graph):
    """Gets the annotations used in a BEL Graph

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :return: Dictionary of {annotation: set of values}
    :rtype: dict
    """
    result = defaultdict(set)

    for _, _, data in graph.edges_iter(data=True):
        for key, value in data[ANNOTATIONS].items():
            result[key].add(value)

    return result


# ERROR HISTOGRAMS

def count_error_types(graph):
    """Counts the occurrence of each type of error in a graph

    :param graph: A BEL graph
    :type graph: pybel.BELGraph
    :rtype: Counter
    """
    return Counter(e.__class__.__name__ for _, _, e, _ in graph.warnings)


def count_naked_names(graph):
    """Counts the frequency of each naked name (names without namespaces)

    :param graph: A BEL graph
    :type graph: pybel.BELGraph
    :rtype: Counter
    """
    return Counter(e.name for _, _, e, _ in graph.warnings if isinstance(e, NakedNameWarning))


def calculate_incorrect_name_dict(graph):
    """Groups all of the incorrect identifiers in a dict of {namespace: list of wrong names}

    :param graph: A BEL graph
    :type graph: pybel.BELGraph
    :rtype: dict
    """
    missing = defaultdict(list)

    for line_number, line, e, ctx in graph.warnings:
        if not isinstance(e, MissingNamespaceNameWarning):
            continue
        missing[e.namespace].append(e.name)

    return missing


def calculate_suggestions(incorrect_name_dict, namespace_dict):
    """Uses fuzzy string matching to try and find the appropriate names for each of the incorrectly identified names

    :param incorrect_name_dict: A dictionary of {namespace: list of wrong names}
    :type incorrect_name_dict: dict
    :param namespace_dict: A dictionary of {namespace: list of allowed names}
    :type namespace_dict: dict
    :return: A dictionary of suggestions for each wrong namespace, name pair
    :rtype: dict
    """
    suggestions_cache = defaultdict(list)

    for namespace in incorrect_name_dict:
        for name in incorrect_name_dict[namespace]:
            if (namespace, name) in suggestions_cache:
                continue

            for putative, score in process.extract(name, set(namespace_dict[namespace]),
                                                   scorer=fuzz.partial_token_set_ratio):
                suggestions_cache[namespace, name].append((putative, score))

    return suggestions_cache


def calculate_error_by_annotation(graph, annotation):
    """Groups the graph by a given annotation and builds lists of errors for each

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param annotation: The annotation to group errors by
    :type annotation: str
    :return:
    :rtype: dict
    """
    results = defaultdict(list)

    for line_number, line, e, context in graph.warnings:
        if not context or not check_has_annotation(context, annotation):
            continue

        values = context[ANNOTATIONS][annotation]

        if isinstance(values, str):
            results[values].append(e.__class__.__name__)
        elif isinstance(values, (set, tuple, list)):
            for value in values:
                results[value].append(e.__class__.__name__)

    return results


def calculate_subgraph_overlap(graph, annotation='Subgraph'):
    """Builds a dataframe to show the overlap between different subgraphs

    Options:
    1. Total number of edges overlap (intersection)
    2. Percentage overlap (tanimoto similarity)


    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param annotation: The annotation to group by and compare. Defaults to 'Subgraph'
    :type annotation: str
    :return: {subgraph: set of edges}, {(subgraph 1, subgraph2): set of intersecting edges},
            {(subgraph 1, subgraph2): set of unioned edges}, {(subgraph 1, subgraph2): tanimoto similarity},
    """

    sg2edge = defaultdict(set)

    for u, v, d in graph.edges_iter(data=True):
        if not check_has_annotation(d, annotation):
            continue
        sg2edge[d[ANNOTATIONS][annotation]].add((u, v))

    subgraph_intersection = {}
    subgraph_union = {}
    subgraph_overlap = {}

    for sg1, sg2 in itt.combinations(sorted(sg2edge), 2):
        subgraph_intersection[sg1, sg2] = sg2edge[sg1] & sg2edge[sg2]
        subgraph_union[sg1, sg2] = sg2edge[sg1] | sg2edge[sg2]
        subgraph_overlap[sg1, sg2] = len(subgraph_intersection[sg1, sg2]) / len(subgraph_union[sg1, sg2])

    return sg2edge, subgraph_intersection, subgraph_union, subgraph_overlap


def summarize_subgraph_overlap(graph, annotation='Subgraph'):
    """Returns a distance matrix between all subgraphs (or other given annotation)

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param annotation: The annotation to group by and compare. Defaults to :code:`"Subgraph"`
    :type annotation: str
    :return: A similarity matrix in a pandas dataframe
    :rtype: pd.DataFrame
    """
    sg2edge, subgraph_intersection, subgraph_union, subgraph_overlap = calculate_subgraph_overlap(graph, annotation)
    labels = sorted(sg2edge)
    mat = []
    for sg1 in labels:
        row = []
        for sg2 in labels:
            if sg1 == sg2:
                row.append(1)
            elif (sg1, sg2) in subgraph_overlap:
                row.append(subgraph_overlap[sg1, sg2])
            elif (sg2, sg1) in subgraph_overlap:
                row.append(subgraph_overlap[sg2, sg1])
        mat.append(row)
    return pd.DataFrame(mat, index=labels, columns=labels)


# Visualization with matplotlib

def plot_summary_axes(graph, lax, rax):
    """Plots your graph summary statistics on the given axes.

    After, you should run :code:`plt.tight_layout()` and you must run :code:`plt.show()` to view.

    Shows:
    1. Count of nodes, grouped by function type
    2. Count of edges, grouped by relation type

    :param graph: A BEL graph
    :type graph: pybel.BELGraph
    :param lax: An axis object from matplotlib
    :param rax: An axis object from matplotlib

    Example usage:

    >>> import matplotlib.pyplot as plt
    >>> from pybel import from_pickle
    >>> from pybel_tools.summary import plot_summary_axes
    >>> graph = from_pickle('~/dev/bms/aetionomy/parkinsons.gpickle')
    >>> fig, axes = plt.subplots(1, 2, figsize=(16, 4))
    >>> plot_summary_axes(graph, axes[0], axes[1])
    >>> plt.tight_layout()
    >>> plt.show()
    """

    ntc = count_functions(graph)
    etc = count_relations(graph)

    df = pd.DataFrame.from_dict(ntc, orient='index')
    df_ec = pd.DataFrame.from_dict(etc, orient='index')

    df.sort_values(0, ascending=True).plot(kind='barh', logx=True, ax=lax)
    lax.set_title('Number Nodes: {}'.format(graph.number_of_nodes()))

    df_ec.sort_values(0, ascending=True).plot(kind='barh', logx=True, ax=rax)
    rax.set_title('Number Edges: {}'.format(graph.number_of_edges()))


def plot_summary(graph, plt, figsize=(11, 4), **kwargs):
    """Plots your graph summary statistics. This function is a thin wrapper around :code:`plot_summary_axis`. It
    automatically takes care of building figures given matplotlib's pyplot module as an argument. After, you need
    to run :code:`plt.show()`.

    :code:`plt` is given as an argument to avoid needing matplotlib as a dependency for this function

    Shows:

    1. Count of nodes, grouped by function type
    2. Count of edges, grouped by relation type

    :param graph: A BEL graph
    :type graph: pybel.BELGraph
    :param plt: Give :code:`matplotlib.pyplot` to this parameter

    Example usage:

    >>> import matplotlib.pyplot as plt
    >>> from pybel import from_pickle
    >>> from pybel_tools.summary import plot_summary
    >>> graph = from_pickle('~/dev/bms/aetionomy/parkinsons.gpickle')
    >>> plot_summary(graph, plt, figsize=(16, 4))
    >>> plt.show()

    """
    fig, axes = plt.subplots(1, 2, figsize=figsize, **kwargs)
    lax = axes[0]
    rax = axes[1]

    plot_summary_axes(graph, lax, rax)
    plt.tight_layout()
