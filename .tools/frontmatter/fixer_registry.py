from typing import Callable, Pattern
import re

# Type aliases
TextFixer = Callable[[str], tuple[str, list[str]]]
DataFixer = Callable[[dict], tuple[bool, list[str], dict]]

# Registry of text-based fixers (operating on raw string content)
TEXT_FIXERS: list[TextFixer] = []

# Registry of data-based fixers (operating on parsed YAML data)
DATA_FIXERS: list[DataFixer] = []

# Pattern-based text fixers
TEXT_PATTERNS: list[tuple[Pattern, str, str]] = [
    # Pattern, replacement, description
    (re.compile(r'(\w+): ([^"\'\n]*:[^\n]*)'), r'\1: "\2"', "Added quotes around value containing colon"),
    (re.compile(r'<br\s*\/?>'), r'\n', "Converted HTML line breaks to newlines"), 
    # Add more patterns as needed
]

def register_text_fixer(fixer: TextFixer) -> TextFixer:
    """Decorator to register a text fixer function."""
    TEXT_FIXERS.append(fixer)
    return fixer

def register_data_fixer(fixer: DataFixer) -> DataFixer:
    """Decorator to register a data fixer function."""
    DATA_FIXERS.append(fixer)
    return fixer

def apply_all_text_fixers(content: str) -> tuple[str, list[str]]:
    """Apply all registered text fixers to content."""
    all_fixes = []
    
    # First apply pattern-based fixers
    for pattern, replacement, description in TEXT_PATTERNS:
        original = content
        content = pattern.sub(replacement, content)
        if content != original:
            all_fixes.append(description)
    
    # Then apply function-based fixers
    for fixer in TEXT_FIXERS:
        content, fixes = fixer(content)
        all_fixes.extend(fixes)
    
    return content, all_fixes

def apply_all_data_fixers(data: dict) -> tuple[bool, list[str], dict]:
    """Apply all registered data fixers to parsed YAML data."""
    modified = False
    all_fixes = []
    
    for fixer in DATA_FIXERS:
        fixer_modified, fixes, data = fixer(data)
        if fixer_modified:
            modified = True
            all_fixes.extend(fixes)
    
    return modified, all_fixes, data
