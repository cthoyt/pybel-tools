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


@main.command()
@click.option('--host')
@click.option('--debug', is_flag=True)
def run_full(host, debug):
    from .web.pybelweb import app
    app.run(debug=debug, host=host)

if __name__ == '__main__':
    main()
