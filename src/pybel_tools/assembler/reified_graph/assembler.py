# -*- coding: utf-8 -*-

"""Utilities to assemble a BEL graph as bipartite graph of nodes and
reified edges."""

# TODO ASK if v loses pmod(Ph), we won't be able to capture
#  paths like X -> p(Y, pmod(Ph)) -> Z
# TODO ASK what to do if it is a decrease of the
#  phosphorylation (dephosphorylation or -1 phosphorylation)
#  *In BioKEEN, it is increasesAmount / decreasesAmount


from itertools import count
import logging
import unittest

import networkx as nx

from abc import ABC, abstractmethod
from pybel import BELGraph
from pybel.constants import (
    ACTIVITY, CAUSAL_INCREASE_RELATIONS, MODIFIER, OBJECT
)

from pybel.dsl import abundance, activity, BaseEntity, pmod, protein
from pybel.testing.utils import n
from typing import Dict, Optional, Tuple

__all__ = [
    'reify_bel_graph',
]

REIF_SUBJECT = 'subject'
REIF_OBJECT = 'object'

ACTIVATES = 'activates'
PHOSPHORYLATES = 'phosphorylates'
INCREASES_ABUNDANCE = "increasesAbundanceOf"

REIFIED_RELATIONS = [
    ACTIVATES, PHOSPHORYLATES, INCREASES_ABUNDANCE
]


class ReifiedConverter(ABC):
    """Base class for BEL -> Reified edges graph conversion"""

    target_relation = ...

    @staticmethod
    @abstractmethod
    def predicate(u: BaseEntity, v: BaseEntity,
                  key: str, edge_data: Dict) -> bool:
        """Test if a BEL edge corresponds to the converter."""

    @classmethod
    def convert(cls, u: BaseEntity, v: BaseEntity, key: str, edge_data: Dict) \
            -> Tuple[BaseEntity, str, BaseEntity]:
        """Convert a BEL edge to a reified edge."""

        pred_vertex = cls.target_relation
        return u, pred_vertex, v


class PhosphorylationConverter(ReifiedConverter):
    """Converts BEL statements of the form A B p(C, pmod(Ph))"""

    target_relation = "phosphorylates"

    @classmethod
    def predicate(cls, u: BaseEntity, v: BaseEntity,
                  key: str, edge_data: Dict) -> bool:
        return ("relation" in edge_data and
                edge_data['relation'] in CAUSAL_INCREASE_RELATIONS and
                "variants" in v and
                pmod('Ph') in v["variants"])


class AbundanceIncreaseConverter(ReifiedConverter):
    """Converts BEL statements of the form A B C, where B in [->, =>]
    and A and C don't fall in another special case (pmod, act, ...)
    """

    target_relation = INCREASES_ABUNDANCE

    @classmethod
    def predicate(cls, u: BaseEntity, v: BaseEntity,
                  key: str, edge_data: Dict) -> bool:
        return ("relation" in edge_data and
                edge_data['relation'] in CAUSAL_INCREASE_RELATIONS)


class ActivationConverter(ReifiedConverter):
    """Converts BEL statements of the form A B act(C)"""

    target_relation = "activates"

    @classmethod
    def predicate(cls, u: BaseEntity, v: BaseEntity,
                  key: str, edge_data: Dict) -> bool:
        return (
                "relation" in edge_data and
                edge_data['relation'] in CAUSAL_INCREASE_RELATIONS and
                edge_data.get(OBJECT) and
                edge_data.get(OBJECT).get(MODIFIER) == ACTIVITY
        )


def reify_edge(u: BaseEntity, v: BaseEntity, key: str, edge_data: Dict) \
        -> Optional[Tuple[BaseEntity, str, BaseEntity]]:

    converters = [
        PhosphorylationConverter,
        AbundanceIncreaseConverter
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
    gen = count()

    for edge in bel_graph.edges(keys=True):
        (u, v, key) = edge
        data = bel_graph[u][v][key]

        reified_edge = reify_edge(u, v, key, data)
        if reified_edge:
            new_u, reif_edge_label, new_v = reified_edge
            reif_edge_num = next(gen)
            reified_graph.add_node(reif_edge_num, label=reif_edge_label)
            reified_graph.add_edge(new_u, reif_edge_num, label=REIF_SUBJECT)
            reified_graph.add_edge(new_v, reif_edge_num, label=REIF_OBJECT)

    return reified_graph


cdk5 = protein('HGNC', 'CDK5', 'HGNC:1774')
gsk3b = protein('HGNC', 'GSK3B', 'HGNC:4617')
p_tau = protein('HGNC', 'MAPT', 'HGNC:6893', variants=pmod('Ph'))
# act(p(HGNC:FAS), ma(cat)) increases act(p(HGNC:CASP8), ma(cat))
fas = protein('HGNC', 'FAS', 'HGNC:11920')
# TODO ^ ma = molecular_activity ? cat = GO:0003824 (catalytic activity)

# a(CHEBI:oxaliplatin) increases a(MESHC:"Reactive Oxygen Species")
oxaliplatin = abundance('CHEBI', 'oxaliplatin', 'CHEBI:31941')
reactive_o_species = abundance('MESHC', 'Reactive Oxygen Species', 'D017382')
# p(HGNC:MYC) decreases r(HGNC:CCNB1)


class TestAssembleReifiedGraph(unittest.TestCase):
    """Test assembly of reified graphs."""

    def help_test_graphs_equal(self, expected: nx.DiGraph, actual: nx.DiGraph)\
            -> None:
        """Test that two DiGraphs are equal."""
        self.assertIsNotNone(actual)
        self.assertIsInstance(actual, nx.DiGraph)
        self.assertEqual(expected.number_of_nodes(), actual.number_of_nodes())
        self.assertEqual(expected.number_of_edges(), actual.number_of_edges())
        for node in expected:
            self.assertIn(node, actual)

        actual_edges_list = [(u_, expected.nodes[v_])
                             for u_, v_ in actual.edges]
        for u, v in expected.edges():
            self.assertIn((u, expected.nodes[v]), actual_edges_list)
        # TODO if the reified graph was a class,edge comparison can be a method

    # TODO repeat for acetylation, activation, increases, decreases
    def test_convert_phosphorylates(self):
        """Test the conversion of a BEL statement like
        ``act(p(X)) -> p(Y, pmod(Ph))."""
        bel_graph = BELGraph()
        bel_graph.add_directly_increases(
            cdk5,
            p_tau,
            evidence=n(),
            citation=n(),
            subject_modifier=activity('kin'),
        )

        r_edge = 0
        expected_reified_graph = \
            TestAssembleReifiedGraph.help_make_simple_expected_graph(
                cdk5,
                p_tau,
                PHOSPHORYLATES,
                r_edge
            )

        reified_graph = reify_bel_graph(bel_graph)
        self.help_test_graphs_equal(expected_reified_graph, reified_graph)

    def test_convert_two_phosphorylates(self):
        """Test that two phosphorylations of the same object get
        different reified nodes."""
        bel_graph = BELGraph()
        for kinase in (cdk5, gsk3b):
            bel_graph.add_directly_increases(
                kinase,
                p_tau,
                evidence=n(),
                citation=n(),
                subject_modifier=activity('kin'),
            )

        re1, re2 = 0, 1
        expected_reified_graph = \
            TestAssembleReifiedGraph.help_make_simple_expected_graph(
                cdk5,
                p_tau,
                PHOSPHORYLATES,
                re1
            )
        expected_reified_graph.add_node(re2, label='phosphorylates')
        expected_reified_graph.add_edge(gsk3b, re2, label=REIF_SUBJECT)
        expected_reified_graph.add_edge(p_tau, re2, label=REIF_OBJECT)

        reified_graph = reify_bel_graph(bel_graph)
        self.help_test_graphs_equal(expected_reified_graph, reified_graph)

    def planned_test_convert_activates(self):
        """Test the conversion of a bel statement like p(x) -> act(p(y))"""

        bel_graph = BELGraph()

        expected_reified_graph = \
            TestAssembleReifiedGraph.help_make_simple_expected_graph(
                cdk5,
                p_tau,
                ACTIVATES,
                0
            )

        reified_graph = reify_bel_graph(bel_graph)
        self.help_test_graphs_equal(expected_reified_graph, reified_graph)

    def test_convert_increases_abundance(self):
        """Test the conversion of a bel statement like A X B, when
        X in [->, =>] and A and B don't fall in any special case
        (activity, pmod, ...)
        """

        bel_graph = BELGraph()
        bel_graph.add_increases(
            oxaliplatin,
            reactive_o_species,
            evidence='10.1093/jnci/djv394',
            citation='PubMed:26719345'
        )

        expected_reified_graph = \
            TestAssembleReifiedGraph.help_make_simple_expected_graph(
                oxaliplatin,
                reactive_o_species,
                INCREASES_ABUNDANCE,
                0
            )

        reified_graph = reify_bel_graph(bel_graph)
        self.help_test_graphs_equal(expected_reified_graph, reified_graph)

    def test_convert_increases_abundance_then_phosphorylates(self):
        """Test the conversion of a bel graph containing one increases
        abundance and one phosphorylates relationship"""

        bel_graph = BELGraph()
        bel_graph.add_increases(
            oxaliplatin,
            reactive_o_species,
            evidence='10.1093/jnci/djv394',
            citation='PubMed:26719345'
        )
        bel_graph.add_directly_increases(
            reactive_o_species,
            p_tau,
            evidence=n(),
            citation=n()
        )

        re1, re2 = 0, 1
        expected_reified_graph = \
            TestAssembleReifiedGraph.help_make_simple_expected_graph(
                oxaliplatin,
                reactive_o_species,
                INCREASES_ABUNDANCE,
                re1
            )

        expected_reified_graph.add_node(re2, label=PHOSPHORYLATES)
        expected_reified_graph.add_edge(
            reactive_o_species, re2, label=REIF_SUBJECT
        )
        expected_reified_graph.add_edge(p_tau, re2, label=REIF_OBJECT)

        reified_graph = reify_bel_graph(bel_graph)
        self.help_test_graphs_equal(expected_reified_graph, reified_graph)

    @staticmethod
    def help_make_simple_expected_graph(u, v, label, edge_num):
        expected_reified_graph = nx.DiGraph()
        expected_reified_graph.add_node(edge_num, label=label)
        expected_reified_graph.add_edge(u, edge_num, label=REIF_SUBJECT)
        expected_reified_graph.add_edge(v, edge_num, label=REIF_OBJECT)
        return expected_reified_graph


if __name__ == '__main__':
    unittest.main()
