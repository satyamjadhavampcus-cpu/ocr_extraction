import sys
sys.path.append('.')
from app.services.ocr_service import process_document

# Test with the Disability-IN certificate
result = process_document('uploads/Disability-IN-cert.jpg')
print('Full result:')
print(result)
print()
fields = result.get('extracted_fields', {})
print('Organization:', fields.get('organization'))
print('Certificate Number:', fields.get('certificate_number'))
print('Issued Date:', fields.get('issued_date'))
print('Expiry Date:', fields.get('expiry_date'))
print('NAICS:', fields.get('naics'))
print('UNSPSC:', fields.get('unspsc'))