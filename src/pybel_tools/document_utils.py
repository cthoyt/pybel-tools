"""Utilities to merge multiple BEL documents on the same topic"""

from __future__ import print_function

import os
import sys
from itertools import islice
from operator import itemgetter

import requests

from .constants import default_namespaces, default_annotations
from .constants import title_url_fmt, citation_format, abstract_url_fmt, evidence_format

NAMESPACE_FMT = 'DEFINE NAMESPACE {} AS URL "{}"'
ANNOTATION_FMT = 'DEFINE ANNOTATION {} AS URL "{}"'


def split_document(lines):
    """Splits the lines over a document into the documents, definitions, and statements section

    :param lines: A file or file-like that is an iterable over the lines of a document
    """
    lines = list(lines)
    end_document_section = 1 + max(i for i, line in enumerate(lines) if line.startswith('SET DOCUMENT'))
    end_definitions_section = 1 + max(i for i, line in enumerate(lines) if
                                      line.startswith('DEFINE ANNOTATION') or line.startswith('DEFINE NAMESPACE'))
    documents = [line for line in islice(lines, end_document_section) if not line.startswith('#')]
    definitions = [line for line in islice(lines, end_document_section, end_definitions_section) if
                   not line.startswith('#')]

    statements = lines[end_definitions_section:]

    return documents, definitions, statements


def merge(output_path, *input_paths, merge_document_name=None, merge_document_contact=None,
          merge_document_description=None):
    """Merges multiple BEL documents and maintains author information in comments

    Steps:

    1. Load all documents
    2. Identify document metadata information and ns/annot defs
    3. Postpend all statement groups with "- {author email}" and add comments with document information

    :param output_path: Path to file to write merged BEL document
    :param input_paths: List of paths to input BEL document files
    :param merge_document_name: name for combined document
    :param merge_document_contact: contact information for combine document
    :param merge_document_description: description of combine document
    """
    metadata, defs, statements = [], [], []

    for input_path in input_paths:
        with open(os.path.expanduser(input_path)) as f:
            a, b, c = split_document([line.strip() for line in f])
            metadata.append(a)
            defs.append(set(b))
            statements.append(c)

    merge_document_contact = merge_document_contact if merge_document_contact is not None else ''
    merge_document_name = merge_document_name if merge_document_name is not None else 'MERGED DOCUMENT'
    merge_document_description = merge_document_description if merge_document_description is not None else 'This is a merged document'

    with open(os.path.expanduser(output_path), 'w') as f:
        for line in make_document_metadata(merge_document_name, merge_document_contact, merge_document_description):
            print(line, file=f)

        for line in sorted(set().union(*defs)):
            print(line, file=f)

        for md, st in zip(metadata, statements):
            print(file=f)

            for line in md:
                print('# SUBDOCUMENT {}'.format(line), file=f)

            print(file=f)

            for line in st:
                print(line, file=f)


def make_document_metadata(document_name, contact, description, version='1.0.0', copyright=None, authors=None,
                           licenses=None):
    """Builds a list of lines for the document metadata section of a BEL document

    :param document_name: The unique name for this BEL document
    :param contact: The email address of the maintainer
    :param description: A description of the contents of this document
    :param version: The version. Defaults to 1.0.0
    :param copyright: Copyright information about this document
    :param authors: The authors of this document
    :param licenses: The license applied to this document
    :type document_name: str
    :type contact: str
    :type description: str
    :type version: str
    :type copyright: str
    :type authors: str
    :type licenses: str
    :return: A list of lines for the document metadata section
    :rtype: list of str
    """
    lines = []

    lines.append('SET DOCUMENT Name = "{}'.format(document_name))
    lines.append('SET DOCUMENT Version = "{}"'.format(version))

    if licenses is not None:
        lines.append('SET DOCUMENT License = "{}"'.format(licenses))

    lines.append('SET DOCUMENT Description = "{}"'.format(description))

    if authors is not None:
        lines.append('SET DOCUMENT Authors = {}'.format(authors))

    lines.append('SET DOCUMENT ContactInfo = "{}"'.format(contact))

    if copyright is not None:
        lines.append('SET DOCUMENT Copyright = "{}"'.format(copyright))

    return lines


def make_document_namespaces(namespace_dict=None):
    """Builds a list of lines for the namespace definitions

    :param namespace_dict: dictionary of {str name: str URL} of namespaces
    :type namespace_dict: dict
    :return: List of lines for the namespace definitions
    :rtype: list of str
    """

    namespace_dict = default_namespaces if namespace_dict is None else namespace_dict

    return [NAMESPACE_FMT.format(name, url) for name, url in sorted(namespace_dict.items(), key=itemgetter(1))]


def make_document_annotations(annotation_dict=None):
    """Builds a list of lines for the annotation definitions

    :param annotation_dict: A dictionary of {str name: str URL} of annotations
    :type annotation_dict: dict
    :return: A list of lines for the annotation definitions
    :rtype: list of str
    """

    annotation_dict = default_annotations if annotation_dict is None else annotation_dict

    return [ANNOTATION_FMT.format(name, url) for name, url in sorted(annotation_dict.items(), key=itemgetter(1))]


def make_document_statement_group(pmids):
    lines = []

    for i, pmid in enumerate(pmids, start=1):
        lines.append('SET STATEMENT_GROUP = "Group {}"\n'.format(i))
        res = requests.get(title_url_fmt.format(pmid))
        title = res.content.decode('utf-8').strip()

        lines.append(citation_format.format(title, pmid))

        res = requests.get(abstract_url_fmt.format(pmid))
        abstract = res.content.decode('utf-8').strip()

        lines.append(evidence_format.format(abstract))
        lines.append('UNSET STATEMENT_GROUP')

    return lines


def write_boilerplate(document_name, contact, description, version=None, copyright=None, authors=None,
                      licenses=None, namespace_dict=None, annotations_dict=None, pmids=None, file=None):
    """Writes a boilerplate BEL document, with standard document metadata, definitions. Optionally, if a
    list of PubMed identifiers are given, the citations and abstracts will be written for each.


    :param document_name: The unique name for this BEL document
    :type document_name: str
    :param contact: The email address of the maintainer
    :type contact: str
    :param description: A description of the contents of this document
    :type description: str
    :param version: The version. Defaults to :code:`1.0.0`
    :type version: str
    :param copyright: Copyright information about this document
    :type copyright: str
    :param authors: The authors of this document
    :type authors: str
    :param licenses: The license applied to this document
    :type licenses: str
    :param file: output stream. If None, defaults to :code:`sys.stdout`
    :param namespace_dict: an optional dictionary of {str name: str URL} of namespaces
    :type namespace_dict: dict
    :param annotations_dict: an optional dictionary of {str name: str URL} of annotations
    :type annotations_dict: dict
    :param pmids: an optional list of PMID's to autopopulate with citation and abstract
    :type pmids: iterable
    """

    file = sys.stdout if file is None else file

    for line in make_document_metadata(document_name, contact, description, version, copyright, authors, licenses):
        print(line, file=file)
    print('', file=file)

    for line in make_document_namespaces(namespace_dict):
        print(line, file=file)
    print('', file=file)

    for line in make_document_annotations(annotations_dict):
        print(line, file=file)
    print('', file=file)

    if pmids is not None:
        for line in make_document_statement_group(pmids):
            print(line, file=file)
