# -*- coding: utf-8 -*-

import logging

from pybel.struct.grouping import get_subgraphs_by_annotation

log = logging.getLogger(__name__)

__all__ = [
    'get_subgraphs_by_annotation_filtered',
]


def get_subgraphs_by_annotation_filtered(graph, annotation, values):
    """Stratifies the given graph into subgraphs based on the values for edges' annotations, but filter by a set
    of given values

    :param pybel.BELGraph graph: A BEL graph
    :param str annotation: The annotation to group by
    :param iter[str] values: The values to keep
    :rtype: dict[str,pybel.BELGraph]
    """
    return {
        k: v
        for k, v in get_subgraphs_by_annotation(graph, annotation).items()
        if k in values
    }
