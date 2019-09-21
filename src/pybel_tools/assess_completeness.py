# -*- coding: utf-8 -*-

"""Assess the completeness of a graph.

Run on CONIB with ``python -m pybel_tools.assess_completeness [PMID]``.
"""

import logging
import math
from dataclasses import dataclass
from typing import Iterable, List, Optional, Set, Tuple, Union

import click
from indra.sources.indra_db_rest.api import get_statements_for_paper
from indra.sources.indra_db_rest.util import logger as indra_logger

from pybel import BELGraph, BaseEntity, from_indra_statements
from pybel.cli import _from_pickle_callback

__all__ = [
    'assess_completeness',
]


@dataclass
class CompletenessSummary:
    """Information about the assessment of the completeness of a reference graph versus a set of documents."""

    documents: List[Tuple[str, str]]
    reference_nodes: Set[BaseEntity]
    indra_nodes: Set[BaseEntity]

    @property
    def novel_nodes(self) -> Set[BaseEntity]:
        return self.indra_nodes - self.reference_nodes

    def summary_str(self) -> str:
        ids_pretty = ', '.join(f'{x}:{y}' for x, y in self.documents)

        indra_novel = len(self.novel_nodes) / len(self.indra_nodes)
        reference_novel = len(self.novel_nodes) / len(self.reference_nodes)
        score_novel = len(self.novel_nodes) / math.sqrt(len(self.indra_nodes) * len(self.reference_nodes))

        return f"""
Novelty check for {ids_pretty}:
    Reference had: {len(self.reference_nodes)} nodes
    INDRA found: {len(self.indra_nodes)} nodes ({len(self.novel_nodes)} new, {indra_novel:.2%})
    Curation novelty: {reference_novel:.2%}
    Score: {score_novel:.2%}
"""

    def summarize(self, file=None) -> None:
        print(self.summary_str(), file=file)


def assess_completeness(
    ids: Union[str, Tuple[str, str], List[Tuple[str, str]]],
    reference_nodes: Union[Iterable[BaseEntity], BELGraph],
    *,
    verbose_indra_logger: bool = False,
) -> Optional[CompletenessSummary]:
    """Check INDRA if the given document has new interesting content compared to the graph.

    :param ids: A CURIE (e.g., pmid:30606258, pmc:PMC6318896),
     a pair of database/identifier (e.g. `('pmid', '30606258')`) or a list of pairs.
    :param reference_nodes: A set of nodes or a BEL graph (which is a set of nodes)
    :param verbose_indra_logger: Should the INDRA logger show any output below the WARNING level?
    """
    if not verbose_indra_logger:
        indra_logger.setLevel(logging.WARNING)

    if isinstance(ids, str):
        ids = [ids.split(':')]
    elif isinstance(ids, tuple):
        ids = [ids]

    # Normalize PMC database name as well as stringify all identifiers
    ids = [
        ('pmcid' if db == 'pmc' else db, str(db_id))
        for db, db_id in ids
    ]

    stmts = get_statements_for_paper(ids=ids)
    indra_graph = from_indra_statements(stmts)

    indra_nodes = set(indra_graph)
    if not indra_nodes:
        print(f'INDRA did not return any results for {ids}')
        return

    return CompletenessSummary(
        documents=ids,
        reference_nodes=set(reference_nodes),
        indra_nodes=indra_nodes,
    )


@click.command()
@click.argument('pmid')
@click.option(
    '-g', '--graph',
    metavar='path',
    type=click.File('rb'),
    callback=_from_pickle_callback,
    help='Path to BEL file. Loads CONIB as an example if none given',
)
@click.option('-v', '--verbose', is_flag=True)
def main(pmid: str, graph: Optional[BELGraph], verbose: bool) -> None:
    """Check a BEL graph for added value of a given article.

    Example: 30606258 for paper entitled "A pathogenic tau fragment compromises microtubules,
    disrupts insulin signaling and induces the unfolded protein response."
    """
    if graph is None:
        import hbp_knowledge
        graph = hbp_knowledge.get_graph()

    s = assess_completeness(('pmid', pmid), graph, verbose_indra_logger=verbose)
    s.summarize()


if __name__ == '__main__':
    main()
