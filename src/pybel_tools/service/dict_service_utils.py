"""
This module contains all of the services necessary through the PyBEL API Definition, backed by a network
dictionary
"""

import logging

import networkx as nx

from pybel import from_bytes, BELGraph
from pybel.canonicalize import decanonicalize_node
from pybel.constants import *
from pybel.io import to_json_dict
from pybel.manager.graph_cache import GraphCacheManager
from pybel.manager.models import Network

log = logging.getLogger(__name__)

CNAME = 'cname'

#: dictionary of {id : BELGraph}
networks = {}

#: dictionary of {node: hash}
node_hash = {}

#: dictionary of {hash: node}
hash_node = {}


# Helper functions

def _validate_network_id(network_id):
    if network_id not in networks:
        raise ValueError()


def _citation_to_tuple(citation):
    return tuple([
        citation.get(CITATION_TYPE),
        citation.get(CITATION_NAME),
        citation.get(CITATION_REFERENCE),
        citation.get(CITATION_DATE),
        citation.get(CITATION_AUTHORS),
        citation.get(CITATION_COMMENTS)
    ])


def _build_edge_json(u, v, d):
    return {
        'source': u,
        'target': v,
        'data': d
    }


def _node_to_identifier(node, graph):
    return hash(graph.nodes[node])


# Graph loading functions

def load_networks(connection=None, check_version=None):
    """This function needs to get all networks from the graph cache manager and make a dictionary"""
    gcm = GraphCacheManager(connection=connection)

    for nid, blob in gcm.session.query(Network.id, Network.blob).all():
        log.info('loading network %s')
        graph = from_bytes(blob, check_version=check_version)
        networks[nid] = graph

    update_all_hashes()


# Graph mutation functions

def update_all_hashes():
    for network_id in get_network_ids():
        network = get_network_by_id(network_id)
        update_hashes(network)


def update_hashes(graph):
    """Updates hashes in the hash dicts based on the given graph

    :param graph: A BEL Graph
    :type graph: BELGraph
    """
    for node in graph.nodes_iter():
        h = hash(node)

        node_hash[node] = h
        hash_node[h] = node


def add_canonical_names(graph):
    """Keeps cute names for identifiers and uses BEL names for others"""
    for node, data in graph.nodes_iter(data=True):
        if data[FUNCTION] == COMPLEX and NAMESPACE in data:
            graph.node[node][CNAME] = graph.node[node][NAME]
        elif set(data) == {FUNCTION, NAMESPACE, NAME}:
            graph.node[node][CNAME] = graph.node[node][NAME]
        elif VARIANTS in data:
            graph.node[node][CNAME] = decanonicalize_node(graph, node)
        elif FUSION in data:
            graph.node[node][CNAME] = decanonicalize_node(graph, node)
        elif data[FUNCTION] in {REACTION, COMPOSITE, COMPLEX}:
            graph.node[node][CNAME] = decanonicalize_node(graph, node)
        elif CNAME in graph.node[node]:
            log.debug('cname already in dictionary')
        else:
            raise ValueError('Unexpected dict: {}'.format(data))


def relabel_nodes_to_hashes(graph):
    """Relabels all nodes by their hashes, in place"""
    nx.relabel.relabel_nodes(graph, node_hash, copy=False)


# Graph selection functions

def get_network_ids():
    """Returns a list of all network IDs

    :rtype: list of int
    """
    return list(networks)


def get_network_by_id(network_id):
    """Gets a network by its ID

    :param network_id: The internal ID of the network to get
    :type network_id: int
    :return: A BEL Graph
    :rtype: BELGraph
    """
    return networks[network_id]


def get_namespaces_in_network(network_id):
    return list(get_network_by_id(network_id).namespace_url.values())


def get_annotations_in_network(network_id):
    return list(get_network_by_id(network_id).annotation_url.values())


def get_citations_in_network(network_id):
    g = get_network_by_id(network_id)
    citations = set(data[CITATION] for _, _, data in g.edges_iter(data=True))
    return list(sorted(citations, key=_citation_to_tuple))


def get_edges_in_network(network_id):
    g = get_network_by_id(network_id)
    return list(_build_edge_json(*x) for x in g.edges_iter(data=True))


def get_edges_in_network_filtered(network_id, **kwargs):
    g = get_network_by_id(network_id)
    return list(_build_edge_json(u, v, d) for u, v, d in g.edges_iter(data=True, **kwargs))


def expand_graph_around_node(graph, query_graph, node):
    """Expands around the neighborhoods of the given nodes in the result graph by looking at the original_graph,
    in place.

    :param graph: The graph to add stuff to
    :type graph: BELGraph
    :param query_graph: The graph containing the stuff to add
    :type query_graph: BELGraph
    :param node: A node tuples from the query graph
    :type node: tuple
    """
    if node not in query_graph:
        raise ValueError('{} not in graph {}'.format(node, graph.name))

    if node not in graph:
        graph.add_node(node, attr_dict=query_graph.node[node])

    skip_predecessors = set()
    for predecessor in query_graph.predecessors_iter(node):
        if predecessor in graph:
            skip_predecessors.add(predecessor)
            continue
        graph.add_node(predecessor, attr_dict=query_graph.node[node])

    for predecessor, _, k, d in query_graph.in_edges_iter(node, data=True, keys=True):
        if predecessor in skip_predecessors:
            continue

        if k < 0:
            graph.add_edge(predecessor, node, key=k, attr_dict=d)
        else:
            graph.add_edge(predecessor, node, attr_dict=d)

    skip_successors = set()
    for successor in query_graph.successors_iter(node):
        if successor in graph:
            continue
        graph.add_node(successor, attr_dict=query_graph.node[node])

    for _, successor, k, d in query_graph.out_edges_iter(node, data=True, keys=True):
        if successor in skip_successors:
            continue

        if k < 0:
            graph.add_edge(node, successor, key=k, attr_dict=d)
        else:
            graph.add_edge(node, successor, attr_dict=d)


def query_builder(network_id, expand_nodes=None, remove_nodes=None, **kwargs):
    """

    1. Match by annotations
    2. Add nodes
    3. Remove nodes

    :param network_id:
    :type network_id: int
    :param expand_nodes: Add the neighborhoods around all of these nodes
    :param remove_nodes: Remove these nodes and all of their in/out edges
    :param kwargs: Annotation filters (match all with :code:`pybel.utils.subdict_matches`)
    :return:
    :rtype: BELGraph
    """

    expand_nodes = [] if expand_nodes is None else expand_nodes
    remove_nodes = [] if remove_nodes is None else remove_nodes

    original_graph = get_network_by_id(network_id)

    result_graph = BELGraph()

    for u, v, k, d in original_graph.edges_iter(keys=True, data=True, **{ANNOTATIONS: kwargs}):
        result_graph.add_edge(u, v, key=k, attr_dict=d)

    for node in result_graph.nodes_iter():
        result_graph.node[node] = original_graph.node[node]

    for node in expand_nodes:
        expand_graph_around_node(result_graph, original_graph, node)

    for node in remove_nodes:
        if node not in result_graph:
            log.warning('%s is not in graph %s', node, network_id)
            continue

        result_graph.remove_node(node)

    add_canonical_names(result_graph)
    relabel_nodes_to_hashes(result_graph)

    return result_graph

# TODO create another view for rendering the filters only
# TODO form with all filters and when submit only the ones selected pass to the view
# TODO @ddomingof change this function to build appropriate JSON dictionary
def to_node_link(graph):
    json_graph = to_json_dict(graph)
    return json_graph
