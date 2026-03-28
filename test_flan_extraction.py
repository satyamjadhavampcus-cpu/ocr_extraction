#!/usr/bin/env python3
"""Test Flan-T5 extraction with the NMSDC certificate"""

import sys
sys.path.append('.')
from app.services.field_extractor import extract_fields_from_divs

# Mock divs from the NMSDC certificate
divs = [
    {"content": "THIS CERTIFIES THAT | 17%\nnmspc\nThe Kirkland Consulting Group, L.L.C. Nationa Supper"},
    {"content": "* Nationally certified by the: NORTHWEST MOUNTAIN MINORITY SUPPLIER DEVELOPMENT COUNCIL"},
    {"content": "*NAICS Code(s): 541611; 541618"},
    {"content": "* Description of their product/services as defined by the North American Industry Classification System (NAICS)"},
    {"content": "05/31/2022 NW05277"},
    {"content": "Issued Date Certificate Number"},
    {"content": "05/31/2023 NMSDC Ying CEO McGuire and President"},
    {"content": "Expiration Date Fernando Martinez, President and CEO"},
    {"content": "By using your password (NMSDC issued only), authorized users may log into NMSDC Central to view the entire profile: htipy/nmsdc.org"},
    {"content": "Certify, Develop, Connect, Advocate.\n* MBEs certified by an Affiliate of the National Minority Supplier Development Council, Inc.®"},
    {"content": ">"}
]

print("=" * 70)
print("Testing NMSDC Certificate Extraction with Flan-T5")
print("=" * 70)

result = extract_fields_from_divs(divs)

print("\n📋 Extracted Fields:")
print("-" * 70)
print(f"Organization: {result.get('organization')}")
print(f"  Confidence: {result['confidence'].get('organization', 0)}")
print()
print(f"Certificate Number: {result.get('certificate_number')}")
print(f"  Confidence: {result['confidence'].get('certificate_number', 0)}")
print()
print(f"Issued Date: {result.get('issued_date')}")
print(f"  Confidence: {result['confidence'].get('issued_date', 0)}")
print()
print(f"Expiry Date: {result.get('expiry_date')}")
print(f"  Confidence: {result['confidence'].get('expiry_date', 0)}")
print()
print(f"NAICS Codes: {result.get('naics')}")
print(f"  Confidence: {result['confidence'].get('naics', 0)}")
print()

print("=" * 70)
print("✅ EXPECTED:")
print("  Organization: The Kirkland Consulting Group, L.L.C.")
print("  Certificate Number: NW05277")
print("  Issued Date: 05/31/2022")
print("  Expiry Date: 05/31/2023")
print("  NAICS: ['541611', '541618']")
print("=" * 70)
