"""

This module runs the dictionary-backed PyBEL API

"""

import logging

from flask import Flask, request, jsonify, render_template

from ..summary import get_unique_annotations
from .dict_service_utils import query_builder, nid_node, get_network_ids, to_node_link, load_networks, \
    get_incident_edges, get_network_by_id

log = logging.getLogger(__name__)

app = Flask(__name__)

APPEND_PARAM = 'append'
REMOVE_PARAM = 'remove'


@app.route('/')
def list_networks():
    return render_template('network_list.html', nids=get_network_ids())


# TODO @ddomingof create html for this for rendering the filters only in multiple dropdowns wrapped in a form
@app.route('/network/filter/<int:network_id>', methods=['GET'])
def get_filter(network_id):
    graph = get_network_by_id(network_id)

    unique_annotation_dict = get_unique_annotations(graph)

    return render_template('base.html', context={'filters': unique_annotation_dict})


@app.route('/network/<int:network_id>', methods=['GET'])
def get_network(network_id):
    # Convert from list of hashes (as integers) to node tuples
    expand_nodes = [nid_node[int(h)] for h in request.args.getlist(APPEND_PARAM)]
    remove_nodes = [nid_node[int(h)] for h in request.args.getlist(REMOVE_PARAM)]
    annotations = {k: request.args.getlist(k) for k in request.args if k not in {APPEND_PARAM, REMOVE_PARAM}}

    graph = query_builder(network_id, expand_nodes, remove_nodes, **annotations)

    graph_json = to_node_link(graph)

    return jsonify(graph_json)


@app.route('/edges/<int:network_id>/<int:node_id>')
def get_edges(network_id, node_id):
    res = get_incident_edges(network_id, node_id)
    return jsonify(res)


@app.route('/nid/')
def get_node_hashes():
    return jsonify(nid_node)


@app.route('/nid/<nid>')
def get_node_hash(nid):
    return nid_node[nid]


@app.route('/reload')
def reload():
    load_networks()
