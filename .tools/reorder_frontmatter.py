import os
from pathlib import Path


def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by '---' to separate frontmatter
    parts = content.split("---", 2)
    if len(parts) < 3:
        return  # Skip files without proper frontmatter

    # Get the middle part (frontmatter content)
    frontmatter = parts[1].strip()

    # Process lines
    lines = frontmatter.split("\n")
    unindented_lines = []
    indented_lines = []
    indented_slug = None
    params_line = None

    # Process each line
    for line in lines:
        if line == "params:":
            params_line = line
        elif line.startswith("  slug:"):
            indented_slug = line.lstrip()  # Remove leading spaces
        elif line.startswith("  "):
            indented_lines.append(line)  # Keep other indented lines
        else:
            unindented_lines.append(line)

    # Add the unindented slug if we found an indented one
    if indented_slug and indented_slug not in unindented_lines:
        unindented_lines.append(indented_slug)

    # Sort unindented lines
    unindented_lines.sort()

    # Reconstruct the file
    new_content = "---\n"
    new_content += "\n".join(unindented_lines)
    if params_line:
        new_content += "\n" + params_line
    if indented_lines:
        new_content += "\n" + "\n".join(indented_lines)
    new_content += "\n---"

    # Add the rest of the content if it exists
    if parts[2].strip():
        new_content += "\n" + parts[2].strip()

    # Write back to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)


def main():
    # Get the project root (assuming script is in .tools folder)
    project_root = Path(__file__).parent.parent
    content_dir = project_root / "content"

    # Walk through all subdirectories in content
    for root, _, files in os.walk(content_dir):
        for file in files:
            if file.endswith(".md"):
                filepath = Path(root) / file
                process_file(filepath)


if __name__ == "__main__":
    main()
