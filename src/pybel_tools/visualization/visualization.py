from __future__ import print_function

import json
import os

import jinja2

import pybel


HERE = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_ENVIRONMENT = jinja2.Environment(
    autoescape=False,
    loader=jinja2.FileSystemLoader(os.path.join(HERE, 'templates')),
    trim_blocks=False
)

TEMPLATE_ENVIRONMENT.globals['STATIC_PREFIX'] =  HERE + '/static/'


def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def render_graph_template(context):
    return render_template('graph_template.html', context)


def build_graph_context(graph):
    """
    :param graph:
    :type graph: pybel.BELGraph
    :return:
    """
    graph_json_str = pybel.io.to_jsons(graph)

    node_dict = {node: hash(node) for node in graph}

    return {
        'json': graph_json_str,
        # 'node_hashes': json.dumps(node_dict),
        'number_nodes': '10',
        'number_edges': '32434'
    }


def to_html(graph):
    """Creates an HTML visualization for the given JSON representation of a BEL graph

    :param graph:
    :type graph:
    :return:
    """
    return render_graph_template(build_graph_context(graph))


# def main():
#     with open(os.path.expanduser('~/Desktop/graph.json')) as f:
#         data = json.load(f)
#
#     with open(os.path.expanduser('~/Desktop/test.html'), 'w') as f:
#         print(render_graph_template({
#             'json': json.dumps(data),
#             'number_nodes': '10',
#             'number_edges': '32434'
#         }), file=f)


if __name__ == "__main__":
    main()
