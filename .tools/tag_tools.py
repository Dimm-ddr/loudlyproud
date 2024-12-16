#!/usr/bin/env python3

import sys
from pathlib import Path
import click

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from .tags.clean import (
    get_removable_mapping_keys,
    get_removable_color_tags,
    print_removable_tags,
)


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
@click.option(
    "--mapping-file",
    type=click.Path(exists=True, path_type=Path),
    default="data/tags/mapping.json",
    help="Path to mapping file",
)
@click.option(
    "--patterns-file",
    type=click.Path(exists=True, path_type=Path),
    default="data/tags/patterns.yaml",
    help="Path to patterns file",
)
def mapping(mapping_file: Path, patterns_file: Path):
    """Find tags that could be removed from mapping file."""
    removable = get_removable_mapping_keys(mapping_file, patterns_file)
    print_removable_tags(removable, "Tags that could be removed from mapping file")


@clean.command()
@click.option(
    "--colors-file",
    type=click.Path(exists=True, path_type=Path),
    default="data/tags/colors.toml",
    help="Path to colors file",
)
@click.option(
    "--mapping-file",
    type=click.Path(exists=True, path_type=Path),
    default="data/tags/mapping.json",
    help="Path to mapping file",
)
def colors(colors_file: Path, mapping_file: Path):
    """Find tags that could be removed from colors file."""
    removable = get_removable_color_tags(colors_file, mapping_file)
    print_removable_tags(removable, "Tags that could be removed from colors file")


@clean.command(name="frontmatter", aliases=["content"])
def clean_content():
    """Clean up tags in book files."""
    from tags.clean import clean_frontmatter
    from tags.normalize import TagNormalizer

    project_root = Path.cwd()
    content_dir = project_root / "content"
    normalizer = TagNormalizer(project_root)

    clean_frontmatter(content_dir, normalizer)


cli.add_command(validate)
cli.add_command(sort)
cli.add_command(monitor)
cli.add_command(clean)

if __name__ == "__main__":
    cli()
