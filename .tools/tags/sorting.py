import json

# Load the file
with open("data/tags/mapping.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Sort alphabetically
sorted_data = dict(sorted(data.items(), key=lambda x: x[0].lower()))

# Save back with proper formatting
with open("data/tags/mapping.json", "w", encoding="utf-8") as f:
    json.dump(sorted_data, f, indent=4, ensure_ascii=False)
