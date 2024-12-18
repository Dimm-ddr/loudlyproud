#!/usr/bin/env python3

import re
from pathlib import Path
from typing import TypeAlias
from collections.abc import Sequence
from .common import TagStats, MAPPING_FILE, PATTERNS_FILE, TO_REMOVE_FILE
from .sorting import sort_strings
from .file_ops import load_patterns, load_tags_map, load_removable_tags

# Type aliases
TagValue: TypeAlias = str | list[str] | None


class TagNormalizer:
    def __init__(
        self,
        project_root: Path = None,
    ) -> None:
        """Initialize normalizer with patterns and mapping files."""
        self.project_root = project_root or Path.cwd()

        # Load patterns and mapping
        self.patterns = load_patterns(PATTERNS_FILE)
        self.mapping = load_tags_map(MAPPING_FILE)
        self.removable_tags = load_removable_tags(TO_REMOVE_FILE)

        # Create case-insensitive lookup
        self.mapping_lower = {k.lower(): k for k in self.mapping}
        self.removable_tags_lower = {t.lower() for t in self.removable_tags}

        # Build set of valid tags from mapping values
        self.valid_tags = set()
        for value in self.mapping.values():
            if value is not None:
                if isinstance(value, str):
                    self.valid_tags.add(value.lower())
                elif isinstance(value, list):
                    self.valid_tags.update(tag.lower() for tag in value)

        # Initialize stats
        self.stats = TagStats()

    def should_remove(self, tag: str) -> bool:
        """Check if tag should be removed."""
        tag = tag.lower().strip()

        # Check if tag is in removable tags
        if tag in self.removable_tags_lower:
            return True

        # Check patterns
        prefixes = self.patterns.get("remove", {}).get("prefixes", [])
        for prefix in prefixes:
            if tag.startswith(prefix.lower()):
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
        1. Check if tag matches any valid tag (case-insensitive)
        2. Clean and transform the tag (trim, remove trailing dots)
        3. Convert to lowercase
        4. Check if tag should be removed
        5. Apply patterns (split/transform)
        6. Apply mapping
        """
        # 1. Check if tag matches any valid tag
        if tag.lower() in self.valid_tags:
            # If tag is in valid tags, only normalize its case via mapping
            if tag.lower() in self.mapping_lower:
                proper_key = self.mapping_lower[tag.lower()]
                return self.mapping[proper_key]
            return tag

        # 2. Clean the tag first
        tag = tag.strip()
        # Apply cleanup patterns (like removing trailing dots)
        for rule in self.patterns.get("split", {}).get("separators", []):
            if "replace" in rule:
                tag = re.sub(rule["pattern"], rule["replace"], tag)

        # 3. Convert to lowercase
        tag = tag.lower()

        # 4. Check if should be removed
        if self.should_remove(tag):
            return None

        # 5. Apply patterns
        result = self.apply_compound_rules(tag)
        if isinstance(result, list):
            transformed_tags = result
        else:
            # Try splitting if compound rules didn't apply
            result = self.split_tag(tag)
            transformed_tags = result if isinstance(result, list) else [result]

        # 6. Apply mapping and track unknown tags
        mapped_tags = []
        for tag in transformed_tags:
            if tag in self.mapping_lower:
                proper_key = self.mapping_lower[tag]
                mapped = self.mapping[proper_key]
                if mapped is not None:
                    mapped_tags.append(mapped)
            else:
                self.stats.unknown_tags.add(tag)
                mapped_tags.append(tag)

        # Fix: Handle empty mapped_tags case
        if not mapped_tags:
            return None
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

        return sort_strings(normalized)

    def to_dict(self) -> dict:
        """Convert stats to dictionary for JSON output."""
        from .sorting import sort_stats_dict

        return sort_stats_dict(
            {
                "total_files": self.stats.total_files,
                "files_with_changes": self.stats.files_with_changes,
                "unknown_tags": list(self.stats.unknown_tags),
                "normalized_tags": dict(self.stats.normalized_tags),
            }
        )
