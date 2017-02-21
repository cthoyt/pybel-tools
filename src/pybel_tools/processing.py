from pybel.constants import *
from pybel.parser.language import unqualified_edge_code

IS_PRODUCT_OF = 'isProductOf'
IS_REACTANT_OF = 'isReactantOf'
IS_VARIANT_OF = 'isVariantOf'
IS_COMPONENT_OF = 'isComponentOf'
TRANSCRIBED_FROM = 'transcribedFrom'
TRANSLATED_FROM = 'translatedFrom'

INFERRED_INVERSE = {
    HAS_PRODUCT: IS_PRODUCT_OF,
    HAS_REACTANT: IS_REACTANT_OF,
    HAS_VARIANT: IS_VARIANT_OF,
    HAS_COMPONENT: IS_COMPONENT_OF,
    TRANSCRIBED_TO: TRANSCRIBED_FROM,
    TRANSLATED_TO: TRANSLATED_FROM
}


def prune_by_type(graph, type):
    """Removes all nodes in graph (in-place) with only a connection to one node. Useful for gene and RNA.

    :param graph: a BEL network
    :type graph: BELGraph
    """
    to_prune = []
    for gene, data in graph.nodes_iter(data=True, type=type):
        if 1 >= len(graph.adj[gene]):
            to_prune.append(gene)
    graph.remove_nodes_from(to_prune)


def prune(graph):
    """Prunes genes, then RNA in-place

    :param graph: a BEL network
    :type graph: BELGraph

    """
    prune_by_type(graph, 'Gene')
    prune_by_type(graph, 'RNA')


def add_inferred_edges(graph, relations):
    """Adds inferred edges based on pre-defined axioms

    :param graph: a BEL network
    :type graph: BELGraph
    :param relation: single or iterable of relation names to add their inverse inferred edges
    """

    if isinstance(relations, str):
        return add_inferred_edges(graph, [relations])

    for relation in relations:
        for u, v in graph.edges_iter(relation=relation):
            graph.add_edge(v, u, key=unqualified_edge_code[relation], relation=INFERRED_INVERSE[relation])


# TODO: Implement
def add_inferred_two_way_edge(graph, u, v):
    pass
