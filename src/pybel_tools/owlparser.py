"""Utilities for serializing OWL namespaces in the XML format from Protege to BEL Namespace File
"""

import os
import time
import xml.etree.ElementTree as ET

import networkx as nx


def make_namespace_header(name, keyword, description, domain=None, species=None, version=None, created=None):
    lines = ['[Namespace]']
    lines.append('NameString={}'.format(name))
    lines.append('Keyword={}'.format(keyword))
    lines.append('DescriptionString={}'.format(description))
    lines.append('VersionString={}'.format(version if version else '1.0'))
    lines.append('CreatedDateTime={}'.format(created if created else time.asctime()))

    if domain is not None:
        lines.append('DomainString={}'.format(domain))
    if species is not None:
        lines.append('SpeciesString={}'.format(species))

    return lines


def make_author_header(author, contact, copyright=None):
    lines = ['[Author]']

    lines.append('NameString={}'.format(author))
    lines.append('ContactInfoString={}'.format(contact))

    if copyright is not None:
        lines.append('CopyrightString={}'.format(copyright))

    return lines


def make_citation_header(name, description, url, version=None, date=None):
    lines = ['[Citation]']

    lines.append('NameString={}'.format(name))
    lines.append('DescriptionString={}'.format(description))
    lines.append('ReferenceURL={}'.format(url))
    lines.append('PublishedVersionString={}'.format(version if version else '1.0'))
    lines.append('PublishedDate={}'.format(date if date else time.asctime()))

    return lines


def make_properties_header():
    return [
        '[Processing]',
        'CaseSensitiveFlag=yes',
        'DelimiterString=|',
        'CacheableFlag=yes'
    ]


def make_values(value_dict):
    lines = ['[Values]']
    for key in sorted(value_dict.keys()):
        lines.append('{}|{}'.format(key, value_dict[key]))


class OWLParser:
    def __init__(self, path):
        """Builds a model of an OWL document using a NetworkX graph
        :param path: input OWL path
        """

        tree = ET.parse(path)
        root = tree.getroot()

        self.name_url = root.attrib['ontologyIRI']

        label_dict = {}
        edges = []
        self.G = nx.DiGraph()

        # TODO in ./owl:Annotation look for dc:title, dc:creator, dc:date, dc:description, dc:contributor, dc:rights, and dc:subject

        for child in root:
            if child.tag == '{http://www.w3.org/2002/07/owl#}SubClassOf':
                u = child[0].attrib['IRI'].strip()
                v = child[1].attrib['IRI'].strip()
                edges.append((u, v))

            elif child.tag == '{http://www.w3.org/2002/07/owl#}AnnotationAssertion':
                if 'abbreviatedIRI' in child[0].attrib and 'rdfs:label' == child[0].attrib['abbreviatedIRI']:
                    iri = child[1].text.strip()
                    label = child[2].text.strip()
                    label_dict[iri] = label

        for u, v in edges:
            source = u.strip('#').strip() if u not in label_dict else label_dict[u]
            target = v.strip('#').strip() if v not in label_dict else label_dict[v]
            self.G.add_edge(source, target)


def build(input_path, output_path, ns_name, ns_keyword, ns_description, author, contact):
    """

    :param input_path: Path to .OWL file in
    :param output_path:
    :param ns_name:
    :param ns_keyword:
    :param ns_description:
    :param author:
    :param contact:
    :return:
    """
    owl = OWLParser(os.path.expanduser(input_path))

    with open(os.path.expanduser(output_path), 'w') as f:
        for line in make_namespace_header(ns_name, ns_keyword, ns_description):
            print(line, file=f)
        print(file=f)

        for line in make_author_header(author, contact):
            print(line, file=f)
        print(file=f)

        for line in make_citation_header(author, ns_description, owl.name_url):
            print(line, file=f)
        print(file=f)

        for line in make_properties_header():
            print(line, file=f)
        print(file=f)

        print('[Values]', file=f)
        for node in sorted(owl.G.nodes()):
            print('{}|'.format(node), file=f)
