#!/usr/bin/env python3

import json
from pathlib import Path


def sort_mapping(mapping_file: Path) -> None:
    """Sort mapping file alphabetically by keys."""
    with open(mapping_file) as f:
        mapping = json.load(f)

    sorted_mapping = dict(sorted(mapping.items()))

    with open(mapping_file, "w") as f:
        json.dump(sorted_mapping, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    mapping_file = project_root / "data" / "tags" / "mapping.json"
    sort_mapping(mapping_file)
