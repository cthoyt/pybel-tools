"""Utilities for serializing OWL namespaces in the XML format from Protege to BEL Namespace File"""

import sys
import time

from pybel.manager.utils import parse_owl
from pybel.parser import language

from pybel.manager.cache import CacheManager

TIME_FMT = '%Y-%m-%dT%H:%M:%S'


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


def make_author_header(author, contact, copyright_str=None):
    return [
        '[Author]',
        'NameString={}'.format(author),
        'ContactInfoString={}'.format(contact),
        'CopyrightString={}'.format('Other/Proprietary' if copyright_str is None else copyright_str)
    ]


def make_citation_header(name, description, url, version=None, date=None):
    lines = [
        '[Citation]',
        'NameString={}'.format(name),
        'DescriptionString={}'.format(description),
        'ReferenceURL={}'.format(url),
        'PublishedVersionString={}'.format(version if version else '1.0'),
        'PublishedDate={}'.format(date if date else time.strftime(TIME_FMT))
    ]

    return lines


def make_properties_header():
    return [
        '[Processing]',
        'CaseSensitiveFlag=yes',
        'DelimiterString=|',
        'CacheableFlag=yes'
    ]


def build_namespace(title, subject, description, creator, email, url, values, functions=None, output=sys.stdout, value_prefix=''):
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

    function_values = ''.join(sorted(functions if functions is not None else language.value_map.keys()))

    print('[Values]', file=output)
    for node in sorted(value.strip() for value in values if value.strip()):
        print('{}{}|{}'.format(value_prefix, node, function_values), file=output)


def build_namespace_from_owl(url, output=sys.stdout):
    """

    :param url: Path to OWL file or filelike object
    :param output: output stream. Defaults to sys.stdout
    :return:
    """

    owl = parse_owl(url)

    build_namespace(owl['title'],
                    owl['subject'],
                    owl['desription'],
                    owl['creator'],
                    owl['email'],
                    url,
                    owl.graph.nodes(),
                    output=output)
