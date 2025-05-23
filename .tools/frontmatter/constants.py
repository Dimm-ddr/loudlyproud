"""
Constants for the frontmatter validator.
"""
# Folders to scan for book markdown files
BOOK_CONTENT_PATHS: list[str] = [
    "content/ru/books",
    "content/en/books",
    "content/fa/books",
    "content/ku/books",
]

# File extension for markdown files
MARKDOWN_EXTENSION = ".md"

# YAML frontmatter delimiters
FRONTMATTER_DELIMITER = "---"

# Date format for validation (ISO 8601 / RFC 3339)
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"  # e.g., 2023-01-01T12:00:00+00:00 