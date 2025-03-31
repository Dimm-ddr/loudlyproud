#!/usr/bin/env python3
import argparse
import re
from ruamel.yaml import YAML
from pathlib import Path
from typing import Set, List, Union

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

def get_languages_from_frontmatter(frontmatter: dict) -> Set[str]:
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

def analyze_file(file_path: Union[str, Path]) -> Set[str]:
    """Analyze a single markdown file and return its languages."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    frontmatter = extract_frontmatter(content)
    return get_languages_from_frontmatter(frontmatter)

def analyze_directory(directory: Union[str, Path]) -> Set[str]:
    """Analyze all markdown files in a directory and return combined languages."""
    all_languages = set()
    directory = Path(directory)
    
    for file_path in directory.rglob('*.md'):
        all_languages.update(analyze_file(file_path))
    
    return all_languages

def main():
    parser = argparse.ArgumentParser(description='Analyze language entries in Hugo frontmatter files')
    parser.add_argument('path', help='Path to a markdown file or directory containing markdown files')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    
    args = parser.parse_args()
    
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path '{path}' does not exist")
        return
    
    if path.is_file():
        languages = analyze_file(path)
    else:
        languages = analyze_directory(path)
    
    # Sort languages for consistent output
    sorted_languages = sorted(languages)
    
    # Prepare output
    output = f"Found {len(sorted_languages)} unique language entries:\n\n"
    for lang in sorted_languages:
        output += f"- {lang}\n"
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)

if __name__ == '__main__':
    main() 