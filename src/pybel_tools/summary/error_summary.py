# -*- coding: utf-8 -*-

"""This module contains functions that provide summaries of the errors encountered while parsing a BEL script."""

from collections import Counter, Iterable, defaultdict
from typing import List, Mapping, Set

from pybel import BELGraph
from pybel.constants import ANNOTATIONS
from pybel.parser.exc import (
    MissingNamespaceNameWarning, MissingNamespaceRegexWarning, UndefinedAnnotationWarning, UndefinedNamespaceWarning,
)
from pybel.struct.filters.edge_predicates import edge_has_annotation
from pybel.struct.summary import count_error_types, count_naked_names, get_naked_names
from pybel.struct.summary.node_summary import get_names_by_namespace, get_namespaces
from ..utils import count_dict_values

__all__ = [
    'count_error_types',
    'count_naked_names',
    'get_naked_names',
    'get_incorrect_names_by_namespace',
    'get_incorrect_names',
    'get_undefined_namespaces',
    'get_undefined_namespace_names',
    'calculate_incorrect_name_dict',
    'calculate_error_by_annotation',
    'group_errors',
    'get_names_including_errors',
    'get_names_including_errors_by_namespace',
    'get_undefined_annotations',
    'get_namespaces_with_incorrect_names',
    'get_most_common_errors',
]


def get_namespaces_with_incorrect_names(graph: BELGraph) -> Set[str]:
    """Return the set of all namespaces with incorrect names in the graph."""
    return {
        e.namespace
        for _, _, e, _ in graph.warnings
        if isinstance(e, (MissingNamespaceNameWarning, MissingNamespaceRegexWarning))
    }


def get_incorrect_names_by_namespace(graph: BELGraph, namespace: str) -> Set[str]:
    """Return the set of all incorrect names from the given namespace in the graph.

    :return: The set of all incorrect names from the given namespace in the graph
    """
    return {
        e.name
        for _, _, e, _ in graph.warnings
        if isinstance(e, (MissingNamespaceNameWarning, MissingNamespaceRegexWarning)) and e.namespace == namespace
    }


def get_incorrect_names(graph: BELGraph) -> Mapping[str, Set[str]]:
    """Return the dict of the sets of all incorrect names from the given namespace in the graph.

    :return: The set of all incorrect names from the given namespace in the graph
    """
    return {
        namespace: get_incorrect_names_by_namespace(graph, namespace)
        for namespace in get_namespaces(graph)
    }


def get_undefined_namespaces(graph: BELGraph) -> Set[str]:
    """Get all namespaces that are used in the BEL graph aren't actually defined."""
    return {
        e.namespace
        for _, _, e, _ in graph.warnings
        if isinstance(e, UndefinedNamespaceWarning)
    }


def get_undefined_namespace_names(graph: BELGraph, namespace: str) -> Set[str]:
    """Get the names from a namespace that wasn't actually defined.
    
    :return: The set of all names from the undefined namespace
    """
    return {
        e.name
        for _, _, e, _ in graph.warnings
        if isinstance(e, UndefinedNamespaceWarning) and e.namespace == namespace
    }


def get_undefined_annotations(graph: BELGraph) -> Set[str]:
    """Get all annotations that aren't actually defined.
    
    :return: The set of all undefined annotations
    """
    return {
        e.annotation
        for _, _, e, _ in graph.warnings
        if isinstance(e, UndefinedAnnotationWarning)
    }


def calculate_incorrect_name_dict(graph: BELGraph) -> Mapping[str, str]:
    """Group all of the incorrect identifiers in a dict of {namespace: list of erroneous names}.

    :return: A dictionary of {namespace: list of erroneous names}
    """
    missing = defaultdict(list)

    for line_number, line, e, ctx in graph.warnings:
        if not isinstance(e, (MissingNamespaceNameWarning, MissingNamespaceRegexWarning)):
            continue
        missing[e.namespace].append(e.name)

    return dict(missing)


def calculate_error_by_annotation(graph: BELGraph, annotation: str) -> Mapping[str, List[str]]:
    """Group the graph by a given annotation and builds lists of errors for each.

    :return: A dictionary of {annotation value: list of errors}
    """
    results = defaultdict(list)

    for line_number, line, e, context in graph.warnings:
        if not context or not edge_has_annotation(context, annotation):
            continue

        values = context[ANNOTATIONS][annotation]

        if isinstance(values, str):
            results[values].append(e.__class__.__name__)
        elif isinstance(values, Iterable):
            for value in values:
                results[value].append(e.__class__.__name__)

    return dict(results)


def group_errors(graph: BELGraph) -> Mapping[str, List[int]]:
    """Group the errors together for analysis of the most frequent error.

    :return: A dictionary of {error string: list of line numbers}
    """
    warning_summary = defaultdict(list)

    for ln, _, e, _ in graph.warnings:
        warning_summary[str(e)].append(ln)

    return dict(warning_summary)


def get_most_common_errors(graph: BELGraph, number: int = 20):
    """Get the most common errors in a graph.

    :param pybel.BELGraph graph:
    :param int number:
    :rtype: Counter
    """
    return count_dict_values(group_errors(graph)).most_common(number)


def get_names_including_errors_by_namespace(graph: BELGraph, namespace: str) -> Set[str]:
    """Takes the names from the graph in a given namespace (:func:`pybel.struct.summary.get_names_by_namespace`) and
    the erroneous names from the same namespace (:func:`get_incorrect_names_by_namespace`) and returns them together
    as a unioned set

    :return: The set of all correct and incorrect names from the given namespace in the graph
    """
    return get_names_by_namespace(graph, namespace) | get_incorrect_names_by_namespace(graph, namespace)


def get_names_including_errors(graph: BELGraph) -> Mapping[str, Set[str]]:
    """Takes the names from the graph in a given namespace and the erroneous names from the same namespace and returns
    them together as a unioned set

    :return: The dict of the sets of all correct and incorrect names from the given namespace in the graph
    """
    return {
        namespace: get_names_including_errors_by_namespace(graph, namespace)
        for namespace in get_namespaces(graph)
    }
