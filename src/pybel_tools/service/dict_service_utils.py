"""
This module contains all of the services necessary through the PyBEL API Definition, backed by a network
dictionary
"""

import logging

import networkx as nx

from pybel import from_bytes, BELGraph
from pybel.constants import *
from pybel.manager.graph_cache import GraphCacheManager
from pybel.manager.models import Network
from ..mutation import add_canonical_names, left_merge
from ..selection import filter_graph

log = logging.getLogger(__name__)


def _citation_to_tuple(citation):
    return tuple([
        citation.get(CITATION_TYPE),
        citation.get(CITATION_NAME),
        citation.get(CITATION_REFERENCE),
        citation.get(CITATION_DATE),
        citation.get(CITATION_AUTHORS),
        citation.get(CITATION_COMMENTS)
    ])


def _node_to_identifier(node, graph):
    return hash(graph.nodes[node])


class DictionaryService:
    def __init__(self):
        #: dictionary of {int id: BELGraph graph}
        self.networks = {}

        #: dictionary of {tuple node: int id}
        self.node_nid = {}

        #: dictionary of {int id: tuple node}
        self.nid_node = {}

        self.full_network = None

    def _validate_network_id(self, network_id):
        if network_id not in self.networks:
            raise ValueError()

    def _build_edge_json(self, graph, u, v, d):
        return {
            'source': graph.node[u] + {'id': self.node_nid[u]},
            'target': graph.node[v] + {'id': self.node_nid[v]},
            'data': d
        }

    def add_network(self, network_id, graph):
        """Adds a network to the module-level cache

        :param network_id: The ID (from the database) to use
        :type network_id: int
        :param graph: A BEL Graph
        :type graph: pybel.BELGraph
        """
        if network_id in self.networks:
            return

        self.networks[network_id] = graph
        self.update_node_indexes(graph)

    def load_networks(self, connection=None, check_version=True):
        """This function needs to get all networks from the graph cache manager and make a dictionary

        :param connection: The database connection string. Default location described in
                           :code:`pybel.manager.cache.BaseCacheManager`
        :type connection: str
        :param check_version: Should the version of the BELGraphs be checked from the database? Defaults to :code`True`.
        :type check_version: bool
        """
        gcm = GraphCacheManager(connection=connection)

        for nid, blob in gcm.session.query(Network.id, Network.blob).all():
            graph = from_bytes(blob, check_version=check_version)
            self.add_network(nid, graph)
            log.info('loaded network: [%s] %s ', nid, graph.document.get(METADATA_NAME, 'UNNAMED'))

        self.full_network = None

    def update_node_indexes(self, graph):
        """Updates identifiers for nodes based on addition order

        :param graph: A BEL Graph
        :type graph: pybel.BELGraph
        """
        for node in graph.nodes_iter():
            if node in self.node_nid:
                continue

            self.node_nid[node] = len(self.node_nid)
            self.nid_node[self.node_nid[node]] = node

    # Graph mutation functions

    def relabel_nodes_to_identifiers(self, graph):
        """Relabels all nodes by their identifiers, in place. This function is a thin wrapper around
        :code:`relabel.relabel_nodes` with the module level variable :code:`node_id` used as the mapping.

        :param graph: A BEL Graph
        :type graph: pybel.BELGraph
        """
        mapping = {k: v for k, v in self.node_nid.items() if k in graph}
        nx.relabel.relabel_nodes(graph, mapping, copy=False)

    # Graph selection functions

    def get_network_ids(self):
        """Returns a list of all network IDs

        :rtype: list of int
        """
        return list(self.networks)

    def get_network_by_id(self, network_id):
        """Gets a network by its ID

        :param network_id: The internal ID of the network to get
        :type network_id: int
        :return: A BEL Graph
        :rtype: BELGraph
        """
        return self.networks[network_id]

    def get_super_network(self):
        """Gets all networks and merges them together. Caches in self.full_network.

        :return: A BEL Graph
        :rtype: pybel.BELGraph
        """

        if self.full_network is not None:
            return self.full_network

        result = BELGraph()

        for network_id in self.get_network_ids():
            left_merge(result, self.get_network_by_id(network_id))

        self.full_network = result

        return result

    def get_node_by_id(self, node_id):
        """Returns the node tuple based on the node id

        :param node_id: The node's id
        :type node_id: int
        :return: the node tuple
        :rtype: tuple
        """
        return self.nid_node[node_id]

    def get_namespaces_in_network(self, network_id):
        """Returns the namespaces in a given network

        :param network_id: The internal ID of the network to get
        :type network_id: int
        :return:
        """
        return list(self.get_network_by_id(network_id).namespace_url.values())

    def get_annotations_in_network(self, network_id):
        return list(self.get_network_by_id(network_id).annotation_url.values())

    def get_citations_in_network(self, network_id):
        g = self.get_network_by_id(network_id)
        citations = set(data[CITATION] for _, _, data in g.edges_iter(data=True))
        return list(sorted(citations, key=_citation_to_tuple))

    def get_edges_in_network(self, network_id):
        g = self.get_network_by_id(network_id)
        return list(self._build_edge_json(*x) for x in g.edges_iter(data=True))

    def get_incident_edges(self, network_id, node_id):
        graph = self.get_network_by_id(network_id)
        node = self.get_node_by_id(node_id)

        successors = list(self._build_edge_json(graph, u, v, d) for u, v, d in graph.out_edges_iter(node, data=True))
        predecessors = list(self._build_edge_json(graph, u, v, d) for u, v, d in graph.in_edges_iter(node, data=True))

        return successors + predecessors

    def _query_helper(self, original_graph, expand_nodes=None, remove_nodes=None, **annotations):
        result_graph = filter_graph(original_graph, expand_nodes=expand_nodes, remove_nodes=remove_nodes, **annotations)
        add_canonical_names(result_graph)
        self.relabel_nodes_to_identifiers(result_graph)
        return result_graph

    def query_all_builder(self, expand_nodes=None, remove_nodes=None, **annotations):
        original_graph = self.get_super_network()
        return self._query_helper(original_graph, expand_nodes, remove_nodes, **annotations)

    def query_filtered_builder(self, network_id, expand_nodes=None, remove_nodes=None, **annotations):
        """Filters a dictionary from the module level cache.

        1. Thin wrapper around :code:`pybel_tools.selection.filter_graph`:
            1. Filter edges by annotations
            2. Add nodes
            3. Remove nodes
        2. Add canonical names
        3. Relabel nodes to identifiers

        :param network_id: The identifier of the network in the database
        :type network_id: int
        :param expand_nodes: Add the neighborhoods around all of these nodes
        :type expand_nodes: list
        :param remove_nodes: Remove these nodes and all of their in/out edges
        :type remove_nodes: list
        :param annotations: Annotation filters (match all with :code:`pybel.utils.subdict_matches`)
        :type annotations: dict
        :return: A BEL Graph
        :rtype: BELGraph
        """
        log.debug('Requested: %s', {
            'network_id': network_id,
            'expand': expand_nodes,
            'delete': remove_nodes,
            'annotations': annotations
        })
        original_graph = self.get_network_by_id(network_id)
        return self._query_helper(original_graph, expand_nodes, remove_nodes, **annotations)
