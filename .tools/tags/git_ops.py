#!/usr/bin/env python3

import os
from pathlib import Path


def get_changed_files(base_ref: str = None) -> list[str]:
    """Get list of changed files compared to base ref."""
    if base_ref is None:
        base_ref = os.environ.get("GITHUB_BASE_REF", "main")

    diff_command = f"git diff --name-only origin/{base_ref}...HEAD"
    return os.popen(diff_command).read().splitlines()


def get_changed_book_files(content_dir: Path, base_ref: str = None) -> list[str]:
    """Get list of changed book files."""
    changed_files = get_changed_files(base_ref)
    return [
        f for f in changed_files if f.startswith(str(content_dir)) and f.endswith(".md")
    ]
