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
        Check if tag should be removed. The logic is:
        1. First check if tag starts with any of the prefixes - if yes, remove the whole tag
        2. If no prefix match, check if tag exactly matches one of the exact patterns
        """
        tag = tag.lower().strip()

        # 1. First check prefixes - if tag starts with any prefix, remove it
        prefixes = self.patterns.get("remove", {}).get("prefixes", [])
        for prefix in prefixes:
            if tag.startswith(prefix.lower()):
                return True

        # 2. Then check exact matches - must match the whole tag exactly
        exact_matches = self.patterns.get("remove", {}).get("exact", [])
        for exact in exact_matches:
            if tag == exact.lower():
                return True

        return False

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
        tag = tag.strip()
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

        # 2. Convert to lowercase for mapping lookup
        lowercase_tags = [t.lower() for t in transformed_tags]

        # 3. Apply mapping and track unknown tags
        mapped_tags = []
        for tag in lowercase_tags:
            if tag in self.mapping_lower:
                proper_key = self.mapping_lower[tag]
                mapped = self.mapping[proper_key]
                if mapped is not None:
                    mapped_tags.append(mapped)
            else:
                # Track the original case of unknown tags
                original_tag = tag.lower()
                for t in transformed_tags:
                    if t.lower() == tag:
                        original_tag = t
                        break
                self.stats.unknown_tags.add(original_tag)
                mapped_tags.append(original_tag)

        return mapped_tags if len(mapped_tags) > 1 else mapped_tags[0]

    def normalize_tags(self, tags: Sequence[str]) -> list[str]:
        """
        Normalize a list of tags:
        1. Apply normalization to each tag
        2. Flatten the results
        3. Remove duplicates (case-sensitive since mapping was already applied)
        """
        normalized = []
        seen = set()

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

        return sorted(normalized)


def load_tag_normalization() -> tuple[dict[str, str], dict[str, str]]:
    """Load tag normalization rules."""
    yaml = YAML(typ="safe")
    with open(Path("data/tags/tag_normalization.yaml")) as f:
        data = yaml.load(f)
        return (
            {k.lower(): v for k, v in data.get("normalizations", {}).items()},
            data.get("display", {}),
        )
