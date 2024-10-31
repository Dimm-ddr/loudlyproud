#!/usr/bin/env python3

import os
import yaml
from pathlib import Path

# Path to the books directory
BOOKS_DIR = "./content/ru/books"


def process_file(filepath):
    try:
        # Read the file
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        # Split the front matter
        parts = content.split("---\n")
        if len(parts) < 3:
            raise ValueError(
                "Invalid markdown file format - missing front matter delimiters"
            )

        # Parse the YAML front matter
        front_matter = yaml.safe_load(parts[1])
        if not front_matter:
            raise ValueError("Empty or invalid front matter")

        # Extract slug from params
        if "params" not in front_matter:
            raise ValueError("No 'params' section found in front matter")
        if "slug" not in front_matter["params"]:
            raise ValueError("No 'slug' field found in params")

        # Move slug to top level
        front_matter["slug"] = front_matter["params"]["slug"]

        # Write back to file
        with open(filepath, "w", encoding="utf-8") as file:
            file.write("---\n")
            file.write(yaml.dump(front_matter, allow_unicode=True, sort_keys=False))
            file.write("---\n")
            if len(parts) > 2:
                file.write(
                    parts[2]
                )  # Write back the content after front matter if it exists

        print(f"Successfully processed: {filepath}")

    except Exception as e:
        print(f"Error processing {filepath}: {str(e)}")


def main():
    # Convert the path to absolute path and resolve any symlinks
    books_dir = Path(BOOKS_DIR).resolve()

    if not books_dir.exists():
        print(f"Error: Directory not found: {books_dir}")
        return

    # Process all markdown files in the directory
    for filepath in books_dir.glob("**/*.md"):
        process_file(filepath)


if __name__ == "__main__":
    main()
