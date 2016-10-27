import click


@click.group(help="PyBEL-Tools Command Line Utilities")
@click.version_option()
def main():
    pass


@main.command()
@click.option('--host')
@click.option('--debug', is_flag=True)
def run(host, debug):
    from .webparser.app import app as webparserapp
    webparserapp.run(debug=debug, host=host)
