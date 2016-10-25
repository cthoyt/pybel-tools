from pybel_tools.boilerplate import make_boilerplate
from pybel_tools.merger import merge

if __name__ == '__main__':
    make_boilerplate('~/Desktop/boilerplate1.bel', 'BP1', 'cthoyt+1@gmail.com', 'Boilerplate Test Document 1',
                     pmids=[26209472, 26940375])

    make_boilerplate('~/Desktop/boilerplate2.bel', 'BP2', 'cthoyt+2@gmail.com', 'Boilerplate Test Document 2',
                     pmids=[26839406, 26612754])

    merge('~/Desktop/bp_merge.bel', '~/Desktop/boilerplate1.bel', '~/Desktop/boilerplate2.bel')
