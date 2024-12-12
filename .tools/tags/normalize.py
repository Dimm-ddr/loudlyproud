#!/usr/bin/env python3

import re
from pathlib import Path
from typing import TypeAlias
from collections.abc import Sequence
from ruamel.yaml import YAML
import json
from .common import TAGS_CONFIG_DIR, TagStats

# Type aliases
TagValue: TypeAlias = str | list[str] | None


class TagNormalizer:
    def __init__(
        self,
        project_root: Path = None,
        patterns_file: Path = None,
        mapping_file: Path = None,
    ) -> None:
        """Initialize normalizer with patterns and mapping files."""
        self.project_root = project_root or Path.cwd()

        if patterns_file is None:
            patterns_file = self.project_root / TAGS_CONFIG_DIR / "patterns.yaml"
        if mapping_file is None:
            mapping_file = self.project_root / TAGS_CONFIG_DIR / "mapping.json"

        yaml = YAML(typ="safe")
        with open(patterns_file) as f:
            self.patterns = yaml.load(f)

        # Load mapping for correct capitalization
        with open(mapping_file) as f:
            self.mapping = json.load(f)
            self.mapping_lower = {k.lower(): k for k in self.mapping}

        # Initialize stats
        self.stats = TagStats()

    def should_remove(self, tag: str) -> bool:
        """
        Check if tag should be removed entirely.
        - exact: remove if the tag matches exactly
        - prefixes: remove if the tag starts with any of these prefixes
        """
        tag = tag.lower().strip()

        # Check exact matches - must match the whole tag
        exact_matches = self.patterns.get("remove", {}).get("exact", [])
        if tag in (x.lower() for x in exact_matches):
            return True

        # Check prefixes - if tag starts with prefix, remove the whole tag
        prefixes = self.patterns.get("remove", {}).get("prefixes", [])
        return any(tag.startswith(prefix.lower()) for prefix in prefixes)

    def split_tag(self, tag: str) -> list[str] | str:
        """Split tag if it matches any splitting patterns."""
        # Get separators from patterns, default to empty list if not present
        separators = self.patterns.get("split", {}).get("separators", [])

        for rule in separators:
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
        Normalize a single tag in steps:
        1. Check if tag should be removed
        2. Apply patterns (split/transform)
        3. Convert to lowercase
        4. Apply mapping
        """
        if self.should_remove(tag):
            return None

        # 1. Apply patterns
        result = self.apply_compound_rules(tag)
        if isinstance(result, list):
            transformed_tags = result
        else:
            # Try splitting if compound rules didn't apply
            result = self.split_tag(tag)
            transformed_tags = result if isinstance(result, list) else [result]

        # 2. Convert to lowercase
        lowercase_tags = [t.lower() for t in transformed_tags]

        # 3. Apply mapping
        mapped_tags = []
        for tag in lowercase_tags:
            # First try to get the proper capitalization from mapping
            if tag in self.mapping_lower:
                proper_key = self.mapping_lower[tag]
                mapped = self.mapping[proper_key]
                if mapped is not None:
                    mapped_tags.append(mapped)
            else:
                self.stats.unknown_tags.add(tag)
                mapped_tags.append(tag)

        return mapped_tags if len(mapped_tags) > 1 else mapped_tags[0]

    def normalize_tags(self, tags: Sequence[str]) -> list[str]:
        """
        Normalize a list of tags:
        1. Apply normalization to each tag
        2. Flatten the results
        3. Remove duplicates (case-sensitive since mapping was already applied)
        4. Remove redundant tags (e.g. if we have both "YA" and "young adult")
        """
        print("\nNormalizing tags:", tags)  # Debug
        normalized = []
        seen = set()

        # First pass: normalize all tags
        for tag in tags:
            result = self.normalize(tag)
            if isinstance(result, list):
                for r in result:
                    if r and r.lower() not in seen:
                        normalized.append(r)
                        seen.add(r.lower())
                        self.stats.normalized_tags[r] += 1
            elif result:
                if result.lower() not in seen:
                    normalized.append(result)
                    seen.add(result.lower())
                    self.stats.normalized_tags[result] += 1

        print(f"\nAfter first pass: {normalized}")  # Debug

        # Second pass: remove redundant tags
        final_tags = []
        seen_lower = set()

        for tag in sorted(normalized):  # Sort to ensure consistent order
            tag_lower = tag.lower()

            # Skip if we've seen this tag in any form
            if tag_lower in seen_lower:
                print(f"  Skipping duplicate: {tag}")  # Debug
                continue

            # Skip if this is a redundant form
            is_redundant = False
            for other in normalized:
                if other != tag and other.lower() != tag_lower:
                    # Check if this tag is a part of another tag
                    if tag_lower in other.lower().split():
                        print(f"  Skipping redundant: {tag} (part of {other})")  # Debug
                        is_redundant = True
                        break

            if not is_redundant:
                final_tags.append(tag)
                seen_lower.add(tag_lower)

        print(f"\nFinal tags: {sorted(final_tags)}")  # Debug
        return sorted(final_tags)


def load_tag_normalization() -> tuple[dict[str, str], dict[str, str]]:
    """Load tag normalization rules."""
    yaml = YAML(typ="safe")
    with open(Path("data/tags/tag_normalization.yaml")) as f:
        data = yaml.load(f)
        return (
            {k.lower(): v for k, v in data.get("normalizations", {}).items()},
            data.get("display", {}),
        )
