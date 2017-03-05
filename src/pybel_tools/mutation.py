"""

This module contains functions that help mutate a network

"""

import logging
from collections import defaultdict

from pybel.canonicalize import decanonicalize_node
from pybel.constants import *
from .constants import INFERRED_INVERSE, CNAME

log = logging.getLogger(__name__)


def left_merge(g, h):
    """Adds nodes and edges from H to G, in-place for G

    :param g: A BEL Graph
    :type g: pybel.BELGraph
    :param h: A BEL Graph
    :type h: pybel.BELGraph
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
    :type graph: pybel.BELGraph
    :param dict_of_sets_of_nodes: A dictionary of {node: set of nodes}
    :type dict_of_sets_of_nodes: dict
    """

    for key_node, value_nodes in dict_of_sets_of_nodes.items():
        for value_node in value_nodes:
            for successor in graph.successors_iter(value_node):
                for key, data in graph.edge[value_node][successor].items():
                    if key >= 0:
                        graph.add_edge(key_node, successor, attr_dict=data)
                    elif successor not in graph.edge[key_node] or key not in graph.edge[key_node][successor]:
                        graph.add_edge(key_node, successor, key=key, **{RELATION: unqualified_edges[-1 - key]})

            for predecessor in graph.predecessors_iter(value_node):
                for key, data in graph.edge[predecessor][value_node].items():
                    if key >= 0:
                        graph.add_edge(predecessor, key_node, attr_dict=data)
                    elif predecessor not in graph.pred[key_node] or key not in graph.edge[predecessor][key_node]:
                        graph.add_edge(predecessor, key_node, key=key, **{RELATION: unqualified_edges[-1 - key]})

            graph.remove_node(value_node)

    # Remove self edges
    for u, v, k in graph.edges(keys=True):
        if u == v:
            graph.remove_edge(u, v, k)


# TODO improve edge traversal efficiency from 2|E| to |E| with something like a disjoint union agglomeration
def build_central_dogma_collapse_dict(graph):
    """Builds a dictionary to direct the collapsing on the central dogma

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :return: A dictionary of {node: set of nodes}
    :rtype: dict
    """
    collapse_dict = defaultdict(set)

    r2p = {}

    for rna_node, protein_node, d in graph.edges_iter(data=True):
        if d[RELATION] != TRANSLATED_TO:
            continue

        collapse_dict[protein_node].add(rna_node)
        r2p[rna_node] = protein_node

    for gene_node, rna_node, d in graph.edges_iter(data=True):
        if d[RELATION] != TRANSCRIBED_TO:
            continue

        if rna_node in r2p:
            collapse_dict[r2p[rna_node]].add(gene_node)
        else:
            collapse_dict[rna_node].add(gene_node)

    return collapse_dict


def build_central_dogma_collapse_gene_dict(graph):
    """Builds a dictionary to direct the collapsing on the central dogma

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :return: A dictionary of {node: set of nodes}
    :rtype: dict
    """
    collapse_dict = defaultdict(set)

    r2g = {}
    for gene_node, rna_node, d in graph.edges_iter(data=True):
        if d[RELATION] != TRANSCRIBED_TO:
            continue

        collapse_dict[gene_node].add(rna_node)
        r2g[rna_node] = gene_node

    for rna_node, protein_node, d in graph.edges_iter(data=True):
        if d[RELATION] != TRANSLATED_TO:
            continue

        if rna_node not in r2g:
            raise ValueError('Should complete origin before running this function')

        collapse_dict[r2g[rna_node]].add(protein_node)

    return collapse_dict


def collapse_by_central_dogma(graph):
    """Collapses all nodes from the central dogma (GENE, RNA, PROTEIN) to PROTEIN, or most downstream possible entity, in place

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    """
    collapse_dict = build_central_dogma_collapse_dict(graph)
    log.info('Collapsing %d groups', len(collapse_dict))
    collapse_nodes(graph, collapse_dict)


def collapse_by_central_dogma_to_genes(graph):
    """Collapses all nodes from the central dogma (GENE, RNA, PROTEIN) to GENE in place

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    """
    collapse_dict = build_central_dogma_collapse_gene_dict(graph)
    log.info('Collapsing %d groups', len(collapse_dict))
    collapse_nodes(graph, collapse_dict)


def collapse_variants_to_genes(graph):
    """Finds all protein variants that are pointing to a gene and not a protein and fixes them

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    """
    for node, data in graph.nodes(data=True):
        if data[FUNCTION] != PROTEIN:
            continue
        if VARIANTS not in data:
            continue
        if any(d[RELATION] == TRANSCRIBED_TO for u, v, d in graph.in_edges_iter(data=True)):
            graph.node[node][FUNCTION] = GENE


def _infer_converter_helper(node, data, new_function):
    new_tup = list(node)
    new_tup[0] = new_function
    new_tup = tuple(new_tup)
    new_dict = data.copy()
    new_dict[FUNCTION] = new_function
    return new_tup, new_dict


def infer_central_dogmatic_translations(graph):
    """For all Protein entities, adds the missing origin RNA and RNA-Protein translation edge

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    """
    for node, data in graph.nodes(data=True):
        if data[FUNCTION] == PROTEIN and NAMESPACE in data and VARIANTS not in data:
            new_tup, new_dict = _infer_converter_helper(node, data, RNA)
            graph.add_node(new_tup, attr_dict=new_dict)
            graph.add_edge(new_tup, node, key=unqualified_edge_code[TRANSLATED_TO], **{RELATION: TRANSLATED_TO})


def infer_central_dogmatic_transcriptions(graph):
    """For all RNA entities, adds the missing origin Gene and Gene-RNA transcription edge

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    """
    for node, data in graph.nodes(data=True):
        if data[FUNCTION] == RNA and NAMESPACE in data and VARIANTS not in data:
            new_tup, new_dict = _infer_converter_helper(node, data, GENE)
            graph.add_node(new_tup, attr_dict=new_dict)
            graph.add_edge(new_tup, node, key=unqualified_edge_code[TRANSCRIBED_TO], **{RELATION: TRANSCRIBED_TO})


def infer_central_dogma(graph):
    """Adds all RNA-Protein translations then all Gene-RNA transcriptions by applying
    :code:`infer_central_dogmatic_translations` then :code:`infer_central_dogmatic_transcriptions`

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    """
    infer_central_dogmatic_translations(graph)
    infer_central_dogmatic_transcriptions(graph)


def opening_by_central_dogma(graph):
    """Performs origin completion then collapsing to furthest downstream, in place

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    """
    infer_central_dogma(graph)
    collapse_by_central_dogma(graph)


def opening_by_central_dogma_to_genes(graph):
    """Performs origin completion then collapsing to gene, in place

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    """
    infer_central_dogma(graph)
    collapse_by_central_dogma_to_genes(graph)


def prune_by_namespace(graph, function, namespace):
    """Prunes all nodes of a given namespace

    This might be useful to exclude information learned about distant species, such as excluding all information
    from MGI and RGD in diseases where mice and rats don't give much insight to the human disease mechanism.

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param function: The function to filter
    :type function: str
    :param namespace: The namespace to filter
    :type namespace: str
    """
    to_prune = []

    for node, data in graph.nodes_iter(data=True):
        if function == data[FUNCTION] and NAMESPACE in data and namespace == data[NAMESPACE]:
            to_prune.append(node)

    graph.remove_nodes_from(to_prune)


def prune_by_type(graph, function=None, prune_threshold=1):
    """Removes all nodes in graph (in-place) with only a connection to one node. Useful for gene and RNA.
    Allows for optional filter by function type.


    :param graph: a BEL network
    :type graph: pybel.BELGraph
    :param function: If set, filters by the node's function from :code:`pybel.constants` like :code:`GENE`, :code:`RNA`,
                     :code:`PROTEIN`, or :code:`BIOPROCESS`
    :type function: str
    :param prune_threshold: Removes nodes with less than or equal to this number of connections. Defaults to :code:`1`
    :type prune_threshold: int
    :return: The number of nodes pruned
    :rtype: int
    """
    to_prune = []

    for gene, data in graph.nodes_iter(data=True):
        if len(graph.adj[gene]) <= prune_threshold and (not function or function == data.get(FUNCTION)):
            to_prune.append(gene)

    graph.remove_nodes_from(to_prune)

    return len(to_prune)


def prune(graph):
    """Prunes genes, then RNA, in place

    :param graph: a BEL network
    :type graph: pybel.BELGraph

    """
    prune_by_type(graph, GENE)
    prune_by_type(graph, RNA)


def add_inferred_edges(graph, relations):
    """Adds inferred edges based on pre-defined axioms

    :param graph: a BEL network
    :type graph: pybel.BELGraph
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
    :type graph: pybel.BELGraph
    :param u: the source node
    :type u: tuple
    :param v: the target node
    :type v: tuple
    """
    raise NotImplementedError


def calculate_canonical_name(graph, node):
    """Calculates the canonical name for a given node. If it is a simple node, uses the already given name.
    Otherwise, it uses the BEL string.

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param node: A node
    :type node: tuple
    :return: Canonical node name
    :rtype: str
    """
    data = graph.node[node]

    if data[FUNCTION] == COMPLEX and NAMESPACE in data:
        return graph.node[node][NAME]

    if VARIANTS in data:
        return decanonicalize_node(graph, node)

    if FUSION in data:
        return decanonicalize_node(graph, node)

    if data[FUNCTION] in {REACTION, COMPOSITE, COMPLEX}:
        return decanonicalize_node(graph, node)

    if VARIANTS not in data and FUSION not in data:  # this is should be a simple node
        return graph.node[node][NAME]

    raise ValueError('Unexpected node data: {}'.format(data))


def add_canonical_names(graph):
    """Adds a canonical name to each node's data dictionary if they are missing

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    """
    for node, data in graph.nodes_iter(data=True):
        if CNAME in data:
            log.debug('Canonical name already in dictionary for %s', data[CNAME])
            continue

        graph.node[node][CNAME] = calculate_canonical_name(graph, node)
