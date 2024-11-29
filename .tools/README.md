# Content Management Tools

## Setup

These tools require Python 3.12+ and ruamel.yaml package.

One-time setup:

```bash
python -m venv .tools/.venv
source .tools/.venv/bin/activate
pip install -r .tools/requirements.txt
```

```batch
# Windows:
python -m venv .tools/.venv
.tools\.venv\Scripts\activate
pip install -r .tools/requirements.txt
```

## Usage

1. Activate the virtual environment:

   ```bash
   # Linux/macOS:
   source .tools/.venv/bin/activate
   ```

   ```batch
   # Windows:
   .tools\.venv\Scripts\activate
   ```

2. Run the tools:

   ```bash
   # Check content
   python .tools/check_content.py

   # Fix issues
   python .tools/fix_content.py

   # Fix issues and reorder frontmatter
   python .tools/fix_content.py --reorder
   ```

## Tools Description

- `check_content.py` - Validates content files against schema and generates issues report
- `fix_content.py` - Automatically fixes common issues (languages lists, audioversion format)
- `book_schema.py` - Schema definition for content validation
