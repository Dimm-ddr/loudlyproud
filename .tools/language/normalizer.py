"""Module for normalizing language names in frontmatter files."""

from pathlib import Path
from typing import Dict, Set
from ruamel.yaml import YAML

def create_language_map() -> Dict[str, str]:
    """Create a mapping from translated language names to uniform names.
    
    Returns:
        Dict mapping translated names to uniform names (e.g. "Английский" -> "English")
    """
    yaml = YAML(typ='safe')
    language_map: Dict[str, str] = {}
    
    # Determine the correct path to i18n directory
    current_dir = Path.cwd()
    if current_dir.name == '.tools':
        i18n_dir = current_dir.parent / 'i18n'
    else:
        i18n_dir = current_dir / 'i18n'
    
    if not i18n_dir.exists():
        raise FileNotFoundError(f"Translation directory not found at {i18n_dir}")
    
    # List of known UI-related keys to exclude
    ui_keys = {'language_switcher_label', 'language_tooltip'}
    
    # First pass: collect all language keys and their translations
    for lang_file in i18n_dir.glob('*.yaml'):
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                data = yaml.load(f)
                if not data:
                    continue
                
                # Get the language code from filename (e.g., 'en' from 'en.yaml')
                lang_code = lang_file.stem
                
                # Process each language key
                for key, value in data.items():
                    if not key.startswith('language_') or key in ui_keys:
                        continue
                    
                    # Extract the uniform name (e.g., 'english' from 'language_english')
                    uniform_name = key[9:].lower()
                    
                    # Map the translated value to the uniform name
                    # Use the English translation as the canonical form
                    if lang_code == 'en':
                        language_map[value.lower()] = uniform_name.capitalize()
                    else:
                        language_map[value.lower()] = uniform_name.capitalize()
        except Exception as e:
            print(f"Warning: Could not process {lang_file}: {e}")
    
    return language_map

def normalize_languages_in_file(file_path: Path, language_map: Dict[str, str]) -> bool:
    """Normalize language names in a single markdown file's frontmatter.
    
    Args:
        file_path: Path to the markdown file
        language_map: Mapping from translated names to uniform names
        
    Returns:
        True if changes were made, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract frontmatter
        if not content.startswith('---'):
            return False
            
        _, frontmatter, content = content.split('---', 2)
        
        # Parse frontmatter
        yaml = YAML(typ='safe')
        data = yaml.load(frontmatter)
        
        if not data or 'language' not in data:
            return False
            
        # Normalize languages
        languages = data['language']
        if isinstance(languages, str):
            languages = [languages]
            
        normalized_languages = []
        changed = False
        
        for lang in languages:
            lang_lower = lang.lower()
            if lang_lower in language_map:
                normalized = language_map[lang_lower]
                if normalized != lang:
                    changed = True
                normalized_languages.append(normalized)
            else:
                normalized_languages.append(lang)
        
        if not changed:
            return False
            
        # Update frontmatter
        data['language'] = normalized_languages
        yaml.dump(data, frontmatter)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('---\n')
            f.write(frontmatter)
            f.write('---\n')
            f.write(content)
            
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def normalize_directory(directory: Path) -> tuple[int, int]:
    """Normalize language names in all markdown files in a directory.
    
    Args:
        directory: Path to the directory to process
        
    Returns:
        Tuple of (files changed, total files processed)
    """
    language_map = create_language_map()
    changed = 0
    total = 0
    
    for file_path in directory.rglob('*.md'):
        total += 1
        if normalize_languages_in_file(file_path, language_map):
            changed += 1
            
    return changed, total 