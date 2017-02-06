import networkx as nx

import pybel


def graph_equal(G, H):
    """Tests that two graphs are equal, defined by having the same nodes, and all edges (with same attributes)"""
    return nx.MultiDiGraph()


def graph_intersection(a, b):
    """

    :param a:
    :type a: :class:`pybel.BELGraph`
    :param b:
    :type b: :class:`pybel.BELGraph`
    :return:
    :rtype: :class:`pybel.BELGraph`
    """
    return nx.MultiDiGraph()


def graph_asymmetric_subtract(G, H):
    """

    :param a:
    :type a: :class:`pybel.BELGraph`
    :param b:
    :type b: :class:`pybel.BELGraph`
    :return:
    :rtype: :class:`pybel.BELGraph`
    """
    return nx.MultiDiGraph()


def graph_difference(a, b):
    """

    :param a:
    :type a: :class:`pybel.BELGraph`
    :param b:
    :type b: :class:`pybel.BELGraph`
    :return:
    :rtype: :class:`pybel.BELGraph`
    """
    return nx.MultiDiGraph()
