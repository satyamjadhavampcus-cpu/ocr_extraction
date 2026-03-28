from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os

from app.services.ocr_service import process_document

router = APIRouter()

# Ensure upload directory exists and use absolute path
UPLOAD_DIR = os.path.abspath("uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}

@router.post("/extract")
async def extract_certificate(file: UploadFile = File(...)):
    try:
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not supported. Allowed: PDF, JPG, PNG, GIF, BMP, TIFF"
            )
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Verify file was saved
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file to {file_path}"
            )

        result = process_document(file_path)
        
        # Return the full result including file path, raw text, clean text, div blocks, and extracted fields
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Certificate extraction failed: {str(e)}"
        )