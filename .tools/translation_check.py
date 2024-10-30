# .tools/translation_check.py
import re
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def find_missing_translations(language_code: str) -> None:
    project_root = get_project_root()
    i18n_file = project_root / "i18n" / f"{language_code}.toml"

    if not i18n_file.exists():
        print(f"The i18n file for language '{language_code}' does not exist.")
        return

    # Read all translation keys from the i18n file
    with i18n_file.open("r", encoding="utf-8") as file:
        i18n_keys = set(re.findall(r"^\[(.+?)\]", file.read(), re.MULTILINE))

    # Scan the templates for translation keys
    template_dir = project_root / "layouts"
    missing_keys = set()

    # Regex to find {{ i18n "key" }} in templates
    key_pattern = re.compile(r'{{\s*i18n\s+"(.*?)"\s*}}')

    for file_path in template_dir.rglob("*.html"):
        try:
            content = file_path.read_text(encoding="utf-8")
            template_keys = key_pattern.findall(content)
            for key in template_keys:
                if key not in i18n_keys:
                    missing_keys.add(key)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Report missing keys
    if missing_keys:
        print(f"Missing translation keys for language '{language_code}':")
        for key in sorted(missing_keys):
            print(key)
    else:
        print(f"All translation keys are present for language '{language_code}'.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python translation_check.py <language_code>")
    else:
        language_code = sys.argv[1]
        find_missing_translations(language_code)
