import sys
sys.path.append('.')
from app.services.field_extractor import extract_fields_from_divs

# Mock divs based on the actual OCR output from the new certificate
divs = [
    {"content": "WOMEN’S BUSINESS ENTERPRISE\nNATIONAL COUNCIL"},
    {"content": "JOIN FORCES. SUCCEED TOGETHER."},
    {"content": "HEREBY GRANTS\nWOMAN OWNED SMALL BUSINESS (WOSB) CERTIFICATION TO"},
    {"content": "Timbelo Inc"},
    {"content": "The identified small business is an eligible WOSB for the WOSB Program, as set forth in 13 C.F.R. part 127 and has been certified as such by an\nSBA approved Third Party Certifier pursuant to the Third Party Agreement, dated June 30, 2011, and available at www.sba.gov/wosb."},
    {"content": "The WOSB Certification expires on the date herein unless there is a change in the SBA’s regulation that makes the WOSB ineligible or there is a change in the\nWOSB that makes the WOSE ligible. If either occurs, this WOSB Certification is immediately invalid. The WOSB must not misrepresent ification\nstatus to any other party, including any local or State government or contracting official or the Federal government or any of its contracting officials."},
    {"content": "NAICS: 541611, 541512, 541990, 561320 La\nUNSPSC: 80111609 Sheila Mixon, Ohio River Valley Women's Business Council\nExecutive Director\nCertification Number. WOSB170255 BEGORV"},
    {"content": "Expiration Date: February 28, 2022 NOMEN’S BUSINESS VALLEY ENTERPRISE COUNCIL Pamela Prince-Eason, WBENC President & CEO"},
    {"content": "5 < Ayé\nLaura Taylor, WBENC Vice President"}
]

result = extract_fields_from_divs(divs)
print('Full result:')
print(result)
print()
print('Organization:', result.get('organization'))
print('Certificate Number:', result.get('certificate_number'))
print('Expiry Date:', result.get('expiry_date'))
print('NAICS:', result.get('naics'))
print('Expiry Date:', result.get('expiry_date'))