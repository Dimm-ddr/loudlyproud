#!/usr/bin/env python3

import re
from pathlib import Path
from typing import TypeAlias
from collections.abc import Sequence
from ruamel.yaml import YAML

# Type aliases
TagValue: TypeAlias = str | list[str] | None


class TagNormalizer:
    def __init__(self, patterns_file: Path | None = None) -> None:
        if patterns_file is None:
            patterns_file = Path("data/tags/patterns.yaml")
        yaml = YAML(typ="safe")
        with open(patterns_file) as f:
            self.patterns = yaml.load(f)

    def should_remove(self, tag: str) -> bool:
        """Check if tag should be removed entirely."""
        tag = tag.lower()
        # Check prefixes
        for prefix in self.patterns["remove"]["prefixes"]:
            if tag.startswith(prefix.lower()):
                return True
        # Check exact matches
        return tag in (x.lower() for x in self.patterns["remove"]["exact"])

    def trim_tag(self, tag: str) -> str:
        """Remove common prefixes and suffixes."""
        for suffix in self.patterns["trim"]["suffixes"]:
            if tag.lower().endswith(suffix.lower()):
                tag = tag[: -len(suffix)]
        for prefix in self.patterns["trim"]["prefixes"]:
            if tag.lower().startswith(prefix.lower()):
                tag = tag[len(prefix) :]
        return tag.strip()

    def split_tag(self, tag: str) -> list[str] | str:
        """Split tag if it matches any splitting patterns."""
        for rule in self.patterns["split"]["separators"]:
            pattern = rule["pattern"]
            if "extract_groups" in rule and rule["extract_groups"]:
                if match := re.search(pattern, tag):
                    parts = [tag.replace(match.group(0), "").strip()]
                    parts.extend(g.strip() for g in match.groups())
                    return [p for p in parts if p]
            elif "replace" in rule:
                tag = re.sub(pattern, rule["replace"], tag)
            elif "keep_parts" in rule and rule["keep_parts"]:
                if pattern in tag:
                    return [p.strip() for p in tag.split(pattern) if p.strip()]
        return tag

    def apply_compound_rules(self, tag: str) -> list[str] | str:
        """Apply compound mapping rules."""
        for rule in self.patterns["compounds"]:
            pattern = rule["pattern"]
            if match := re.match(pattern, tag, re.IGNORECASE):
                return [
                    part.format(*(match.groups())) if "{}" in part else part.strip()
                    for part in rule["map_to"]
                ]
        return tag

    def normalize(self, tag: str) -> TagValue:
        """
        Normalize a single tag, returning either:
        - None if tag should be removed
        - A string if tag should be kept as is (after cleanup)
        - A list of strings if tag should be split into multiple tags
        """
        if self.should_remove(tag):
            return None

        # First try compound rules
        result = self.apply_compound_rules(tag)
        if isinstance(result, list):
            return result

        # Then try splitting
        tag = self.trim_tag(tag)
        result = self.split_tag(tag)

        return result if result else None

    def normalize_tags(self, tags: Sequence[str]) -> list[str]:
        """Normalize a list of tags, expanding any that split into multiple tags."""
        normalized = []
        for tag in tags:
            result = self.normalize(tag)
            if isinstance(result, list):
                normalized.extend(result)
            elif result:
                normalized.append(result)
        return list(
            dict.fromkeys(normalized)
        )  # Remove duplicates while preserving order


def normalize_tag(tag: str) -> str:
    """Legacy normalize function for backward compatibility."""
    return tag.lower().strip()


def get_tag_display_name(tag: str) -> str:
    """Get display name for a tag."""
    return tag
