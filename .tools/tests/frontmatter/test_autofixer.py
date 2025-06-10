"""
Tests for the autofixer module.
"""
from unittest.mock import patch

from frontmatter.autofixer import autofix_frontmatter, fix_field_order
from frontmatter.types import ValidationError


def test_fix_validation_errors(file_content_factory, validation_result_factory) -> None:
    """Test that fixable validation errors are fixed correctly."""
    # Arrange
    frontmatter = {
        "title": "Test Book",
        "type": "wrong_type",  # Should be "books"
        "unknown_field": "remove",  # Should be removed
        "params": {
            "authors": "single_author",  # Should be list
            "unknown_param": "remove"  # Should be removed
        }
    }
    file_content = file_content_factory(frontmatter=frontmatter)
    
    result = validation_result_factory()
    result.errors = [
        ValidationError(
            message="Type should be 'books'",
            path=["type"],
            fixable=True,
            suggested_fix="books"
        ),
        ValidationError(
            message="Unknown field",
            path=["unknown_field"],
            fixable=True,
            suggested_fix=None
        ),
        ValidationError(
            message="Authors should be list",
            path=["params", "authors"],
            fixable=True,
            suggested_fix=["single_author"]
        ),
        ValidationError(
            message="Unknown param",
            path=["params", "unknown_param"],
            fixable=True,
            suggested_fix=None
        )
    ]
    
    # Act
    with patch("frontmatter.autofixer.write_frontmatter") as mock_write:
        fixed = autofix_frontmatter(file_content, result)
    
    # Assert
    assert fixed
    assert file_content.frontmatter["type"] == "books"
    assert "unknown_field" not in file_content.frontmatter
    assert file_content.frontmatter["params"]["authors"] == ["single_author"]
    assert "unknown_param" not in file_content.frontmatter["params"]
    mock_write.assert_called_once_with(file_content)


def test_skip_non_fixable_errors(file_content_factory, validation_result_factory) -> None:
    """Test that non-fixable errors are skipped."""
    # Arrange
    frontmatter = {
        "title": 123,  # Non-fixable type error
        "type": "wrong_type"  # Fixable
    }
    file_content = file_content_factory(frontmatter=frontmatter)
    
    result = validation_result_factory()
    result.errors = [
        ValidationError(
            message="Title wrong type",
            path=["title"],
            fixable=False
        ),
        ValidationError(
            message="Wrong type",
            path=["type"],
            fixable=True,
            suggested_fix="books"
        )
    ]
    
    # Act
    with patch("frontmatter.autofixer.write_frontmatter") as mock_write:
        fixed = autofix_frontmatter(file_content, result)
    
    # Assert
    assert fixed  # Some fixes were applied
    assert file_content.frontmatter["type"] == "books"
    assert file_content.frontmatter["title"] == 123  # Unchanged
    mock_write.assert_called_once_with(file_content)


def test_fix_where_to_get_items(file_content_factory, validation_result_factory) -> None:
    """Test fixing where_to_get items."""
    # Arrange
    frontmatter = {
        "title": "Test Book",
        "params": {
            "authors": ["Author"],
            "where_to_get": [
                {
                    "store": "Amazon",
                    "link": "https://amazon.com",
                    "wrong_field": "remove"  # Should be removed
                }
            ]
        }
    }
    file_content = file_content_factory(frontmatter=frontmatter)
    
    result = validation_result_factory()
    result.errors = [
        ValidationError(
            message="Unknown field in where_to_get",
            path=["params", "where_to_get", "0", "wrong_field"],
            fixable=True,
            suggested_fix=None
        )
    ]
    
    # Act
    with patch("frontmatter.autofixer.write_frontmatter") as mock_write:
        fixed = autofix_frontmatter(file_content, result)
    
    # Assert
    assert fixed
    assert "wrong_field" not in file_content.frontmatter["params"]["where_to_get"][0]
    mock_write.assert_called_once_with(file_content)


def test_fix_field_order(file_content_factory) -> None:
    """Test that fields are reordered correctly."""
    # Arrange
    frontmatter = {
        "params": {
            "isbn": "123-456-789",
            "book_title": "Book Title",
            "authors": ["Author"]
        },
        "draft": False,
        "title": "Test Book",
        "type": "books",
        "slug": "test-book",
        "unknown_field": "value"
    }
    file_content = file_content_factory(frontmatter=frontmatter)
    
    # Act
    with patch("frontmatter.autofixer.write_frontmatter") as mock_write:
        fixed = fix_field_order(file_content)
    
    # Assert
    assert fixed
    # Check root level order
    root_keys = list(file_content.frontmatter.keys())
    assert root_keys[:5] == ["title", "draft", "slug", "type", "params"]
    assert "unknown_field" in root_keys[5:]  # Unknown fields at end
    
    # Check params order
    params_keys = list(file_content.frontmatter["params"].keys())
    assert params_keys[:2] == ["authors", "book_title"]  # Required fields first
    assert "isbn" in params_keys[2:]  # Optional fields after
    
    mock_write.assert_called_once_with(file_content)


def test_no_changes_needed(file_content_factory) -> None:
    """Test that no changes are made when frontmatter is already correct."""
    # Arrange
    frontmatter = {
        "title": "Test Book",
        "draft": False,
        "slug": "test-book",
        "type": "books",
        "params": {
            "authors": ["Author"],
            "book_title": "Book Title"
        }
    }
    file_content = file_content_factory(frontmatter=frontmatter)
    
    # Act
    with patch("frontmatter.autofixer.write_frontmatter") as mock_write:
        fixed = fix_field_order(file_content)
    
    # Assert
    assert not fixed  # No changes needed
    mock_write.assert_not_called() 