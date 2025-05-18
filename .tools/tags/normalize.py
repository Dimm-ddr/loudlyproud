#!/usr/bin/env python3

import re
from pathlib import Path
from typing import TypeAlias
from collections.abc import Sequence
from .common import TagStats, MAPPING_FILE, PATTERNS_FILE, TO_REMOVE_FILE
from .file_ops import load_patterns, load_tags_map, load_removable_tags

# Type aliases
TagValue: TypeAlias = str | list[str] | None


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

    def apply_mapping(self, tag: str) -> TagValue:
        """Apply mapping rules to a tag, returning the mapped value or None."""
        tag_lower = tag.lower()
        if tag_lower in self.mapping_lower:
            proper_key = self.mapping_lower[tag_lower]
            mapped = self.mapping[proper_key]
            if mapped is not None:
                return mapped
        return None

    def process_tag_part(self, part: str) -> list[str] | None:
        """
        Process a single part of a split tag through the normalization pipeline.
        
        Steps:
        1. Convert to lowercase for consistent comparisons
        2. Check if tag should be removed based on:
           - Exact matches in removable tags
           - Prefix matches in removal patterns
        3. Apply word replacements for common variations:
           - Plural to singular forms
           - Regional spelling variations
        4. Apply compound rules to handle:
           - Special tag combinations
           - Tag transformations
           - Multi-part tag mappings
        5. Process each resulting compound part:
           - Apply mapping rules
           - Track unknown tags
           - Preserve original case for unmapped tags

        Args:
            part: A single tag part to process

        Returns:
            - None if the part should be removed
            - A list of normalized tags resulting from this part
        """
        # Convert to lowercase for comparisons
        part_lower = part.lower()

        # Check if should be removed
        if self.should_remove(part_lower):
            return None

        # Apply word replacements
        part = self.apply_word_replacements(part)

        # Apply compound rules
        result = self.apply_compound_rules(part)
        if result is None:
            return None

        # Convert result to list
        compound_parts = result if isinstance(result, list) else [result]

        # Process each compound part
        mapped_tags = []
        for compound_part in compound_parts:
            # Try to map the tag
            mapped = self.apply_mapping(compound_part)
            if mapped is not None:
                if isinstance(mapped, list):
                    mapped_tags.extend(mapped)
                else:
                    mapped_tags.append(mapped)
            else:
                # Track unknown tags
                self.stats.unknown_tags.add(compound_part.lower())
                mapped_tags.append(compound_part)

        return mapped_tags if mapped_tags else None

    def normalize(self, tag: str) -> TagValue:
        """
        Normalize a single tag through the following steps:
        0. Check if the full tag has a direct mapping
        1. Clean and transform the tag:
           - Trim whitespace
           - Remove trailing dots
           - Apply cleanup patterns
        2. Split the tag if it matches any splitting patterns:
           - Check for separators like "/", "--", etc.
           - Split into parts while preserving meaningful components
        3. Process each part:
           a. Convert to lowercase for comparisons
           b. Check if tag should be removed (based on removable tags and patterns)
           c. Apply word replacements (e.g., plurals to singular)
           d. Apply compound rules (e.g., "young adult fiction" -> ["young adult", "fiction"])
           e. Apply mapping to get canonical forms
        4. Combine results:
           - Collect all valid normalized tags
           - Return as list if multiple tags, single tag otherwise
           - Return None if no valid tags remain

        Args:
            tag: The tag string to normalize

        Returns:
            - None if the tag should be removed
            - A single string if one normalized tag results
            - A list of strings if multiple normalized tags result
        """
        # Check for direct mapping first
        tag_lower = tag.lower()
        if tag_lower in self.mapping_lower:
            proper_key = self.mapping_lower[tag_lower]
            mapped = self.mapping[proper_key]
            if mapped is not None:
                return mapped
            return None

        # Clean the tag
        tag = self.clean_tag(tag)

        # Check if the full tag should be removed
        if self.should_remove(tag_lower):
            return None

        # Split the tag
        result = self.split_tag(tag)
        parts = result if isinstance(result, list) else [result]

        # Process each part
        all_tags = []
        for part in parts:
            # Check if part should be removed before processing
            if self.should_remove(part.lower()):
                continue
                
            processed = self.process_tag_part(part)
            if processed:
                all_tags.extend(processed)

        # Return results
        if not all_tags:
            return None
        return all_tags if len(all_tags) > 1 else all_tags[0]

    def normalize_tags(self, tags: Sequence[str | None]) -> list[str]:
        """
        Normalize a list of tags:
        1. Apply normalization to each tag
        2. Flatten the results
        3. Remove duplicates (case-sensitive since mapping was already applied)
        """
        normalized: set[str] = set()

        for tag in tags:
            if tag is None:
                continue
            result = self.normalize(tag)
            if result is None:
                continue
                
            # Handle both single tags and lists of tags
            results = [result] if isinstance(result, str) else result
            normalized.update(r for r in results if r is not None)

        return list(normalized)  # Convert set to list for return

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
