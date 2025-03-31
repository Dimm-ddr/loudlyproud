"""Main entry point for the language tool."""

import click
from pathlib import Path

from .analyzer import analyze_content, analyze_translation_tables
from .normalizer import normalize_directory

@click.group()
def cli():
    """Language tool for analyzing and normalizing language entries in Hugo frontmatter."""
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

@cli.command()
@click.argument('path', type=click.Path(exists=True))
def normalize(path: str):
    """Normalize language names in frontmatter files to use uniform names.
    
    This command will:
    1. Create a mapping from translated language names to uniform names
    2. Process all markdown files in the given directory or a single file
    3. Update language entries in frontmatter to use uniform names
    """
    path_obj = Path(path)
    changed, total = normalize_directory(path_obj)
    
    print(f"\nNormalization complete:")
    print(f"Files changed: {changed}")
    print(f"Total files processed: {total}")

if __name__ == '__main__':
    cli() 