#!/usr/bin/env python3

import pytest
from pathlib import Path
from ..registry import (
    get_display_name,
    get_tag_color,
    generate_registry,
)
from ..validate import validate_mapping_against_colors
from ..transform import get_internal_name
from ..file_ops import (
    write_mapping_file,
    write_colors_file,
    write_patterns_file,
    load_patterns,
    load_colors_file,
)


@pytest.fixture
def mock_data_dir(tmp_path: Path) -> Path:
    """Create mock data directory with test files."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    return data_dir


@pytest.fixture
def test_files(mock_data_dir: Path) -> tuple[Path, Path, Path]:
    """Create test files with sample data."""
    # Create test mapping file
    mapping = {
        "science fiction": "Science Fiction",
        "ya": "Young Adult",
        "lgbtqia+": "LGBTQIA+",
    }
    mapping_file = mock_data_dir / "mapping.json"
    write_mapping_file(mapping_file, mapping)

    # Create test colors file
    colors = {
        "Genres": {
            "Science Fiction": "forest",
            "Young Adult": "burgundy",
            "LGBTQIA+": "rust",
        }
    }
    colors_file = mock_data_dir / "colors.toml"
    write_colors_file(colors_file, colors)

    # Create test normalization file
    patterns = {
        "split": {"separators": []},
        "compounds": {"values": []},
        "remove": {"prefixes": [], "exact": []},
        "normalizations": {
            "ya": "young-adult",
            "lgbtqia+": "lgbtqia-plus",
        },
        "url_normalizations": {
            "LGBTQIA+": "lgbtqia-plus",
        },
        "display": {
            "young-adult": "Young Adult",
            "lgbtqia-plus": "LGBTQIA+",
            "science-fiction": "Science Fiction",
        },
    }
    patterns_file = mock_data_dir / "patterns.toml"
    write_patterns_file(patterns_file, patterns)

    return mapping_file, colors_file, patterns_file


def test_compare_tag_sets(test_files: tuple[Path, Path, Path]):
    """Test comparing tag sets with normalization."""
    # Test data
    mapping_tags = {"science fiction", "ya", "lgbtqia+"}
    colors_tags = {"Science Fiction", "Young Adult", "LGBTQIA+"}

    # Compare sets
    missing_in_colors, missing_in_mapping = validate_mapping_against_colors(
        mapping_file=test_files[0],
        colors_file=test_files[1],
    )

    # Should match after normalization
    assert not missing_in_colors
    assert not missing_in_mapping


def test_compare_tag_sets_with_mismatches(test_files: tuple[Path, Path, Path]):
    """Test comparing tag sets with actual mismatches."""
    # Create test mapping file with mismatches
    mapping = {"science fiction": "Science Fiction", "unknown tag": "Unknown Tag"}
    write_mapping_file(test_files[0], mapping)

    # Create test colors file with mismatches
    colors = {"Genres": {"Science Fiction": "forest", "missing tag": "burgundy"}}
    write_colors_file(test_files[1], colors)

    missing_in_colors, missing_in_mapping = validate_mapping_against_colors(
        mapping_file=test_files[0],
        colors_file=test_files[1],
    )

    assert "unknown-tag" in missing_in_colors
    assert "missing-tag" in missing_in_mapping


def test_get_internal_name():
    """Test tag internal name generation."""
    # Test basic normalization
    assert get_internal_name("Some Tag") == "some-tag"

    # Test parenthetical removal
    assert get_internal_name("Young Adult (YA)") == "young-adult"

    # Test special character handling
    assert get_internal_name("Children's Books") == "childrens-books"
    assert get_internal_name("Sci-Fi & Fantasy") == "sci-fi-&-fantasy"
