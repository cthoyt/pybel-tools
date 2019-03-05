# -*- coding: utf-8 -*-

"""Utilities to assemble a BEL graph as bipartite graph of nodes and reified edges."""

import unittest

import networkx as nx

from pybel import BELGraph
from pybel.dsl import activity, pmod, protein
from pybel.testing.utils import n

__all__ = [
    'reify_bel_graph',
]

SUBJECT = 'subject'
OBJECT = 'object'


def reify_bel_graph(bel_graph: BELGraph) -> nx.DiGraph:
    """Generate a new graph with reified edges."""
    raise NotImplementedError


cdk5 = protein('HGNC', 'CDK5', 'HGNC:1774')
gsk3b = protein('HGNC', 'GSK3B', 'HGNC:4617')
p_tau = protein('HGNC', 'MAPT', 'HGNC:6893', variants=pmod('Ph'))


class TestAssembleReifiedGraph(unittest.TestCase):
    """Test assembly of reified graphs."""

    def help_test_graphs_equal(self, expected: nx.DiGraph, actual: nx.DiGraph) -> None:
        """Test that two DiGraphs are equal."""
        self.assertIsNotNone(actual)
        self.assertIsInstance(actual, nx.DiGraph)
        self.assertEqual(expected.number_of_nodes(), actual.number_of_nodes())
        self.assertEqual(expected.number_of_edges(), actual.number_of_edges())
        for node in expected:
            self.assertIn(node, actual)

        for u, v in expected.edges():
            self.assertIn((u, v), actual.edges)

    def test_convert_phosphorylates(self):
        """Test the conversion of a BEL statement like ``act(p(X)) -> p(Y, pmod(Ph))."""
        bel_graph = BELGraph()
        bel_graph.add_directly_increases(
            cdk5,
            p_tau,
            evidence=n(),
            citation=n(),
            subject_modifier=activity('kin'),
        )

        expected_reified_graph = nx.DiGraph()
        r_edge = 0
        expected_reified_graph.add_node(r_edge, label='phosphorylates')
        expected_reified_graph.add_edge(cdk5, r_edge, label=SUBJECT)
        expected_reified_graph.add_edge(p_tau, r_edge, label=OBJECT)

        reified_graph = reify_bel_graph(bel_graph)
        self.help_test_graphs_equal(expected_reified_graph, reified_graph)

    def test_convert_two_phosphorylates(self):
        """Test that two phosphorylations of the same object get different reified nodes."""
        bel_graph = BELGraph()
        for kinase in (cdk5, gsk3b):
            bel_graph.add_directly_increases(
                kinase,
                p_tau,
                evidence=n(),
                citation=n(),
                subject_modifier=activity('kin'),
            )

        expected_reified_graph = nx.DiGraph()
        re1, re2 = 0, 1
        expected_reified_graph.add_node(re1, label='phosphorylates')
        expected_reified_graph.add_edge(cdk5, re1, label=SUBJECT)
        expected_reified_graph.add_edge(p_tau, re1, label=OBJECT)

        expected_reified_graph.add_node(re2, label='phosphorylates')
        expected_reified_graph.add_edge(gsk3b, re2, label=SUBJECT)
        expected_reified_graph.add_edge(p_tau, re2, label=OBJECT)

        reified_graph = reify_bel_graph(bel_graph)
        self.help_test_graphs_equal(expected_reified_graph, reified_graph)

        # FIXME how to test the reified edges that have random numbers on them?


if __name__ == '__main__':
    unittest.main()
