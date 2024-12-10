#!/usr/bin/env python3

import sys
from pathlib import Path
import click

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

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
def cleanup():
    """Clean up tags in book files."""
    from tags.cleanup import main
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

cli.add_command(validate)
cli.add_command(cleanup)
cli.add_command(sort)
cli.add_command(monitor)

if __name__ == "__main__":
    cli()