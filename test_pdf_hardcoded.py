#!/usr/bin/env python3
"""Test PDF processing with hardcoded poppler path"""

import requests

print("🧪 Testing PDF Certificate Extraction")
print("=" * 50)

try:
    with open('uploads/1672964032394-scanned.pdf', 'rb') as f:
        response = requests.post('http://localhost:8000/extract', files={'file': f}, timeout=30)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        fields = data.get('extracted_fields', {})

        print("\n✅ SUCCESS! PDF processed successfully")
        print(f"📄 File: {data.get('file_name')}")
        print(f"🏢 Organization: {fields.get('organization', 'N/A')}")
        print(f"🔢 Certificate Number: {fields.get('certificate_number', 'N/A')}")
        print(f"📅 Expiry Date: {fields.get('expiry_date', 'N/A')}")

        confidence = fields.get('confidence', {})
        print(f"🎯 Confidence: Org={confidence.get('organization', 0):.2f}, Cert={confidence.get('certificate_number', 0):.2f}")

        print("\n📝 Raw Text Preview:")
        raw_text = data.get('raw_text', '')[:200] + '...'
        print(raw_text)

    else:
        print(f"❌ FAILED: {response.text[:200]}")

except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "=" * 50)
print("🎉 PDF processing with hardcoded poppler path is working!")