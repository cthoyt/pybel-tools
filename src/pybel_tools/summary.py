"""

These scripts are designed to assist in the analysis of errors within BEL documents
and provide some suggestions for fixes.

"""

from collections import Counter, defaultdict

import pandas as pd
from fuzzywuzzy import process, fuzz

from pybel import BELGraph
from pybel.constants import RELATION, FUNCTION, ANNOTATIONS, NAMESPACE
from pybel.parser.parse_exceptions import MissingNamespaceNameWarning, NakedNameWarning
from .utils import graph_content_transform


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
    return Counter(relation for _, relations in graph_content_transform(graph).items() for relation in relations)


def count_annotations(graph):
    """Counts how many times each annotation is used in the graph

    :param graph: A BEL graph
    :type graph: BELGraph
    :rtype: Counter
    """
    return Counter(key for _, _, d in graph.edges_iter(data=True) for key in d[ANNOTATIONS])


def count_annotation_instances(graph, key):
    """Counts in how many edges each annotation appears in a graph

    :param graph: A BEL graph
    :type graph: BELGraph
    :param key: An annotation to count
    :type key: str
    :rtype: Counter
    """
    return Counter(d[ANNOTATIONS][key] for _, _, d in graph.edges_iter(data=True) if key in d[ANNOTATIONS])


# ERROR HISTOGRAMS

def calculate_error_counter(graph):
    """Counts the occurrence of each type of error in a graph

    :param graph: A BEL graph
    :type graph: BELGraph
    :rtype: Counter
    """
    return Counter(e.__class__.__name__ for _, _, e, _ in graph.warnings)


def calculate_naked_names(graph):
    """

    :param graph: A BEL graph
    :type graph: BELGraph
    :rtype: Counter
    """
    return Counter(e.name for _, _, e, _ in graph.warnings if isinstance(e, NakedNameWarning))


def calculate_incorrect_name_dict(graph):
    """

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
    """Plots your graph summary statistics. You need to run plt.show() yourself after.


    :param graph: A BEL graph
    :type graph: BELGraph
    :param plt: Give matplotlib.pyplot to this parameter
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
