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
                
                # Process each language key
                for key, value in data.items():
                    if not key.startswith('language_') or key in ui_keys:
                        continue
                    
                    # Extract the uniform name (e.g., 'english' from 'language_english')
                    uniform_name = key[9:].lower()
                    
                    # Map the translated value to the uniform name
                    # Store everything in lowercase in the map
                    value_lower = value.lower()
                    if value_lower not in language_map:
                        language_map[value_lower] = uniform_name
        except Exception as e:
            print(f"Warning: Could not process {lang_file}: {e}")
    
    return language_map

def normalize_languages_in_file(file_path: Path, language_map: Dict[str, str]) -> bool:
    """Normalize language names in a single markdown file's frontmatter.
    
    Args:
        file_path: Path to the markdown file
        language_map: Mapping from translated names to uniform names (all lowercase)
        
    Returns:
        True if changes were made, False otherwise
    """
    try:
        # Read the entire file as text
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Locate the frontmatter boundaries
        if not lines or not lines[0].strip() == '---':
            print("No frontmatter found")
            return False
        
        frontmatter_end = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                frontmatter_end = i
                break
        
        if frontmatter_end == -1:
            print("Incomplete frontmatter")
            return False
        
        # Find the params section and languages subsection within the frontmatter
        params_section_start = -1
        language_section_start = -1
        language_lines = []
        in_params_section = False
        in_languages_section = False
        
        for i in range(1, frontmatter_end):
            line = lines[i]
            stripped = line.strip()
            
            # Check if this line contains the params field
            if not in_params_section and stripped == "params:":
                params_section_start = i
                in_params_section = True
                continue
                
            # Look for languages field inside params section
            if in_params_section:
                # Check if we've left the params section (unindented line)
                if stripped and not line.startswith((' ', '\t')):
                    in_params_section = False
                    continue
                
                # Check for languages field within params
                if not in_languages_section and "languages:" in stripped and stripped.endswith("languages:"):
                    language_section_start = i
                    in_languages_section = True
                    continue
                
                # Collect language lines
                if in_languages_section:
                    # Check if we're still in the languages section (indented list items)
                    if stripped.startswith('-'):
                        language_lines.append(i)
                    # Check if we've left the languages section (new field at same indent level as languages)
                    elif stripped and not stripped.startswith('-'):
                        indent_level = len(line) - len(line.lstrip())
                        languages_indent = len(lines[language_section_start]) - len(lines[language_section_start].lstrip())
                        
                        if indent_level <= languages_indent:
                            in_languages_section = False
        
        if language_section_start == -1 or not language_lines:
            print("No languages section found")
            return False
        
        print(f"Found languages section at line {language_section_start+1}, with {len(language_lines)} languages")
        
        # Process each language line and replace if needed
        changed = False
        for line_idx in language_lines:
            line = lines[line_idx]
            # Extract just the language name (after the dash and whitespace)
            dash_pos = line.find('-')
            if dash_pos == -1:
                continue
                
            # Skip whitespace after the dash
            name_start = dash_pos + 1
            while name_start < len(line) and line[name_start].isspace():
                name_start += 1
            
            # Extract the language name
            lang_name = line[name_start:].strip()
            lang_lower = lang_name.lower()
            
            print(f"Processing language: {lang_name} (lowercase: {lang_lower})", end=' ')
            
            # Check if we need to normalize this language
            if lang_lower in language_map:
                normalized = language_map[lang_lower].capitalize()
                print(f"-> {normalized}")
                
                if normalized != lang_name:
                    # Replace just the language name part, keeping whitespace/formatting
                    new_line = line[:name_start] + normalized + '\n'
                    lines[line_idx] = new_line
                    changed = True
                else:
                    print("(already normalized)")
            else:
                print("(not found in language map)")
        
        if not changed:
            print("No changes needed")
            return False
        
        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

def normalize_directory(directory: Path) -> tuple[int, int]:
    """Normalize language names in all markdown files in a directory or a single file.
    
    Args:
        directory: Path to the directory or file to process
        
    Returns:
        Tuple of (files changed, total files processed)
    """
    language_map = create_language_map()
    print(f"Created language map with {len(language_map)} entries")
    changed = 0
    total = 0
    
    if directory.is_file():
        print(f"Processing single file: {directory}")
        total = 1
        try:
            if normalize_languages_in_file(directory, language_map):
                changed = 1
                print(f"✓ Changed language names in {directory}")
            else:
                print(f"✗ No changes applied to {directory}")
        except Exception as e:
            print(f"✗ Error processing {directory}: {e}")
        return changed, total
    
    print(f"Processing directory: {directory}")
    for file_path in directory.rglob('*.md'):
        total += 1
        print(f"Processing {file_path}...", end=' ')
        try:
            if normalize_languages_in_file(file_path, language_map):
                changed += 1
                print("✓ Changed")
            else:
                print("✗ No changes")
        except Exception as e:
            print(f"✗ Error: {e}")
            
    return changed, total 