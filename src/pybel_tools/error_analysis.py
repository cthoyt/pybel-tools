"""
These scripts are designed to assist in the analysis of errors within BEL documents
and provide some suggestions for fixes.


"""

from collections import Counter, defaultdict

from fuzzywuzzy import process, fuzz

from pybel.parser.parse_exceptions import MissingNamespaceNameWarning, NakedNameWarning


def count_defaultdict(d):
    """Takes a defaultdict(list) and applys a counter to each list"""
    return {k: Counter(v) for k, v in d.items()}


def count_dict_values(dict_of_counters):
    """Counts the number of elements in each value (can be list, Counter, etc)"""
    return {k: len(v) for k, v in dict_of_counters.items()}


def calculate_error_counter(graph):
    """

    :type graph: :class:`pybel.BELGraph`
    """
    return Counter(e.__class__.__name__ for _, _, e, _ in graph.warnings)


def calculate_naked_names(graph):
    return Counter(e.name for _, _, e, _ in graph.warnings if isinstance(e, NakedNameWarning))


def calculate_incorrect_name_dict(graph):
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


def calculate_size_by_annotation(graph, annotation):
    return Counter(data[annotation] for _, _, data in graph.edges_iter(data=True) if annotation in data)


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
