import itertools as itt
from collections import defaultdict, Counter

from pybel.constants import RELATION, FUNCTION


def count_nodes(g):
    """Returns a histogram of the different functions present in a graph"""
    return Counter(data[FUNCTION] for _, data in g.nodes_iter(data=True))


def graph_content_transform(g):
    edge_relations = defaultdict(set)
    for u, v, d in g.edges_iter(data=True):
        edge_relations[u, v].add(d[RELATION])
    return edge_relations


def count_edges(g):
    """Returns a histogram of the different types of relations present in a graph.

    Note: this operation only counts each type of edge once for each pair of nodes
    """
    return Counter(relation for _, relations in graph_content_transform(g).items() for relation in relations)


def graph_entities_equal(g, h):
    """Tests that two graphs have the same nodes

    :type g: pybel.BELGraph
    :type h: pybel.BELGraph
    """
    return set(g.nodes_iter()) == set(h.nodes_iter())


def graph_topologically_equal(g, h):
    """Tests that two graphs are topologically equal, defined by having the same nodes, and same connections

        :type g: pybel.BELGraph
        :type h: pybel.BELGraph
        """
    if not graph_entities_equal(g, h):
        return False

    return set(g.edges_iter()) == set(h.edges_iter())


def graph_relations_equal(g, h):
    """Tests that two graphs are equal, defined by having the same nodes, same connections, and existence of
    same connection types

    :type g: pybel.BELGraph
    :type h: pybel.BELGraph
    """
    if not graph_topologically_equal(g, h):
        return False

    g_t = graph_content_transform(g)
    h_t = graph_content_transform(h)

    return all(g_t[u, v] == h_t[u, v] for u, v in g.edges_iter())


def graph_provenance_equal(g, h):
    """Tests that two graphs are equal, defined by having the same nodes, same connections with same types,
    and same attributes exactly.

    :type g: pybel.BELGraph
    :type h: pybel.BELGraph
    """
    if not graph_relations_equal(g, h):
        return False

    for u, v in g.edges():
        r = sum(gv == hv for gv, hv in itt.product(g.edge[u][v].values(), h.edge[u][v].values()))
        if len(g.edge[u][v]) != r:
            return False

    return True


def graph_edges_intersection(g, h):
    """

    :param g:
    :type g: :class:`pybel.BELGraph`
    :param h:
    :type h: :class:`pybel.BELGraph`
    :return:
    :rtype: :class:`pybel.BELGraph`
    """
    return set(g.edges()).intersection(h.edges())


def graph_edges_subtract(g, h):
    """

    :param g:
    :type g: :class:`pybel.BELGraph`
    :param h:
    :type h: :class:`pybel.BELGraph`
    :rtype: :class:`pybel.BELGraph`
    """
    return set(g.edges()).difference(set(h.edges()))


def graph_edges_xor(g, h):
    """

    :param g:
    :type g: :class:`pybel.BELGraph`
    :param h:
    :type h: :class:`pybel.BELGraph`
    :rtype: :class:`pybel.BELGraph`
    """
    return set(g.edges()).symmetric_difference(h.edges())
