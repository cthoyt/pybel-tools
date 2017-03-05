"""

This module runs the dictionary-backed PyBEL API

"""

import logging

from flask import Flask, request, jsonify, render_template

from .dict_service_utils import query_builder, id_node, get_network_ids, to_node_link, load_networks

log = logging.getLogger(__name__)

app = Flask(__name__)

APPEND_PARAM = 'append'
REMOVE_PARAM = 'remove'

@app.route('/')
def list_networks():
    return render_template('network_list.html', nids=get_network_ids())


@app.route('/network/<int:network_id>', methods=['GET'])
def get_network(network_id):
    # Convert from list of hashes (as integers) to node tuples
    expand_nodes = [id_node[int(h)] for h in request.args.getlist(APPEND_PARAM)]
    remove_nodes = [id_node[int(h)] for h in request.args.getlist(REMOVE_PARAM)]
    annotations = {k: request.args.getlist(k) for k in request.args if k not in {APPEND_PARAM, REMOVE_PARAM}}

    graph = query_builder(network_id, expand_nodes, remove_nodes, **annotations)

    graph_json = to_node_link(graph)

    return jsonify(graph_json)


@app.route('/nid/')
def get_node_hashes():
    return jsonify(id_node)


@app.route('/nid/<nid>')
def get_node_hash(nid):
    return id_node[nid]


@app.route('/reload')
def reload():
    load_networks()
