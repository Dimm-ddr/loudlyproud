from datetime import datetime
from typing import Any
from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    """Check if string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except (ValueError, AttributeError):
        return False

def is_valid_date(date_str: str) -> bool:
    """Check if string is a valid date in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_value(
    value: Any, field_type: str, field_def: dict
) -> str | None:
    """Validate a value against its type definition from schema."""
    match field_type:
        case "string":
            if not isinstance(value, str):
                if field_def.get("format") == "isbn":
                    return "Must be a string (currently a number)"
                return "Must be a string"
            # Check format if specified
            match field_def.get("format"):
                case "url" if not is_valid_url(value):
                    return "Must be a valid URL"
                case "date" if not is_valid_date(value):
                    return "Must be a valid date in YYYY-MM-DD format"
                case "isbn" if not is_valid_isbn(value):
                    return "Must be a valid ISBN-10 or ISBN-13"
        case "boolean":
            if not isinstance(value, bool):
                return "Must be a boolean"
        case "array":
            if not isinstance(value, list):
                return "Must be a list"
            if item_type := field_def.get("item_type"):
                for item in value:
                    if error := validate_value(item, item_type, {}):
                        return f"List item error: {error}"
        case "object":
            if not isinstance(value, dict):
                return "Must be an object"

    if enum_values := field_def.get("enum"):
        if value not in enum_values:
            return f"Must be one of: {', '.join(str(v) for v in enum_values)}"

    return None

# Import from book_schema.py (we'll move this here later)
def is_valid_isbn(isbn: str) -> bool:
    """Validate ISBN format."""
    # Remove any hyphens or spaces
    cleaned = isbn.replace("-", "").replace(" ", "")

    # Check if it's a valid ISBN-10 or ISBN-13
    if len(cleaned) == 10:
        return cleaned.isdigit() or (
            cleaned[:-1].isdigit() and cleaned[-1] in "0123456789X"
        )
    elif len(cleaned) == 13:
        return cleaned.isdigit()

    return False
