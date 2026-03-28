import requests
import json

# Test Ampcus WBENC
with open('uploads/Ampcus WBENC Certificate-Expires 102825.pdf', 'rb') as f:
    files = {'file': ('test.pdf', f, 'application/pdf')}
    response = requests.post('http://localhost:8001/extract', files=files)

print('Full API Response:')
result = response.json()
print(json.dumps(result, indent=2))