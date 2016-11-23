"""Utilities for serializing OWL namespaces in the XML format from Protege to BEL Namespace File"""

import sys
import time
import xml.etree.ElementTree as ET

import networkx as nx

from pybel.parser.language import value_map


def make_namespace_header(name, keyword, description, domain=None, species=None, version=None, created=None):
    lines = [
        '[Namespace]',
        'NameString={}'.format(name),
        'Keyword={}'.format(keyword),
        'DescriptionString={}'.format(description),
        'VersionString={}'.format(version if version else '1.0'),
        'CreatedDateTime={}'.format(created if created else time.asctime())
    ]

    if domain is not None:
        lines.append('DomainString={}'.format(domain))

    if species is not None:
        lines.append('SpeciesString={}'.format(species))

    return lines


def make_author_header(author, contact, copyright=None):
    lines = [
        '[Author]',
        'NameString={}'.format(author),
        'ContactInfoString={}'.format(contact)
    ]

    if copyright is not None:
        lines.append('CopyrightString={}'.format(copyright))

    return lines


def make_citation_header(name, description, url, version=None, date=None):
    lines = [
        '[Citation]',
        'NameString={}'.format(name),
        'DescriptionString={}'.format(description),
        'ReferenceURL={}'.format(url),
        'PublishedVersionString={}'.format(version if version else '1.0'),
        'PublishedDate={}'.format(date if date else time.asctime())
    ]

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


def find_dc(r, term, ns):
    for el in r.findall('./owl:Annotation/owl:AnnotationProperty[@abbreviatedIRI="dc:{}"]/../owl:Literal'.format(term),
                        ns):
        return el.text.strip()

    for el in r.findall(
            './owl:Annotation/owl:AnnotationProperty[@IRI="http://purl.org/dc/elements/1.1/{}"]/../owl:Literal'.format(
                term), ns):
        return el.text.strip()


class OWLParser:
    def __init__(self, source):
        """Builds a model of an OWL document using a NetworkX graph
        :param source: input OWL path or filelike object
        """

        tree = ET.parse(source)
        root = tree.getroot()

        self.name_url = root.attrib['ontologyIRI']

        labels = {}
        self.graph = nx.DiGraph()
        self.metadata = {}

        owl_ns = {
            'owl': 'http://www.w3.org/2002/07/owl#',
            'dc': 'http://purl.org/dc/elements/1.1'
        }

        email = root.find('''./owl:Annotation/owl:AnnotationProperty[@IRI='#email']/../owl:Literal''', owl_ns)
        if not email:
            raise Exception('Missing #email document Annotation. Add this custom metadata with protege')
        self.metadata['email'] = email.text.strip()

        required_dc = 'title', 'subject', 'creator', 'description', 'date'

        for dc_term in required_dc:
            self.metadata[dc_term] = find_dc(root, dc_term, owl_ns)

        if not all(key in self.metadata and self.metadata[key] for key in required_dc):
            raise Exception(
                'Missing DC terms in Annotation section. Required: {}. See purl.org/dc/elements/1.1/. Found {}'.format(
                    required_dc, self.metadata))

        for el in root.findall('./owl:AnnotationAssertion', owl_ns):
            if len(el) == 3:
                prop, iri, lit = el

                if '{http://www.w3.org/XML/1998/namespace}lang' in lit.attrib:
                    if 'en' != lit.attrib['{http://www.w3.org/XML/1998/namespace}lang']:
                        print('non-english detected')
                        continue

                labels[iri.text.lstrip('#').strip()] = lit.text.strip()

        for el in root.findall('./owl:SubClassOf', owl_ns):
            children = el.findall('./owl:Class[@IRI]', owl_ns)
            if len(children) == 2:
                sub, sup = children

                u = sub.attrib['IRI'].lstrip('#').strip()
                v = sup.attrib['IRI'].lstrip('#').strip()

                if u in labels:
                    u = labels[u]
                if v in labels:
                    v = labels[v]

                self.graph.add_edge(u, v)

    def __getitem__(self, item):
        return self.metadata[item]


def build_from_owl(source, output=sys.stdout):
    """

    :param source: Path to OWL file or filelike object
    :param output: output stream. Defaults to sys.stdout
    :return:
    """
    owl = OWLParser(source)

    build(owl['title'], owl['subject'], owl['desription'], owl['creator'], owl['email'], owl.name_url,
          owl.graph.nodes(), output=output)


def build(title, subject, description, creator, email, url, values, functions=None, output=sys.stdout, value_prefix=''):
    for line in make_namespace_header(title, subject, description):
        print(line, file=output)
    print(file=output)

    for line in make_author_header(creator, email):
        print(line, file=output)
    print(file=output)

    for line in make_citation_header(creator, description, url):
        print(line, file=output)
    print(file=output)

    for line in make_properties_header():
        print(line, file=output)
    print(file=output)

    function_values = ''.join(sorted(functions if functions is not None else value_map.keys()))

    print('[Values]', file=output)
    for node in sorted(value.strip() for value in values if value.strip()):
        print('{}{}|{}'.format(value_prefix, node, function_values), file=output)
