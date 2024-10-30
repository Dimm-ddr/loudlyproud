# .tools/files_concat.py
import os
import git
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


# List of filenames to skip (filename only, not full paths)
skip_filenames = [
    "node_modules",
    "public",
    "package-lock.json",
    ".vscode",
]


def process_files(directory: Path) -> None:
    # Initialize git repository to parse .gitignore
    repo = git.Repo(directory, search_parent_directories=True)
    ignored_files = repo.git.ls_files(
        "--others", "--ignored", "--exclude-standard"
    ).splitlines()

    output_file = directory / ".data" / "merged_files_output.txt"
    output_file.parent.mkdir(exist_ok=True)

    # Delete the output file if it exists
    if output_file.exists():
        output_file.unlink()

    with output_file.open("w", encoding="utf-8") as output:
        for root, dirs, files in os.walk(directory):
            # Ignore the '.git' folder and other special directories
            dirs[:] = [
                d
                for d in dirs
                if d not in [".git", ".tools", ".data"] and d not in ignored_files
            ]

            for file in files:
                if file in skip_filenames:
                    continue

                file_path = Path(root) / file
                relative_path = file_path.relative_to(directory)

                # Skip ignored files and files inside special directories
                if str(relative_path) in ignored_files or any(
                    part.startswith(".") for part in relative_path.parts
                ):
                    continue

                output.write(f"{relative_path}\n")
                output.write("```\n")

                try:
                    output.write(file_path.read_text(encoding="utf-8"))
                except Exception as e:
                    output.write(f"Error reading file: {e}\n")

                output.write("```\n\n")


if __name__ == "__main__":
    project_root = get_project_root()
    process_files(project_root)
