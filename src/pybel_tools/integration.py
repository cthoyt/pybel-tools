"""

pybel_tools.integrate holds functions that help add more data to the network

"""
import logging

from pybel.constants import FUNCTION, NAMESPACE, NAME

log = logging.getLogger(__name__)


def overlay_data(graph, data, label, overwrite=False):
    """Overlays tabular data on the network

    :type graph: BELGraph
    :param data: A dictionary of {pybel node: data for that node}
    :type data: dict
    :param label: The annotation label to put in the node dictionary
    :type label: str
    :param overwrite: Should old annotations be overwritten?
    :type overwrite: bool
    """
    for node, annotation in data.items():
        if node not in graph:
            log.debug('%s not in graph', node)
            continue
        elif label in graph.node[node] and not overwrite:
            log.debug('%s already on %s', label, node)
            continue
        graph.node[node][label] = annotation


def overlay_type_data(graph, data, label, function, namespace, overwrite=False, impute=None):
    """Overlays tabular data on the network for data that comes from an data set with identifiers that lack
    namespaces.

    For example, if you want to overlay differential gene expression data from a table, that table
    probably has HGNC identifiers, but no specific annotations that they are in the HGNC namespace or
    that the entities to which they refer are RNA.

    :type graph: BELGraph
    :param data: A dictionary of {name: data}
    :type data: dict
    :param label: The annotation label to put in the node dictionary
    :type label: str
    :param function: The function of the keys in the data dictionary
    :type function: str
    :param namespace: The namespace of the keys in the data dictionary
    :type namespace: str
    :param overwrite: Should old annotations be overwritten?
    :type overwrite: bool
    :param impute: The value to use for missing data
    """
    new_data = {}

    for node, d in graph.nodes_iter(data=True):
        if NAMESPACE not in d:
            continue

        if d[FUNCTION] == function and d[NAMESPACE] == namespace:
            new_data[node] = data.get(d[NAME], impute)

    overlay_data(graph, new_data, label, overwrite=overwrite)
