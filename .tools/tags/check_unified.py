#!/usr/bin/env python3
import hashlib
import json
import os
from pathlib import Path


def calculate_file_hash(filepath):
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def check_unified_tags():
    """Check if unified tags file needs regeneration."""
    data_dir = Path("data/tags")
    unified_path = data_dir / "unified.json"

    if not unified_path.exists():
        print("Unified tags file does not exist!")
        return True

    with open(unified_path) as f:
        unified_data = json.load(f)

    source_hashes = unified_data["metadata"]["source_files"]

    # Check each source file
    files_to_check = {
        "mapping": data_dir / "mapping.json",
        "colors": data_dir / "colors.toml",
        "normalization": data_dir / "tag_normalization.yaml",
    }

    needs_update = False
    for key, filepath in files_to_check.items():
        current_hash = calculate_file_hash(filepath)
        if current_hash != source_hashes[key]:
            print(f"File {filepath} has changed since last generation")
            needs_update = True

    return needs_update


if __name__ == "__main__":
    needs_update = check_unified_tags()
    exit(0 if not needs_update else 1)
