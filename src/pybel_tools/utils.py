from collections import defaultdict, Counter

from pybel.constants import RELATION


# TODO rename this function
def graph_content_transform(graph):
    """Builds a dictionary of {node pair: set of edge types}"""
    edge_relations = defaultdict(set)
    for u, v, d in graph.edges_iter(data=True):
        edge_relations[u, v].add(d[RELATION])
    return edge_relations


def count_defaultdict(d):
    """Takes a defaultdict(list) and applys a counter to each list"""
    return {k: Counter(v) for k, v in d.items()}


def count_dict_values(dict_of_counters):
    """Counts the number of elements in each value (can be list, Counter, etc)"""
    return {k: len(v) for k, v in dict_of_counters.items()}
