import re

# Test the regex pattern directly
text = 'Y4L1 7QDY'
text_no_space = text.replace(' ', '')

patterns = [
    (r'\b([A-Z]\d[A-Z]\d[A-Z0-9]+)\b', 'pattern1 (word boundary)'),
    (r'([A-Z]\d[A-Z]\d[A-Z0-9]+)', 'pattern2 (no boundary)'),
    (r'([A-Z0-9]{8,})', 'pattern3 (8+ alphanumeric)'),
]

print(f'Testing text: "{text}" -> "{text_no_space}"')
for pattern, name in patterns:
    match = re.search(pattern, text_no_space)
    print(f'{name}: {match.group(1) if match else "NO MATCH"}')
