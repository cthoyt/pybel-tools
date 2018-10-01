# -*- coding: utf-8 -*-

"""This module contains tests for the SPIA exporter."""

import logging
import unittest

from pandas import DataFrame

from pybel.dsl import protein, pmod
from pybel.examples.sialic_acid_example import sialic_acid_graph
from pybel_tools.analysis.spia import build_matrices, get_matrix_index, update_matrix

log = logging.getLogger(__name__)
log.setLevel(10)


class TestSpia(unittest.TestCase):
    """Test SPIA Exporter."""

    def setUp(self):
        self.sialic_acid_graph = sialic_acid_graph.copy()

    def test_build_matrix(self):
        """Test build empty matrix."""

        node_names = get_matrix_index(self.sialic_acid_graph)

        matrix_dict = build_matrices(node_names)

        nodes = {'PTPN11', 'TREM2', 'PTPN6', 'TYROBP', 'CD33', 'SYK'}

        self.assertEqual(set(matrix_dict["activation"].columns), nodes)
        self.assertEqual(set(matrix_dict["repression"].index), nodes)

    def test_update_matrix_inhibition_ubiquination(self):
        """Test updating the matrix with an inhibition ubiquitination."""
        sub = protein(namespace='HGNC', name='A', identifier='1')
        obj = protein(namespace='HGNC', name='B', identifier='2', variants=[pmod('Ub')])

        index = {'A', 'B'}

        test_dict = {}

        test_matrix= DataFrame(0, index=index, columns=index)
        # Initialize matrix correctly
        self.assertEqual(test_matrix.values.all(), 0)

        test_dict["inhibition_ubiquination"] = test_matrix

        update_matrix(test_dict, sub, obj, {'relation': 'decrease'})

        self.assertEqual(test_dict["inhibition_ubiquination"]['A']['B'], 1)
        self.assertEqual(test_dict["inhibition_ubiquination"]['A']['A'], 0)
        self.assertEqual(test_dict["inhibition_ubiquination"]['B']['A'], 0)
        self.assertEqual(test_dict["inhibition_ubiquination"]['B']['B'], 0)
