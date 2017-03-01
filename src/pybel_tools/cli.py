import sys
from getpass import getuser

import click

from .definition_utils import write_namespace
from .document_utils import write_boilerplate


@click.group(help="PyBEL-Tools Command Line Utilities on {}".format(sys.executable))
@click.version_option()
def main():
    pass


@main.command()
@click.option('--host')
@click.option('--debug', is_flag=True)
def web(host, debug):
    from .web.app import app
    app.run(debug=debug, host=host)


@main.command()
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
@click.option('--values', default=sys.stdin)
@click.option('--functions')
@click.option('--output', type=click.File('w'), default=sys.stdout)
@click.option('--value-prefix', default='')
def buildns(name, keyword, domain, citation, author, description, species, version, contact, license, values, functions,
            output, value_prefix):
    write_namespace(name, keyword, domain, author, citation, values, namespace_description=description,
                    namespace_species=species, namespace_version=version, author_contact=contact,
                    author_copyright=license, functions=functions, file=output, value_prefix=value_prefix)


@main.command()
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
    write_boilerplate(document_name, contact, description, version, copyright, authors, licenses, pmids=pmids,
                      file=output)


if __name__ == '__main__':
    main()
