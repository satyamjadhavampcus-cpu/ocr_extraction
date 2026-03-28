import sys
sys.path.append('.')
from app.services.field_extractor import extract_fields_from_divs, normalize_date
import re

layout_divs = [
    {'div_id': 0, 'content': 'CERTIFICATION'},
    {'div_id': 1, 'content': 'is hereby granted to:'},
    {'div_id': 2, 'content': 'Roberts & Ryan Investments, Inc.'},
    {'div_id': 3, 'content': 'The National Veteran Business Development Council certifies\nthat the named entity has met all criteria established to be\nrecognized as a Service Disabled Veteran Owned Business (SDVOB)'},
    {'div_id': 4, 'content': 'A n>\nCEO\nKeith King,\nY4L1 7QDY\n(os December 01, 2020\nDate Earned Certificate Code'},
    {'div_id': 5, 'content': 'December 01, 2021 §23120, 523110, 523930, 522320, 523999'},
    {'div_id': 6, 'content': 'Date Expires NAICS Codes'}
]

# Test normalize_date with OCR noise
print("Testing normalize_date:")
print(f"  '(os December 01, 2020' -> {normalize_date('(os December 01, 2020')}")
print(f"  'December 01, 2021' -> {normalize_date('December 01, 2021')}")

# Test certificate regex
print("\nTesting certificate extraction:")
for div in layout_divs:
    text = div['content']
    text_no_spaces = text.replace(' ', '')
    cert_mixed = re.search(r'\b([A-Z]\d[A-Z]\d[A-Z0-9]+)\b', text_no_spaces)
    if cert_mixed:
        print(f"  Found in div {div['div_id']}: {cert_mixed.group(1)}")

# Extract
print("\nFull extraction:")
try:
    raw_text = '''CERTIFICATION
is hereby granted to:
Roberts & Ryan Investments, Inc.
The National Veteran Business Development Council certifies
that the named entity has met all criteria established to be
recognized as a Service Disabled Veteran Owned Business (SDVOB)
A n>
CEO
Keith King,
Y4L1 7QDY
(os December 01, 2020
Date Earned Certificate Code
December 01, 2021 §23120, 523110, 523930, 522320, 523999
Date Expires NAICS Codes'''
    result = extract_fields_from_divs(layout_divs, raw_text)
    print(f"  Certificate Number: {result['certificate_number']}")
    print(f"  Issued Date: {result['issued_date']}")
    print(f"  Expiry Date: {result['expiry_date']}")
    print(f"  Organization: {result['organization']}")
    print(f"  NAICS: {result['naics']}")
except Exception as e:
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()
