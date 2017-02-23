import logging
from collections import defaultdict

from pybel import BELGraph
from pybel.constants import ANNOTATIONS

log = logging.getLogger(__name__)


def left_merge(g, h):
    """Performs an in-place operation, adding nodes and edges in H that aren't already in G

    :param g:
    :type g: BELGraph
    :param h:
    :type h: BELGraph
    :rtype: BELGraph
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


def overlay_type_data(graph, data, label, function, namespace, overwrite=False):
    """Overlays tabular data on the network for data that comes from an un-namespaced data set

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
    """
    new_data = {(function, namespace, name): value for name, value in data.items()}
    overlay_data(graph, new_data, label, overwrite=overwrite)


def group_subgraphs(graph, annotation):
    """Groups the nodes that occur in edges by the given annotation

    :param graph: A BEL graph
    :type graph: BELGraph
    :param annotation: An annotation to use to group edges
    :type annotation: str
    :return: dict of sets of BELGraph nodes
    """
    result = defaultdict(set)
    for u, v, d in graph.edges_iter(data=True):
        if annotation not in d[ANNOTATIONS]:
            continue
        result[d[ANNOTATIONS][annotation]].add(u)
        result[d[ANNOTATIONS][annotation]].add(v)

    return result


def filter_edge_properties(edges, annotations_filter=None, relation=None):
    pass


def filter_node_properties(edges, function_keep=None, namespace_keep=None, function_delete=None, namespace_delete=None):
    pass


def get_subgraph_by_annotation(graph, key, value):
    bg = BELGraph()

    for u, v, k, d in graph.edges_iter(keys=True, data=True):
        if ANNOTATIONS not in d or key not in d[ANNOTATIONS]:
            continue

        if d[ANNOTATIONS][key] == value:

            if u not in bg:
                bg.add_node(u, graph.node[u])

            if v not in bg:
                bg.add_node(v, graph.node[v])

            bg.add_edge(u, v, key=key, attr_dict=d)

    return bg
