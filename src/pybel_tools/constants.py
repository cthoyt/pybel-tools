from pybel.constants import HAS_PRODUCT, HAS_REACTANT, HAS_VARIANT, HAS_COMPONENT, TRANSCRIBED_TO, TRANSLATED_TO

IS_PRODUCT_OF = 'isProductOf'
IS_REACTANT_OF = 'isReactantOf'
IS_VARIANT_OF = 'isVariantOf'
IS_COMPONENT_OF = 'isComponentOf'
TRANSCRIBED_FROM = 'transcribedFrom'
TRANSLATED_FROM = 'translatedFrom'

INFERRED_INVERSE = {
    HAS_PRODUCT: IS_PRODUCT_OF,
    HAS_REACTANT: IS_REACTANT_OF,
    HAS_VARIANT: IS_VARIANT_OF,
    HAS_COMPONENT: IS_COMPONENT_OF,
    TRANSCRIBED_TO: TRANSCRIBED_FROM,
    TRANSLATED_TO: TRANSLATED_FROM
}

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

abstract_url_fmt = "http://togows.dbcls.jp/entry/ncbi-pubmed/{}/abstract"
title_url_fmt = "http://togows.dbcls.jp/entry/ncbi-pubmed/{}/title"
#: SO gives short citation information
so_url_fmt = "http://togows.dbcls.jp/entry/ncbi-pubmed/{}/so"
citation_format = 'SET Citation = {{"PubMed","{}","{}"}}\n'
evidence_format = 'SET Evidence = "{}"\n\n\n'
