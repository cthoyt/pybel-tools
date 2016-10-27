import click
from .webparser.app import app as webparserapp


@click.group(help="PyBEL-Tools Command Line Utilities")
@click.version_option()
def main():
    pass


@main.command()
def run():
    webparserapp.run()
