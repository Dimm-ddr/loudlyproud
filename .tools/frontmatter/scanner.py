"""
File scanner for finding markdown files to validate.
"""
from pathlib import Path
from typing import Generator

from .constants import BOOK_CONTENT_PATHS, MARKDOWN_EXTENSION


def get_all_markdown_files(project_root: Path) -> Generator[Path, None, None]:
    """
    Scan for markdown files in the specified content directories.
    
    Args:
        project_root: Path to the project root directory
        
    Yields:
        Path objects for each markdown file found.
    """
    for content_path in BOOK_CONTENT_PATHS:
        path = project_root / content_path
        if not path.exists():
            continue
            
        for file_path in path.rglob(f"*{MARKDOWN_EXTENSION}"):
            if file_path.is_file():
                yield file_path 