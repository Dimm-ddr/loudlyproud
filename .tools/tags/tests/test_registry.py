#!/usr/bin/env python3

import pytest
from pathlib import Path
from ..registry import (
    compare_tag_sets,
    normalize_tag,
    get_display_name,
    get_tag_color,
    generate_registry,
)
from ..file_ops import (
    write_mapping_file,
    write_colors_file,
    write_patterns_file,
    load_patterns,
    load_colors_file,
)


@pytest.fixture
def mock_data_dir(tmp_path: Path, monkeypatch) -> Path:
    """Create and set up a mock data directory."""
    data_dir = tmp_path / "data" / "tags"
    data_dir.mkdir(parents=True)
    monkeypatch.setattr("tags.common.DATA_DIR", data_dir)
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
    patterns_file = mock_data_dir / "tag_normalization.yaml"
    write_patterns_file(patterns_file, patterns)

    return mapping_file, colors_file, patterns_file


def test_compare_tag_sets(test_files: tuple[Path, Path, Path]):
    """Test comparing tag sets with normalization."""
    # Test data
    mapping_tags = {"science fiction", "ya", "lgbtqia+"}
    colors_tags = {"Science Fiction", "Young Adult", "LGBTQIA+"}

    # Load normalization rules
    _, _, patterns_file = test_files
    normalization_rules = load_patterns(patterns_file)

    # Compare sets
    missing_in_colors, missing_in_mapping = compare_tag_sets(
        mapping_tags, colors_tags, normalization_rules
    )

    # Should match after normalization
    assert not missing_in_colors
    assert not missing_in_mapping


def test_compare_tag_sets_with_mismatches(test_files: tuple[Path, Path, Path]):
    """Test comparing tag sets with actual mismatches."""
    mapping_tags = {"science fiction", "unknown tag"}
    colors_tags = {"Science Fiction", "missing tag"}

    _, _, patterns_file = test_files
    normalization_rules = load_patterns(patterns_file)

    missing_in_colors, missing_in_mapping = compare_tag_sets(
        mapping_tags, colors_tags, normalization_rules
    )

    assert "unknown tag" in missing_in_colors
    assert "missing tag" in missing_in_mapping


def test_normalize_tag(test_files: tuple[Path, Path, Path]):
    """Test tag normalization."""
    _, _, patterns_file = test_files
    normalization_rules = load_patterns(patterns_file)

    # Test direct normalization
    assert normalize_tag("ya", normalization_rules) == "young-adult"

    # Test URL normalization
    assert normalize_tag("LGBTQIA+", normalization_rules) == "lgbtqia-plus"

    # Test default normalization
    assert normalize_tag("some tag", normalization_rules) == "some-tag"


def test_get_display_name(test_files: tuple[Path, Path, Path]):
    """Test getting display names for tags."""
    _, _, patterns_file = test_files
    normalization_rules = load_patterns(patterns_file)

    # Test display override
    assert get_display_name("ya", normalization_rules) == "Young Adult"
    assert get_display_name("lgbtqia+", normalization_rules) == "LGBTQIA+"

    # Test fallback to original
    assert get_display_name("unknown tag", normalization_rules) == "unknown tag"


def test_get_tag_color(test_files: tuple[Path, Path, Path]):
    """Test getting colors for tags."""
    _, colors_file, _ = test_files
    colors_data = load_colors_file(colors_file)

    # Test existing colors
    assert get_tag_color("Science Fiction", colors_data) == "forest"
    assert get_tag_color("Young Adult", colors_data) == "burgundy"

    # Test fallback color
    assert get_tag_color("unknown tag", colors_data) == "fallback"
