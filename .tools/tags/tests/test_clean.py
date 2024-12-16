#!/usr/bin/env python3

from pathlib import Path
from ..clean import (
    get_removable_mapping_keys,
    get_removable_color_tags,
    clean_frontmatter,
    process_book_file,
)
from ..normalize import TagNormalizer
from ..file_ops import (
    write_mapping_file,
    write_colors_file,
    write_patterns_file,
    write_removable_tags,
    split_frontmatter,
)
import pytest

# Test data
SAMPLE_FRONTMATTER = """---
draft: false
slug: test-book
title: Test Book
type: books
params:
  authors:
    - Test Author
  book_title: Test Book
  tags:
    - fiction
    - general
    - science fiction
    - nyt:bestseller
    - test tag
---
"""

SAMPLE_BOOK_CONTENT = f"{SAMPLE_FRONTMATTER}\nTest book content.\n"


def write_sample_book(file_path: Path) -> None:
    """Write sample book content to file."""
    file_path.write_text(SAMPLE_BOOK_CONTENT, encoding="utf-8")


def test_get_removable_mapping_keys(tmp_path: Path):
    # Create test mapping file
    mapping = {
        "fiction": None,
        "general": None,
        "science fiction": "science fiction",
        "nyt:bestseller": None,
        "test tag": "test tag",
    }
    mapping_file = tmp_path / "mapping.json"
    write_mapping_file(mapping_file, mapping)

    # Create test patterns file
    patterns = {"remove": {"prefixes": ["nyt:"], "exact": ["fiction", "general"]}}
    patterns_file = tmp_path / "patterns.yaml"
    write_patterns_file(patterns_file, patterns)

    result = get_removable_mapping_keys(mapping_file, patterns_file)

    assert "prefixes" in result
    assert "exact matches" in result
    assert "nyt:bestseller" in result["prefixes"]
    assert "fiction" in result["exact matches"]
    assert "general" in result["exact matches"]
    assert "science fiction" not in result["exact matches"]
    assert "test tag" not in result["exact matches"]


def test_get_removable_color_tags(tmp_path: Path):
    # Create test mapping file
    mapping = {
        "valid tag": "Valid Tag",
        "another tag": "Another Tag",
    }
    mapping_file = tmp_path / "mapping.json"
    write_mapping_file(mapping_file, mapping)

    # Create test colors file
    colors = {
        "category1": {
            "Valid Tag": "#123456",
            "Obsolete Tag": "#654321",
        },
        "category2": {
            "Another Tag": "#abcdef",
            "Old Tag": "#fedcba",
        },
    }
    colors_file = tmp_path / "colors.toml"
    write_colors_file(colors_file, colors)

    result = get_removable_color_tags(colors_file, mapping_file)

    assert "category1" in result
    assert "category2" in result
    assert "Obsolete Tag" in result["category1"]
    assert "Old Tag" in result["category2"]
    assert "Valid Tag" not in result["category1"]
    assert "Another Tag" not in result["category2"]


@pytest.fixture
def test_config(tmp_path: Path) -> dict:
    """Return test configuration."""
    config = {
        "mapping": {
            "fiction": None,
            "general": None,
            "science fiction": "science fiction",
            "nyt:bestseller": None,
            "test tag": "test tag",
        },
        "patterns": {
            "remove": {"prefixes": ["nyt:"]},
            "split": {"separators": []},
            "compounds": [],
        },
        "to_remove": [
            "fiction",
            "general",
        ],
    }

    # Write to_remove.toml file
    remove_file = tmp_path / "data/tags/to_remove.toml"
    write_removable_tags(remove_file, config["to_remove"])

    return config


def test_clean_frontmatter(tmp_path: Path, test_config):
    # Set up test environment
    content_dir = tmp_path / "content"
    locale_dir = content_dir / "en"
    books_dir = locale_dir / "books"
    books_dir.mkdir(parents=True, exist_ok=True)

    # Write sample book file
    book_file = books_dir / "test-book.md"
    write_sample_book(book_file)

    # Create test configuration files
    mapping = test_config["mapping"]
    mapping_file = tmp_path / "data/tags/mapping.json"
    mapping_file.parent.mkdir(parents=True, exist_ok=True)
    write_mapping_file(mapping_file, mapping)

    patterns = test_config["patterns"]
    patterns_file = tmp_path / "data/tags/patterns.yaml"
    write_patterns_file(patterns_file, patterns)

    # Create normalizer with test configuration
    normalizer = TagNormalizer(tmp_path)

    # Run clean_frontmatter
    clean_frontmatter(content_dir, normalizer)

    # Verify results
    assert normalizer.stats.total_files == 1
    assert normalizer.stats.files_with_changes == 1

    # Check updated content
    content = book_file.read_text(encoding="utf-8")

    # Parse the frontmatter using our function
    if result := split_frontmatter(content):
        frontmatter, _ = result
        tags = frontmatter["params"]["tags"]

        assert "fiction" not in tags
        assert "general" not in tags
        assert "nyt:bestseller" not in tags
        assert "science fiction" in tags
        assert "test tag" in tags
    else:
        pytest.fail("Failed to parse frontmatter")


def test_process_book_file(tmp_path: Path, test_config):
    # Create test book file
    book_file = tmp_path / "test-book.md"
    write_sample_book(book_file)

    # Create test configuration
    mapping = test_config["mapping"]
    mapping_file = tmp_path / "data/tags/mapping.json"
    mapping_file.parent.mkdir(parents=True, exist_ok=True)
    write_mapping_file(mapping_file, mapping)

    patterns = test_config["patterns"]
    patterns_file = tmp_path / "data/tags/patterns.yaml"
    write_patterns_file(patterns_file, patterns)

    # Create normalizer with test configuration
    normalizer = TagNormalizer(tmp_path)

    # Test processing
    changed, original_tags = process_book_file(book_file, normalizer)

    # Verify results
    assert changed is True
    assert set(original_tags) == {
        "fiction",
        "general",
        "science fiction",
        "nyt:bestseller",
        "test tag",
    }

    # Check updated content
    content = book_file.read_text(encoding="utf-8")

    # Parse the frontmatter using our function
    if result := split_frontmatter(content):
        frontmatter, _ = result
        tags = frontmatter["params"]["tags"]

        assert "fiction" not in tags
        assert "general" not in tags
        assert "nyt:bestseller" not in tags
        assert "science fiction" in tags
        assert "test tag" in tags
    else:
        pytest.fail("Failed to parse frontmatter")
