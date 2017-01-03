import sys
from getpass import getuser

import click

from .boilerplate import make_boilerplate
from .namespace_utils import build_namespace


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
@click.option('--title', default='')
@click.option('--subject', default='')
@click.option('--description', default='')
@click.option('--creator', default=getuser())
@click.option('--email', default='')
@click.option('--url', default='')
@click.option('--values', default=sys.stdin)
@click.option('--functions')
@click.option('--output', default=sys.stdout)
@click.option('--value-prefix', default='')
def buildns(title, subject, description, creator, email, url, values, functions, output, value_prefix):
    build_namespace(title, subject, description, creator, email, url, values, functions, output, value_prefix)


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
    make_boilerplate(document_name, contact, description, version, copyright, authors, licenses, pmids=pmids,
                     file=output)


if __name__ == '__main__':
    main()
