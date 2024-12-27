#!/usr/bin/env python3

import pytest
from pathlib import Path
from ..normalize import TagNormalizer
from .test_helpers import detailed_assert, with_context
from ..file_ops import (
    write_mapping_file,
    write_patterns_file,
)
from ..common import MAPPING_FILE, PATTERNS_FILE, TO_REMOVE_FILE, DATA_DIR


@pytest.fixture
def normalizer(test_project: Path) -> TagNormalizer:
    """Create normalizer with test configuration."""
    return TagNormalizer(test_project)


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
            ["American", "short stories"],
        ),  # split via mapping
        (
            ["detective and mystery stories"],
            ["detective", "mystery"],
        ),  # another mapping example
        (
            ["venice (italy)"],
            ["Venice"],
        ),  # parentheses pattern with proper capitalization
    ],
)
def test_normalize_tags_parametrized(input_tags, expected, normalizer):
    """Test tag normalization with various inputs."""
    result = normalizer.normalize_tags(input_tags)
    assert set(result) == set(
        expected
    ), f"Failed to normalize {input_tags}. Got {result}, expected {expected}"
