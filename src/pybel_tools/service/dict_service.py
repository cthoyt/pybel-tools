"""
This module contains all of the services necessary through the PyBEL API Definition, backed by a network
dictionary
"""

import logging

from pybel import from_bytes
from pybel.constants import *
from pybel.manager.graph_cache import GraphCacheManager
from pybel.manager.models import Network
from pybel.parser.utils import subdict_matches

log = logging.getLogger(__name__)

#: dictionary of {id : BELGraph}
networks = {}


def load_networks(connection=None):
    """This function needs to get all networks from the graph cache manager and make a dictionary"""
    gcm = GraphCacheManager(connection=connection)

    for nid, blob in gcm.session.query(Network.id, Network.blob).all():
        log.info('loading network %s')
        graph = from_bytes(blob)
        networks[nid] = graph


def get_networks():
    return list(networks)


def _validate_network_id(network_id):
    if network_id not in networks:
        raise ValueError()


def get_network_by_id(network_id):
    return networks[network_id]


def get_namespaces_in_network(network_id):
    return list(get_network_by_id(network_id).namespace_url.values())


def get_annotations_in_network(network_id):
    return list(get_network_by_id(network_id).annotations_url.values())


def _citation_to_tuple(citation):
    return tuple([
        citation.get(CITATION_TYPE),
        citation.get(CITATION_NAME),
        citation.get(CITATION_REFERENCE),
        citation.get(CITATION_DATE),
        citation.get(CITATION_AUTHORS),
        citation.get(CITATION_COMMENTS)
    ])


def get_citations_in_network(network_id):
    g = get_network_by_id(network_id)
    citations = set(data[CITATION] for _, _, data in g.edges_iter(data=True))
    return list(sorted(citations, key=_citation_to_tuple))


def _node_to_identifier(node, graph):
    return hash(graph.nodes[node])


def _build_edge_json(u, v, d):
    return {
        'source': u,
        'target': v,
        'data': d
    }


def get_edges_in_network(network_id):
    g = get_network_by_id(network_id)
    return list(_build_edge_json(*x) for x in g.edges_iter(data=True))


def get_edges_in_network_filtered(network_id, **kwargs):
    g = get_network_by_id(network_id)
    return list(
        _build_edge_json(u, v, d) for u, v, d in g.edges_iter(data=True) if subdict_matches(d[ANNOTATIONS], kwargs))
