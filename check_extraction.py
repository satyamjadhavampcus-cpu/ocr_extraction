#!/usr/bin/env python3
"""Check WBENC extraction results in detail"""

import requests
import json

print('=' * 80)
print('TESTING WBENC CERTIFICATE - DETAILED FIELD ANALYSIS')
print('=' * 80)

with open('uploads/WBENC-Cert.jpg', 'rb') as f:
    r = requests.post('http://localhost:8000/extract', files={'file': f}, timeout=120)

if r.status_code == 200:
    data = r.json()
    extracted = data.get('extracted_fields', {})
    print(f'Organization: {extracted.get("organization")}')
    print(f'Certificate Number: {extracted.get("certificate_number")}')
    print(f'Expiry Date: {extracted.get("expiry_date")}')
    print(f'Issued Date: {extracted.get("issued_date")}')
    print(f'NAICS: {extracted.get("naics")}')
    
    print(f'\nLayout blocks for context:')
    layout = data.get('layout_divs', [])
    for i, block in enumerate(layout):
        content = block['content']
        if len(content) > 80:
            content = content[:80] + '...'
        print(f'  [{i}] {content}')
else:
    print(f'Error: {r.status_code}')
    print(r.text)
    
print('\n' + '=' * 80)
print('✅ Analysis complete')
print('=' * 80)
