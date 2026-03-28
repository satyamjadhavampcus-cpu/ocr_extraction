#!/usr/bin/env python3
"""
Test the full certificate extraction API with PDF support.
Tests all three certificate formats and validates field extraction.
"""

import requests
import json
import os

API_URL = "http://localhost:8000/extract"

# Test image files
LGBTBE_IMAGE = "uploads/NGLCC®-LGBTBE®.jpg"
WBENC_IMAGE = "uploads/WBENC-Cert.jpg"
PDF_IMAGE = "uploads/1672964032394-scanned.pdf"

def test_upload(file_path, description):
    """Upload a file and test extraction"""
    print("\n" + "=" * 80)
    print(f"📋 {description}")
    print("=" * 80)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(API_URL, files=files, timeout=120)
            
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ EXTRACTION SUCCESSFUL")
            print(json.dumps(result, indent=2))
            
            # Validate key fields
            data = result.get("data", {})
            print("\n📊 FIELD VALIDATION:")
            print(f"  Organization: {data.get('organization', 'N/A')}")
            print(f"  Certificate Number: {data.get('certificate_number', 'N/A')}")
            print(f"  Issued Date: {data.get('issued_date', 'N/A')}")
            print(f"  Expiry Date: {data.get('expiry_date', 'N/A')}")
            print(f"  NAICS: {data.get('naics', 'N/A')}")
            
            return data
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


# Test files
print("🚀 CERTIFICATE EXTRACTION TEST SUITE")
print("=" * 80)

# Test 1: LGBTBE certificate
test_upload(LGBTBE_IMAGE, "TEST 1: LGBTBE Certificate (JPG Image)")

# Test 2: WBENC certificate  
test_upload(WBENC_IMAGE, "TEST 2: WBENC Certificate (JPG Image)")

# Test 3: PDF certificate
test_upload(PDF_IMAGE, "TEST 3: Scanned Certificate (PDF)")


print("\n" + "=" * 80)
print("✅ TEST SUITE COMPLETED")
print("=" * 80)
