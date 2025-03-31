"""Core functionality for analyzing language entries in Hugo frontmatter files."""

import re
from pathlib import Path
from ruamel.yaml import YAML

def load_translation_tables() -> tuple[set[str], dict[str, set[str]]]:
    """Load all translation tables and return combined valid languages and per-file languages."""
    yaml = YAML(typ='safe')
    valid_languages = set()
    per_file_languages = {}
    
    # Determine the correct path to i18n directory
    current_dir = Path.cwd()
    if current_dir.name == '.tools':
        i18n_dir = current_dir.parent / 'i18n'
    else:
        i18n_dir = current_dir / 'i18n'
    
    if not i18n_dir.exists():
        print(f"Warning: Translation directory not found at {i18n_dir}")
        return valid_languages, per_file_languages
    
    # list of known UI-related keys to exclude
    ui_keys = {'language_switcher_label', 'language_tooltip'}
    
    for lang_file in i18n_dir.glob('*.yaml'):
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                data = yaml.load(f)
                if data:
                    # Extract language keys (remove 'language_' prefix) and convert to lowercase
                    # Exclude UI-related keys
                    lang_keys = {k[9:].lower() for k in data.keys() 
                               if k.startswith('language_') and k not in ui_keys}
                    valid_languages.update(lang_keys)
                    per_file_languages[lang_file.name] = lang_keys
        except Exception as e:
            print(f"Warning: Could not load {lang_file}: {e}")
    
    return valid_languages, per_file_languages

def check_translation_consistency(per_file_languages: dict[str, set[str]]) -> list[str]:
    """Check for inconsistencies between translation tables and return warning messages."""
    warnings = []
    
    # Get all unique languages across all files
    all_languages = set()
    for langs in per_file_languages.values():
        all_languages.update(langs)
    
    # Check each file against the complete set
    for filename, langs in per_file_languages.items():
        missing = all_languages - langs
        if missing:
            warnings.append(f"Warning: {filename} is missing translations for: {', '.join(sorted(missing))}")
    
    return warnings

def analyze_translation_tables(output_file: str | None = None) -> None:
    """Analyze translation tables for consistency."""
    valid_languages, per_file_languages = load_translation_tables()
    warnings = check_translation_consistency(per_file_languages)
    
    output = []
    
    # Add translation table summary
    output.append("Translation Table Coverage:")
    for filename, langs in sorted(per_file_languages.items()):
        output.append(f"- {filename}: {len(langs)} languages")
    output.append("")
    
    # Add all available languages
    output.append("Available Languages:")
    for lang in sorted(valid_languages):
        output.append(f"- {lang}")
    output.append("")
    
    # Add warnings if any
    if warnings:
        output.append("Translation Table Warnings:")
        output.extend(warnings)
    
    # Join output with newlines
    output_text = "\n".join(output)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"Results written to {output_file}")
    else:
        print(output_text)

def extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content."""
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if frontmatter_match:
        try:
            yaml = YAML(typ='safe')
            return yaml.load(frontmatter_match.group(1))
        except Exception:
            return {}
    return {}

def get_languages_from_frontmatter(frontmatter: dict) -> set[str]:
    """Extract languages from frontmatter, handling both direct lists and nested structures."""
    languages = set()
    
    # Check direct languages field
    if 'languages' in frontmatter:
        if isinstance(frontmatter['languages'], list):
            languages.update(frontmatter['languages'])
        elif isinstance(frontmatter['languages'], str):
            languages.add(frontmatter['languages'])
    
    # Check params.languages if it exists
    if 'params' in frontmatter and 'languages' in frontmatter['params']:
        if isinstance(frontmatter['params']['languages'], list):
            languages.update(frontmatter['params']['languages'])
        elif isinstance(frontmatter['params']['languages'], str):
            languages.add(frontmatter['params']['languages'])
    
    return languages

def validate_languages(languages: set[str], valid_languages: set[str]) -> tuple[set[str], set[str]]:
    """Validate languages against the valid set and return valid and invalid languages."""
    valid_langs = {lang for lang in languages if lang.lower() in valid_languages}
    invalid_langs = languages - valid_langs
    return valid_langs, invalid_langs

def analyze_file(file_path: str | Path, valid_languages: set[str]) -> tuple[set[str], set[str]]:
    """Analyze a single markdown file and return its valid and invalid languages."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    frontmatter = extract_frontmatter(content)
    languages = get_languages_from_frontmatter(frontmatter)
    return validate_languages(languages, valid_languages)

def analyze_directory(directory: str | Path, valid_languages: set[str]) -> tuple[set[str], set[str]]:
    """Analyze all markdown files in a directory and return combined valid and invalid languages."""
    all_valid_languages = set()
    all_invalid_languages = set()
    directory = Path(directory)
    
    for file_path in directory.rglob('*.md'):
        valid_langs, invalid_langs = analyze_file(file_path, valid_languages)
        all_valid_languages.update(valid_langs)
        all_invalid_languages.update(invalid_langs)
    
    return all_valid_languages, all_invalid_languages

def analyze_content(path: str | Path, output_file: str | None = None) -> None:
    """Analyze content files for language entries."""
    valid_languages, per_file_languages = load_translation_tables()
    warnings = check_translation_consistency(per_file_languages)
    
    path = Path(path)
    if not path.exists():
        print(f"Error: Path '{path}' does not exist")
        return
    
    if path.is_file():
        valid_langs, invalid_langs = analyze_file(path, valid_languages)
    else:
        valid_langs, invalid_langs = analyze_directory(path, valid_languages)
    
    # Sort languages for consistent output
    sorted_valid_langs = sorted(valid_langs)
    sorted_invalid_langs = sorted(invalid_langs)
    
    # Prepare output
    output = []
    
    # Add translation consistency warnings
    if warnings:
        output.append("Translation Table Warnings:")
        output.extend(warnings)
        output.append("")
    
    # Add content analysis results
    output.append(f"Found {len(sorted_valid_langs)} valid and {len(sorted_invalid_langs)} invalid language entries in content:\n")
    
    if sorted_valid_langs:
        output.append("Valid languages:")
        for lang in sorted_valid_langs:
            output.append(f"- {lang}")
        output.append("")
    
    if sorted_invalid_langs:
        output.append("Invalid languages (need to be updated):")
        for lang in sorted_invalid_langs:
            output.append(f"- {lang}")
        output.append("")
    
    # Add translation table summary
    output.append("Translation table coverage:")
    for filename, langs in sorted(per_file_languages.items()):
        output.append(f"- {filename}: {len(langs)} languages")
    
    # Join output with newlines
    output_text = "\n".join(output)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"Results written to {output_file}")
    else:
        print(output_text) 