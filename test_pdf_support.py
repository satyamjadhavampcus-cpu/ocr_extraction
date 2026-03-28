#!/usr/bin/env python3
"""Test PDF extraction support"""

import sys
import os
sys.path.append('.')

print("🔍 Checking PDF support...")

try:
    from pdf2image import convert_from_path
    print("✅ pdf2image module available")
except ImportError:
    print("❌ pdf2image not installed")
    sys.exit(1)

try:
    from pdf2image.exceptions import PDFPageCountError
    print("✅ pdf2image exceptions available")
except ImportError:
    print("⚠️ pdf2image exceptions module not fully available")

print("\n📝 Note: pdf2image requires poppler-utils")
print("   On Windows: Install from https://github.com/oschwartz10612/poppler-windows/releases/")
print("   Or via: choco install poppler (if using Chocolatey)")
print("   Or via: apt-get install poppler-utils (if using WSL/Linux)")
print("\nTo test PDF: python test_pdf_support.py")
