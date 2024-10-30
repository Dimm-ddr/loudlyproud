import os
import re
import sys


def find_missing_translations(language_code) -> None:
    i18n_file: str = f"i18n/{language_code}.toml"

    # Check if the specified i18n file exists
    if not os.path.exists(i18n_file):
        print(f"The i18n file for language '{language_code}' does not exist.")
        return

    # Read all translation keys from the i18n file
    with open(i18n_file, "r", encoding="utf-8") as file:
        i18n_keys = set(re.findall(r"^\[(.+?)\]", file.read(), re.MULTILINE))

    # Scan the templates for translation keys
    template_dir = "layouts/"
    missing_keys = set()

    # Regex to find {{ i18n "key" }} in templates
    key_pattern: re.Pattern[str] = re.compile(r'{{\s*i18n\s+"(.*?)"\s*}}')

    for root, _, files in os.walk(template_dir):
        for file_name in files:
            if file_name.endswith(".html"):
                file_path: str = os.path.join(root, file_name)
                with open(file_path, "r", encoding="utf-8") as f:
                    content: str = f.read()
                    template_keys = key_pattern.findall(content)
                    for key in template_keys:
                        if key not in i18n_keys:
                            missing_keys.add(key)

    # Report missing keys
    if missing_keys:
        print(f"Missing translation keys for language '{language_code}':")
        for key in missing_keys:
            print(key)
    else:
        print(f"All translation keys are present for language '{language_code}'.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python find_missing_translations.py <language_code>")
    else:
        language_code: str = sys.argv[1]
        find_missing_translations(language_code)
