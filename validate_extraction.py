#!/usr/bin/env python3
"""
Comprehensive Certificate OCR Extraction Validation

This script tests the complete pipeline:
1. File upload validation
2. Image/PDF processing
3. Field extraction
4. Result quality metrics
"""

import requests
import json
import os
from datetime import datetime

API_URL = "http://localhost:8000/extract"

# Test certificates with expected values
TESTS = [
    {
        "file": "uploads/WBENC-Cert.jpg",
        "name": "WBENC Certificate",
        "expected": {
            "organization": "WilMarc Medical",  # Substring match
            "certificate_number": "WOSB181227",
            "expiry_date": "2019-08-31"
        }
    },
    {
        "file": "uploads/dummy_cert.jpg",
        "name": "LGBTBE Certificate",
        "expected": {
            "organization": "Lookit Design",
            "certificate_number": "10164",
            "expiry_date": "2027-07-31"
        }
    }
]

def normalize_date_str(date_str):
    """Normalize date to YYYY-MM-DD format for comparison"""
    if not date_str:
        return None
    
    date_str = str(date_str).strip()
    
    # Already in YYYY-MM-DD format
    if len(date_str) >= 10 and date_str[4] == '-' and date_str[7] == '-':
        return date_str[:10]
    
    # MM/DD/YYYY format
    if '/' in date_str:
        parts = date_str.split('/')
        if len(parts) == 3:
            month, day, year = parts[0].strip(), parts[1].strip(), parts[2].strip()
            # Ensure proper length and format
            if len(year) == 4:
                return f"{year.strip()}-{month.strip().zfill(2)}-{day.strip().zfill(2)}"
    
    return date_str

def validate_field(actual, expected, field_name):
    """Check if field matches expected value"""
    if not actual:
        return False, "Empty"
    
    # Special handling for dates - normalize both formats
    if field_name in ("expiry_date", "issued_date"):
        actual_normalized = normalize_date_str(actual)
        expected_normalized = normalize_date_str(expected)
        return actual_normalized == expected_normalized, str(actual)
    
    if isinstance(expected, str):
        return expected.lower() in str(actual).lower(), str(actual)
    return actual == expected, str(actual)

def test_certificate(file_path, test_name, expected):
    """Test a single certificate file"""
    if not os.path.exists(file_path):
        return None, f"File not found: {file_path}"
    
    try:
        with open(file_path, "rb") as f:
            response = requests.post(API_URL, files={"file": f}, timeout=120)
        
        if response.status_code != 200:
            return None, f"HTTP {response.status_code}: {response.text[:100]}"
        
        data = response.json()
        fields = data.get("extracted_fields", {})
        
        # Validate each expected field
        results = {}
        for field, expected_val in expected.items():
            actual_val = fields.get(field)
            is_valid, display_val = validate_field(actual_val, expected_val, field)
            results[field] = {
                "valid": is_valid,
                "expected": str(expected_val),
                "actual": display_val,
                "confidence": fields.get("confidence", {}).get(field, 0.0)
            }
        
        return results, None
    
    except Exception as e:
        return None, str(e)

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def main():
    print("\n🚀 CERTIFICATE OCR EXTRACTION VALIDATION SUITE")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   API: {API_URL}")
    
    passed = 0
    failed = 0
    
    for test in TESTS:
        print_header(test["name"])
        print(f"File: {test['file']}")
        
        results, error = test_certificate(
            test["file"],
            test["name"],
            test["expected"]
        )
        
        if error:
            print(f"❌ ERROR: {error}")
            failed += 1
            continue
        
        # Display results
        all_valid = True
        for field, result in results.items():
            status = "✅" if result["valid"] else "❌"
            print(f"\n{status} {field.upper()}")
            print(f"   Expected: {result['expected']}")
            print(f"   Actual:   {result['actual']}")
            print(f"   Conf:     {result['confidence']:.2f}")
            
            if not result["valid"]:
                all_valid = False
        
        if all_valid:
            print(f"\n✅ PASSED")
            passed += 1
        else:
            print(f"\n❌ FAILED")
            failed += 1
    
    # Summary
    print_header("TEST SUMMARY")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {passed}/{len(TESTS)} ({100*passed//len(TESTS)}%)" if TESTS else "No tests")
    
    if passed == len(TESTS):
        print("\n🎉 ALL TESTS PASSED!")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())
