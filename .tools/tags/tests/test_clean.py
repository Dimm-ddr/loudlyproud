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
    write_frontmatter,
)
from ..common import (
    MAPPING_FILE,
    PATTERNS_FILE,
    TO_REMOVE_FILE,
    DATA_DIR,
)
import pytest


# Test data
@pytest.fixture
def test_book_frontmatter() -> dict:
    """Return test book frontmatter with tags."""
    return {
        "draft": False,
        "slug": "test-book",
        "title": "Test Book",
        "type": "books",
        "params": {
            "authors": ["Test Author"],
            "book_title": "Test Book",
            "tags": [
                "fiction",
                "general",
                "science fiction",
                "nyt:bestseller",
                "test tag",
            ],
        },
    }


def write_sample_book(file_path: Path, frontmatter: dict) -> None:
    """Write sample book content to file."""
    write_frontmatter(file_path, frontmatter, "Test book content.\n")


def test_get_removable_mapping_keys(tmp_path: Path):
    """Test finding removable mapping keys."""
    # Create test data directory
    data_dir = tmp_path / DATA_DIR.name / "tags"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Create test mapping file
    mapping = {
        "fiction": None,
        "general": None,
        "science fiction": "science fiction",
        "nyt:bestseller": None,
        "test tag": "test tag",
    }
    mapping_file = data_dir / "test_mapping.json"
    write_mapping_file(mapping_file, mapping)

    # Create test patterns file
    patterns = {"remove": {"prefixes": ["nyt:"], "exact": ["fiction", "general"]}}
    patterns_file = data_dir / "test_patterns.toml"
    write_patterns_file(patterns_file, patterns)

    # Get removable keys
    result = get_removable_mapping_keys(mapping_file, patterns_file)

    # Verify results
    assert "prefixes" in result
    assert "exact matches" in result
    assert "nyt:bestseller" in result["prefixes"]
    assert "fiction" in result["exact matches"]
    assert "general" in result["exact matches"]
    assert "science fiction" not in result["exact matches"]
    assert "test tag" not in result["exact matches"]


def test_get_removable_mapping_keys_empty_files(tmp_path: Path):
    # Empty mapping file
    mapping_file = tmp_path / MAPPING_FILE.name
    write_mapping_file(mapping_file, {})

    patterns_file = tmp_path / PATTERNS_FILE.name
    write_patterns_file(patterns_file, {"remove": {"prefixes": ["nyt:"]}})

    result = get_removable_mapping_keys(mapping_file, patterns_file)
    assert not result  # Should return empty dict

    # Empty patterns file
    mapping = {"test": None}
    write_mapping_file(mapping_file, mapping)
    write_patterns_file(patterns_file, {})

    result = get_removable_mapping_keys(mapping_file, patterns_file)
    assert not result  # Should return empty dict


def test_get_removable_mapping_keys_no_removable(tmp_path: Path):
    # No tags match removal patterns
    mapping = {
        "valid_tag": "Valid Tag",
        "another_tag": "Another Tag",
    }
    mapping_file = tmp_path / MAPPING_FILE.name
    write_mapping_file(mapping_file, mapping)

    patterns = {"remove": {"prefixes": ["nyt:"]}}
    patterns_file = tmp_path / PATTERNS_FILE.name
    write_patterns_file(patterns_file, patterns)

    result = get_removable_mapping_keys(mapping_file, patterns_file)
    assert not result  # Should return empty dict


def test_get_removable_color_tags(tmp_path: Path):
    """Test finding removable color tags."""
    # Create test data directory
    data_dir = tmp_path / DATA_DIR.name / "tags"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Create test mapping file
    mapping = {
        "science fiction": "science fiction",
        "test tag": "test tag",
    }
    mapping_file = data_dir / "test_mapping.json"
    write_mapping_file(mapping_file, mapping)

    # Create test colors file
    colors = {
        "Genres": {
            "science fiction": "forest",
            "unmapped tag": "forest",
        }
    }
    colors_file = data_dir / "test_colors.toml"
    write_colors_file(colors_file, colors)

    # Get removable tags
    result = get_removable_color_tags(colors_file, mapping_file)

    # Verify results
    assert "Genres" in result
    assert "unmapped tag" in result["Genres"]
    assert "science fiction" not in result["Genres"]


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
    remove_file = tmp_path / DATA_DIR.name / TO_REMOVE_FILE.name
    remove_file.parent.mkdir(parents=True, exist_ok=True)
    write_removable_tags(remove_file, config["to_remove"])

    return config


def test_clean_frontmatter(tmp_path: Path, test_book_frontmatter: dict):
    """Test cleaning frontmatter in book files."""
    # Set up test environment
    content_dir = tmp_path / "content"
    locale_dir = content_dir / "en"
    books_dir = locale_dir / "books"
    books_dir.mkdir(parents=True, exist_ok=True)

    # Write sample book file
    book_file = books_dir / "test-book.md"
    write_sample_book(book_file, test_book_frontmatter)

    # Create test configuration files
    data_dir = tmp_path / "data" / "tags"
    data_dir.mkdir(parents=True, exist_ok=True)

    mapping_file = data_dir / "mapping.json"
    patterns_file = data_dir / "patterns.toml"
    to_remove_file = data_dir / "to_remove.toml"

    # Create test mapping file
    mapping = {
        "fiction": None,
        "general": None,
        "science fiction": "science fiction",
        "nyt:bestseller": None,
        "test tag": "test tag",
    }
    write_mapping_file(mapping_file, mapping)

    # Create test patterns file
    patterns = {
        "remove": {"prefixes": ["nyt:"], "exact": ["fiction", "general"]},
        "compounds": {
            "values": [
                {
                    "pattern": r"^young adult fiction (.+)$",
                    "map_to": ["young adult (YA)", "{}"],
                }
            ]
        },
    }
    write_patterns_file(patterns_file, patterns)
    write_removable_tags(to_remove_file, [])

    # Create normalizer with test configuration
    normalizer = TagNormalizer(
        project_root=tmp_path,
        mapping_file=mapping_file,
        patterns_file=patterns_file,
        to_remove_file=to_remove_file,
    )

    # Run clean_frontmatter with test files
    clean_frontmatter(
        content_dir,
        normalizer,
        mapping_file=mapping_file,
        patterns_file=patterns_file,
        to_remove_file=to_remove_file,
    )

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


def test_process_book_file(tmp_path: Path, test_book_frontmatter: dict):
    """Test processing a single book file."""
    # Create test book file
    book_file = tmp_path / "test-book.md"
    write_sample_book(book_file, test_book_frontmatter)

    # Create test configuration files
    data_dir = tmp_path / "data" / "tags"
    data_dir.mkdir(parents=True, exist_ok=True)

    mapping_file = data_dir / "mapping.json"
    patterns_file = data_dir / "patterns.toml"
    to_remove_file = data_dir / "to_remove.toml"

    # Create test mapping file
    mapping = {
        "fiction": None,
        "general": None,
        "science fiction": "science fiction",
        "nyt:bestseller": None,
        "test tag": "test tag",
    }
    write_mapping_file(mapping_file, mapping)

    # Create test patterns file
    patterns = {
        "remove": {"prefixes": ["nyt:"], "exact": ["fiction", "general"]},
        "compounds": {
            "values": [
                {
                    "pattern": r"^young adult fiction (.+)$",
                    "map_to": ["young adult (YA)", "{}"],
                }
            ]
        },
    }
    write_patterns_file(patterns_file, patterns)
    write_removable_tags(to_remove_file, [])

    # Create normalizer with test configuration
    normalizer = TagNormalizer(
        project_root=tmp_path,
        mapping_file=mapping_file,
        patterns_file=patterns_file,
        to_remove_file=to_remove_file,
    )

    # Process book file with test files
    changed, original_tags = process_book_file(
        book_file,
        normalizer,
        mapping_file=mapping_file,
        patterns_file=patterns_file,
        to_remove_file=to_remove_file,
    )

    # Verify results
    assert changed is True
    assert "fiction" in original_tags
    assert "general" in original_tags
    assert "nyt:bestseller" in original_tags

    # Check updated content
    content = book_file.read_text(encoding="utf-8")
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
