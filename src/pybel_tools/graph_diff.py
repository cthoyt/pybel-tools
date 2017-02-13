import itertools as itt


def graph_edges_equal(g, h):
    """Tests that two graphs are equal, defined by having the same nodes, and all edges (with same attributes)

    :type g: pybel.BELGraph
    :type h: pybel.BELGraph
    """
    assert set(g.nodes_iter()) == set(h.nodes_iter())
    assert set(g.edges_iter()) == set(h.edges_iter())

    for u, v in g.edges():
        i = itt.product(g.edge[u][v].values(), h.edge[u][v].values())
        r = list(filter(lambda q: q[0] == q[1], i))
        assert len(g.edge[u][v]) == len(r)


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
    return set(g.edges()) - set(h.edges())


def graph_edges_xor(g, h):
    """

    :param g:
    :type g: :class:`pybel.BELGraph`
    :param h:
    :type h: :class:`pybel.BELGraph`
    :rtype: :class:`pybel.BELGraph`
    """
    return set(g.edges()).symmetric_difference(h.edges())
