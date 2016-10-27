import click


@click.group(help="PyBEL-Tools Command Line Utilities")
@click.version_option()
def main():
    pass


@main.command()
def run():
    from .webparser.app import app as webparserapp
    webparserapp.run()
