from typing import Tuple, List, Dict, Any

def fix_languages_field(data: dict) -> tuple[bool, list[str]]:
    """Fix languages field in the data."""
    fixes = []
    modified = False

    if "params" in data and "languages" in data["params"]:
        params = data["params"]
        if isinstance(params["languages"], str):
            langs = [l.strip() for l in params["languages"].split(",")]
            params["languages"] = langs
            fixes.append("Converted 'languages' from string to list")
            modified = True
        elif isinstance(params["languages"], list):
            new_langs = []
            for lang in params["languages"]:
                if "," in lang:
                    new_langs.extend(l.strip() for l in lang.split(","))
                    modified = True
                else:
                    new_langs.append(lang)
            if modified:
                params["languages"] = new_langs
                fixes.append("Split comma-separated language entries")

    return modified, fixes


def fix_audioversion_field(data: dict) -> tuple[bool, list[str]]:
    """Fix russian_audioversion field in the data."""
    fixes = []
    modified = False

    if "params" in data and "russian_audioversion" in data["params"]:
        params = data["params"]
        if isinstance(params["russian_audioversion"], str):
            value = params["russian_audioversion"].lower()
            params["russian_audioversion"] = value == "yes"
            fixes.append("Converted 'russian_audioversion' from string to boolean")
            modified = True

    return modified, fixes


def fix_isbn_field(data: dict) -> tuple[bool, list[str]]:
    """Fix ISBN fields that are numbers instead of strings."""
    fixes = []
    modified = False

    if "params" in data:
        params = data["params"]
        if "isbn" in params and not isinstance(params["isbn"], str):
            params["isbn"] = str(params["isbn"])
            fixes.append("Converted numeric ISBN to string")
            modified = True

        if "additional_isbns" in params and isinstance(params["additional_isbns"], list):
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

    return modified, fixes


def apply_yaml_fixes(data: dict) -> tuple[bool, list[str], dict]:
    """Apply all YAML-based fixes to data."""
    modified = False
    all_fixes = []

    # Apply fixes
    langs_modified, lang_fixes = fix_languages_field(data)
    if langs_modified:
        modified = True
        all_fixes.extend(lang_fixes)

    audio_modified, audio_fixes = fix_audioversion_field(data)
    if audio_modified:
        modified = True
        all_fixes.extend(audio_fixes)

    isbn_modified, isbn_fixes = fix_isbn_field(data)
    if isbn_modified:
        modified = True
        all_fixes.extend(isbn_fixes)

    return modified, all_fixes, data