import requests
import json

with open('uploads/Bravens Inc. Certificate.pdf', 'rb') as f:
    files = {'file': ('test.pdf', f, 'application/pdf')}
    r = requests.post('http://localhost:8001/extract', files=files)

print(json.dumps(r.json(), indent=2))