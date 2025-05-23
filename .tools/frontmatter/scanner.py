"""
File scanner for finding markdown files to validate.
"""
from pathlib import Path
from typing import Generator, List

from .constants import BOOK_CONTENT_PATHS, MARKDOWN_EXTENSION


def scan_markdown_files() -> Generator[Path, None, None]:
    """
    Scan for markdown files in the specified content directories.
    
    Yields:
        Path objects for each markdown file found.
    """
    for content_path in BOOK_CONTENT_PATHS:
        path = Path(content_path)
        if not path.exists():
            continue
            
        for file_path in path.rglob(f"*{MARKDOWN_EXTENSION}"):
            if file_path.is_file():
                yield file_path


def get_all_markdown_files() -> List[Path]:
    """
    Return a list of all markdown files in the content directories.
    
    Returns:
        List of Path objects for each markdown file found.
    """
    return list(scan_markdown_files()) 