import yaml
import re

class TagPatternHandler:
    def __init__(self, patterns_file='data/tags/patterns.yaml'):
        with open(patterns_file) as f:
            self.patterns = yaml.safe_load(f)

    def should_remove(self, tag):
        for prefix in self.patterns['remove']['prefixes']:
            if tag.startswith(prefix):
                return True
        return tag in self.patterns['remove']['exact']

    def process_tag(self, tag):
        if self.should_remove(tag):
            return None

        # Apply cleanup rules
        for rule in self.patterns['cleanup']:
            tag = re.sub(rule['pattern'], rule['replace'], tag)

        # Apply splitting rules
        for split_rule in self.patterns['split']['separators']:
            if split_rule['pattern'] in tag:
                parts = tag.split(split_rule['pattern'])
                return [p.strip() for p in parts]

        return tag