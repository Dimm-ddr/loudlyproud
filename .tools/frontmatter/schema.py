"""
Schema definition for book content validation.
"""

SCHEMA = {
    "root_required": ["title", "draft", "slug", "type", "params"],
    "root_optional": ["date", "lastmod", "weight", "description"],
    "root_types": {
        "title": str,
        "draft": bool,
        "slug": str,
        "type": "books",  # Must be exactly this string
        "params": dict,
        "date": str,       # ISO or RFC3339 format (validated)
        "lastmod": str,    # ISO or RFC3339
        "weight": int,
        "description": str,  # Short meta description (not book summary)
    },
    "root_additionalProperties": False,

    "params_required": [
        "authors",
        "book_title",
    ],
    "params_optional": [
        "translators", "short_book_description", "cover", "cover_alt", "isbn",
        "additional_isbns", "languages", "page_count", "publication_year", "goodreads_link",
        "series", "where_to_get", "publishers", "russian_translation_status",
        "russian_audioversion", "tags"
    ],
    "params_types": {
        "authors": [str],
        "translators": [str],
        "book_title": str,
        "short_book_description": str,
        "cover": str,
        "cover_alt": str,
        "isbn": str,
        "additional_isbns": [str],
        "languages": [str],
        "page_count": str,
        "publication_year": str,
        "goodreads_link": str,
        "series": str,
        "where_to_get": [{
            "store": str,
            "link": str,
            "date": str,  # ISO-8601; optional
        }],
        "publishers": [str],
        "russian_translation_status": (
            "unknown", "might_exist", "unlikely_to_exist", "does_not_exist", "exists"
        ),
        "russian_audioversion": bool,
        "tags": [str],
    },
    "params_additionalProperties": False,
    "where_to_get_types": {
        "store": str,
        "link": str,
        "date": str,
    },
    "where_to_get_required": ["store", "link"],
    "where_to_get_additionalProperties": False,
} 