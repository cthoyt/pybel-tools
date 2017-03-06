import os

from pybel.constants import FUNCTION, NAMESPACE, NAME

dir_path = os.path.dirname(os.path.realpath(__file__))
resources_path = os.path.join(dir_path, 'resources')

rgd_orthologs_path = os.path.join(resources_path, 'RGD_ORTHOLOGS.txt')


def add_simple(graph, function, namespace, name):
    """Adds a simple node to the graph that just has a function, namespace, and name

    :param graph: A BEL Graph
    :type graph: BELGraph
    :param function: The function of the node from :code:`pybel.constants` (GENE, RNA, PROTEIN, etc)
    :type function: str
    :param namespace: The namespace for this node
    :type namespace: str
    :param name: The name for this node
    :type name: str
    """
    graph.add_node((function, namespace, name), **{FUNCTION: function, NAMESPACE: namespace, NAME: name})