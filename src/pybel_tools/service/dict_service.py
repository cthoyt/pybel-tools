"""

This module runs the dictionary-backed PyBEL API

"""

import logging

from flask import Flask, request, jsonify, render_template

from pybel.io import to_json_dict
from .dict_service_utils import DictionaryService
from ..summary import get_unique_annotations

log = logging.getLogger(__name__)

APPEND_PARAM = 'append'
REMOVE_PARAM = 'remove'
DICTIONARY_SERVICE = 'dictionary_service'


def get_dict_service(dsa):
    """Gets the latent PyBEL Dictionary Service from a Flask app

    :param dsa: A Flask App
    :type dsa: Flask
    :return: The latent dictionary service
    :rtype: DictionaryService
    """
    return dsa.config[DICTIONARY_SERVICE]


def build_dictionary_service_app(dsa):
    """Builds the PyBEL Dictionary-Backed API Service

    :param dsa: A Flask App
    :type dsa: Flask
    """

    api = DictionaryService()

    dsa.config[DICTIONARY_SERVICE] = api

    @dsa.route('/')
    def list_networks():
        nids = api.get_network_ids()
        return render_template('network_list.html', nids=nids)

    @dsa.route('/network/filter/<int:network_id>', methods=['GET'])
    def get_filter(network_id):
        graph = api.get_network_by_id(network_id)

        unique_annotation_dict = get_unique_annotations(graph)

        json_dict = [{'text': k, 'children': [{'text': annotation} for annotation in v]} for k, v in
                     unique_annotation_dict.items()]

        return render_template('network_visualization.html', **{'filter_json': json_dict, 'network_id': network_id})

    @dsa.route('/network/<int:network_id>', methods=['GET'])
    def get_network(network_id):
        # Convert from list of hashes (as integers) to node tuples
        expand_nodes = [api.nid_node[int(h)] for h in request.args.getlist(APPEND_PARAM)]
        remove_nodes = [api.nid_node[int(h)] for h in request.args.getlist(REMOVE_PARAM)]
        annotations = {k: request.args.getlist(k) for k in request.args if k not in {APPEND_PARAM, REMOVE_PARAM}}

        graph = api.query_builder(network_id, expand_nodes, remove_nodes, **annotations)

        graph_json = to_node_link(graph)

        return jsonify(graph_json)

    @dsa.route('/edges/<int:network_id>/<int:node_id>')
    def get_edges(network_id, node_id):
        res = api.get_incident_edges(network_id, node_id)
        return jsonify(res)

    @dsa.route('/nid/')
    def get_node_hashes():
        return jsonify(api.nid_node)

    @dsa.route('/nid/<nid>')
    def get_node_hash(nid):
        return api.get_node_by_id(nid)

    @dsa.route('/reload')
    def reload():
        api.load_networks()


def to_node_link(graph):
    """Converts the graph to a JSON object that is appropriate for the PyBEL API. This is not necessarily the same
    as :code:`pybel.io.to_json_dict` because that function makes a standard node-link structure, and this function
    auguments/improves on the standard structure.

    After conversion to json, this dict will be passed to :code:`flask.jsonify` for rendering

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :return: The JSON object representing this dictionary
    :rtype: dict
    """
    json_graph = to_json_dict(graph)
    return json_graph


app = Flask(__name__)
build_dictionary_service_app(app)
