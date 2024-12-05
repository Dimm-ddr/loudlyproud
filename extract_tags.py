"""Script to extract unique tags from book markdown files."""
import glob
from ruamel.yaml import YAML

def extract_tags():
    # Initialize YAML parser and empty set for unique tags
    yaml = YAML(typ='safe')
    all_tags = set()

    # Look for markdown files in both en and ru directories
    book_files = glob.glob("content/*/books/*.md")

    for file_path in book_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read the content
            content = file.read()

            # Split on the frontmatter markers
            try:
                # Extract the YAML part between --- markers
                yaml_content = content.split('---')[1]
                # Parse the YAML content
                data = yaml.load(yaml_content)

                # Get tags if they exist
                if data.get('params', {}).get('tags'):
                    all_tags.update(data['params']['tags'])
            except Exception as e:
                print(f"Error processing file: {file_path}")
                print(f"Error details: {str(e)}")
                continue

    # Sort tags alphabetically and return as a list
    return sorted(list(all_tags))

if __name__ == "__main__":
    tags = extract_tags()
    print("\nUnique tags found:")
    for tag in tags:
        print(f"- {tag}")