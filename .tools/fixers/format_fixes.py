from typing import Dict

def reorder_frontmatter(data: Dict) -> Dict:
    """Reorder frontmatter fields in a consistent way."""
    root_order = ["draft", "slug", "title", "type", "params"]
    params_order = [
        "authors", "book_title", "book_description", "short_book_description",
        "cover", "isbn", "languages", "goodreads_link", "page_count",
        "publication_year", "publishers", "russian_audioversion",
        "russian_translation_status", "tags",
    ]

    ordered = {}
    for field in root_order:
        if field in data:
            ordered[field] = data[field]
    for field in data:
        if field not in ordered:
            ordered[field] = data[field]

    if "params" in ordered and isinstance(ordered["params"], dict):
        params = ordered["params"]
        ordered_params = {}
        for field in params_order:
            if field in params:
                ordered_params[field] = params[field]
        for field in params:
            if field not in ordered_params:
                ordered_params[field] = params[field]
        ordered["params"] = ordered_params

    return ordered