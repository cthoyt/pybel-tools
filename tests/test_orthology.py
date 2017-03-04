import unittest

from pybel import BELGraph
from pybel_tools.orthology import integrate_orthologies, HGNC, MGI, RGD
from pybel.constants import *
from tests.constants import orthology_path


class TestOrthology(unittest.TestCase):
    def test_orthology(self):
        graph = BELGraph()


        g1 = GENE, HGNC, 'A1BG'
        g2 = GENE, HGNC, 'b'
        g3 = GENE, MGI, 'a'

        graph.add_simple_node(*g1)
        graph.add_simple_node(*g2)
        graph.add_simple_node(*g3)

        with open(orthology_path) as f:
            integrate_orthologies(graph, f)
