"""

These scripts are designed to assist in the analysis of errors within BEL documents
and provide some suggestions for fixes.

"""

import itertools as itt
from collections import Counter, defaultdict

import pandas as pd
from fuzzywuzzy import process, fuzz

from pybel import BELGraph
from pybel.constants import RELATION, FUNCTION, ANNOTATIONS, NAMESPACE, NAME
from pybel.parser.parse_exceptions import MissingNamespaceNameWarning, NakedNameWarning
from .utils import graph_content_transform, check_has_annotation, keep_node


# NODE HISTOGRAMS

def count_functions(graph):
    """Counts the frequency of each function present in a graph

    :param graph: A BEL graph
    :type graph: BELGraph
    :rtype: Counter
    """
    return Counter(data[FUNCTION] for _, data in graph.nodes_iter(data=True))


def count_namespaces(graph):
    """Counts the frequency of each namespace across all nodes (that have namespaces)

    :param graph: A BEL graph
    :type graph: BELGraph
    :rtype: Counter
    """
    return Counter(data[NAMESPACE] for _, data in graph.nodes_iter(data=True) if NAMESPACE in data)


def get_names(graph, namespace):
    """Get the set of all of the names in a given namespace that are in the graph

    :param graph: A BEL graph
    :type graph: BELGraph
    :param namespace: A namespace
    :type namespace: str
    :return: A set of names belonging to the given namespace that are in the given graph
    :rtype: set of str
    """

    return {data[NAME] for _, data in graph.nodes_iter(data=True) if NAMESPACE in data and data[NAMESPACE] == namespace}


# EDGE HISTOGRAMS

def count_relations(graph):
    """Returns a histogram over all relationships in a graph

    :param graph: A BEL graph
    :type graph: BELGraph
    :rtype: Counter
    """
    return Counter(d[RELATION] for _, _, d in graph.edges_iter(data=True))


def count_unique_relations(graph):
    """Returns a histogram of the different types of relations present in a graph.

    Note: this operation only counts each type of edge once for each pair of nodes

    :param graph: A BEL graph
    :type graph: BELGraph
    :rtype: Counter
    """
    return Counter(itt.chain.from_iterable(graph_content_transform(graph).values()))


def count_annotations(graph):
    """Counts how many times each annotation is used in the graph

    :param graph: A BEL graph
    :type graph: BELGraph
    :rtype: Counter
    """
    return Counter(key for _, _, d in graph.edges_iter(data=True) if ANNOTATIONS in d for key in d[ANNOTATIONS])


def count_annotation_instances(graph, key):
    """Counts in how many edges each annotation appears in a graph

    :param graph: A BEL graph
    :type graph: BELGraph
    :param key: An annotation to count
    :type key: str
    :rtype: Counter
    """
    return Counter(d[ANNOTATIONS][key] for _, _, d in graph.edges_iter(data=True) if check_has_annotation(d, key))


def count_annotation_instances_filtered(graph, key, source_filter=None, target_filter=None):
    """Counts in how many edges each annotation appears in a graph, but filter out source nodes and target nodes

    Default filters get rid of PATHOLOGY nodes. These functions take graph, node as arguments.

    :param graph: A BEL graph
    :type graph: BELGraph
    :param key: An annotation to count
    :type key: str
    :rtype: Counter
    """
    source_filter = keep_node if source_filter is None else source_filter
    target_filter = keep_node if target_filter is None else target_filter

    return Counter(d[ANNOTATIONS][key] for u, v, d in graph.edges_iter(data=True) if
                   check_has_annotation(d, key) and source_filter(graph, u) and target_filter(graph, v))


# ERROR HISTOGRAMS

def count_error_types(graph):
    """Counts the occurrence of each type of error in a graph

    :param graph: A BEL graph
    :type graph: BELGraph
    :rtype: Counter
    """
    return Counter(e.__class__.__name__ for _, _, e, _ in graph.warnings)


def count_naked_names(graph):
    """Counts the frequency of each naked name (names without namespaces)

    :param graph: A BEL graph
    :type graph: BELGraph
    :rtype: Counter
    """
    return Counter(e.name for _, _, e, _ in graph.warnings if isinstance(e, NakedNameWarning))


def calculate_incorrect_name_dict(graph):
    """Groups all of the incorrect identifiers in a dict of {namespace: list of wrong names}

    :param graph: A BEL graph
    :type graph: BELGraph
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
    :param namespace_dict: A dictinary of {namespace: list of allowed names}
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

    :param graph:
    :type graph: BELGraph
    :param annotation:
    :type annotation: str
    :return:
    :rtype: dict
    """
    results = defaultdict(list)

    for line_number, line, e, context in graph.warnings:
        if not context or annotation not in context:
            continue

        values = context[annotation]

        if isinstance(values, str):
            results[values].append(e.__class__.__name__)
        elif isinstance(values, (set, tuple, list)):
            for value in values:
                results[value].append(e.__class__.__name__)

    return results


# Visualization with Matplotlib

def plot_summary(graph, plt, figsize=(11, 4), **kwargs):
    """Plots your graph summary statistics. After, you need to run :code:`plt.show()`.

    1. Count of nodes, grouped by function type
    2. Count of edges, grouped by relation type

    :param graph: A BEL graph
    :type graph: BELGraph
    :param plt: Give :code:`matplotlib.pyplot` to this parameter
    """
    fig, axes = plt.subplots(1, 2, figsize=figsize, **kwargs)

    ntc = count_functions(graph)
    etc = count_relations(graph)

    df = pd.DataFrame.from_dict(ntc, orient='index')
    df_ec = pd.DataFrame.from_dict(etc, orient='index')

    df.sort_values(0, ascending=True).plot(kind='barh', logx=True, ax=axes[0])
    axes[0].set_title('Number Nodes: {}'.format(graph.number_of_nodes()))

    df_ec.sort_values(0, ascending=True).plot(kind='barh', logx=True, ax=axes[1])
    axes[1].set_title('Number Edges: {}'.format(graph.number_of_edges()))

    plt.tight_layout()
