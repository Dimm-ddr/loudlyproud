#!/usr/bin/env python3

from pathlib import Path
from ruamel.yaml import YAML
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Replacement:
    from_str: str
    to: str

@dataclass
class SpecialCase:
    from_str: str
    normalized: str
    display: Optional[str] = None

class TagNormalizer:
    def __init__(self, rules_file: Path):
        yaml = YAML(typ='safe')
        rules = yaml.load(rules_file.read_text())

        self.replacements = [
            Replacement(r['from'], r['to'])
            for r in rules['replacements']
        ]

        self.special_cases = [
            SpecialCase(
                from_str=sc['from'],
                normalized=sc['normalized'],
                display=sc.get('display')
            )
            for sc in rules['special_cases']
        ]

        self.display_overrides = rules.get('display_overrides', {})

    def normalize(self, tag: str) -> str:
        """Normalize a tag according to the rules."""
        tag = tag.lower()

        # Check special cases first
        for case in self.special_cases:
            if tag == case.from_str:
                return case.normalized

        # Apply basic replacements
        for replacement in self.replacements:
            tag = tag.replace(replacement.from_str, replacement.to)

        return tag

    def get_display_name(self, tag: str) -> str:
        """Get the display name for a tag."""
        normalized = self.normalize(tag)

        # Check special cases first
        for case in self.special_cases:
            if tag.lower() == case.from_str:
                return case.display or tag

        # Check display overrides
        if normalized in self.display_overrides:
            return self.display_overrides[normalized]

        return tag

# Create a singleton instance
_normalizer: Optional[TagNormalizer] = None

def get_normalizer() -> TagNormalizer:
    """Get or create the TagNormalizer instance."""
    global _normalizer
    if _normalizer is None:
        rules_file = Path(__file__).parent.parent.parent / 'data' / 'tags' / 'normalization_rules.yaml'
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