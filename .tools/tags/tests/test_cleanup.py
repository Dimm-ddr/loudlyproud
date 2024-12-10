#!/usr/bin/env python3

import pytest
from tags.cleanup import TagStats, process_book_file, normalize_tags
from tags.normalize import TagNormalizer


@pytest.fixture
def test_data_dir(tmp_path):
    """Create test data directory with sample files"""
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
    return tmp_path


def test_normalize_tags():
    """Test tag normalization"""
    tags = ["venice", "italy", "romance"]
    normalizer = TagNormalizer()
    normalized = normalizer.normalize_tags(tags)
    assert "Venice" in normalized
    assert "Italy" in normalized
    assert "romance" in normalized


def test_process_book_file(test_data_dir):
    """Test book file processing"""
    normalizer = TagNormalizer()
    stats = TagStats()
    book_file = test_data_dir / "content" / "en" / "books" / "test-book.md"

    # Create minimal tags map
    tags_map = {"romance": "romance", "venice": "Venice", "italy": "Italy"}

    changed = process_book_file(book_file, tags_map, normalizer, stats)
    assert changed is True
    assert stats.files_with_changes == 0  # Gets incremented by caller
    assert len(stats.normalized_tags) > 0
