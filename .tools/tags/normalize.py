#!/usr/bin/env python3

import re
from pathlib import Path
from typing import TypeAlias
from collections.abc import Sequence
from .common import TagStats, MAPPING_FILE, PATTERNS_FILE, TO_REMOVE_FILE
from .file_ops import load_patterns, load_tags_map, load_removable_tags

# Type aliases
TagValue: TypeAlias = str | list[str]


class TagNormalizer:
    def __init__(
        self,
        project_root: Path | None = None,
        mapping_file: Path = MAPPING_FILE,
        patterns_file: Path = PATTERNS_FILE,
        to_remove_file: Path = TO_REMOVE_FILE,
    ) -> None:
        """Initialize normalizer with patterns and mapping files.
        
        Args:
            project_root: Root path of the project (optional)
            mapping_file: Path to mapping file (defaults to MAPPING_FILE from common)
            patterns_file: Path to patterns file (defaults to PATTERNS_FILE from common)
            to_remove_file: Path to to_remove file (defaults to TO_REMOVE_FILE from common)
        """
        self.project_root = project_root or Path.cwd()

        # Load patterns and mapping
        self.patterns = load_patterns(patterns_file)
        self.mapping = load_tags_map(mapping_file)
        self.removable_tags = load_removable_tags(to_remove_file)

        # Create case-insensitive lookups
        self.mapping_lower = {k.lower(): k for k in self.mapping}
        self.removable_tags_lower = {t.lower() for t in self.removable_tags}

        # Build set of valid tags from mapping values
        self.valid_tags: set[str] = set()
        for value in self.mapping.values():
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
        if isinstance(separators, dict):
            separators = [separators]

        for rule in separators:
            pattern = rule.get("pattern", "")
            if "extract_groups" in rule and rule["extract_groups"]:
                if match := re.search(pattern, tag, re.IGNORECASE):
                    parts = [tag.replace(match.group(0), "").strip()]
                    parts.extend(g.strip() for g in match.groups())
                    return [p for p in parts if p and isinstance(p, str)]
            elif "replace" in rule:
                tag = re.sub(pattern, rule["replace"], tag, flags=re.IGNORECASE)
            elif "keep_parts" in rule and rule["keep_parts"]:
                if re.search(pattern, tag, re.IGNORECASE):
                    return [
                        p.strip()
                        for p in re.split(pattern, tag, flags=re.IGNORECASE)
                        if p.strip() and isinstance(p, str)
                    ]
        return tag  # Return original case

    def apply_compound_rules(self, tag: str) -> list[str] | str | None:
        """Apply compound mapping rules."""
        # Get compounds list from patterns, default to empty list if not present
        compounds = self.patterns.get("compounds", {})
        if isinstance(compounds, dict):
            compounds = compounds.get("values", [])

        for pattern in compounds:
            if not isinstance(pattern, dict):
                # Handle string patterns
                try:
                    if match := re.match(pattern, tag, re.IGNORECASE):
                        groups = match.groups()
                        # For patterns like "term1 & term2", return both terms as separate tags
                        if pattern == "^(.+) & (.+)$":
                            return [
                                g.strip() for g in groups if g and isinstance(g, str)
                            ]
                        # For other patterns, just return the groups
                        return [g.strip() for g in groups if g and isinstance(g, str)]
                except (re.error, TypeError):
                    continue  # Skip invalid patterns
            else:
                # Handle dictionary patterns with map_to field
                try:
                    if match := re.match(pattern["pattern"], tag, re.IGNORECASE):
                        groups = match.groups()
                        if "map_to" in pattern:
                            result = []
                            for mapped in pattern["map_to"]:
                                if mapped == "{}":
                                    result.extend(
                                        g.strip()
                                        for g in groups
                                        if g and isinstance(g, str)
                                    )
                                elif "{" in mapped and "}" in mapped:
                                    # Handle format strings like "{0}" and "{1}"
                                    try:
                                        formatted = mapped.format(*groups)
                                        result.append(formatted.strip())
                                    except (IndexError, KeyError):
                                        continue
                                else:
                                    # Preserve case for fixed strings
                                    result.append(mapped)
                            return result if result else None
                        return None  # If no map_to field, remove the tag
                except (re.error, TypeError, KeyError):
                    continue  # Skip invalid patterns
        return tag.lower()  # Return lowercase version for consistency

    def clean_tag(self, tag: str) -> str:
        """Clean a tag by removing trailing dots and applying cleanup patterns."""
        tag = tag.strip()
        for rule in self.patterns.get("split", {}).get("separators", []):
            if "replace" in rule:
                tag = re.sub(rule["pattern"], rule["replace"], tag, flags=re.IGNORECASE)
        return tag

    def apply_word_replacements(self, tag: str) -> str:
        """Apply word replacement rules to a tag."""
        tag_lower = tag.lower()
        word_replacements = self.patterns.get("word_replacements", {})
        for old, new in word_replacements.items():
            if old.lower() in tag_lower:
                tag = tag.replace(old.lower(), new)
        return tag

    def apply_mapping(self, tag: str) -> TagValue | None:
        """Apply mapping rules to a tag, returning the mapped value or None."""
        tag_lower = tag.lower()
        if tag_lower in self.mapping_lower:
            proper_key = self.mapping_lower[tag_lower]
            return self.mapping[proper_key]
        return None

    def _check_direct_mapping(self, tag: str) -> list[str] | None:
        """Check if tag has a direct mapping in the mapping dictionary."""
        tag_lower = tag.lower()
        if tag_lower in self.mapping_lower:
            proper_key = self.mapping_lower[tag_lower]
            mapped = self.mapping[proper_key]
            return [mapped] if isinstance(mapped, str) else mapped
        return None

    def _process_tag_part(self, part: str) -> set[str]:
        """Process a single tag part through the normalization pipeline."""
        normalized: set[str] = set()
        
        # First check if this tag has a direct mapping
        tag_lower = part.lower()
        if tag_lower in self.mapping_lower:
            proper_key = self.mapping_lower[tag_lower]
            mapped = self.mapping[proper_key]
            if isinstance(mapped, list):
                normalized.update(mapped)
            else:
                normalized.add(mapped)
            return normalized

        # If no direct mapping, proceed with normalization pipeline
        if self.should_remove(tag_lower):
            return normalized

        # Apply word replacements
        part = self.apply_word_replacements(part)

        # Apply compound rules
        result = self.apply_compound_rules(part)
        if result is None:
            return normalized

        # Convert result to list
        compound_parts = result if isinstance(result, list) else [result]

        # Process each compound part
        for compound_part in compound_parts:
            # Try to map the tag
            mapped = self.apply_mapping(compound_part)
            if mapped is not None:
                if isinstance(mapped, list):
                    normalized.update(mapped)
                else:
                    normalized.add(mapped)
            else:
                # Track unknown tags
                self.stats.unknown_tags.add(compound_part.lower())
                normalized.add(compound_part)

        return normalized

    def normalize(self, tag: str) -> list[str] | None:
        """
        Normalize a single tag through the following steps:
        1. Clean and transform the tag
        2. Split the tag if it matches splitting patterns
        3. Process each part through the normalization pipeline
        4. Return list of normalized tags or None if no valid tags remain

        Args:
            tag: The tag string to normalize

        Returns:
            - None if the tag should be removed
            - A list of normalized tags (empty list if no valid tags)
        """
        # Clean the tag first
        tag = self.clean_tag(tag)

        # Split the tag
        result = self.split_tag(tag)
        parts = result if isinstance(result, list) else [result]

        # Process each part
        normalized: set[str] = set()
        for part in parts:
            normalized.update(self._process_tag_part(part))

        return list(normalized) if normalized else None

    def normalize_tags(self, tags: Sequence[str | None]) -> list[str]:
        """
        Normalize a list of tags by applying normalization to each tag and removing duplicates.
        Returns a list of unique normalized tags.
        """
        return list({tag for t in tags if t is not None and (result := self.normalize(t)) is not None for tag in result})

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
