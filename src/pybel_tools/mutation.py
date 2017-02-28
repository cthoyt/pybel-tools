"""

This module contains functions that help mutate a network

"""

import logging
from collections import defaultdict

from pybel import BELGraph
from pybel.constants import RELATION, TRANSLATED_TO, FUNCTION, GENE, RNA
from pybel.parser.language import unqualified_edge_code
from .constants import INFERRED_INVERSE

log = logging.getLogger(__name__)


def left_merge(g, h):
    """Performs an in-place operation, adding nodes and edges in H that aren't already in G

    :param g: A BEL Graph
    :type g: BELGraph
    :param h: A BEL Graph
    :type h: BELGraph
    :return: A merged BEL Graph, taking precedence from the left graph
    :rtype: BELGraph
    """

    for node, data in h.nodes_iter(data=True):
        if node not in g:
            g.add_node(node, data)

    for u, v, k, d in h.edges_iter(keys=True, data=True):
        if 0 <= k:  # not an unqualified edge

            if all(d != gd for gd in g.edge[u][v].values()):
                g.add_edge(u, v, attr_dict=d)

        elif k not in g.edge[u][v]:  # unqualified edge that's not in G yet
            g.add_edge(u, v, key=k, attr_dict=d)


def collapse_nodes(graph, dict_of_sets_of_nodes):
    """Collapses all nodes in values to the key nodes in place

    :param graph: A BEL Graph
    :type graph: BELGraph
    :param dict_of_sets_of_nodes: A dictionary of {node: set of nodes}
    :type dict_of_sets_of_nodes: dict
    """

    for key_node, value_nodes in dict_of_sets_of_nodes.items():
        for value_node in value_nodes:
            for successor in graph.successors_iter(value_node):
                for key, data in graph.edge[value_node][successor].items():
                    graph.add_edge(key_node, successor, key=key, attr_dict=data)

            for predecessor in graph.predecessors_iter(value_node):
                for key, data in graph.edge[predecessor][value_node].items():
                    graph.add_edge(predecessor, key_node, key=key, attr_dict=data)

            graph.remove_node(value_node)


def collapse_by_central_dogma(graph):
    """Collapses all nodes from the central dogma (GENE, RNA, PROTEIN) to PROTEIN in place

    :param graph: A BEL Graph
    :type graph: BELGraph
    """

    collapse_dict = defaultdict(set)

    for rna_node, protein_node in graph.edges_iter(**{RELATION: TRANSLATED_TO}):
        collapse_dict[protein_node].add(rna_node)

        for successor in graph.successors_iter(rna_node):
            if unqualified_edge_code[TRANSLATED_TO] in graph.edge[successor][rna_node]:
                collapse_dict[protein_node].add(successor)

    log.info('Collapsing %d groups', len(collapse_dict))

    collapse_nodes(graph, collapse_dict)


def prune_by_type(graph, function, prune_threshold=2):
    """Removes all nodes in graph (in-place) with only a connection to one node. Useful for gene and RNA.

    :param graph: a BEL network
    :type graph: BELGraph
    :param function: The node's function from :code:`pybel.constants` like GENE, RNA, PROTEIN, or BIOPROCESS
    :type function: str
    :param prune_threshold: Defaults to 2
    :type prune_threshold: int
    :return: The number of nodes pruned
    :rtype: int
    """
    to_prune = []

    for gene, data in graph.nodes_iter(data=True):
        if len(graph.adj[gene]) < prune_threshold and function == data.get(FUNCTION):
            to_prune.append(gene)

    graph.remove_nodes_from(to_prune)

    return len(to_prune)


def prune(graph):
    """Prunes genes, then RNA, in place

    :param graph: a BEL network
    :type graph: BELGraph

    """
    prune_by_type(graph, GENE)
    prune_by_type(graph, RNA)


def add_inferred_edges(graph, relations):
    """Adds inferred edges based on pre-defined axioms

    :param graph: a BEL network
    :type graph: BELGraph
    :param relations: single or iterable of relation names to add their inverse inferred edges
    :type relations: str or list
    """

    if isinstance(relations, str):
        return add_inferred_edges(graph, [relations])

    for relation in relations:
        for u, v in graph.edges_iter(**{RELATION: relation}):
            graph.add_edge(v, u, key=unqualified_edge_code[relation], **{RELATION: INFERRED_INVERSE[relation]})


# TODO: Implement
def add_inferred_two_way_edge(graph, u, v):
    """If a two way edge exists, and the opposite direction doesn't exist, add it to the graph

    Use: two way edges from BEL definition and/or axiomatic inverses of membership relations

    :param graph: A BEL Graph
    :type graph: BELGraph
    :param u: the source node
    :param v: the target node
    """
