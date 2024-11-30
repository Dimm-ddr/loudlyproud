"""Schema definition for book content validation."""


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


SCHEMA = {
    "required_fields": ["draft", "slug", "title", "type", "params"],
    "field_types": {
        "draft": {"type": "boolean"},
        "slug": {"type": "string"},
        "title": {"type": "string"},
        "type": {"type": "string", "enum": ["books"]},
        "params": {"type": "object"},
    },
    "params": {
        "required_fields": ["authors", "book_title"],
        "field_types": {
            "authors": {"type": "array", "item_type": "string"},
            "translators": {"type": "array", "item_type": "string"},
            "book_title": {"type": "string"},
            "book_description": {"type": "string"},
            "short_book_description": {"type": "string"},
            "cover": {"type": "string", "format": "url"},
            "cover_alt": {
                "type": "string",
                "description": "Alternative text description for the cover image(s)",
            },
            "isbn": {
                "type": "string",
                "format": "isbn",
                "description": "ISBN-10 or ISBN-13, can include hyphens",
            },
            "additional_isbns": {
                "type": "array",
                "item_type": "string",
                "format": "isbn",
                "description": "Additional ISBNs for other editions",
            },
            "languages": {"type": "array", "item_type": "string"},
            "page_count": {"type": "string"},  # String to allow "~300" format
            "publication_year": {"type": "string"},  # String to allow approximate dates
            "goodreads_link": {"type": "string", "format": "url"},
            "buy_link": {"type": "string", "format": "url"},
            "series": {"type": "string"},
            "where_to_get": {
                "type": "array",
                "item_type": "object",
                "properties": {
                    "store": {"type": "string"},
                    "link": {"type": "string", "format": "url"},
                    "date": {"type": "string", "format": "date"},
                },
            },
            "publishers": {"type": "array", "item_type": "string"},
            "russian_translation_status": {
                "type": "string",
                "enum": [
                    "unknown",
                    "might_exist",
                    "unlikely_to_exist",
                    "does_not_exist",
                    "exists",
                ],
            },
            "russian_audioversion": {"type": "boolean"},
            "tags": {"type": "array", "item_type": "string"},
        },
    },
}
