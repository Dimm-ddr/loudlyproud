#!/usr/bin/env python3

import re
from pathlib import Path
from typing import TypeAlias
from collections.abc import Sequence
from ruamel.yaml import YAML
import json

# Type aliases
TagValue: TypeAlias = str | list[str] | None


class TagNormalizer:
    def __init__(
        self, patterns_file: Path | None = None, mapping_file: Path | None = None
    ) -> None:
        if patterns_file is None:
            patterns_file = Path("data/tags/patterns.yaml")
        if mapping_file is None:
            mapping_file = Path("data/tags/mapping.json")

        yaml = YAML(typ="safe")
        with open(patterns_file) as f:
            self.patterns = yaml.load(f)

        # Load mapping for correct capitalization
        with open(mapping_file) as f:
            self.mapping = json.load(f)
            self.mapping_lower = {k.lower(): k for k in self.mapping}

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
        Normalize a single tag in steps:
        1. Apply patterns (split/transform)
        2. Convert to lowercase
        3. Apply mapping
        """
        if self.should_remove(tag):
            return None

        # 1. Apply patterns
        result = self.apply_compound_rules(tag)
        if isinstance(result, list):
            transformed_tags = result
        else:
            # Try splitting if compound rules didn't apply
            tag = self.trim_tag(tag)
            result = self.split_tag(tag)
            transformed_tags = result if isinstance(result, list) else [result]

        # 2. Convert to lowercase
        lowercase_tags = [t.lower() for t in transformed_tags]

        # 3. Apply mapping
        mapped_tags = [self.mapping.get(tag, tag) for tag in lowercase_tags]

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
            elif result:
                if result.lower() not in seen:
                    normalized.append(result)
                    seen.add(result.lower())

        return normalized


def load_tag_normalization() -> tuple[dict[str, str], dict[str, str]]:
    """Load tag normalization rules."""
    yaml = YAML(typ="safe")
    with open(Path("data/tags/tag_normalization.yaml")) as f:
        data = yaml.load(f)
        return (
            {k.lower(): v for k, v in data.get("normalizations", {}).items()},
            data.get("display", {}),
        )