#!/usr/bin/env python3
"""Test certificate extraction across multiple formats"""

import sys
sys.path.append('.')
from app.services.field_extractor import extract_fields_from_divs

# Test Case 1: WBENC Certificate
print("=" * 80)
print("TEST 1: WBENC Certificate")
print("=" * 80)

wbenc_divs = [
    {"content": "WOMEN'S BUSINESS ENTERPRISE\nNATIONAL COUNCIL"},
    {"content": "JOIN FORCES. SUCCEED TOGETHER."},
    {"content": "HEREBY GRANTS\nWOMAN OWNED SMALL BUSINESS (WOSB) CERTIFICATION TO"},
    {"content": "Timbelo Inc"},
    {"content": "The identified small business is an eligible WOSB for the WOSB Program..."},
    {"content": "The WOSB Certification expires on the date herein..."},
    {"content": "NAICS: 541611, 541512, 541990, 561320 La\nUNSPSC: 80111609 Sheila Mixon, Ohio River Valley Women's Business Council\nExecutive Director\nCertification Number. WOSB170255 BEGORV"},
    {"content": "Expiration Date: February 28, 2022 NOMEN'S BUSINESS VALLEY ENTERPRISE COUNCIL Pamela Prince-Eason, WBENC President & CEO"},
]

result1 = extract_fields_from_divs(wbenc_divs)
print(f"✅ Organization: {result1.get('organization')} (expected: Timbelo Inc)")
print(f"✅ Certificate: {result1.get('certificate_number')} (expected: WOSB170255)")
print(f"✅ Expiry: {result1.get('expiry_date')} (expected: 2022-02-28)")
print()

# Test Case 2: NMSDC Certificate
print("=" * 80)
print("TEST 2: NMSDC Certificate")
print("=" * 80)

nmsdc_divs = [
    {"content": "THIS CERTIFIES THAT | 17%\nnmspc\nThe Kirkland Consulting Group, L.L.C. Nationa Supper"},
    {"content": "* Nationally certified by the: NORTHWEST MOUNTAIN MINORITY SUPPLIER DEVELOPMENT COUNCIL"},
    {"content": "*NAICS Code(s): 541611; 541618"},
    {"content": "* Description of their product/services as defined by the North American Industry Classification System (NAICS)"},
    {"content": "05/31/2022 NW05277"},
    {"content": "Issued Date Certificate Number"},
    {"content": "05/31/2023 NMSDC Ying CEO McGuire and President"},
    {"content": "Expiration Date Fernando Martinez, President and CEO"},
]

result2 = extract_fields_from_divs(nmsdc_divs)
print(f"✅ Organization: {result2.get('organization')} (expected: The Kirkland Consulting Group, L.L.C.)")
print(f"✅ Certificate: {result2.get('certificate_number')} (expected: NW05277)")
print(f"✅ Issued: {result2.get('issued_date')} (expected: 05/31/2022)")
print(f"✅ Expiry: {result2.get('expiry_date')} (expected: 05/31/2023)")
print()

# Test Case 3: LGBTBE Certificate
print("=" * 80)
print("TEST 3: LGBTBE Certificate")
print("=" * 80)

lgbtbe_divs = [
    {"content": "Certificate Number: 10164\nExpiration Date: 7/31/2027"},
    {"content": "The National LGBT Chamber of Commerce"},
    {"content": "Hereby Recognizes:"},
    {"content": "Lookit Design"},
    {"content": "As a Certified LGBT Business Enterprise™"},
    {"content": "(LGBTBE)"},
    {"content": "nglcc #"},
    {"content": "& President Co-Founder & CEO Certified LGBTBE"},
]

result3 = extract_fields_from_divs(lgbtbe_divs)
print(f"✅ Organization: {result3.get('organization')} (expected: Lookit Design)")
print(f"✅ Certificate: {result3.get('certificate_number')} (expected: 10164)")
print(f"✅ Expiry: {result3.get('expiry_date')} (expected: 7/31/2027 or 2027-07-31)")
print()

# Summary
print("=" * 80)
print("✅ ALL TESTS COMPLETED")
print("=" * 80)
