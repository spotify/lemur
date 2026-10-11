import click
from flask.cli import with_appcontext


@click.group(name="dns_providers", help="DNS provider zone management (ACME removed).")
@with_appcontext
def cli():
    pass
