"""Utilities for building boilerplate BEL documents"""

import os
from operator import itemgetter

import requests

default_namespaces = {
    'ADO': 'http://belief.scai.fraunhofer.de/openbel/repository/namespaces/ADO.belns',
    'AFFX': 'http://resource.belframework.org/belframework/20150611/namespace/affy-probeset-ids.belns',
    'BRCO': 'http://belief.scai.fraunhofer.de/openbel/repository/namespaces/BRCO.belns',
    'CHEBI': 'http://resource.belframework.org/belframework/20150611/namespace/chebi.belns',
    'CHEBIID': 'http://resource.belframework.org/belframework/20150611/namespace/chebi-ids.belns',
    'CHEMBL': 'http://belief-demo.scai.fraunhofer.de/openbel/repository/namespaces/chembl-names.belns',
    'CHEMBLID': 'http://belief-demo.scai.fraunhofer.de/openbel/repository/namespaces/chembl-ids.belns',
    'CTO': 'http://belief.scai.fraunhofer.de/openbel/repository/namespaces/CTO.belns',
    'DO': 'http://resource.belframework.org/belframework/20150611/namespace/disease-ontology.belns',
    'DOID': 'http://resource.belframework.org/belframework/20150611/namespace/disease-ontology-ids.belns',
    'EGID': 'http://resource.belframework.org/belframework/20150611/namespace/entrez-gene-ids.belns',
    'FlyBase': 'http://belief.scai.fraunhofer.de/openbel/repository/namespaces/Dmel.belns',
    'GOBP': 'http://resource.belframework.org/belframework/20150611/namespace/go-biological-process.belns',
    'GOBPID': 'http://resource.belframework.org/belframework/20150611/namespace/go-biological-process-ids.belns',
    'GOCC': 'http://resource.belframework.org/belframework/20150611/namespace/go-cellular-component.belns',
    'GOCCID': 'http://resource.belframework.org/belframework/20150611/namespace/go-cellular-component-ids.belns',
    'HGNC': 'http://resource.belframework.org/belframework/20150611/namespace/hgnc-human-genes.belns',
    'LMSD': 'http://belief-demo.scai.fraunhofer.de/openbel/repository/namespaces/LMSD.belns',
    'MESHC': 'http://resource.belframework.org/belframework/20150611/namespace/mesh-chemicals.belns',
    'MESHCID': 'http://resource.belframework.org/belframework/20150611/namespace/mesh-chemicals-ids.belns',
    'MESHCS': 'http://resource.belframework.org/belframework/20150611/namespace/mesh-cellular-structures.belns',
    'MESHCSID': 'http://resource.belframework.org/belframework/20150611/namespace/mesh-cellular-structures-ids.belns',
    'MESHD': 'http://resource.belframework.org/belframework/20150611/namespace/mesh-diseases.belns',
    'MESHDID': 'http://resource.belframework.org/belframework/20150611/namespace/mesh-diseases-ids.belns',
    'MESHPP': 'http://resource.belframework.org/belframework/20150611/namespace/mesh-processes.belns',
    'MESHPPID': 'http://resource.belframework.org/belframework/20150611/namespace/mesh-processes-ids.belns',
    'MGI': 'http://resource.belframework.org/belframework/20150611/namespace/mgi-mouse-genes.belns',
    'NIFT': 'http://belief.scai.fraunhofer.de/openbel/repository/namespaces/NIFT.belns',
    'NTN': 'http://belief.scai.fraunhofer.de/openbel/repository/namespaces/Nutrition.belns',
    'PDO': 'http://belief.scai.fraunhofer.de/openbel/repository/namespaces/PDO.belns',
    'PH': 'http://belief-demo.scai.fraunhofer.de/openbel/repository/namespaces/Placeholder.belns',
    'PMIBP': 'http://belief-demo.scai.fraunhofer.de/BeliefDashboard/dicten/namespaces/pmibp.belns',
    'PMICHEM': 'http://belief-demo.scai.fraunhofer.de/BeliefDashboard/dicten/namespaces/pmichem.belns',
    'PMICOMP': 'http://belief-demo.scai.fraunhofer.de/BeliefDashboard/dicten/namespaces/pmicomp.belns',
    'PMIDIS': 'http://belief-demo.scai.fraunhofer.de/BeliefDashboard/dicten/namespaces/pmidis.belns',
    'PMIPFAM': 'http://belief-demo.scai.fraunhofer.de/BeliefDashboard/dicten/namespaces/pmipfam.belns',
    'PTS': 'http://belief.scai.fraunhofer.de/openbel/repository/namespaces/PTS.belns',
    'RGD': 'http://resource.belframework.org/belframework/20150611/namespace/rgd-rat-genes.belns',
    'SCHEM': 'http://resource.belframework.org/belframework/20150611/namespace/selventa-legacy-chemicals.belns',
    'SCOMP': 'http://resource.belframework.org/belframework/20150611/namespace/selventa-named-complexes.belns',
    'SDIS': 'http://resource.belframework.org/belframework/20150611/namespace/selventa-legacy-diseases.belns',
    'SFAM': 'http://resource.belframework.org/belframework/20150611/namespace/selventa-protein-families.belns',
    'SP': 'http://resource.belframework.org/belframework/20150611/namespace/swissprot.belns',
    'SPID': 'http://resource.belframework.org/belframework/20150611/namespace/swissprot-ids.belns',
    'dbSNP': 'http://belief.scai.fraunhofer.de/openbel/repository/namespaces/SNP.belns'
}

default_annotations = {
    'Anatomy': 'http://resource.belframework.org/belframework/20131211/annotation/anatomy.belanno',
    'BodyRegion': 'http://resource.belframework.org/belframework/1.0/annotation/mesh-body-region.belanno',
    'CardiovascularSystem': 'http://resource.belframework.org/belframework/1.0/annotation/mesh-cardiovascular-system.belanno',
    'Cell': 'http://resource.belframework.org/belframework/20131211/annotation/cell.belanno',
    'CellLine': 'http://resource.belframework.org/belframework/20131211/annotation/cell-line.belanno',
    'CellStructure': 'http://resource.belframework.org/belframework/20131211/annotation/cell-structure.belanno',
    'DigestiveSystem': 'http://resource.belframework.org/belframework/1.0/annotation/mesh-digestive-system.belanno',
    'Disease': 'http://resource.belframework.org/belframework/20131211/annotation/disease.belanno',
    'FluidAndSecretion': 'http://resource.belframework.org/belframework/1.0/annotation/mesh-fluid-and-secretion.belanno',
    'HemicAndImmuneSystem': 'http://resource.belframework.org/belframework/1.0/annotation/mesh-hemic-and-immune-system.belanno',
    'IntegumentarySystem': 'http://resource.belframework.org/belframework/1.0/annotation/mesh-integumentary-system.belanno',
    'MeSHAnatomy': 'http://resource.belframework.org/belframework/20131211/annotation/mesh-anatomy.belanno',
    'MeSHDisease': 'http://resource.belframework.org/belframework/20131211/annotation/mesh-diseases.belanno',
    'NervousSystem': 'http://resource.belframework.org/belframework/1.0/annotation/mesh-nervous-system.belanno',
    'RespiratorySystem': 'http://resource.belframework.org/belframework/1.0/annotation/mesh-respiratory-system.belanno',
    'Species': 'http://resource.belframework.org/belframework/20131211/annotation/species-taxonomy-id.belanno',
    'Tissue': 'http://resource.belframework.org/belframework/1.0/annotation/mesh-tissue.belanno',
    'UrogenitalSystem': 'http://resource.belframework.org/belframework/1.0/annotation/mesh-urogenital-system.belanno'
}


def make_document_metadata(document_name, contact, description, version=None, copyright=None, authors=None,
                           licenses=None):
    """Builds a document metadata section for a BEL document

    :param document_name: The unique name for this BEL document
    :param contact: The email address of the maintainer
    :param description: A description of the contents of this document
    :param version: The version. Defaults to 1.0
    :param copyright: Copyright information about this document
    :param authors: The authors of this document
    :param licenses: The license applied to this document
    :type document_name: str
    :type contact: str
    :type description: str
    :type version: str
    :type copyright: str
    :type authors: str
    :type licenses: str
    :return:
    """

    s = list()

    s.append('SET DOCUMENT Name = "{}'.format(document_name))
    s.append('SET DOCUMENT Version = "{}"'.format(version if version else '1.0'))

    if licenses is not None:
        s.append('SET DOCUMENT License = "{}"'.format(licenses))

    s.append('SET DOCUMENT Description = "{}"'.format(description))

    if authors is not None:
        s.append('SET DOCUMENT Authors = {}'.format(authors))

    s.append('SET DOCUMENT ContactInfo = "{}"'.format(contact))

    if copyright is not None:
        s.append('SET DOCUMENT Copyright = "{}"'.format(copyright))

    return s


def make_document_namespaces(namespace_dict=None):
    """
    :param namespace_dict: dictionary of {str name: str URL} of namespaces
    :type namespace_dict: dict
    :return:
    """

    namespace_dict = namespace_dict if namespace_dict is not None else default_namespaces

    s = list()

    namespace_fmt = 'DEFINE NAMESPACE {} AS URL "{}"'
    for name, url in sorted(namespace_dict.items(), key=itemgetter(1)):
        s.append(namespace_fmt.format(name, url))
    return s


def make_document_annotations(annotation_dict=None):
    """
    :param annotation_dict: dictionary of {str name: str URL} of annotations
    :type annotation_dict: dict
    :return:
    """

    annotation_dict = annotation_dict if annotation_dict is not None else default_annotations
    s = list()
    annotation_fmt = 'DEFINE ANNOTATION {} AS URL "{}"'
    for name, url in sorted(annotation_dict.items(), key=itemgetter(1)):
        s.append(annotation_fmt.format(name, url))
    return s


abstract_url_fmt = "http://togows.dbcls.jp/entry/ncbi-pubmed/{}/abstract"
title_url_fmt = "http://togows.dbcls.jp/entry/ncbi-pubmed/{}/title"

# SO gives short citaiton information
so_url_fmt = "http://togows.dbcls.jp/entry/ncbi-pubmed/{}/so"

citation_format = 'SET Citation = {{"PubMed","{}","{}"}}\n'
evidence_format = 'SET Evidence = "{}"\n\n\n'


def make_document_statement_group(pmids):
    s = list()

    for i, pmid in enumerate(pmids, start=1):
        s.append('SET STATEMENT_GROUP = "Group {}"\n'.format(i))
        res = requests.get(title_url_fmt.format(pmid))
        title = res.content.decode('utf-8').strip()

        s.append(citation_format.format(title, pmid))

        res = requests.get(abstract_url_fmt.format(pmid))
        abstract = res.content.decode('utf-8').strip()

        s.append(evidence_format.format(abstract))
        s.append('UNSET STATEMENT_GROUP')
    return s


def make_boilerplate(output_path, document_name, contact, description, version=None, copyright=None, authors=None,
                     licenses=None, namespace_dict=None, annoations_dict=None, pmids=None):
    """

    :param output_path: file path to output file
    :param document_name: The unique name for this BEL document
    :param contact: The email address of the maintainer
    :param description: A description of the contents of this document
    :param version: The version. Defaults to 1.0
    :param copyright: Copyright information about this document
    :param authors: The authors of this document
    :param licenses: The license applied to this document
    :type document_name: str
    :type contact: str
    :type description: str
    :type version: str
    :type copyright: str
    :type authors: str
    :type licenses: str
    :param namespace_dict: an optional dictionary of {str name: str URL} of namespaces
    :type namespace_dict: dict
    :param annotation_dict: an optional dictionary of {str name: str URL} of annotations
    :type annotation_dict: dict
    :param pmids: an optional list of PMID's to autopopulate with citation and abstract
    :type pmids: iterable
    :return:
    """
    with open(os.path.expanduser(output_path), 'w') as f:
        for line in make_document_metadata(document_name, contact, description, version, copyright, authors, licenses):
            print(line, file=f)
        print(file=f)
        for line in make_document_namespaces(namespace_dict):
            print(line, file=f)
        print(file=f)
        for line in make_document_annotations(annoations_dict):
            print(line, file=f)
        print(file=f)

        if pmids is not None:
            for line in make_document_statement_group(pmids):
                print(line, file=f)

