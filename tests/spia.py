# -*- coding: utf-8 -*-

"""This module contains tests for the SPIA exporter."""

import logging
import unittest

from pandas import DataFrame

from pybel.dsl import protein, pmod, rna
from pybel.examples.sialic_acid_example import sialic_acid_graph
from pybel_tools.analysis.spia import build_matrices, update_matrix, get_matrix_index, bel_to_spia, spia_to_excel

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

        update_matrix(test_dict, sub, obj, {'relation': 'decreases'})

        self.assertEqual(test_dict["inhibition_ubiquination"]['A']['B'], 1)
        self.assertEqual(test_dict["inhibition_ubiquination"]['A']['A'], 0)
        self.assertEqual(test_dict["inhibition_ubiquination"]['B']['A'], 0)
        self.assertEqual(test_dict["inhibition_ubiquination"]['B']['B'], 0)

    def test_update_matrix_activation_ubiquination(self):
        """Test updating the matrix with an activation ubiquitination."""
        sub = protein(namespace='HGNC', name='A', identifier='1')
        obj = protein(namespace='HGNC', name='B', identifier='2', variants=[pmod('Ub')])

        index = {'A', 'B'}

        test_dict = {}

        test_matrix= DataFrame(0, index=index, columns=index)

        test_dict["activation_ubiquination"] = test_matrix

        update_matrix(test_dict, sub, obj, {'relation': 'increases'})

        self.assertEqual(test_dict["activation_ubiquination"]['A']['B'], 1)
        self.assertEqual(test_dict["activation_ubiquination"]['A']['A'], 0)
        self.assertEqual(test_dict["activation_ubiquination"]['B']['A'], 0)
        self.assertEqual(test_dict["activation_ubiquination"]['B']['B'], 0)

    def test_update_matrix_inhibition_phosphorylation(self):
        """Test updating the matrix with an inhibition phosphorylation."""
        sub = protein(namespace='HGNC', name='A', identifier='1')
        obj = protein(namespace='HGNC', name='B', identifier='2', variants=[pmod('Ph')])

        index = {'A', 'B'}

        test_dict = {}

        test_matrix= DataFrame(0, index=index, columns=index)

        test_dict["inhibition_phosphorylation"] = test_matrix

        update_matrix(test_dict, sub, obj, {'relation': 'decreases'})

        self.assertEqual(test_dict["inhibition_phosphorylation"]['A']['B'], 1)
        self.assertEqual(test_dict["inhibition_phosphorylation"]['A']['A'], 0)
        self.assertEqual(test_dict["inhibition_phosphorylation"]['B']['A'], 0)
        self.assertEqual(test_dict["inhibition_phosphorylation"]['B']['B'], 0)

    def test_update_matrix_activation_phosphorylation(self):
        """Test updating the matrix with an activation phosphorylation."""
        data = bel_to_spia(self.sialic_acid_graph)
        spia_to_excel(data, 'test')

        sub = protein(namespace='HGNC', name='A', identifier='1')
        obj = protein(namespace='HGNC', name='B', identifier='2', variants=[pmod('Ph')])

        index = {'A', 'B'}

        test_dict = {}

        test_matrix= DataFrame(0, index=index, columns=index)

        test_dict["activation_phosphorylation"] = test_matrix

        update_matrix(test_dict, sub, obj, {'relation': 'increases'})

        self.assertEqual(test_dict["activation_phosphorylation"]['A']['B'], 1)
        self.assertEqual(test_dict["activation_phosphorylation"]['A']['A'], 0)
        self.assertEqual(test_dict["activation_phosphorylation"]['B']['A'], 0)
        self.assertEqual(test_dict["activation_phosphorylation"]['B']['B'], 0)

    def test_update_matrix_expression(self):
        """Test updating the matrix with RNA expression."""
        sub = protein(namespace='HGNC', name='A', identifier='1')
        obj = rna(namespace='HGNC', name='B', identifier='2')

        index = {'A', 'B'}

        test_dict = {}

        test_matrix= DataFrame(0, index=index, columns=index)

        test_dict["expression"] = test_matrix

        update_matrix(test_dict, sub, obj, {'relation': 'increases'})

        self.assertEqual(test_dict["expression"]['A']['B'], 1)
        self.assertEqual(test_dict["expression"]['A']['A'], 0)
        self.assertEqual(test_dict["expression"]['B']['A'], 0)
        self.assertEqual(test_dict["expression"]['B']['B'], 0)

    def test_update_matrix_activation(self):
        """Test updating the matrix with activation."""
        sub = protein(namespace='HGNC', name='A', identifier='1')
        obj = protein(namespace='HGNC', name='B', identifier='2')

        index = {'A', 'B'}

        test_dict = {}

        test_matrix= DataFrame(0, index=index, columns=index)

        test_dict["activation"] = test_matrix

        update_matrix(test_dict, sub, obj, {'relation': 'increases'})

        self.assertEqual(test_dict["activation"]['A']['B'], 1)
        self.assertEqual(test_dict["activation"]['A']['A'], 0)
        self.assertEqual(test_dict["activation"]['B']['A'], 0)
        self.assertEqual(test_dict["activation"]['B']['B'], 0)

    def test_update_matrix_association(self):
        """Test updating the matrix with association."""
        sub = protein(namespace='HGNC', name='A', identifier='1')
        obj = protein(namespace='HGNC', name='B', identifier='2')

        index = {'A', 'B'}

        test_dict = {}

        test_matrix= DataFrame(0, index=index, columns=index)

        test_dict["binding_association"] = test_matrix

        update_matrix(test_dict, sub, obj, {'relation': 'association'})

        self.assertEqual(test_dict["binding_association"]['A']['B'], 1)
        self.assertEqual(test_dict["binding_association"]['A']['A'], 0)
        self.assertEqual(test_dict["binding_association"]['B']['A'], 0)
        self.assertEqual(test_dict["binding_association"]['B']['B'], 0)
