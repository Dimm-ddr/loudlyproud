#!/usr/bin/env python3

import sys
from pathlib import Path
import click

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from tags.clean import (
    get_removable_mapping_keys,
    get_removable_color_tags,
    print_removable_tags,
    clean_frontmatter,
)
from tags.normalize import TagNormalizer
from tags.common import CONTENT_DIR, MAPPING_FILE, PATTERNS_FILE, COLORS_FILE


@click.group()
def cli():
    """Tag management tools for book metadata."""
    pass


@click.command()
def validate():
    """Validate tags against mapping and colors."""
    from tags.validate import main
    main()


@click.command()
def sort():
    """Sort tags mapping and colors files."""
    from tags.sorting import main
    main()


@click.command()
def monitor():
    """Monitor tag changes in PR."""
    from tags.monitor import main
    main()


@click.group()
def clean():
    """Clean tag files and content."""
    pass


@clean.command()
def mapping():
    """Find tags that could be removed from mapping file."""
    removable = get_removable_mapping_keys(MAPPING_FILE, PATTERNS_FILE)
    print_removable_tags(removable, "Tags that could be removed from mapping file")


@clean.command()
def colors():
    """Find tags that could be removed from colors file."""
    removable = get_removable_color_tags(COLORS_FILE, MAPPING_FILE)
    print_removable_tags(removable, "Tags that could be removed from colors file")


@clean.command()
def frontmatter():
    """Clean up tags in book files."""
    project_root = Path.cwd()
    normalizer = TagNormalizer(project_root)
    clean_frontmatter(CONTENT_DIR, normalizer)


@clean.command()
def content():
    """Clean up tags in book files (alias for frontmatter)."""
    project_root = Path.cwd()
    normalizer = TagNormalizer(project_root)
    clean_frontmatter(CONTENT_DIR, normalizer)


cli.add_command(validate)
cli.add_command(sort)
cli.add_command(monitor)
cli.add_command(clean)

if __name__ == "__main__":
    cli()
