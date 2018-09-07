# -*- coding: utf-8 -*-

"""This module builds mutation functions that are bound to a manager"""

from pybel.struct.mutation.expansion.neighborhood import expand_node_neighborhood
from pybel.struct.pipeline import in_place_transformation, uni_in_place_transformation
from pybel import Manager


__all__ = [
    'build_expand_node_neighborhood_by_hash',
    'build_delete_node_by_hash',
]


def build_expand_node_neighborhood_by_hash(manager: Manager):
    """Make an expand function that's bound to the manager.

    :rtype: (pybel.BELGraph, pybel.BELGraph, str) -> None
    """

    @uni_in_place_transformation
    def expand_node_neighborhood_by_hash(universe, graph, node_hash):
        """Expands around the neighborhoods of a node by identifier

        :param pybel.BELGraph universe: A BEL graph
        :param pybel.BELGraph graph: A BEL graph
        :param str node_hash: The node hash
        """
        node = manager.get_dsl_by_hash(node_hash)
        return expand_node_neighborhood(universe, graph, node)

    return expand_node_neighborhood_by_hash


def build_delete_node_by_hash(manager: Manager):
    """Make a delete function that's bound to the manager.

    :rtype: (pybel.BELGraph, str) -> None
    """

    @in_place_transformation
    def delete_node_by_hash(graph, node_hash):
        """Removes a node by identifier

        :param pybel.BELGraph graph: A BEL graph
        :param str node_hash: A node hash
        """
        node = manager.get_dsl_by_hash(node_hash)
        graph.remove_node(node)

    return delete_node_by_hash
