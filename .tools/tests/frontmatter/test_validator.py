"""
Tests for the validator module.
"""

from frontmatter.validator import validate_frontmatter


def test_valid_book_frontmatter(file_content_factory) -> None:
    """Test that a valid book frontmatter passes validation."""
    frontmatter = {
        "title": "Test Book",
        "draft": False,
        "slug": "test-book",
        "type": "books",
        "params": {
            "authors": ["John Doe"],
            "book_title": "The Test Book",
            "where_to_get": [
                {
                    "store": "Amazon",
                    "link": "https://amazon.com"
                }
            ]
        }
    }
    
    file_content = file_content_factory(frontmatter=frontmatter)
    result = validate_frontmatter(file_content)
    
    assert result.is_valid
    assert len(result.errors) == 0
    assert len(result.warnings) == 0


def test_missing_required_fields(file_content_factory) -> None:
    """Test that missing required fields are detected."""
    frontmatter = {
        "title": "Test Book",
        # Missing: draft, slug, type, params
    }
    
    file_content = file_content_factory(frontmatter=frontmatter)
    result = validate_frontmatter(file_content)
    
    assert not result.is_valid
    assert len(result.errors) == 4  # All required fields missing


def test_invalid_field_types(file_content_factory) -> None:
    """Test that invalid field types are detected."""
    frontmatter = {
        "title": 123,           # Should be str
        "draft": "not_bool",    # Should be bool
        "slug": ["list"],       # Should be str
        "type": "wrong_type",   # Should be "books"
        "params": "not_dict"    # Should be dict
    }
    
    file_content = file_content_factory(frontmatter=frontmatter)
    result = validate_frontmatter(file_content)
    
    assert not result.is_valid
    assert len(result.errors) >= 4  # At least 4 type errors


def test_invalid_params_structure(file_content_factory) -> None:
    """Test that invalid params structure is detected."""
    frontmatter = {
        "title": "Test Book",
        "draft": False,
        "slug": "test-book",
        "type": "books",
        "params": {
            "authors": "not_a_list",    # Should be list
            "book_title": 123,          # Should be str
            "unknown_param": "value"    # Unknown field
        }
    }
    
    file_content = file_content_factory(frontmatter=frontmatter)
    result = validate_frontmatter(file_content)
    
    assert not result.is_valid
    assert len(result.errors) >= 3  # At least 3 errors in params


def test_invalid_where_to_get(file_content_factory) -> None:
    """Test that invalid where_to_get items are detected."""
    frontmatter = {
        "title": "Test Book",
        "draft": False,
        "slug": "test-book",
        "type": "books",
        "params": {
            "authors": ["Author"],
            "book_title": "Title",
            "where_to_get": [
                {  # Missing required field
                    "store": "Amazon"
                    # Missing: link
                },
                {  # Wrong types
                    "store": 123,
                    "link": ["not_string"]
                }
            ]
        }
    }
    
    file_content = file_content_factory(frontmatter=frontmatter)
    result = validate_frontmatter(file_content)
    
    assert not result.is_valid
    assert len(result.errors) >= 2  # At least 2 errors in where_to_get


def test_date_format_validation(file_content_factory) -> None:
    """Test that invalid date formats are detected as warnings."""
    frontmatter = {
        "title": "Test Book",
        "draft": False,
        "slug": "test-book",
        "type": "books",
        "params": {
            "authors": ["Author"],
            "book_title": "Title"
        },
        "date": "2023-01-01",          # Invalid format
        "lastmod": "not a date"        # Invalid format
    }
    
    file_content = file_content_factory(frontmatter=frontmatter)
    result = validate_frontmatter(file_content)
    
    assert len(result.warnings) == 2  # Two date format warnings 