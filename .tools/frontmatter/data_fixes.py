from .fixer_registry import register_data_fixer

@register_data_fixer
def fix_languages_field(data: dict) -> tuple[bool, list[str], dict]:
    """Fix languages field in the data."""
    fixes = []
    modified = False

    if "params" in data and "languages" in data["params"]:
        params = data["params"]
        if isinstance(params["languages"], str):
            langs = [lang.strip() for lang in params["languages"].split(",")]
            params["languages"] = langs
            fixes.append("Converted 'languages' from string to list")
            modified = True
        elif isinstance(params["languages"], list):
            new_langs = []
            for lang in params["languages"]:
                if isinstance(lang, str) and "," in lang:
                    new_langs.extend(part.strip() for part in lang.split(","))
                    modified = True
                else:
                    new_langs.append(lang)
            if modified:
                params["languages"] = new_langs
                fixes.append("Split comma-separated language entries")

    return modified, fixes, data

@register_data_fixer
def fix_audioversion_field(data: dict) -> tuple[bool, list[str], dict]:
    """Fix russian_audioversion field in the data."""
    fixes = []
    modified = False

    if "params" in data and "russian_audioversion" in data["params"]:
        params = data["params"]
        if isinstance(params["russian_audioversion"], str):
            value = params["russian_audioversion"].lower()
            params["russian_audioversion"] = value in ("yes", "true", "1")
            msg = "Converted 'russian_audioversion' from string to boolean"
            fixes.append(msg)
            modified = True

    return modified, fixes, data

@register_data_fixer
def fix_isbn_field(data: dict) -> tuple[bool, list[str], dict]:
    """Fix ISBN fields that are numbers instead of strings."""
    fixes = []
    modified = False

    if "params" in data:
        params = data["params"]
        if "isbn" in params and not isinstance(params["isbn"], str):
            params["isbn"] = str(params["isbn"])
            fixes.append("Converted numeric ISBN to string")
            modified = True

        if "additional_isbns" in params and isinstance(
            params["additional_isbns"], list
        ):
            new_isbns = []
            needs_fix = False
            for isbn in params["additional_isbns"]:
                if not isinstance(isbn, str):
                    new_isbns.append(str(isbn))
                    needs_fix = True
                else:
                    new_isbns.append(isbn)

            if needs_fix:
                params["additional_isbns"] = new_isbns
                fixes.append("Converted numeric additional ISBNs to strings")
                modified = True

    return modified, fixes, data

@register_data_fixer
def fix_frontmatter_format(data: dict) -> tuple[bool, list[str], dict]:
    """Fix malformed YAML frontmatter with extra newlines and structure issues."""
    fixes = []
    modified = False

    # Check for extra newlines in text fields
    if "params" in data:
        params = data["params"]
        text_fields = ["book_description", "short_book_description"]
        for field in text_fields:
            if field in params and isinstance(params[field], str):
                value = params[field]
                # Remove extra newlines and normalize line endings
                if "\n\n" in value or "\r\n" in value:
                    # Convert to YAML multiline string format
                    value = value.replace("\r\n", "\n").replace("\n\n", "\n")
                    # Remove any leading/trailing whitespace
                    value = value.strip()
                    params[field] = value
                    modified = True
                    fixes.append(f"Fixed formatting in {field}")

    return modified, fixes, data

@register_data_fixer
def fix_duplicate_fields(data: dict) -> tuple[bool, list[str], dict]:
    """Fix duplicate or conflicting fields in the data."""
    fixes = []
    modified = False

    # Look for possible duplicate fields with different casing
    if "params" in data:
        params = data["params"]
        field_map = {}
        
        # Group fields by lowercase name
        for field in list(params.keys()):
            field_lower = field.lower()
            if field_lower not in field_map:
                field_map[field_lower] = []
            field_map[field_lower].append(field)
        
        # Check for duplicates
        for field_lower, field_variations in field_map.items():
            if len(field_variations) > 1:
                # Use the first variation as canonical
                canonical = field_variations[0]
                for variant in field_variations[1:]:
                    # Merge data if needed
                    if isinstance(params[canonical], list) and isinstance(params[variant], list):
                        # For lists, combine and deduplicate
                        params[canonical].extend(params[variant])
                        # Remove duplicates while preserving order
                        seen = set()
                        params[canonical] = [x for x in params[canonical] 
                                           if not (x in seen or seen.add(x))]
                    elif params[canonical] == params[variant]:
                        # Same value, just delete the duplicate
                        pass
                    else:
                        # Different scalar values - keep canonical
                        fixes.append(f"Kept '{canonical}' value over conflicting '{variant}'")
                    
                    # Remove the variant field
                    del params[variant]
                    modified = True
                    fixes.append(f"Removed duplicate field '{variant}' (kept '{canonical}')")

    return modified, fixes, data
