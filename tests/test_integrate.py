import unittest

from pybel import BELGraph
from pybel.constants import *
from pybel_tools.integration import overlay_type_data
from pybel_tools.mutation import left_merge
import json
HGNC = 'HGNC'


class TestIntegrate(unittest.TestCase):
    def test_overlay(self):
        g = BELGraph()

        g1 = GENE, HGNC, 'a'
        g2 = GENE, HGNC, 'b'
        g3 = GENE, HGNC, 'c'
        g4 = GENE, HGNC, 'd'
        r1 = RNA, HGNC, 'e'
        p1 = PROTEIN, HGNC, 'f'

        g.add_simple_node(*g1)
        g.add_simple_node(*g2)
        g.add_simple_node(*g3)
        g.add_simple_node(*g4)
        g.add_simple_node(*r1)
        g.add_simple_node(*p1)

        label = 'dgxp'

        overlay_type_data(g, {'a': 1, 'b': 2, 'c': -1}, label, GENE, HGNC, impute=0)

        for node in g1, g2, g3, g4:
            self.assertIn(label, g.node[node])

        for node in r1, p1:
            self.assertNotIn(label, g.node[node])

        self.assertEqual(1, g.node[g1][label])
        self.assertEqual(2, g.node[g2][label])
        self.assertEqual(-1, g.node[g3][label])
        self.assertEqual(0, g.node[g4][label])

    def test_left_merge(self):

        p1 = PROTEIN, HGNC, 'a'
        p2 = PROTEIN, HGNC, 'b'
        p3 = PROTEIN, HGNC, 'c'

        g = BELGraph()

        g.add_simple_node(*p1)
        g.add_simple_node(*p2)

        g.add_edge(p1, p2, attr_dict={
            RELATION: INCREASES,
            CITATION: {
                CITATION_TYPE: 'PubMed',
                CITATION_REFERENCE: 1,
                CITATION_NAME: 'PMID1'
            },
            EVIDENCE: 'Evidence 1',
            ANNOTATIONS: {}
        })

        h = BELGraph()

        h.add_simple_node(*p1)
        h.add_simple_node(*p2)
        h.add_simple_node(*p3)

        h.node[p1]['EXTRANEOUS'] = 'MOST DEFINITELY'
        h.node[p3]['EXTRANEOUS'] = 'MOST DEFINITELY'

        h.add_edge(p1, p2, attr_dict={
            RELATION: INCREASES,
            CITATION: {
                CITATION_TYPE: 'PubMed',
                CITATION_REFERENCE: 1,
                CITATION_NAME: 'PMID1'
            },
            EVIDENCE: 'Evidence 1',
            ANNOTATIONS: {}
        })

        h.add_edge(p1, p2, attr_dict={
            RELATION: INCREASES,
            CITATION: {
                CITATION_TYPE: 'PubMed',
                CITATION_REFERENCE: 2,
                CITATION_NAME: 'PMID2'
            },
            EVIDENCE: 'Evidence 2',
            ANNOTATIONS: {}
        })

        h.add_edge(p1, p3, attr_dict={
            RELATION: INCREASES,
            CITATION: {
                CITATION_TYPE: 'PubMed',
                CITATION_REFERENCE: 1,
                CITATION_NAME: 'PMID1'
            },
            EVIDENCE: 'Evidence 3',
            ANNOTATIONS: {}
        })

        self.assertEqual(2, g.number_of_nodes())
        self.assertEqual(1, g.number_of_edges())
        self.assertEqual(3, h.number_of_nodes())
        self.assertEqual(3, h.number_of_edges())

        left_merge(g, h)

        self.assertNotIn('EXTRANEOUS', g.node[p1])
        self.assertIn('EXTRANEOUS', g.node[p3])
        self.assertEqual('MOST DEFINITELY', g.node[p3]['EXTRANEOUS'])

        self.assertEqual(3, g.number_of_nodes())
        self.assertEqual(3, g.number_of_edges(), msg="G edges:\n{}".format(json.dumps(g.edges(data=True), indent=2)))
        self.assertEqual(3, h.number_of_nodes())
        self.assertEqual(3, h.number_of_edges())



