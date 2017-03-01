import logging
import unittest

from pybel import BELGraph
from pybel.constants import *
from pybel.parser.language import unqualified_edge_code
from pybel_tools.mutation import collapse_by_central_dogma, collapse_nodes, build_central_dogma_collapse_dict

logging.basicConfig(level=20)
HGNC = 'HGNC'

g1 = GENE, HGNC, '1'
r1 = RNA, HGNC, '1'
p1 = PROTEIN, HGNC, '1'

g2 = GENE, HGNC, '2'
r2 = RNA, HGNC, '2'
p2 = PROTEIN, HGNC, '2'

g3 = GENE, HGNC, '3'
r3 = RNA, HGNC, '3'
p3 = PROTEIN, HGNC, '3'


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


class TestCollapse(unittest.TestCase):
    def test_collapse_1(self):
        g = BELGraph()

        add_simple(g, *p1)
        add_simple(g, *p2)
        add_simple(g, *p3)

        g.add_edge(p1, p3, **{RELATION: INCREASES})
        g.add_edge(p2, p3, **{RELATION: DIRECTLY_INCREASES})

        self.assertEqual(3, g.number_of_nodes())
        self.assertEqual(2, g.number_of_edges())

        d = {
            p1: {p2}
        }

        collapse_nodes(g, d)

        self.assertEqual(2, g.number_of_nodes())
        self.assertEqual(2, g.number_of_edges(), msg=g.edges(data=True, keys=True))

    def test_collapse_dogma_1(self):
        g = BELGraph()

        add_simple(g, *p1)
        add_simple(g, *r1)

        g.add_edge(r1, p1, key=unqualified_edge_code[TRANSLATED_TO], **{RELATION: TRANSLATED_TO})

        self.assertEqual(2, g.number_of_nodes())
        self.assertEqual(1, g.number_of_edges())

        cd = build_central_dogma_collapse_dict(g)

        print(cd)

        collapse_by_central_dogma(g)

        self.assertEqual(1, g.number_of_nodes())
        self.assertEqual(0, g.number_of_edges())

    def test_collapse_dogma_2(self):
        g = BELGraph()

        add_simple(g, *p1)
        add_simple(g, *r1)
        add_simple(g, *g1)

        g.add_edge(r1, p1, key=unqualified_edge_code[TRANSLATED_TO], **{RELATION: TRANSLATED_TO})
        g.add_edge(g1, r1, key=unqualified_edge_code[TRANSCRIBED_TO], **{RELATION: TRANSCRIBED_TO})

        self.assertEqual(3, g.number_of_nodes())
        self.assertEqual(2, g.number_of_edges())

        collapse_by_central_dogma(g)

        self.assertEqual(1, g.number_of_nodes())
        self.assertEqual(0, g.number_of_edges())

    def test_collapse_dogma_3(self):
        g = BELGraph()

        add_simple(g, *r1)
        add_simple(g, *g1)

        g.add_edge(g1, r1, key=unqualified_edge_code[TRANSCRIBED_TO], **{RELATION: TRANSCRIBED_TO})

        self.assertEqual(2, g.number_of_nodes())
        self.assertEqual(1, g.number_of_edges())

        collapse_by_central_dogma(g)

        self.assertEqual(1, g.number_of_nodes())
        self.assertEqual(0, g.number_of_edges())
