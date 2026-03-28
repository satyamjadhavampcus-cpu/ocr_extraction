#!/usr/bin/env python3
"""Full test of certificate extraction with updated logic"""

import requests
import json
import os

API_URL = "http://localhost:8000/extract"

tests = [
    ("uploads/NGLCC®-LGBTBE®.jpg", "LGBTBE", "Lookit Design"),
    ("uploads/WBENC-Cert.jpg", "WBENC", "WilMarc Medical, LLC DBA WilMarc"),
    ("uploads/dummy_cert.jpg", "Generic", "Test/Unknown"),
]

print("=" * 80)
print("🚀 FULL CERTIFICATE EXTRACTION TEST")
print("=" * 80)

for file_path, cert_type, expected_org in tests:
    if not os.path.exists(file_path):
        print(f"\n⚠️ File not found: {file_path}")
        continue
        
    print(f"\n📋 TEST: {cert_type} Certificate")
    print(f"   Expected Org: {expected_org}")
    
    try:
        with open(file_path, "rb") as f:
            response = requests.post(API_URL, files={"file": f}, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            extracted = data.get("extracted_fields", {})
            org = extracted.get("organization", "N/A")
            cert_num = extracted.get("certificate_number", "N/A")
            expiry = extracted.get("expiry_date", "N/A")
            
            print(f"   ✅ Organization: {org}")
            print(f"   Certificate: {cert_num}")
            print(f"   Expiry: {expiry}")
        else:
            print(f"   ❌ ERROR {response.status_code}: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

print("\n" + "=" * 80)
print("✅ TEST SUITE COMPLETE")
print("=" * 80)
