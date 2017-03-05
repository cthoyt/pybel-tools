from collections import Counter, defaultdict

from pybel.constants import ANNOTATIONS
from .summary import count_annotation_instances
from .utils import check_has_annotation


def _permissive_node_filter(graph, node):
    return True


def get_possible_successor_edges(graph, subgraph):
    """Gets the set of possible successor edges peripheral to the subgraph

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param subgraph: A set of nodes
    :return: A set of edges
    :rtype: set
    """
    return {(u, v) for u in subgraph for v in graph.successors_iter(u) if v not in subgraph}


def count_possible_successors(graph, subgraph):
    return Counter(v for u, v in get_possible_successor_edges(graph, subgraph))


def get_possible_predecessor_edges(graph, subgraph):
    """Gets the set of possible predecessor edges peripheral to the subgraph

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param subgraph: A set of nodes
    :return: A set of edges
    :rtype: set
    """
    return {(u, v) for v in subgraph for u in graph.predecessors_iter(v) if u not in subgraph}


def count_possible_predecessors(graph, subgraph):
    return Counter(v for u, v in get_possible_predecessor_edges(graph, subgraph))


def get_subgraph_edges(graph, subgraph_name, subgraph_key='Subgraph', source_filter=None, target_filter=None):
    if source_filter is None:
        source_filter = _permissive_node_filter

    if target_filter is None:
        target_filter = _permissive_node_filter

    for u, v, k, d in graph.edges_iter(keys=True, data=True):
        if not check_has_annotation(d, subgraph_key):
            continue
        if d[ANNOTATIONS][subgraph_key] == subgraph_name and source_filter(graph, u) and target_filter(graph, v):
            yield u, v, k, d


def get_subgraph_fill_edges(graph, subgraph, node_filter=None):
    """

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param subgraph: A set of nodes
    :type subgraph: iter
    :param node_filter: Optional filter function (graph, node) -> bool
    :return:
    """

    if node_filter is None:
        node_filter = _permissive_node_filter

    possible_succ = get_possible_successor_edges(graph, subgraph)
    succ_counter = Counter(v for u, v in possible_succ)

    possible_pred = get_possible_predecessor_edges(graph, subgraph)
    pred_counter = Counter(v for u, v in possible_pred)

    gaps = {node for node, freq in (succ_counter + pred_counter).items() if 2 <= freq and node_filter(graph, node)}

    for already_in_graph, new_node in possible_succ:
        if new_node in gaps:
            yield already_in_graph, new_node

    for new_node, already_in_graph in possible_pred:
        if new_node in gaps:
            yield new_node, already_in_graph


def infer_subgraph_expansion(graph, subgraph_key='Subgraph'):
    """Infers the annotations for subgraphs on to edges

    1. Group subgraphs
    2. Build dictionary of {(u,v,k): {set of inferred subgraph names}}

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :return:
    """

    inferred_subgraphs = defaultdict(set)
    subgraph_counts = count_annotation_instances(graph, subgraph_key)
    raise NotImplementedError


def enrich_unqualified(graph, subgraph):
    """Enriches the subgraph with the unqualified edges from the graph.

    The reason you might want to do this is you induce a subgraph from the original graph based on an annotation filter,
    but the unqualified edges that don't have annotations that most likely connect elements within your graph are
    not included.

    TODO: example

    :param graph: A BEL graph
    :type graph: pybel.BELGraph
    :param subgraph: A BEL graph's subgraph
    :type subgraph: pybel.BELGraph
    :return:
    """
    raise NotImplementedError
