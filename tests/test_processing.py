import unittest

import pybel
from pybel.constants import *
from pybel_tools.processing import prune, prune_by_type, add_inferred_edges


class TestProcessing(unittest.TestCase):
    def setUp(self):
        if 'PYBEL_BASE' in os.environ:
            test_bel_simple_path = os.path.join(os.environ['PYBEL_BASE'], 'tests', 'bel', 'test_bel.bel')
            self.graph = pybel.from_path(test_bel_simple_path, complete_origin=True)
        else:
            test_bel_simple_url = 'https://raw.githubusercontent.com/pybel/pybel/develop/tests/bel/test_bel.bel'
            self.graph = pybel.from_url(test_bel_simple_url, complete_origin=True)

        self.graph.add_edge((GENE, 'HGNC', 'AKT1'), 'dummy')
        self.graph.add_edge((RNA, 'HGNC', 'EGFR'), 'dummy2')

    def test_base(self):
        self.assertEqual(14, self.graph.number_of_nodes())
        self.assertEqual(16, self.graph.number_of_edges())

    def test_prune_by_type(self):
        prune_by_type(self.graph, GENE)
        self.assertEqual(14, self.graph.number_of_nodes())

    def test_prune(self):
        prune(self.graph)
        self.assertEqual(20, self.graph.number_of_nodes())

    def test_infer(self):
        add_inferred_edges(self.graph, TRANSLATED_TO)
        self.assertEqual(20, self.graph.number_of_edges())
