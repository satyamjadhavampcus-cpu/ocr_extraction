#!/usr/bin/env python3
"""
Debug script to test field extraction issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Disable LLM for faster testing
os.environ["DISABLE_LLM"] = "1"

from app.services.ocr_service import process_document
from app.services.field_extractor import extract_fields_from_divs

def test_extraction():
    # Test files
    test_files = [
        "uploads/Ampcus NMSDC Certificate-Expire 10312025.pdf",
        # "uploads/Ampcus WBENC Certificate-Expires 102825.pdf",
        # "uploads/Bravens Inc. Certificate.pdf"
    ]

    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\nTesting: {file_path}")
            print("=" * 50)

            try:
                # Process the document without LLM
                from app.services.ocr_service import process_document_no_llm
                result = process_document_no_llm(file_path)
                print(f"Status: {result.get('status')}")
                print(f"Message: {result.get('message')}")

                if 'extracted_fields' in result:
                    data = result['extracted_fields']
                    print(f"Organization: {data.get('organization')}")
                    print(f"Certificate Number: {data.get('certificate_number')}")
                    print(f"Expiry Date: {data.get('expiry_date')}")
                    print(f"Issued Date: {data.get('issued_date')}")
                    print(f"NAICS: {data.get('naics')}")

                    # Show layout divs for debugging
                    if 'layout_divs' in result:
                        print("\nLayout Divs:")
                        for i, div in enumerate(result['layout_divs'][:5]):  # First 5 divs
                            print(f"Div {i}: {div.get('content', '')[:100]}...")

            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"⚠️ File not found: {file_path}")

if __name__ == "__main__":
    test_extraction()