import os
import unittest

from pybel import BELGraph
from pybel.constants import *
from pybel_tools.orthology import integrate_orthologies, HGNC, MGI
from tests.constants import orthology_path, add_simple


@unittest.skipUnless('PYBEL_TOOLS_BASE' in os.environ, 'Not in development environment')
class TestOrthology(unittest.TestCase):
    def test_orthology(self):
        graph = BELGraph()

        g1 = GENE, HGNC, 'A1BG'
        g2 = GENE, HGNC, 'b'
        g3 = GENE, MGI, 'a'

        add_simple(graph, *g1)
        add_simple(graph, *g2)
        add_simple(graph, *g3)

        with open(orthology_path) as f:
            integrate_orthologies(graph, f)
