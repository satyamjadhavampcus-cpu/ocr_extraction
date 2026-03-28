# import re
# from datetime import datetime
# from app.services.fuzzy_matcher import match_label
# from app.services.llm_fallback import llm_extract


def normalize_date(text):
    if not text:
        return None

    m = re.search(r'\b(\d{1,2}/\d{1,2}/\d{4})\b', text)
    if m:
        return m.group(1)

    m = re.search(r'\b([A-Za-z]+ \d{1,2}, \d{4})\b', text)
    if m:
        try:
            dt = datetime.strptime(m.group(1), '%B %d, %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

    m = re.search(r'\b(\d{1,2}[\-/]\d{1,2}[\-/]\d{4})\b', text)
    if m:
        return m.group(1)

    return None


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


def extract_column_pairs(divs):

    issued = None
    expiry = None
    cert = None

    for i in range(len(divs) - 1):
    
        upper = divs[i]["content"]
        lower = divs[i + 1]["content"]

        lower_label = match_label(lower)

        if lower_label == "issued_date" or "issued" in lower.lower():
            parsed = normalize_date(upper)
            if parsed:
                issued = parsed

        if lower_label == "certificate_number" or "certificate" in lower.lower():
            cert_alpha = re.search(r'\b([A-Z]{1,6}\d{4,8})\b', upper)
            if cert_alpha:
                cert = cert_alpha.group(1)
            else:
                cert_match = re.search(r'\b(\d{5,8})\b', upper)
                if cert_match:
                    cert_num = cert_match.group(1)
                    if not (2000 <= int(cert_num) <= 2100):
                        cert = cert_num

        if lower_label == "expiry_date" or "expiration" in lower.lower() or "expiry" in lower.lower():
            parsed = normalize_date(upper)
            if parsed:
                expiry = parsed
        
    

    return issued, expiry, cert



def extract_fields_from_divs(divs, raw_text=None, clean_text=None):

    result = {
        "organization": None,
        "certificate_number": None,
        "expiry_date": None,
        "issued_date": None,
        "naics": [],
        "confidence": {
            "organization": 0.0,
            "certificate_number": 0.0,
            "expiry_date": 0.0,
            "issued_date": 0.0,
            "naics": 0.0
        }
    }

    all_naics_codes = []
    all_unspsc_codes = []

    for div in divs:

        text = div["content"]
        label = match_label(text)

        # ---------- NAICS ----------
        if label == "naics" or "naics" in text.lower():
            # First try to find codes in a structured NAICS line
            naics_match = re.search(r'naics code\(s\):\s*(.+)', text, re.I)
            if naics_match:
                codes_part = naics_match.group(1)
                codes = re.findall(r'\d{6}', codes_part)
            else:
                # Fallback to finding all 6-digit codes in the text
                codes = re.findall(r'\b\d{6}\b', text)
            if codes:
                valid_codes = [c for c in codes if c[:2] in {
                    '11','21','22','23','31','32','33','42','44','45','48','49','51','52','53','54','55','56','61','62','71','72','81','92'
                }]
                all_naics_codes.extend(valid_codes)

        # ---------- UNSPSC ----------
        if label == "unspsc" or "unspsc" in text.lower():
            codes = re.findall(r'\b\d{8}\b', text)
            if codes:
                # UNSPSC codes are 8 digits, no specific validation like NAICS
                all_unspsc_codes.extend(codes)

        # ---------- certificate ----------
        # Support various certificate number formats including "Certificate No", "Certificate Number", "Certificate Code" and "MWBE" patterns
        cert_match = re.search(r'(?:Certificate\s*(?:No(?:\.)?|Number|Code|ID)|Certif(?:icate|ication)\s*(?:Code|Number))\s*[:;]?\s*([A-Z0-9\-\$]{5,})', text, re.I)
        if not cert_match:
            # fallback for specific keyword styles
            cert_match = re.search(r'\bMWBE\d{10,}\b', text, re.I)
        if not cert_match:
            cert_match = re.search(r'\bDISABIN\d{3,}\b', text, re.I)
        if cert_match:
            cert_num = cert_match.group(1).strip() if cert_match.lastindex else cert_match.group(0).strip()
            cert_num = cert_num.replace(' ', '')
            cert_clean = re.match(r'^([A-Z0-9\-\$]+?)(?:\s|$)', cert_num)
            if cert_clean:
                cert_num = cert_clean.group(1)
            if not (cert_num.isdigit() and 2000 <= int(cert_num) <= 2100):
                result["certificate_number"] = cert_num
                result["confidence"]["certificate_number"] = 0.95

        # If no certificate_number yet, look for Sxxxx style without explicit label
        if not result.get("certificate_number"):
            generic_cert = re.search(r'\b([A-Z]{0,3}\d{5,12})\b', text)
            if generic_cert:
                candidate = generic_cert.group(1).strip()
                if not (candidate.isdigit() and 2000 <= int(candidate) <= 2100):
                    result["certificate_number"] = candidate
                    result["confidence"]["certificate_number"] = 0.80

        # ---------- expiry ----------
        expiry_match = re.search(
            r'(?:Expiration|Expiry|Expire|Date Expires|Date of Expiry|Expiration Date)\s*[:\s]*([A-Za-z0-9/,\s]+)',
            text,
            re.I
        )

        if not expiry_match:
            # Disability-IN specific: look for dates near "expires" or "expiration"
            expiry_match = re.search(r'(?:expires|expiration)\s*[:\-]?\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})', text, re.I)

        if not expiry_match:
            expiry_match = re.search(r'\b(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\b', text)

        if expiry_match:
            parsed = normalize_date(expiry_match.group(1))
            if parsed:
                result["expiry_date"] = parsed
                result["confidence"]["expiry_date"] = 0.95

        # ---------- issued ----------
        issued_match = re.search(
            r'(?:Issued|Issue|Certification Granted|Date Earned|Date of Issue|Date issued)\s*[:\s]*([A-Za-z0-9/,\s(]+)',
            text,
            re.I
        )

        if not issued_match:
            # Disability-IN specific: look for dates near "issued" or "certification"
            issued_match = re.search(r'(?:issued|certification)\s*[:\-]?\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})', text, re.I)

        if not issued_match:
            issued_match = re.search(r'\b(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\b', text)

        if issued_match:
            parsed = normalize_date(issued_match.group(1))
            if parsed:
                result["issued_date"] = parsed
                result["confidence"]["issued_date"] = 0.95

    # Fallback: search for explicit date language outside label matches
    if not result.get("issued_date"):
        for div in divs:
            text = div["content"]
            m = re.search(r'(?i)(?:commenced on|date issued|date of issue)\s*[:\-]?\s*([A-Za-z0-9/\- ,]+)', text)
            if m:
                parsed = normalize_date(m.group(1))
                if parsed:
                    result["issued_date"] = parsed
                    result["confidence"]["issued_date"] = 0.85
                    break

    if not result.get("expiry_date"):
        for div in divs:
            text = div["content"]
            m = re.search(r'(?i)(?:date of expiry|expiry date|date expires|expiration date)\s*[:\-]?\s*([A-Za-z0-9/\- ,]+)', text)
            if m:
                parsed = normalize_date(m.group(1))
                if parsed:
                    result["expiry_date"] = parsed
                    result["confidence"]["expiry_date"] = 0.85
                    break

    # Set accumulated codes
    if all_naics_codes:
        result["naics"] = list(dict.fromkeys(all_naics_codes))
        result["confidence"]["naics"] = 0.90

    if all_unspsc_codes:
        result["unspsc"] = list(dict.fromkeys(all_unspsc_codes))
        result["confidence"]["unspsc"] = 0.90

    # Additional extraction from raw_text if provided
    if raw_text:
        # Find all valid NAICS codes in the entire raw_text
        codes = re.findall(r'\b\d{6}\b', raw_text)
        valid_codes = [c for c in codes if c[:2] in {
            '11','21','22','23','31','32','33','42','44','45','48','49','51','52','53','54','55','56','61','62','71','72','81','92'
        }]
        all_naics_codes.extend(valid_codes)
        result["naics"] = list(dict.fromkeys(all_naics_codes))
        if all_naics_codes:
            result["confidence"]["naics"] = 0.90

        # Disability-IN specific: Look for certificate number in raw text
        if not result.get("certificate_number"):
            disab_match = re.search(r'\bDISABIN\d{3,}\b', raw_text, re.I)
            if disab_match:
                result["certificate_number"] = disab_match.group(0)
                result["confidence"]["certificate_number"] = 0.95

        # Disability-IN specific: Look for dates in "Month DD, YYYY" format in raw text
        if not result.get("issued_date"):
            issued_dates = re.findall(r'\b([A-Za-z]+ \d{1,2}, \d{4})\b', raw_text)
            for date_str in issued_dates:
                parsed = normalize_date(date_str)
                if parsed:
                    result["issued_date"] = parsed
                    result["confidence"]["issued_date"] = 0.85
                    break

        if not result.get("expiry_date"):
            expiry_dates = re.findall(r'\b([A-Za-z]+ \d{1,2}, \d{4})\b', raw_text)
            # Take the later date as expiry if we have multiple
            for date_str in expiry_dates:
                parsed = normalize_date(date_str)
                if parsed:
                    if not result.get("expiry_date") or parsed > result["expiry_date"]:
                        result["expiry_date"] = parsed
                        result["confidence"]["expiry_date"] = 0.85

    # ---------- column pairing ----------
    issued, expiry, cert = extract_column_pairs(divs)

    if issued:
        result["issued_date"] = issued
        result["confidence"]["issued_date"] = 0.85

    if expiry:
        result["expiry_date"] = expiry
        result["confidence"]["expiry_date"] = 0.85

    if cert:
        bad_words = {'the', 'and', 'for', 'this', 'that', 'laura', 'president', 'ceo', 'certify',
                     'certified', 'fernando', 'mcguire', 'sheila', 'ying', 'pamela', 'nmsdc', 'ayé'}

        is_bad = (cert.lower() in bad_words or
                  len(cert) < 2 or
                  (cert.isdigit() and 2000 <= int(cert) <= 2100))

        if not is_bad:
            if not result.get("certificate_number") or result["confidence"]["certificate_number"] < 0.9:
                result["certificate_number"] = cert
                result["confidence"]["certificate_number"] = 0.85

    # ---------- Flexible extraction for split/mixed dates and codes ----------
    # For certificates like NVBDC where data is mixed in divs
    if not result.get("certificate_number"):
        # Look for mixed alphanumeric certificates (e.g., Y4L17QDY, Y4L1 7QDY)
        for div in divs:
            text = div["content"]
            # Remove spaces to match patterns like "Y4L1 7QDY"
            text_no_spaces = text.replace(' ', '')
            cert_mixed = re.search(r'\b([A-Z]\d[A-Z]\d[A-Z0-9]+)\b', text_no_spaces)
            if cert_mixed:
                result["certificate_number"] = cert_mixed.group(1)
                result["confidence"]["certificate_number"] = 0.85
                break
    
    if not result.get("issued_date"):
        # Look for dates with OCR noise pattern like "(os December 01, 2020"
        for div in divs:
            text = div["content"]
            date_patterns = [
                r'\(os\s+([A-Za-z\s0-9,]+)',      # OCR artifact pattern
                r'Date Earned[:\s]*([A-Za-z0-9/,\s]+)',  # Explicit label
                r'earned[:\s]*([A-Za-z0-9/,\s]+)'  # Just label
            ]
            for pattern in date_patterns:
                date_match = re.search(pattern, text, re.I)
                if date_match:
                    parsed = normalize_date(date_match.group(1))
                    if parsed:
                        result["issued_date"] = parsed
                        result["confidence"]["issued_date"] = 0.85
                        break
            if result["issued_date"]:
                break

    if not result.get("expiry_date"):
        # Look for expiry dates (may be mixed with NAICS codes)
        for div in divs:
            text = div["content"]
            # Look for dates that appear before NAICS/other codes
            date_patterns = [
                r'([\w]{0,10})\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4})\s+[§\d]',  # Date before code/symbol
                r'Date Expires[:\s]*([A-Za-z0-9/,\s]+)',  # Explicit label
                r'(?:^|\s)(\d{1,2})[/\s]?([A-Za-z]+)[/\s]?(\d{4})(?:\s|$)',  # Flexible date format
            ]
            for pattern in date_patterns:
                date_match = re.search(pattern, text, re.I)
                if date_match:
                    # Extract the date part
                    if 'Date Expires' in text or 'Expires' in text:
                        date_text = date_match.group(1) if date_match.lastindex >= 1 else text
                    else:
                        # For flexible patterns, try to identify which group is the date
                        date_text = date_match.group(0)
                    parsed = normalize_date(date_text)
                    if parsed:
                        result["expiry_date"] = parsed
                        result["confidence"]["expiry_date"] = 0.85
                        break
            if result["expiry_date"]:
                break

    # Collect all text from divs for LLM
    all_text = "\n".join([div.get("content", "") for div in divs])

    org_keywords = [
        "llc", "l.l.c", "inc", "ltd", "group", "corporation", "company",
        "consulting", "services", "design", "enterprise", "chamber", "commerce"
    ]

    # First try: positional extraction for "THIS CERTIFIES THAT" pattern
    for i, div in enumerate(divs):
        if "this certifies that" in div["content"].lower():
            lines = [line.strip() for line in div["content"].split("\n") if line.strip()]
            for j, line in enumerate(lines):
                if any(kw in line.lower() for kw in org_keywords):
                    cleaned_org = clean_organization_name(line)
                    # Ensure we don't use descriptive lines like "This certifies that..."
                    if cleaned_org and cleaned_org.lower() != "this certifies that":
                        result["organization"] = cleaned_org
                        result["confidence"]["organization"] = 0.92
                        break
            if result["organization"]:
                break

    # Second try: positional extraction after standard recognition phrases
    if not result["organization"]:
        recognition_phrases = ["hereby recognizes", "certifies that", "hereby grants", "hereby certifies", "certified to", "to", "this is to certify that", "presented to", "hereby awards"]
        candidates = []
        
        for i, div in enumerate(divs):
            text = div["content"].lower()
            if any(phrase in text for phrase in recognition_phrases):
                # Look ahead to find organization name candidates
                for offset in range(1, 4):  # Look at next 3 divs
                    if i+offset < len(divs):
                        candidate_div = divs[i+offset]["content"]
                        lines = [line.strip() for line in candidate_div.split("\n") if line.strip()]
                        
                        for line in lines:
                            # Skip if it looks like a label (ends with "TO", "FOR")
                            is_label = line.rstrip().endswith(("TO", "FOR", ":"))
                            skip_words = ["hereby", "certified", "™", "(lgbtbe)", "nglcc", "&", "president", "ceo", "council", "national", "owned small", "business"]
                            has_company_keyword = any(k in line.lower() for k in ["inc", "incorporated", "llc", "l.l.c", "corporation", "company", "group", "ltd", "limited"])
                            has_weak_keyword = any(k in line.lower() for k in ["enterprise", "consulting", "services", "design", "chamber", "commerce"])

                            if (3 <= len(line) <= 100 and
                                not is_label and
                                any(kw in line.lower() for kw in org_keywords) and
                                not any(skip in line.lower() for skip in skip_words)):
                                
                                # Score the candidate: strong keywords get higher score
                                score = 0
                                if has_company_keyword:
                                    score += 10
                                if has_weak_keyword:
                                    score += 1
                                # Prefer shorter, cleaner names
                                if len(line.split()) <= 5:
                                    score += 2
                                
                                candidates.append((line, score, has_company_keyword))
                                # print(f"DEBUG: Found org candidate: '{line}' (score={score}, strong={has_company_keyword})")
        
        # Select the best candidate
        if candidates:
            # Sort by score (highest first), then by whether it has strong keywords
            candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)
            best_candidate = candidates[0][0]
            result["organization"] = best_candidate
            result["confidence"]["organization"] = 0.92
            # print(f"✅ Selected organization (second try): '{best_candidate}' from {len(candidates)} candidates")

    # Third try: look for lines with organization keywords (skip headers)
    if not result["organization"]:
        for div in divs[1:6]:
            text = div["content"]
            lines = [line.strip() for line in text.split("\n") if line.strip()]

            for line in lines:
                if any(kw in line.lower() for kw in org_keywords):
                    header_words = ["council", "enterprise", "business", "chamber", "commerce", "description"]
                    has_company_keyword = any(k in line.lower() for k in ["inc", "llc", "l.l.c", "corporation", "company", "group", "enterprise"])
                    if (has_company_keyword or not any(header_word in line.lower() for header_word in header_words)):
                        cleaned_org = clean_organization_name(line)
                        result["organization"] = cleaned_org
                        result["confidence"]["organization"] = 0.85
                        break
            if result["organization"]:
                break

    # Disability-IN style fallback: "has been met by" next line is org name
    if (not result["organization"] or
        result["organization"].strip().lower() in ["enterprise", "service disabled veteran disability-owned business", "disability:in", "disability owned business"]):
        for i, div in enumerate(divs):
            lower = div["content"].lower()
            if "has been met by" in lower or "certification has been met by" in lower or "is hereby granted to" in lower:
                if i + 1 < len(divs):
                    candidate_line = divs[i + 1]["content"].strip()
                    if candidate_line:
                        cleaned_candidate = clean_organization_name(candidate_line)
                        if (cleaned_candidate and cleaned_candidate.strip().lower() not in
                            ["enterprise", "business", "disability:in", "service disabled veteran disability-owned business"]):
                            result["organization"] = cleaned_candidate
                            result["confidence"]["organization"] = 0.90
                            break

    # Additional generic phrases for organization extraction
    if not result["organization"]:
        for i, div in enumerate(divs):
            lower = div["content"].lower()
            if any(phrase in lower for phrase in ["presented to", "this is to certify that", "hereby awards"]):
                if i + 1 < len(divs):
                    candidate = divs[i+1]["content"].strip()
                    if candidate and len(candidate) > 3:
                        cleaned = clean_organization_name(candidate)
                        if cleaned and not any(discard in cleaned.lower() for discard in ["supply nation", "msduk", "council", "certificate"]):
                            result["organization"] = cleaned
                            result["confidence"]["organization"] = 0.95
                            break

    # Certificate number from ABN/ABN-like declarations
    if not result.get("certificate_number"):
        for div in divs:
            abn_match = re.search(r'\b(?:australian business number|abn)\s*[:\s]*([0-9]{8,15})\b', div["content"], re.I)
            if abn_match:
                result["certificate_number"] = abn_match.group(1)
                result["confidence"]["certificate_number"] = 0.95
                break

    # Date labels (issued & expiry) from surrounding text
    for div in divs:
        text = div["content"]

        if not result.get("issued_date"):
            issue_match = re.search(r'(?i)(?:date issued|issued date|date of issue|issued on|certification commenced on|date issued)\s*[:\-]?\s*([0-9]{1,2}[\-/][0-9]{1,2}[\-/][0-9]{2,4}|[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4})', text)
            if issue_match:
                parsed = normalize_date(issue_match.group(1))
                if parsed:
                    result["issued_date"] = parsed
                    result["confidence"]["issued_date"] = 0.95

        if not result.get("expiry_date"):
            expiry_match = re.search(r'(?i)(?:expiration date|expiry date|date expires|valid until)\s*[:\-]?\s*([0-9]{1,2}[\-/][0-9]{1,2}[\-/][0-9]{2,4}|[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4})', text)
            if expiry_match:
                parsed = normalize_date(expiry_match.group(1))
                if parsed:
                    result["expiry_date"] = parsed
                    result["confidence"]["expiry_date"] = 0.95

    # Column pairing fallback only when no high-confidence values found
    issued, expiry, cert = extract_column_pairs(divs)
    if issued and (not result.get("issued_date") or result["confidence"]["issued_date"] < 0.9):
        result["issued_date"] = issued
        result["confidence"]["issued_date"] = 0.85
    if expiry and (not result.get("expiry_date") or result["confidence"]["expiry_date"] < 0.9):
        result["expiry_date"] = expiry
        result["confidence"]["expiry_date"] = 0.85
    if cert and (not result.get("certificate_number") or result["confidence"]["certificate_number"] < 0.9):
        if not (cert.isdigit() and 2000 <= int(cert) <= 2100):
            result["certificate_number"] = cert
            result["confidence"]["certificate_number"] = 0.85

    # ---------- LLM Verification/Correction ----------
    org_is_bad = (
        not result["organization"] or
        len(result["organization"]) < 3 or
        any(bad in (result["organization"] or "").lower() for bad in
            ["naics", "description", "*", "product", "services", "system",
             "classification", "certification", "certify", "hereby"])
    )

    bad_cert_words = {'laura', 'president', 'ceo', 'certify', 'certified', 'fernando',
                      'mcguire', 'sheila', 'ying', 'pamela', 'nmsdc', 'ayé', 'the', 'and', 'that'}
    cert_is_bad = (
        not result["certificate_number"] or
        len(result["certificate_number"]) < 2 or
        result["certificate_number"].lower() in bad_cert_words or
        (result["certificate_number"].isdigit() and 2000 <= int(result["certificate_number"]) <= 2100) or
        "\n" in (result["certificate_number"] or "") or
        "\r" in (result["certificate_number"] or "")
    )

    # ---------- LLM as Fallback for Missing Fields ----------
    # Only use LLM when rule-based extraction has missing or low-confidence results
    needs_llm = (
        not result.get("certificate_number") or
        not result.get("issued_date") or
        not result.get("expiry_date") or
        result["confidence"]["certificate_number"] < 0.8 or
        result["confidence"]["issued_date"] < 0.8 or
        result["confidence"]["expiry_date"] < 0.8
    )
    
    if needs_llm:
        try:
            llm_result = llm_extract(raw_text, clean_text, divs)
            print(f"🔍 LLM fallback result: {llm_result}")

            # Only use LLM results for fields that are missing or low confidence
            # But validate that LLM results are actually present in the source text
            if llm_result and isinstance(llm_result, dict):
                def validate_llm_field(field_name, field_value):
                    """Check if LLM field value appears in the source text"""
                    if not field_value or not isinstance(field_value, str):
                        return False
                    # Check if the field value appears in raw_text or clean_text
                    return field_value.lower() in raw_text.lower() or field_value.lower() in clean_text.lower()
                
                if (not result.get("organization") or result["confidence"]["organization"] < 0.9) and llm_result.get("organization"):
                    if validate_llm_field("organization", llm_result["organization"]):
                        result["organization"] = llm_result["organization"]
                        result["confidence"]["organization"] = 0.95

                if (not result.get("certificate_number") or result["confidence"]["certificate_number"] < 0.9) and llm_result.get("certificate_number"):
                    if validate_llm_field("certificate_number", llm_result["certificate_number"]):
                        result["certificate_number"] = llm_result["certificate_number"]
                        result["confidence"]["certificate_number"] = 0.95

                if (not result.get("issued_date") or result["confidence"]["issued_date"] < 0.9) and llm_result.get("issued_date"):
                    if validate_llm_field("issued_date", llm_result["issued_date"]):
                        result["issued_date"] = llm_result["issued_date"]
                        result["confidence"]["issued_date"] = 0.95

                if (not result.get("expiry_date") or result["confidence"]["expiry_date"] < 0.9) and llm_result.get("expiry_date"):
                    if validate_llm_field("expiry_date", llm_result["expiry_date"]):
                        result["expiry_date"] = llm_result["expiry_date"]
                        result["confidence"]["expiry_date"] = 0.95

                if llm_result.get("naics"):
                    result["naics"] = llm_result["naics"]
                    result["confidence"]["naics"] = 0.95

                if llm_result.get("unspsc"):
                    result["unspsc"] = llm_result["unspsc"]
                    result["confidence"]["unspsc"] = 0.95

        except Exception as e:
            print(f"⚠️ LLM extraction failed, using rule-based results: {e}")

    # Final cleaning of organization name
    if result.get("organization"):
        # print(f"DEBUG: organization before final clean: '{result['organization']}'")
        original = result["organization"]
        result["organization"] = clean_organization_name(result["organization"])
        if result["organization"] != original:
            # print(f"FINAL CLEAN: {original} -> {result['organization']}")
            pass

    return result



import re
from datetime import datetime
from app.services.fuzzy_matcher import match_label
from app.services.llm_fallback import llm_extract


def normalize_date(text):
    if not text:
        return None

    m = re.search(r'\b(\d{1,2}/\d{1,2}/\d{4})\b', text)
    if m:
        return m.group(1)

    m = re.search(r'\b([A-Za-z]+ \d{1,2}, \d{4})\b', text)
    if m:
        try:
            dt = datetime.strptime(m.group(1), '%B %d, %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

    m = re.search(r'\b(\d{1,2}[\-/]\d{1,2}[\-/]\d{4})\b', text)
    if m:
        return m.group(1)

    return None


def extract_column_pairs(divs):
    issued = None
    expiry = None
    cert = None

    for i in range(len(divs) - 1):
        upper = divs[i]["content"]
        lower = divs[i + 1]["content"]
        lower_label = match_label(lower)

        if lower_label == "issued_date" or "issued" in lower.lower():
            parsed = normalize_date(upper)
            if parsed:
                issued = parsed

        if lower_label == "certificate_number" or "certificate" in lower.lower():
            cert_alpha = re.search(r'\b([A-Z]{1,6}\d{4,8})\b', upper)
            if cert_alpha:
                cert = cert_alpha.group(1)
            else:
                cert_match = re.search(r'\b(\d{5,8})\b', upper)
                if cert_match:
                    cert_num = cert_match.group(1)
                    if not (2000 <= int(cert_num) <= 2100):
                        cert = cert_num

        if lower_label == "expiry_date" or "expiration" in lower.lower() or "expiry" in lower.lower():
            parsed = normalize_date(upper)
            if parsed:
                expiry = parsed
        
    

    return issued, expiry, cert


# def extract_fields_from_divs(divs):
    result = {
        "organization": None,
        "certificate_number": None,
        "expiry_date": None,
        "issued_date": None,
        "naics": [],
        "confidence": {
            "organization": 0.0,
            "certificate_number": 0.0,
            "expiry_date": 0.0,
            "issued_date": 0.0,
            "naics": 0.0
        }
    }

    # First pass: regex and label matching
    for div in divs:
        text = div["content"]
        label = match_label(text)

        # NAICS
        if label == "naics" or "naics" in text.lower():
            codes = re.findall(r'\b\d{6}\b', text)
            valid_codes = [c for c in codes if c[:2] in {
                '11','21','22','23','31','32','33','42','44','45','48','49','51','52','53','54','55','56','61','62','71','72','81','92'
            }]
            if valid_codes:
                result["naics"] = list(dict.fromkeys(valid_codes))
                result["confidence"]["naics"] = 0.90

        # Certificate
        cert_match = re.search(r'Certif(?:icate|ication)\s*Number[\.\s:]*([A-Z0-9]+)', text, re.I)
        if cert_match:
            cert_num = cert_match.group(1).strip()
            cert_clean = re.match(r'^([A-Z0-9]+?)(?:\s|$)', cert_num)
            if cert_clean:
                cert_num = cert_clean.group(1)
            if not (cert_num.isdigit() and 2000 <= int(cert_num) <= 2100):
                result["certificate_number"] = cert_num
                result["confidence"]["certificate_number"] = 0.95

        # Expiry
        expiry_match = re.search(r'(Expiration|Expiry|Expire)\s*Date[:\s]*([A-Za-z0-9/,\s]+)', text, re.I)
        if expiry_match:
#             parsed = normalize_date(expiry_match.group(2))
            if parsed:
                result["expiry_date"] = parsed
                result["confidence"]["expiry_date"] = 0.95

        # Issued
        issued_match = re.search(r'(Issued|Issue)\s*Date[:\s]*([A-Za-z0-9/,\s]+)', text, re.I)
        if issued_match:
#             parsed = normalize_date(issued_match.group(2))
            if parsed:
                result["issued_date"] = parsed
                result["confidence"]["issued_date"] = 0.95

    # Column pairing
    issued, expiry, cert = extract_column_pairs(divs)
    if issued:
        result["issued_date"] = issued
        result["confidence"]["issued_date"] = 0.85
    if expiry:
        result["expiry_date"] = expiry
        result["confidence"]["expiry_date"] = 0.85
    if cert:
        bad_words = {'the', 'and', 'for', 'this', 'that', 'laura', 'president', 'ceo', 'certify', 
                     'certified', 'fernando', 'mcguire', 'sheila', 'ying', 'pamela', 'nmsdc', 'ayé'}
        is_bad = (cert.lower() in bad_words or len(cert) < 2 or (cert.isdigit() and 2000 <= int(cert) <= 2100))
        if not is_bad:
            if not result.get("certificate_number") or result["confidence"]["certificate_number"] < 0.9:
                result["certificate_number"] = cert
                result["confidence"]["certificate_number"] = 0.85

    # Collect text for LLM
    all_text = "\n".join([div.get("content", "") for div in divs])

    # ---------- FORCE LLM FOR TESTING ----------
    try:
        llm_result = llm_extract(all_text, divs)
        print("🔍 LLM result:", llm_result)

        if llm_result.get("source") == "flan-t5" and llm_result.get("data"):
            llm_data = llm_result["data"]

            if llm_data.get("organization"):
                result["organization"] = llm_data["organization"]
                result["confidence"]["organization"] = 0.80
                print(f"✅ LLM updated organization to: {llm_data['organization']}")

            if llm_data.get("certificate_number"):
                result["certificate_number"] = llm_data["certificate_number"]
                result["confidence"]["certificate_number"] = 0.80
                print(f"✅ LLM updated certificate_number to: {llm_data['certificate_number']}")
    except Exception as e:
        print(f"⚠️ LLM extraction failed: {e}")

    return result