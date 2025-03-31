"""Language analyzer for Hugo frontmatter files."""

__version__ = "0.1.0"

from .analyzer import (
    load_translation_tables,
    check_translation_consistency,
    analyze_translation_tables,
    analyze_file,
    analyze_directory,
) 