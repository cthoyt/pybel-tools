import pybel
from io import StringIO

def graph_to_json(graph):
    """Returns json representation of the graph"""

    #Tested in notebook
    io = StringIO()

    pybel.to_json(graph, io)

    # to_json output needs to be modified (single quotes and backslashes)
    io.getvalue()

    return io

