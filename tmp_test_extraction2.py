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

with open('tmp_test_results.txt', 'w', encoding='utf-8') as out:
    for f in files:
        try:
            r = process_document(f)
            out.write('--- ' + f + '\n')
            out.write('org=' + str(r['extracted_fields'].get('organization')) + '\n')
            out.write('cert=' + str(r['extracted_fields'].get('certificate_number')) + '\n')
            out.write('issued=' + str(r['extracted_fields'].get('issued_date')) + '\n')
            out.write('expiry=' + str(r['extracted_fields'].get('expiry_date')) + '\n')
            out.write('naics=' + str(r['extracted_fields'].get('naics')) + '\n')
        except Exception as e:
            out.write('--- ' + f + ' ERROR ' + str(e) + '\n')
