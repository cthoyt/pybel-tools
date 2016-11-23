import sys
from getpass import getuser

import click

from .owlparser import build


@click.group(help="PyBEL-Tools Command Line Utilities on {}".format(sys.executable))
@click.version_option()
def main():
    pass


@main.command()
@click.option('--host')
@click.option('--debug', is_flag=True)
def run(host, debug):
    from .webparser.app import app as webparserapp
    webparserapp.run(debug=debug, host=host)


@main.command()
@click.option('--host')
@click.option('--debug', is_flag=True)
def run_full(host, debug):
    from .web.pybelweb import app
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
    build(title, subject, description, creator, email, url, values, functions, output, value_prefix)


if __name__ == '__main__':
    main()
