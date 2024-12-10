#!/usr/bin/env python3

import pytest
from tags.normalize import TagNormalizer
from .test_helpers import detailed_assert, with_context


@pytest.fixture
def normalizer():
    return TagNormalizer()


def test_should_remove():
    """Test tags that should be removed"""
    normalizer = TagNormalizer()
    assert normalizer.should_remove("nyt:something") is True
    assert normalizer.should_remove("collectionID:test") is True
    assert normalizer.should_remove("general") is True
    assert normalizer.should_remove("fiction") is True
    assert normalizer.should_remove("valid tag") is False


def test_trim_tag():
    """Test trimming of common prefixes and suffixes"""
    normalizer = TagNormalizer()
    assert normalizer.trim_tag("fiction something") == "something"
    assert normalizer.trim_tag("something fiction") == "something"
    assert normalizer.trim_tag("something fiction.") == "something"
    assert normalizer.trim_tag("fiction: something") == "something"


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
    """Test full normalization process"""
    normalizer = TagNormalizer()
    input_tags = [
        "nyt:bestseller",
        "fiction romance",
        "venice (italy)",
        "tag--fiction",
    ]
    expected = ["fiction", "romance", "venice", "italy", "tag"]
    assert set(normalizer.normalize_tags(input_tags)) == set(expected)
