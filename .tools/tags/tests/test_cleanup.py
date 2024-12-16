#!/usr/bin/env python3

import pytest
import shutil
from ruamel.yaml import YAML
from tags.cleanup import process_book_file, split_frontmatter
from tags.common import TAGS_CONFIG_DIR
from tags.normalize import TagNormalizer


@pytest.fixture
def test_data_dir(tmp_path):
    """Create test data directory with sample files"""
    # Create test book file with exact format expected by split_frontmatter
    book_content = """---
params:
  tags:
    - "fiction romance"
    - "venice (italy)"
    - "nyt:bestseller"
---
Book content
"""
    book_dir = tmp_path / "content" / "en" / "books"
    book_dir.mkdir(parents=True)
    book_file = book_dir / "test-book.md"
    book_file.write_text(book_content)

    # Copy actual config files
    config_dir = tmp_path / "data" / "tags"
    config_dir.mkdir(parents=True)
    shutil.copy(TAGS_CONFIG_DIR / "patterns.yaml", config_dir / "patterns.yaml")
    shutil.copy(TAGS_CONFIG_DIR / "mapping.json", config_dir / "mapping.json")

    return tmp_path


def test_process_book_file(test_data_dir):
    """Test book file processing"""
    normalizer = TagNormalizer(test_data_dir)
    book_file = test_data_dir / "content" / "en" / "books" / "test-book.md"

    # First verify we can parse the initial content
    initial_content = book_file.read_text()
    initial_result = split_frontmatter(initial_content)
    assert initial_result is not None, "Initial frontmatter parsing failed"

    # Process the file
    changed = process_book_file(book_file, normalizer)
    assert changed is True

    # Verify the changes
    content = book_file.read_text()
    result = split_frontmatter(content)
    assert result is not None, "Failed to parse frontmatter after processing"

    frontmatter, _ = result
    normalized_tags = frontmatter["params"]["tags"]
    assert "Venice" in normalized_tags
    assert "Italy" in normalized_tags
    assert "fiction romance" in normalized_tags
