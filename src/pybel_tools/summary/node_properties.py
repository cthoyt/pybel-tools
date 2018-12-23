# -*- coding: utf-8 -*-

"""This module contains functions that calculate properties of nodes"""

from collections import Counter
from typing import Iterable, Mapping, Optional, Set, Tuple, Union

import networkx as nx

from pybel import BELGraph
from pybel.dsl import BaseEntity
from pybel.struct.filters import get_nodes
from pybel.struct.filters.edge_predicates import is_causal_relation
from pybel.struct.filters.node_predicates import (
    has_activity, is_causal_central, is_causal_sink, is_causal_source, is_degraded, is_translocated,
)

__all__ = [
    'is_causal_relation',
    'get_causal_out_edges',
    'get_causal_in_edges',
    'is_causal_source',
    'is_causal_central',
    'is_causal_sink',
    'get_causal_source_nodes',
    'get_causal_central_nodes',
    'get_causal_sink_nodes',
    'get_degradations',
    'get_activities',
    'get_translocated',
    'count_top_centrality',
    'count_top_degrees',
    'get_modifications_count',
]


def get_causal_out_edges(graph: BELGraph,
                         nbunch: Union[BaseEntity, Iterable[BaseEntity]],
                         ) -> Set[Tuple[BaseEntity, BaseEntity]]:
    """Get the out-edges to the given node that are causal.

    :return: A set of (source, target) pairs where the source is the given node
    """
    return {
        (u, v)
        for u, v, k, d in graph.out_edges(nbunch, keys=True, data=True)
        if is_causal_relation(graph, u, v, k, d)
    }


def get_causal_in_edges(graph: BELGraph,
                        nbunch: Union[BaseEntity, Iterable[BaseEntity]],
                        ) -> Set[Tuple[BaseEntity, BaseEntity]]:
    """Get the in-edges to the given node that are causal.

    :return: A set of (source, target) pairs where the target is the given node
    """
    return {
        (u, v)
        for u, v, k, d in graph.in_edges(nbunch, keys=True, data=True)
        if is_causal_relation(graph, u, v, k, d)
    }


def get_causal_source_nodes(graph: BELGraph, func: str) -> Set[BaseEntity]:
    """Return a set of all nodes that have an in-degree of 0.

    This likely means that it is an external perturbagen and is not known to have any causal origin from within the
    biological system. These nodes are useful to identify because they generally don't provide any mechanistic insight.
    """
    return {
        node
        for node in graph
        if node.function == func and is_causal_source(graph, node)
    }


def get_causal_central_nodes(graph: BELGraph, func: str) -> Set[BaseEntity]:
    """Return a set of all nodes that have both an in-degree > 0 and out-degree > 0.

    This means that they are an integral part of a pathway, since they are both produced and consumed.
    """
    return {
        node
        for node in graph
        if node.function == func and is_causal_central(graph, node)
    }


def get_causal_sink_nodes(graph: BELGraph, func) -> Set[BaseEntity]:
    """Returns a set of all ABUNDANCE nodes that have an causal out-degree of 0.

    This likely means that the knowledge assembly is incomplete, or there is a curation error.
    """
    return {
        node
        for node in graph
        if node.function == func and is_causal_sink(graph, node)
    }


def get_degradations(graph: BELGraph) -> Set[BaseEntity]:
    """Get all nodes that are degraded."""
    return get_nodes(graph, is_degraded)


def get_activities(graph: BELGraph) -> Set[BaseEntity]:
    """Get all nodes that have molecular activities."""
    return get_nodes(graph, has_activity)


def get_translocated(graph: BELGraph) -> Set[BaseEntity]:
    """Get all nodes that are translocated."""
    return get_nodes(graph, is_translocated)


def count_top_degrees(graph: BELGraph, number: Optional[int] = 30):
    dd = graph.degree()
    dc = Counter(dd)
    return dict(dc.most_common(number))


def count_top_centrality(graph: BELGraph, number: Optional[int] = 30) -> Mapping[BaseEntity, int]:
    """Get top centrality dictionary."""
    dd = nx.betweenness_centrality(graph)
    dc = Counter(dd)
    return dict(dc.most_common(number))


def get_modifications_count(graph: BELGraph) -> Mapping[str, int]:
    """Get a modifications count dictionary."""
    translocation_count = len(get_translocated(graph))
    degradation_count = len(get_degradations(graph))
    molecular_count = len(get_activities(graph))

    modification_count_labels = (
        'Translocations',
        'Degradations',
        'Molecular Activities',
    )
    modification_counts = (translocation_count, degradation_count, molecular_count)

    return {
        label: count
        for label, count in zip(modification_count_labels, modification_counts)
        if count
    }
