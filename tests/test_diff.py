import pybel
import unittest
from pybel_tools.graph_diff import graph_difference

test_bel_1 = """
SET DOCUMENT Name = "PyBEL Test Document 1"
SET DOCUMENT Version = "1.6"

DEFINE NAMESPACE HGNC AS URL "http://resources.openbel.org/belframework/20150611/namespace/hgnc-human-genes.belns"
DEFINE ANNOTATION TESTAN1 AS LIST {"1","2","3"}
DEFINE ANNOTATION TESTAN2 AS LIST {"1","2","3"}

SET Citation = {"PubMed","That one article from last week","123455"}
SET TESTAN1 = "1"
SET Evidence = "Evidence 1"

p(HGNC:AKT1) -> p(HGNC:EGFR)

SET Evidence = "Evidence 2"
SET TESTAN2 = "3"

p(HGNC:EGFR) -| p(HGNC:FADD)
p(HGNC:EGFR) =| p(HGNC:CASP8)

SET Citation = {"PubMed","That other article from last week","123456"}
SET TESTAN1 = "2"
SET Evidence = "Evidence 3"

p(HGNC:FADD) -> p(HGNC:CASP8)
p(HGNC:AKT1) -- p(HGNC:CASP8)
"""

test_bel_2 = """
SET DOCUMENT Name = "PyBEL Test Document 1"
SET DOCUMENT Version = "1.6"

DEFINE NAMESPACE HGNC AS URL "http://resources.openbel.org/belframework/20150611/namespace/hgnc-human-genes.belns"
DEFINE ANNOTATION TESTAN1 AS LIST {"1","2","3"}
DEFINE ANNOTATION TESTAN2 AS LIST {"1","2","3"}

SET Citation = {"PubMed","That one article from last week","123455"}
SET TESTAN1 = "1"
SET Evidence = "Evidence 1"

p(HGNC:AKT1) -> p(HGNC:EGFR)
p(HGNC:MIA) =| p(HGNC:AKT1, pmod(P))

SET Evidence = "Evidence 2"
SET TESTAN2 = "3"

p(HGNC:EGFR) -| p(HGNC:FADD)
p(HGNC:EGFR) =| p(HGNC:CASP8)

SET Citation = {"PubMed","That other article from last week","123456"}
SET TESTAN1 = {"2","3"}
SET Evidence = "Evidence 3"

p(HGNC:FADD) -> p(HGNC:CASP8)
p(HGNC:AKT1) -- p(HGNC:CASP8)
"""

MIA = ('Protein', 'HGNC', 'MIA')
FADD = ('Protein', 'HGNC', 'FADD')
CASP8 = ('Protein', 'HGNC', 'CASP8')
AKT1 = 'Protein', 'HGNC', 'AKT1'
AKT1_Ph = ('ProteinVariant', 'HGNC', 'AKT1', ('ProteinModification', 'Ph'))


class TestGraphDiff(unittest.TestCase):
    """Tests the ability to compare to BELGraphs"""

    def test_difference(self):
        a = pybel.from_lines(test_bel_1.split('\n'))
        b = pybel.from_lines(test_bel_2.split('\n'))

        d = graph_difference(b, a)

        d_nodes = {
            MIA,
            AKT1_Ph
        }

        self.assertEqual(d_nodes, set(d.nodes()))

        d_edges = {
            (MIA, AKT1_Ph): {
                'relation': 'directlyDecreases',
                'SupportingText': 'Evidence 2',
                'TESTAN2': '3'
            },
            (FADD, CASP8): {
                'relation': 'increases',
                'SupportingText': 'Evidence 3',
                'TESTAN1': '3'
            },
            (AKT1, CASP8): {
                'relation': 'association',
                'SupportingText': 'Evidence 3',
                'TESTAN1': '3'
            },
            (CASP8, AKT1): {
                'relation': 'association',
                'SupportingText': 'Evidence 3',
                'TESTAN1': '3'
            }
        }

        self.assertEqual(d_edges, set(d.edges_iter(data=True)))
