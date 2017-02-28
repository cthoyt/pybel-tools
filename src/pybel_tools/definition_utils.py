"""Utilities for serializing OWL namespaces in the XML format from Protege to BEL Namespace File"""

from __future__ import print_function

import getpass
import sys
import time

from pybel.constants import NAMESPACE_DOMAIN_TYPES
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
    :param version: Namespace version. Defaults to '1.0.0'
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
        'VersionString={}'.format(version if version else '1.0.0'),
        'CreatedDateTime={}'.format(created if created else time.strftime(DATETIME_FMT))
    ]

    if description is not None:
        lines.append('DescriptionString={}'.format(description))

    if species is not None:
        lines.append('SpeciesString={}'.format(species))

    if query_url is not None:
        lines.append('QueryValueURL={}'.format(query_url))

    return lines


def make_author_header(name=None, contact=None, copyright_str=None):
    """Makes the [Author] section of a BELNS file

    :param name: Namespace's authors
    :param contact: Namespace author's contact info/email address
    :param copyright_str: Namespace's copyright/license information
    :return:
    """
    lines = [
        '[Author]',
        'NameString={}'.format(name if name is not None else getpass.getuser()),
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
                    functions=None, file=None, value_prefix=''):
    """Writes a BEL namespace (BELNS) to a file

    :param namespace_name: The namespace name
    :type namespace_name: str
    :param namespace_keyword: Preferred BEL Keyword, maximum length of 8
    :type namespace_keyword: str
    :param namespace_domain: One of: “BiologicalProcess”, “Chemical”, “Gene and Gene Products”, “Other”
    :type namespace_domain: str
    :param author_name: Namespace's authors
    :type author_name: str
    :param citation_name: Citation name
    :type citation_name: str
    :param values: A dictionary of {values: encodings}
    :type values: dict
    :param namespace_query_url: HTTP URL to query for details on namespace values (must be valid URL)
    :type namespace_query_url: str
    :param namespace_description: Namespace description
    :type namespace_description: str
    :param namespace_species: Comma-separated list of species taxonomy id's
    :type namespace_species: str
    :param namespace_version: Namespace version
    :type namespace_version: str
    :param namespace_created: Namespace public timestamp, ISO 8601 datetime
    :type namespace_created: str
    :param author_contact: Namespace author's contact info/email address
    :type author_contact: str
    :param author_copyright: Namespace's copyright/license information
    :type author_copyright: str
    :param citation_description: Citation description
    :type citation_description: str
    :param citation_url: URL to more citation information
    :type citation_url: str
    :param citation_version: Citation version
    :type citation_version: str
    :param citation_date: Citation publish timestamp, ISO 8601 Date
    :type citation_date: str
    :param functions: The encoding for the elements in this namespace
    :type functions: iterable of characters
    :param file: the stream to print to
    :type file: file or file-like
    :param value_prefix: a prefix for each name
    :type value_prefix: str
    """
    file = sys.stdout if file is None else file

    for line in make_namespace_header(namespace_name, namespace_keyword, namespace_domain,
                                      query_url=namespace_query_url, description=namespace_description,
                                      species=namespace_species, version=namespace_version, created=namespace_created):
        print(line, file=file)
    print(file=file)

    for line in make_author_header(author_name, contact=author_contact, copyright_str=author_copyright):
        print(line, file=file)
    print(file=file)

    for line in make_citation_header(citation_name, description=citation_description, url=citation_url,
                                     version=citation_version, date=citation_date):
        print(line, file=file)
    print(file=file)

    for line in make_properties_header():
        print(line, file=file)
    print(file=file)

    function_values = ''.join(sorted(functions if functions is not None else language.belns_encodings.keys()))

    print('[Values]', file=file)
    for value in sorted(values):
        if not value.strip():
            continue
        print('{}{}|{}'.format(value_prefix, value.strip(), function_values), file=file)


def build_namespace_from_owl(url, output=None):
    """

    :param url: Path to OWL file or filelike object
    :param output: output stream. Defaults to sys.stdout
    :return:
    """

    owl = parse_owl(url)

    build_namespace(owl['title'],
                    owl['subject'],
                    owl['description'],
                    owl['creator'],
                    owl['email'],
                    url,
                    owl.graph.nodes(),
                    file=output)


def make_annotation_header(keyword, description=None, usage=None, version=None, created=None):
    """Makes the [AnnotationDefinition] section of a BELANNO file

    :param keyword: Preferred BEL Keyword, maximum length of 8
    :type keyword: str
    :param description: A description of this annotation
    :type description: str
    :param usage: How to use this annotation
    :type usage: str
    :param version: Namespace version. Defaults to '1.0.0'
    :type version: str
    :param created: Namespace public timestamp, ISO 8601 datetime
    :type created: str
    """

    lines = [
        '[AnnotationDefinition]',
        'Keyword={}'.format(keyword),
        'TypeString={}'.format('list'),
        'VersionString={}'.format(version if version else '1.0.0'),
        'CreatedDateTime={}'.format(created if created else time.strftime(DATETIME_FMT))
    ]

    if description is not None:
        lines.append('DescriptionString={}'.format(description))

    if usage is not None:
        lines.append('UsageString={}'.format(usage))

    return lines


def build_annotation(keyword, values, citation_name, description=None, usage=None, version=None, created=None,
                     author_name=None, author_copyright=None, author_contact=None, file=None, value_prefix=''):
    """Writes a BEL annotation (BELANNO) to a file

    :param keyword: The annotation keyword
    :param citation_name: The citation name
    :param values: A dictionary of {value: description}
    :param description: A description of this annotation
    :param usage: How to use this annotation
    :param version: The version of this annotation (defaults to 1.0.0)
    :param created: The annotation's public timestamp, ISO 8601 datetime
    :param author_name: The author's name
    :param author_copyright: The copyright information for this annotation. Defaults to 'Other/Proprietary'
    :param author_contact: The contact information for the author of this annotation.
    :param file: A file or file-like
    :param value_prefix: An optional prefix for all values
    """
    file = sys.stdout if file is None else file

    for line in make_annotation_header(keyword, description=description, usage=usage, version=version, created=created):
        print(line, file=file)
    print(file=file)

    for line in make_author_header(name=author_name, contact=author_contact, copyright_str=author_copyright):
        print(line, file=file)
    print(file=file)

    print('[Citation]', file=file)
    print('NameString={}'.format(citation_name), file=file)
    print(file=file)

    for line in make_properties_header():
        print(line, file=file)
    print(file=file)

    print('[Values]', file=file)
    for key, value in sorted(values.items()):
        if not key.strip():
            continue
        print('{}{}|{}'.format(value_prefix, key.strip(), value.strip()), file=file)
