import itertools as itt
import logging

from pybel import BELGraph
from .utils import graph_content_transform

log = logging.getLogger(__name__)


def graph_entities_equal(g, h):
    """Tests that two graphs have the same nodes

    :param g: A BEL Graph
    :type g: BELGraph
    :param h: Another BEL Graph
    :type h: BELGraph
    :return: Do the two graphs share the same set of nodes?
    :rtype: bool
    """
    return set(g.nodes_iter()) == set(h.nodes_iter())


def graph_topologically_equal(g, h):
    """Tests that two graphs are topologically equal, defined by having the same nodes, and same connectivity

    :param g: A BEL Graph
    :type g: BELGraph
    :param h: Another BEL Graph
    :type h: BELGraph
    :return: Do the graphs share the same set of nodes, and the same connectivity?
    :rtype: bool
    """
    if not graph_entities_equal(g, h):
        return False

    return set(g.edges_iter()) == set(h.edges_iter())


def graph_relations_equal(g, h):
    """Tests that two graphs are equal, defined by having the same nodes, same connections, and existence of
    same connection types

    :param g: A BEL Graph
    :type g: BELGraph
    :param h: Another BEL Graph
    :type h: BELGraph
    :return: Do the two graphs share the same set of nodes, same connectivity, and types of connections?
    :rtype: bool
    """
    if not graph_topologically_equal(g, h):
        return False

    g_t = graph_content_transform(g)
    h_t = graph_content_transform(h)

    return all(g_t[u, v] == h_t[u, v] for u, v in g.edges_iter())


def graph_provenance_equal(g, h):
    """Tests that two graphs are equal, defined by having the same nodes, same connections with same types,
    and same attributes exactly.

    :param g: A BEL Graph
    :type g: BELGraph
    :param h: Another BEL Graph
    :type h: BELGraph
    :return: Do the two graphs share the same set of nodes, same connectivity, types of connections, evidences, and
              annotations?
    :rtype: bool
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

    :param g: A BEL Graph
    :type g: BELGraph
    :param h: Another BEL Graph
    :type h: BELGraph
    :return: The set of edges shared between the two graphs
    :rtype: set
    """
    return set(g.edges()).intersection(h.edges())


def graph_edges_subtract(g, h):
    """

    :param g: A BEL Graph
    :type g: BELGraph
    :param h: Another BEL Graph
    :type h: BELGraph
    :return: The asymmetric difference between the edges in g and h
    :rtype: set
    """
    return set(g.edges()).difference(set(h.edges()))


def graph_edges_xor(g, h):
    """

    :param g: A BEL Graph
    :type g: BELGraph
    :param h: Another BEL Graph
    :type h: BELGraph
    :return: The symmetric difference between the edges in g and h
    :rtype: set
    """
    return set(g.edges()).symmetric_difference(h.edges())
