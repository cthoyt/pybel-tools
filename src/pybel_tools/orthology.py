"""

This module has tools for downloading and structuring gene orthology data from HGNC, RGD, and MGI

"""
import requests

from pybel import BELGraph
from pybel.constants import GENE, ORTHOLOGOUS, RELATION

#: Columns: HGNC ID, HGNC Symbol, MGI Curated, MGI Dump, RGD Dump
FULL_RESOURCE = 'http://www.genenames.org/cgi-bin/download?col=gd_hgnc_id&col=gd_app_sym&col=gd_mgd_id&col=md_mgd_id&col=md_rgd_id&status=Approved&status_opt=2&where=&order_by=gd_app_sym_sort&format=text&limit=&submit=submit'

#: Columns: HGNC Symbol, MGI Symbols
MGI_ONLY = 'http://www.genenames.org/cgi-bin/download?col=gd_app_sym&col=md_mgd_id&status=Approved&status_opt=2&where=&order_by=gd_app_sym_sort&format=text&limit=&submit=submit'

#: Columns: HGNC Symbol, RGD Symbols
RGD_ONLY = 'http://www.genenames.org/cgi-bin/download?col=gd_app_sym&col=md_rgd_id&status=Approved&status_opt=2&where=&order_by=gd_app_sym_sort&format=text&limit=&submit=submit'

HGNC = 'HGNC'
MGI = 'MGI'
RGD = 'RGD'

MGI_ANNOTATIONS = 'http://www.informatics.jax.org/downloads/reports/MGI_MRK_Coord.rpt'

#: Columns: Human Marker Symbol, Human Entrez Gene ID, HomoloGene ID, Mouse Marker Symbol, MGI Marker Accession ID, High-level Mammalian Phenotype ID (space-delimited)
#: .. seealso:: http://www.informatics.jax.org/downloads/reports/index.html#pheno
MGI_ORTHOLOGY = 'http://www.informatics.jax.org/downloads/reports/HMD_HumanPhenotype.rpt'

#: Columns: RAT_GENE_SYMBOL	RAT_GENE_RGD_ID	RAT_GENE_NCBI_GENE_ID	HUMAN_ORTHOLOG_SYMBOL	HUMAN_ORTHOLOG_RGD	HUMAN_ORTHOLOG_NCBI_GENE_ID	HUMAN_ORTHOLOG_SOURCE	MOUSE_ORTHOLOG_SYMBOL	MOUSE_ORTHOLOG_RGD	MOUSE_ORTHOLOG_NCBI_GENE_ID	MOUSE_ORTHOLOG_MGI	MOUSE_ORTHOLOG_SOURCE	HUMAN_ORTHOLOG_HGNC_ID
#: First 52 rows are comments with # at beginning and line 53 is the header
RGD_ORTHOLOGY = 'ftp://ftp.rgd.mcw.edu/pub/data_release/RGD_ORTHOLOGS.txt'


def download_orthologies(path):
    """Downloads the full dump to the given path

    :param path: output path
    """

    res = requests.get(FULL_RESOURCE)

    with open(path, 'w') as f:
        for line in res.iter_lines(decode_unicode=True):
            print(line, file=f)


def structure_orthologies(lines=None):
    """Structures the orthology data to two lists of pairs of (HGNC, MGI) and (HGNC, RGD) identifiers

    :param lines: The iterable over the downloaded orthologies from HGNC. If None, downloads from HGNC
    :return:
    """
    if lines is None:
        lines = requests.get(FULL_RESOURCE).iter_lines(decode_unicode=True)

    mgi_orthologies = []
    rgd_orthologies = []

    for line in lines:
        hgnc_id, hgnc_symbol, _, mgis, rgds = line.strip().split('\t')

        for mgi in mgis.split(','):
            mgi = mgi.strip()
            mgi = mgi.replace('MGI:', '')
            mgi_orthologies.append((hgnc_symbol, mgi))

        for rgd in rgds.split(','):
            rgd = rgd.strip()
            rgd = rgd.replace('RGD:', '')
            rgd_orthologies.append((hgnc_symbol, rgd))

    return mgi_orthologies, rgd_orthologies


def add_mgi_orthology_statements(graph, mgi_orthologies):
    """Adds orthology statements for all MGI nodes

    :param graph:
    :type graph: BELGraph
    :param mgi_orthologies:
    :type mgi_orthologies: list
    :return:
    """
    for hgnc, mgi in mgi_orthologies:
        hgnc_node = GENE, HGNC, hgnc
        mgi_node = GENE, MGI, mgi

        if mgi_node not in graph:
            continue

        if hgnc_node not in graph:
            graph.add_simple_node(*hgnc_node)

        graph.add_unqualified_edge(hgnc_node, mgi_node, ORTHOLOGOUS)


def add_rgd_orthology_statements(graph, rgd_orthologies):
    """Adds orthology statements for all MGI nodes

    :param graph:
    :type graph: BELGraph
    :param mgi_orthologies:
    :return:
    """
    for hgnc, rgd in rgd_orthologies:
        hgnc_node = GENE, HGNC, hgnc
        rgd_node = GENE, RGD, rgd

        if rgd_node not in graph:
            continue

        if hgnc_node not in graph:
            graph.add_simple_node(*hgnc_node)

        graph.add_unqualified_edge(hgnc_node, rgd_node, ORTHOLOGOUS)


def integrate_orthologies(graph, lines=None):
    """Adds orthology statements to graph

    :param graph:
    :param lines:
    :return:
    """
    mgio, rgdo = structure_orthologies(lines=lines)
    add_mgi_orthology_statements(graph, mgio)
    add_rgd_orthology_statements(graph, rgdo)


def collapse_orthologies(graph):
    """Collapses all orthology relations.

    Assumes: orthologies are annotated for edge (u,v) where u is the higher priority node

    This won't work for two way orthology annotations, so it's best to use :code:`integrate_orthologies` first

    :param graph:
    :type graph: BELGraph
    :return:
    """

    orthologs = []

    for hgnc, ortholog in graph.edges_iter(**{RELATION: ORTHOLOGOUS}):

        for u, _, k, d in graph.in_edges_iter(ortholog, data=True, keys=True):
            if k < 0:
                graph.add_edge(u, hgnc, key=k, attr_dict=d)
            else:
                graph.add_edge(u, hgnc, attr_dict=d)

        for _, v, k, d in graph.out_edges_iter(ortholog, data=True, keys=True):
            if k < 0:
                graph.add_edge(hgnc, v, key=k, attr_dict=d)
            else:
                graph.add_edge(hgnc, v, attr_dict=d)

        orthologs.append(ortholog)

    graph.remove_nodes_from(orthologs)
