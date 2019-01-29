# -*- coding: utf-8 -*-

"""Assemble a BEL graph as an `ideogram <https://github.com/eweitz/ideogram>`_ chart in HTML.."""

import os

import bio2bel_hgnc
import bio2bel_entrez
from bio2bel_hgnc.models import HumanGene
from bio2bel_entrez.models import Gene as EntrezGene
from jinja2 import Template

from pybel import BELGraph
from pybel.constants import GENE
from pybel.struct import get_nodes_by_function
from pybel.struct.mutation import collapse_all_variants, enrich_protein_and_rna_origins

__all__ = [
    'render',
]

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)))

# Create a template object from the template file, load once
template_path = os.path.join(HERE, 'index.html')

with open(template_path, 'rt') as f:
    template_str = f.read()
    template = Template(template_str)


def render(graph: BELGraph) -> str:
    """Render the BEL graph with HTML.

    1. Get all proteins/genes/etc from graph
    2. look up in bio2bel
    3. Make JSON
    """

    graph: BELGraph = graph.copy()
    enrich_protein_and_rna_origins(graph)
    collapse_all_variants(graph)
    genes = get_nodes_by_function(graph, GENE)
    hgnc_symbols = {
        gene.name
        for gene in genes
        if gene.namespace.lower() == 'hgnc'
    }

    hgnc_manager = bio2bel_hgnc.Manager()
    gene_models = (
        hgnc_manager.session
            .query(HumanGene.symbol, HumanGene.location)
            .filter(HumanGene.symbol.in_(hgnc_symbols))
            .all()
    )
    for model in gene_models:
        print(model)

    entrez_manager = bio2bel_entrez.Manager()
    gene_models = (
        entrez_manager.session
    )


if __name__ == '__main__':
    from pybel.examples import sialic_acid_graph

    render(sialic_acid_graph)
