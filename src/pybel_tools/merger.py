"""Utilities to merge multiple BEL documents on the same topic

Steps:

1. load all documents
2. identify document metadata information and ns/annot defs
3. postpend all statement groups with "- {author email}" and add comments with document information
"""

from __future__ import print_function

import os
from itertools import islice

from .boilerplate import make_document_metadata


def split_document(lines):
    lines = list(lines)
    end_document_section = 1 + max(i for i, line in enumerate(lines) if line.startswith('SET DOCUMENT'))
    end_definitions_section = 1 + max(i for i, line in enumerate(lines) if
                                      line.startswith('DEFINE ANNOTATION') or line.startswith('DEFINE NAMESPACE'))
    documents = [line for line in islice(lines, end_document_section) if not line.startswith('#')]
    definitions = [line for line in islice(lines, end_document_section, end_definitions_section) if
                   not line.startswith('#')]

    statements = lines[end_definitions_section:]

    return documents, definitions, statements


def merge(output_path, *input_paths, merge_document_name=None, merge_document_contact=None,merge_document_description=None):
    """

    :param output_path:
    :param input_paths:
    :param merge_document_name:
    :param merge_document_contact:
    :param merge_document_description:
    :return:
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
