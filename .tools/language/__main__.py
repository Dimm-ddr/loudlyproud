"""Command-line interface for the language analyzer package."""

import click
from .analyzer import analyze_content, analyze_translation_tables

@click.group()
def cli():
    """Language analyzer for Hugo frontmatter files."""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('-o', '--output', help='Output file for results')
def content(path, output):
    """Analyze content files for language entries."""
    analyze_content(path, output)

@cli.command()
@click.option('-o', '--output', help='Output file for results')
def translations(output):
    """Analyze translation tables for consistency."""
    analyze_translation_tables(output)

if __name__ == '__main__':
    cli() 