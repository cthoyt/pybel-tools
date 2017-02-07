import pybel
from io import StringIO
import jinja2

import os
import json

PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = jinja2.Environment(
    autoescape=False,
    loader=jinja2.FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False)
TEMPLATE_ENVIRONMENT.globals['STATIC_PREFIX'] = PATH + '/static/'


def graph_to_json(graph):
    """Returns json representation of the graph"""

    # Tested in notebook
    io = StringIO()

    pybel.to_json(graph, io)

    # to_json output needs to be modified (single quotes and backslashes)
    io.getvalue()

    return io


def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def create_graph_html(graph):
    fname = "graph_visualization.html"

    context = {
        'json': graph,
        'number_nodes': '10',
        'number_edges': '32434'
    }

    with open(fname, 'w') as f:
        html = render_template('graph_template.html', context)
        f.write(html)


def main():
    with open('graph.json') as data_file:
        data = json.load(data_file)
    create_graph_html(data)


########################################

if __name__ == "__main__":
    main()
