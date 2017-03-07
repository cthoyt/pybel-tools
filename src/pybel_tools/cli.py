# -*- coding: utf-8 -*-

"""
Module that contains the command line app

Why does this file exist, and why not put this in __main__?
You might be tempted to import things from __main__ later, but that will cause
problems--the code will get executed twice:
 - When you run `python3 -m pybel_tools` python will execute
   ``__main__.py`` as a script. That means there won't be any
   ``pybel_tools.__main__`` in ``sys.modules``.
 - When you import __main__ it will get executed again (as a module) because
   there's no ``pybel_tools.__main__`` in ``sys.modules``.
Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""

import sys
from getpass import getuser

import click

from pybel import from_pickle, to_database
from pybel.constants import DEFAULT_CACHE_LOCATION
from .definition_utils import write_namespace
from .document_utils import write_boilerplate


@click.group(help="PyBEL-Tools Command Line Utilities on {}".format(sys.executable))
@click.version_option()
def main():
    pass


@main.command()
@click.argument('path')
@click.option('--connection', help='Input cache location. Defaults to {}'.format(DEFAULT_CACHE_LOCATION))
@click.option('--skip-check-version', is_flag=True, help='Skip checking the PyBEL version of the gpickle')
def upload(path, connection, skip_check_version):
    """Sketchy uploader that doesn't respect database edge store"""
    graph = from_pickle(path, check_version=(not skip_check_version))
    to_database(graph, connection=connection)


@main.command()
@click.option('--host', help='Flask host')
@click.option('--debug', is_flag=True)
def web(host, debug):
    """Runs the PyBEL web tools"""
    from .web.app import app
    app.run(debug=debug, host=host)


@main.command()
@click.option('--connection', help='Input cache location. Defaults to {}'.format(DEFAULT_CACHE_LOCATION))
@click.option('--host', help='Flask host. Defaults to http://localhost:5000')
@click.option('--debug', is_flag=True)
@click.option('--skip-check-version', is_flag=True, help='Skip checking the PyBEL version of the gpickle')
def service(connection, host, debug, skip_check_version):
    """Runs the PyBEL API RESTful web service"""
    from .service.dict_service import app, get_dict_service
    get_dict_service(app).load_networks(connection=connection, check_version=(not skip_check_version))
    app.run(debug=debug, host=host)


@main.group()
def definition():
    """Definition file utilities"""


@definition.command()
@click.argument('name')
@click.argument('keyword')
@click.argument('domain')
@click.argument('citation')
@click.option('--author', default=getuser())
@click.option('--description')
@click.option('--species')
@click.option('--version')
@click.option('--contact')
@click.option('--license')
@click.option('--values', default=sys.stdin, help="A file containing the list of names")
@click.option('--functions')
@click.option('--output', type=click.File('w'), default=sys.stdout)
@click.option('--value-prefix', default='')
def namespace(name, keyword, domain, citation, author, description, species, version, contact, license, values,
              functions, output, value_prefix):
    """Builds a namespace from items"""
    write_namespace(
        name, keyword, domain, author, citation, values,
        namespace_description=description,
        namespace_species=species,
        namespace_version=version,
        author_contact=contact,
        author_copyright=license,
        functions=functions,
        file=output,
        value_prefix=value_prefix
    )


@main.group()
def document():
    """BEL document utilities"""


@document.command()
@click.argument('document-name')
@click.argument('contact')
@click.argument('description')
@click.argument('pmids', nargs=-1)
@click.option('--version')
@click.option('--copyright')
@click.option('--authors')
@click.option('--licenses')
@click.option('--output', type=click.File('wb'), default=sys.stdout)
def boilerplate(document_name, contact, description, pmids, version, copyright, authors, licenses, output):
    """Builds a template BEL document with the given PMID's"""
    write_boilerplate(
        document_name,
        contact,
        description,
        version,
        copyright,
        authors,
        licenses,
        pmids=pmids,
        file=output
    )


if __name__ == '__main__':
    main()
