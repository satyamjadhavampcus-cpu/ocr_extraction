import sys
sys.path.append('.')
from app.services.ocr_service import process_document

files = [
    'uploads/v2-dde5c221d3e837b6792c3f2beb9d07c8_r.jpg',
    'uploads/Certified-Supplier-Certificate-Certified-Supplier-Certificate-1024x724.jpg',
    'uploads/MSDUK-Certification.jpg',
    'uploads/R.png',
    'uploads/5d07e6e6fd6f2211626b1294_Flroida-DBE.jpg',
    'uploads/NVBDC-cert.png',
    'uploads/Ampcus WBENC Certificate-Expires 102825.pdf',
    'uploads/Ampcus NMSDC Certificate-Expire 10312025.pdf',
    'uploads/Bravens Inc. Certificate.pdf'
]

for f in files:
    try:
        r = process_document(f)
        print('---', f)
        print('org=', r['extracted_fields'].get('organization'))
        print('cert=', r['extracted_fields'].get('certificate_number'))
        print('issued=', r['extracted_fields'].get('issued_date'))
        print('expiry=', r['extracted_fields'].get('expiry_date'))
        print('naics=', r['extracted_fields'].get('naics'))
    except Exception as e:
        print('---', f, 'ERROR', e)
