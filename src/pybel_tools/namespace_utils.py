"""Utilities for serializing OWL namespaces in the XML format from Protege to BEL Namespace File"""

from __future__ import print_function

import sys
import time

from pybel.manager.models import NAMESPACE_DOMAIN_TYPES
from pybel.manager.utils import parse_owl
from pybel.parser import language

DATETIME_FMT = '%Y-%m-%dT%H:%M:%S'
DATE_FMT = '%Y-%m-%d'


def make_namespace_header(name, keyword, domain, query_url=None, description=None, species=None, version=None,
                          created=None):
    """Makes the [Namespace] section of a BELNS file

    :param name: The namespace name
    :param keyword: Preferred BEL Keyword, maximum length of 8
    :param domain: One of: “BiologicalProcess”, “Chemical”, “Gene and Gene Products”, “Other”
    :param query_url: HTTP URL to query for details on namespace values (must be valid URL)
    :param description: Namespace description
    :param species: Comma-separated list of species taxonomy id's
    :param version: Namespace version
    :param created: Namespace public timestamp, ISO 8601 datetime
    :type created: str
    """
    if domain not in NAMESPACE_DOMAIN_TYPES:
        raise ValueError('Invalid domain: {}. Should be one of: {}'.format(domain, NAMESPACE_DOMAIN_TYPES))

    lines = [
        '[Namespace]',
        'Keyword={}'.format(keyword),
        'NameString={}'.format(name),
        'DomainString={}'.format(domain),
        'VersionString={}'.format(version if version else '1.0'),
        'CreatedDateTime={}'.format(created if created else time.strftime(DATETIME_FMT))
    ]

    if description is not None:
        lines.append('DescriptionString={}'.format(description))

    if species is not None:
        lines.append('SpeciesString={}'.format(species))

    if query_url is not None:
        lines.append('QueryValueURL={}'.format(query_url))

    return lines


def make_author_header(name, contact=None, copyright_str=None):
    """Makes the [Author] section of a BELNS file

    :param name: Namespace's authors
    :param contact: Namespace author's contact info/email address
    :param copyright_str: Namespace's copyright/license information
    :return:
    """
    lines = [
        '[Author]',
        'NameString={}'.format(name),
        'CopyrightString={}'.format('Other/Proprietary' if copyright_str is None else copyright_str)
    ]

    if contact is not None:
        lines.append('ContactInfoString={}'.format(contact))

    return lines


def make_citation_header(name, description=None, url=None, version=None, date=None):
    """Makes the [Citation] section of a BELNS file

    :param name: Citation name
    :type name: str
    :param description: Citation description
    :param url: URL to more citation information
    :param version: Citation version
    :param date: Citation publish timestamp, ISO 8601 Date
    :return:
    """
    lines = [
        '[Citation]',
        'NameString={}'.format(name),
    ]

    if date is not None:
        lines.append('PublishedDate={}'.format(date))

    if version is not None:
        lines.append('PublishedVersionString={}'.format(version))

    if description is not None:
        lines.append('DescriptionString={}'.format(description))

    if url is not None:
        lines.append('ReferenceURL={}'.format(url))

    return lines


def make_properties_header():
    """Makes the [Processing] section of a BELNS file"""
    return [
        '[Processing]',
        'CaseSensitiveFlag=yes',
        'DelimiterString=|',
        'CacheableFlag=yes'
    ]


def build_namespace(namespace_name, namespace_keyword, namespace_domain, author_name, citation_name, values,
                    namespace_description=None, namespace_species=None, namespace_version=None,
                    namespace_query_url=None, namespace_created=None, author_contact=None, author_copyright=None,
                    citation_description=None, citation_url=None, citation_version=None, citation_date=None,
                    functions=None, output=sys.stdout, value_prefix=''):
    """Builds a namespace

    :param namespace_name: The namespace name
    :param namespace_keyword: Preferred BEL Keyword, maximum length of 8
    :param namespace_domain: One of: “BiologicalProcess”, “Chemical”, “Gene and Gene Products”, “Other”
    :param author_name: Namespace's authors
    :param citation_name: Citation name
    :param values: A dictionary of {values: encodings}
    :type values: dict
    :param namespace_query_url: HTTP URL to query for details on namespace values (must be valid URL)
    :param namespace_description: Namespace description
    :param namespace_species: Comma-separated list of species taxonomy id's
    :param namespace_version: Namespace version
    :param namespace_created: Namespace public timestamp, ISO 8601 datetime
    :param author_contact: Namespace author's contact info/email address
    :param author_copyright: Namespace's copyright/license information
    :param citation_description: Citation description
    :param citation_url: URL to more citation information
    :param citation_version: Citation version
    :param citation_date: Citation publish timestamp, ISO 8601 Date
    :param functions: The encoding for the elements in this namespace
    :param output: the stream to print to
    :param value_prefix: a prefix for each name"""
    for line in make_namespace_header(namespace_name, namespace_keyword, namespace_domain,
                                      query_url=namespace_query_url, description=namespace_description,
                                      species=namespace_species, version=namespace_version, created=namespace_created):
        print(line, file=output)
    print(file=output)

    for line in make_author_header(author_name, contact=author_contact, copyright_str=author_copyright):
        print(line, file=output)
    print(file=output)

    for line in make_citation_header(citation_name, description=citation_description, url=citation_url,
                                     version=citation_version, date=citation_date):
        print(line, file=output)
    print(file=output)

    for line in make_properties_header():
        print(line, file=output)
    print(file=output)

    function_values = ''.join(sorted(functions if functions is not None else language.belns_encodings.keys()))

    print('[Values]', file=output)
    for value in values:
        if not value.strip():
            continue
        print('{}{}|{}'.format(value_prefix, value.strip(), function_values), file=output)


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
