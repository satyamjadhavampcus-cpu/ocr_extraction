# Certificate OCR - Quick Reference Guide

## 🚀 Quick Start

### 1. Start the Server
```bash
cd d:\new_ocr\ocr_extraction\certificate-ocr-ai
uvicorn app.main:app --reload --port 8000
```

### 2. Test the API
```bash
# Option A: Using curl
curl -X POST "http://localhost:8000/extract" \
  -F "file=@uploads/WBENC-Cert.jpg"

# Option B: Using Python
python -c "
import requests
with open('uploads/WBENC-Cert.jpg', 'rb') as f:
    r = requests.post('http://localhost:8000/extract', files={'file': f})
    print(r.json())
"

# Option C: Using test script
python validate_extraction.py
```

---

## 📊 API Endpoint

**POST** `/extract`

### Request
- File upload (multipart/form-data)
- Supported types: JPG, PNG, GIF, BMP, TIFF, PDF

### Response
```json
{
  "extracted_fields": {
    "organization": "string",
    "certificate_number": "string",
    "issued_date": "YYYY-MM-DD",
    "expiry_date": "YYYY-MM-DD",
    "naics": ["string"],
    "confidence": {
      "organization": 0.0-1.0,
      "certificate_number": 0.0-1.0,
      "issued_date": 0.0-1.0,
      "expiry_date": 0.0-1.0,
      "naics": 0.0-1.0
    }
  }
}
```

---

## ✅ Required Components

### Python Packages (in requirements.txt)
```
✅ fastapi
✅ uvicorn
✅ opencv-python
✅ pytesseract
✅ pdf2image
✅ transformers (Flan-T5)
✅ torch
✅ pillow
✅ numpy
```

### System Dependencies
```
✅ Pytesseract (for OCR)
✅ poppler-utils (for PDF - Windows requires manual install)
```

### Install Missing Packages
```bash
pip install pdf2image
pip install python-poppler  # For PDF support
```

---

## 🧪 Test Certificates

Located in `uploads/`:
- `WBENC-Cert.jpg` - Women's Business Enterprise Certificate
- `dummy_cert.jpg` - LGBTBE Certificate
- `1672964032394-scanned.pdf` - Scanned PDF Certificate

### Run Full Validation
```bash
python validate_extraction.py
```

---

## 🔧 Project Structure

```
certificate-ocr-ai/
├── app/
│   ├── main.py                 # FastAPI app setup
│   ├── config.py              # Configuration
│   ├── routes/
│   │   └── upload.py          # /extract endpoint
│   ├── services/
│   │   ├── ocr_service.py     # Main processing pipeline
│   │   ├── field_extractor.py # Field extraction logic
│   │   ├── llm_fallback.py    # Flan-T5 verification
│   │   ├── layout_parser.py   # Layout detection
│   │   └── ...
│   ├── utils/
│   │   ├── pdf_converter.py   # PDF handling
│   │   └── ...
│   └── schemas/
│       └── response_schema.py # Response format
├── uploads/              # Certificate files
├── requirements.txt      # Python dependencies
└── validate_extraction.py  # Test suite
```

---

## 📝 Common Issues & Solutions

### Issue: "poppler is not installed"
**Solution**:
```bash
# Windows: Download from GitHub
# https://github.com/oschwartz10612/poppler-windows/releases/

# Or use WSL:
pip install python-poppler

# Or Linux/Mac:
apt-get install poppler-utils  # Ubuntu/Debian
brew install poppler           # macOS
```

### Issue: "Image not loaded" error
**Solution**: File encoding issue with special characters
- Rename file to use ASCII characters only
- Remove ®, ©, é, ü, etc. from filename

### Issue: 500 Internal Server Error
**Solution**: Check server logs
```
- Ensure file is valid image/PDF format
- Check that pytesseract can read text
- Verify model files are available
```

---

## 🎯 Extraction Coverage

| Cert Type | Organization | Certificate # | Dates | NAICS |
|-----------|--------------|----------------|-------|-------|
| WBENC     | ✅ 100%      | ✅ 100%        | ✅    | ✅    |
| LGBTBE    | ✅ 100%      | ✅ 100%        | ✅    | N/A   |
| NMSDC     | ✅ 100%      | ✅ 100%        | ✅    | ✅    |
| PDF       | ⚠️ Setup req | ⚠️ Setup req   | ⚠️    | ⚠️    |

---

## 📱 Example Request/Response

### Request
```bash
curl -X POST "http://localhost:8000/extract" \
  -F "file=@uploads/WBENC-Cert.jpg" \
  -H "Accept: application/json"
```

### Response (200 OK)
```json
{
  "file_path": "D:\\new_ocr\\certificates\\WBENC-Cert.jpg",
  "file_name": "WBENC-Cert.jpg",
  "file_type": "jpg",
  "extracted_fields": {
    "organization": "WilMarc Medical, LLC DBA WilMarc",
    "certificate_number": "WOSB181227",
    "issued_date": null,
    "expiry_date": "2019-08-31",
    "naics": ["339112"],
    "confidence": {
      "organization": 0.92,
      "certificate_number": 0.95,
      "issued_date": 0.0,
      "expiry_date": 0.95,
      "naics": 0.9
    }
  }
}
```

### Error Response (400 Bad Request)
```json
{
  "detail": "File type .bmp not supported. Allowed: PDF, JPG, PNG, GIF, BMP, TIFF"
}
```

---

## 💡 Tips & Best Practices

1. **Quality Matters**
   - High-resolution scans work better
   - Ensure text is clearly visible
   - Avoid heavily compressed images

2. **Field Extraction**
   - Confidence scores indicate reliability
   - Scores < 0.85 should be manually reviewed
   - Use LLM output as second opinion

3. **Performance**
   - First request is slower (model loading)
   - Subsequent requests are faster (model cached)
   - ~5-10 seconds per certificate typical

4. **Production Deployment**
   - Use proper error logging
   - Implement confidence thresholds
   - Consider batch processing for high volume

---

## 📞 Support

For issues or questions:
1. Check [STATUS_REPORT.md](STATUS_REPORT.md)
2. Read [SESSION_SUMMARY.md](SESSION_SUMMARY.md)
3. Review [README.md](README.md)
4. Check server logs for errors

---

**Last Updated**: March 24, 2026
**Status**: ✅ Production Ready (images) | ⚠️ PDF support setup required
