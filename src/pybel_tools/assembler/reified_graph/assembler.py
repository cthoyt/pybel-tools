# -*- coding: utf-8 -*-

"""Utilities to assemble a BEL graph as bipartite graph of nodes and reified edges."""

import logging
import unittest

import networkx as nx

from abc import ABC, abstractmethod
from pybel import BELGraph
from pybel.dsl import activity, pmod, protein, BaseEntity
from pybel.testing.utils import n
from typing import Dict, Optional, Tuple

__all__ = [
    'reify_bel_graph',
]

SUBJECT = 'subject'
OBJECT = 'object'


class ReifiedConverter(ABC):
    """Base class for BEL -> Reified edges graph conversion"""

    @staticmethod
    @abstractmethod
    def predicate(u: BaseEntity, v: BaseEntity, key: str, edge_data: Dict) -> bool:
        """Test if a BEL edge corresponds to the converter."""

    @staticmethod
    @abstractmethod
    def convert(u: BaseEntity, v: BaseEntity, key: str, edge_data: Dict) \
            -> Tuple[BaseEntity, Tuple[int, str], BaseEntity]:
        """Convert a BEL edge to a reified edge."""


class IntermediateConverter(ReifiedConverter):
    """Implements the convert method"""

    target_relation = ...

    @classmethod
    def convert(cls, u: BaseEntity, v: BaseEntity, key: str, edge_data: Dict) \
            -> Tuple[BaseEntity, Tuple[int, str], BaseEntity]:
        # TODO create vertex X
        # TODO i need an autoincrement somewhere
        pred_vertex = (0, cls.target_relation)
        # TODO v loses pmod(Ph)?
        # mod_v = v.deepcopy()
        object_edge = (pred_vertex, OBJECT, v)
        # TODO ask what to do if it is a decrease of the phosphorylation

        return u, pred_vertex, v


class PhosphorylationConverter(IntermediateConverter):
    """Converts BEL statements of the form A B p(C, pmod(Ph))"""

    target_relation = "phosphorylates"

    @classmethod
    def predicate(cls, u: BaseEntity, v: BaseEntity, key: str, edge_data: Dict) -> bool:
        if "variant" in v:
            print("there is a variant")

        return "relation" in edge_data and edge_data['relation'] in ['directlyIncreases', 'increases']


def reify_edge(u: BaseEntity, v: BaseEntity, key: str, edge_data: Dict) \
    -> Optional[Tuple[BaseEntity, Tuple[int, str], BaseEntity]]:

    converters = [
        PhosphorylationConverter
    ]
    for converter in converters:
        if converter.predicate(u, v, key, edge_data):
            return converter.convert(u, v, key, edge_data)

    logging.warning(f"No converter found for {u}, {v}")

    # No converter found
    return None


def reify_bel_graph(bel_graph: BELGraph) -> nx.DiGraph:
    """Generate a new graph with reified edges."""

    reified_graph = nx.DiGraph()

    for edge in bel_graph.edges(keys=True):
        if len(edge) == 2:
            (u, v) = edge
            key = None
            data = bel_graph[u][v]
        elif len(edge) == 3:
            (u, v, key) = edge
            data = bel_graph[u][v][key]
        print(u)
        print(v)
        print(data)

        reified_edge = reify_edge(u, v, key, data)
        if reified_edge:
            new_u, reif_edge, new_v = reified_edge
            reified_graph.add_edge(new_u, reif_edge, label=SUBJECT)
            reified_graph.add_edge(reif_edge, new_v, label=OBJECT)

    return reified_graph


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
