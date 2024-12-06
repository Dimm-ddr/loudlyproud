#!/usr/bin/env python3

from pathlib import Path
from ruamel.yaml import YAML
from typing import Dict, Optional

class TagNormalizer:
    def __init__(self, rules_file: Path):
        yaml = YAML(typ='safe')
        rules = yaml.load(rules_file.read_text())
        self.normalizations = rules.get('normalizations', {})
        self.display_overrides = rules.get('display', {})

    def normalize(self, tag: str) -> str:
        """Convert a tag to its normalized form."""
        tag = tag.lower().strip()
        return self.normalizations.get(tag, tag)

    def get_display_name(self, tag: str) -> str:
        """Get the display form of a tag."""
        normalized = self.normalize(tag)
        return self.display_overrides.get(normalized, tag)

# Create a singleton instance
_normalizer: Optional[TagNormalizer] = None

def get_normalizer() -> TagNormalizer:
    """Get or create the TagNormalizer instance."""
    global _normalizer
    if _normalizer is None:
        rules_file = Path(__file__).parent.parent.parent / 'data' / 'tags' / 'tag_normalization.yaml'
        _normalizer = TagNormalizer(rules_file)
    return _normalizer

def normalize_tag(tag: str) -> str:
    """Normalize a single tag."""
    return get_normalizer().normalize(tag)

def get_tag_display_name(tag: str) -> str:
    """Get the display name for a tag."""
    return get_normalizer().get_display_name(tag)

if __name__ == "__main__":
    # Simple test
    test_tags = [
        "LGBTQ+",
        "U.S.A",
        "Science & Fiction",
        "Young Adult (YA)",
    ]

    for tag in test_tags:
        normalized = normalize_tag(tag)
        display = get_tag_display_name(tag)
        print(f"{tag!r} -> normalized: {normalized!r}, display: {display!r}")