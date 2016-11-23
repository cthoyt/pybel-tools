import os
import tempfile
import unittest

from pybel_tools.boilerplate import make_boilerplate
from pybel_tools.merger import merge


class TestBoilerplate(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def doCleanups(self):
        os.remove(self.dir)

    def test_1(self):
        b1 = os.path.join(self.dir, 'boilerplate1.bel')
        b2 = os.path.join(self.dir, 'boilerplate2.bel')
        b3 = os.path.join(self.dir, 'bp_merge.bel')
        make_boilerplate(b1, 'BP1', 'cthoyt+1@gmail.com', 'Boilerplate Test Document 1', pmids=[26209472, 26940375])

        make_boilerplate(b2, 'BP2', 'cthoyt+2@gmail.com', 'Boilerplate Test Document 2', pmids=[26839406, 26612754])

        merge(b3, b1, b2)
