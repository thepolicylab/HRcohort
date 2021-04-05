import click

from . import __version__


@click.command()
@click.version_option(version=__version__)
def main():
  """The HR Cohort Python project."""
  click.echo("Hello World")