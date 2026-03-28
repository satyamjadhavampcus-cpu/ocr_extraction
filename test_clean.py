#!/usr/bin/env python3
import re

def clean_organization_name(text):
    """Clean common OCR noise from organization names"""
    if not text:
        return text

    original = text
    # For lines with extra descriptive text, try to extract just the organization name
    # Look for patterns like "Company Name Inc extra descriptive text"
    org_match = re.search(r'^([A-Za-z0-9\s,&.-]+?(?:Inc|LLC|L\.L\.C|Corporation|Company|Group|Enterprise|Consulting|Services|Design|Chamber|Commerce)\b)', text, re.I)
    if org_match:
        text = org_match.group(1).strip()

    # Remove common OCR artifacts and extra descriptive text
    text = re.sub(r'Coc\b', '', text)  # Remove "Coc" at end of word
    text = re.sub(r'\bCoc', '', text)  # Remove "Coc" at start of word
    text = re.sub(r'\bNational Minority Supplier\b', '', text)  # Remove extra text
    text = re.sub(r'\bNational Minority\b', '', text)  # Remove extra text
    text = re.sub(r'\bMinority Supplier\b', '', text)  # Remove extra text
    text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace

    if text != original:
        print(f"🧹 Cleaned organization: '{original}' -> '{text}'")

    return text

# Test cases
print("Testing clean_organization_name:")
print(repr(clean_organization_name('AMPCUS Incorporated Coc')))
print(repr(clean_organization_name('Bravens Inc National Minority Supplier')))
print(repr(clean_organization_name('Ampcus Incorporated')))