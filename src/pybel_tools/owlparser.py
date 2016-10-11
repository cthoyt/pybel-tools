import os
import xml.etree.ElementTree as ET

import networkx as nx


class OWLParser:
    def __init__(self, path):
        """

        :param path: input OWL path
        :param output: output
        :return:
        """

        tree = ET.parse(path)
        root = tree.getroot()

        self.name_url = root.attrib['ontologyIRI']

        label_dict = {}
        edges = []
        self.G = nx.DiGraph()

        for child in root:
            if child.tag == '{http://www.w3.org/2002/07/owl#}SubClassOf':
                u = child[0].attrib['IRI']
                v = child[1].attrib['IRI']
                edges.append((u, v))

            elif child.tag == '{http://www.w3.org/2002/07/owl#}AnnotationAssertion':
                if 'abbreviatedIRI' in child[0].attrib and 'rdfs:label' == child[0].attrib['abbreviatedIRI']:
                    iri = child[1].text
                    label = child[2].text
                    label_dict[iri] = label

        for u, v in edges:
            source = u.strip('#') if u not in label_dict else label_dict[u]
            target = v.strip('#') if v not in label_dict else label_dict[v]
            self.G.add_edge(source, target)

        self.fmt = """[Namespace]
NameString={name}
Keyword={namespace}
DomainString=
SpeciesString=
DescriptionString=BEL Namespace generated from OWL Ontology at {url}
VersionString=
CreatedDateTime=

[Author]
NameString={author}
CopyrightString=Copyright (c) 2016 Charles Tapley Hoyt
ContactInfoString=

[Citation]
NameString={url}
DescriptionString=
PublishedVersionString=
PublishedDate=
ReferenceURL={url}

[Processing]
CaseSensitiveFlag=yes
DelimiterString=|
CacheableFlag=yes

[Values]"""

    def to_file(self, path):
        with open(os.path.expanduser(path), 'w') as f:
            print(self.fmt.format(name='PTSD Model', namespace='PTSD', url=self.name_url, author='Charlie'), file=f)
            for x in self.G.nodes():
                print('{}|'.format(x), file=f)

    def to_graph(self):
        return self.G
