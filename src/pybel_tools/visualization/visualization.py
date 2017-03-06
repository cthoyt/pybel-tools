"""

This module provides functions for making HTML visualizations of BEL Graphs

"""

from __future__ import print_function

import os

import jinja2

from pybel.io import to_jsons

HERE = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_ENVIRONMENT = jinja2.Environment(
    autoescape=False,
    loader=jinja2.FileSystemLoader(os.path.join(HERE, 'templates')),
    trim_blocks=False
)

TEMPLATE_ENVIRONMENT.globals['STATIC_PREFIX'] = HERE + '/static/'


def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def render_graph_template(context):
    """Renders the graph template as an HTML string

    :param context: The data dictionary to pass to the Jinja templating engine
    :type context: dict
    :rtype: str
    """
    return render_template('graph_template.html', **context)


def build_graph_context(graph):
    """Builds the data dictionary to be used by the Jinja templating engine in :py:func:`to_html`

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    """
    graph_json_str = to_jsons(graph)

    return {
        'json': graph_json_str,
        'number_nodes': '10',
        'number_edges': '32434'
    }


def to_html(graph):
    """Creates an HTML visualization for the given JSON representation of a BEL graph

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :rtype: str
    """
    return render_graph_template(build_graph_context(graph))


def to_html_file(graph, file):
    """Writes the HTML visualization to a file or file-like

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param file: A file or file-like
    :type file: file
    """
    print(to_html(graph), file=file)


def to_html_path(graph, path):
    """Writes the HTML visualization to a file specified by the file path

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param path: The file path
    :type path: str
    """
    with open(os.path.expanduser(path), 'w') as f:
        to_html_file(graph, f)
