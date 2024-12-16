#!/usr/bin/env python3

import pytest
from tags.normalize import TagNormalizer
from .test_helpers import detailed_assert, with_context
from pathlib import Path
from ..file_ops import (
    write_mapping_file,
    write_patterns_file,
)


@pytest.fixture
def normalizer(tmp_path: Path) -> TagNormalizer:
    """Create normalizer with test configuration."""
    # Create test mapping file
    mapping = {
        "american": "American fiction",
        "american fiction": "American fiction",
        "short stories": "short stories",
        "american short stories": ["American fiction", "short stories"],
        "fantasy": "fantasy",
        "strips": None,
        "detective and mystery stories": ["detective", "mystery"],
        "venice": "Venice",
        "italy": "Italy",
    }
    mapping_file = tmp_path / "data/tags/mapping.json"
    mapping_file.parent.mkdir(parents=True, exist_ok=True)
    write_mapping_file(mapping_file, mapping)

    # Create test patterns file
    patterns = {
        "remove": {"prefixes": ["nyt:"]},
        "split": {
            "separators": [
                {"pattern": " \\(([^)]+)\\)", "extract_groups": True},
            ]
        },
        "compounds": [],
    }
    patterns_file = tmp_path / "data/tags/patterns.yaml"
    write_patterns_file(patterns_file, patterns)

    # Create to_remove file
    remove_file = tmp_path / "data/tags/to_remove.toml"
    remove_file.parent.mkdir(parents=True, exist_ok=True)
    with open(remove_file, "w", encoding="utf-8") as f:
        f.write('to_remove = ["fiction", "general", "strips"]\n')

    return TagNormalizer(tmp_path)


def test_should_remove():
    """Test tags that should be removed"""
    normalizer = TagNormalizer()
    assert normalizer.should_remove("nyt:something") is True
    assert normalizer.should_remove("collectionID:test") is True
    assert normalizer.should_remove("general") is True
    assert normalizer.should_remove("fiction") is True
    assert normalizer.should_remove("valid tag") is False


def test_split_tag():
    """Test tag splitting patterns"""
    normalizer = TagNormalizer()
    assert normalizer.split_tag("tag--fiction") == ["tag", "fiction"]
    assert normalizer.split_tag("venice (italy)") == ["venice", "italy"]
    assert normalizer.split_tag("normal tag") == "normal tag"


@with_context
def test_compound_rules():
    """Test compound mapping rules"""
    normalizer = TagNormalizer()

    # Test specific transformations
    test_tag = "young adult fiction romance"
    result = normalizer.apply_compound_rules(test_tag)
    detailed_assert(
        "compound rule transformation",
        test_tag,
        ["young adult (YA)", "romance"],
        result,
        available_patterns=normalizer.patterns["compounds"],
    )

    # Other assertions
    test_tag = "fiction lgbtqia+ gay"
    result = normalizer.apply_compound_rules(test_tag)
    detailed_assert(
        "LGBTQIA+ rule transformation",
        test_tag,
        ["LGBTQIA+", "gay"],
        result,
        available_patterns=normalizer.patterns["compounds"],
    )


def test_normalize_tags():
    """Test normalizing a list of tags."""
    input_tags = [
        "fantasy",
        "romance",
        "strips",  # should be removed
        "contemporary romance",  # should be split via mapping
    ]
    expected = ["fantasy", "romance", "contemporary"]
    normalizer = TagNormalizer()
    assert set(normalizer.normalize_tags(input_tags)) == set(expected)


@pytest.mark.parametrize(
    "input_tags,expected",
    [
        (["fantasy"], ["fantasy"]),
        (["strips"], []),  # should be removed
        (["fantasy", "strips"], ["fantasy"]),
        (
            ["american short stories"],
            ["American fiction", "short stories"],
        ),  # split via mapping
        (
            ["detective and mystery stories"],
            ["detective", "mystery"],
        ),  # another mapping example
        (
            ["venice (italy)"],
            ["Venice", "Italy"],
        ),  # parentheses pattern with proper capitalization
    ],
)
def test_normalize_tags_parametrized(input_tags, expected, normalizer):
    """Test tag normalization with various inputs."""
    assert set(normalizer.normalize_tags(input_tags)) == set(expected)
