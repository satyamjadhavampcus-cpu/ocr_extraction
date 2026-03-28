import cv2
import os
import numpy as np
from pdf2image import convert_from_path

from app.services.bbox_extractor import extract_bounding_boxes
from app.services.layout_parser import group_by_lines, lines_to_text
from app.services.layout_blocks import group_into_blocks, blocks_to_divs
from app.services.field_extractor import extract_fields_from_divs
from app.services.llm_fallback import llm_extract


def process_document(file_path):
    # Verify file exists before processing
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Resolve to absolute path
    abs_file_path = os.path.abspath(file_path)
    file_ext = os.path.splitext(abs_file_path)[1].lower()
    
    # Handle PDF files
    if file_ext == '.pdf':
        try:
            print(f"📄 Converting PDF to image: {abs_file_path}")
            # Hardcoded poppler path for Windows
            poppler_path = r"C:\Users\Satyam.Jadhav\AppData\Local\Programs\poppler-25.12.0\Library\bin"

            pages = convert_from_path(
                abs_file_path,
                first_page=1,
                last_page=1,
                dpi=600,
                poppler_path=poppler_path,
            )

            if not pages:
                raise Exception("PDF conversion failed: no pages extracted")

            # Convert PIL image to OpenCV format
            pil_image = pages[0]
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            print(f"✅ PDF converted to image, size: {image.shape}")
        except Exception as e:
            # Improve error handling for poppler issues
            msg = str(e)
            if "Unable to get page count" in msg or "Poppler" in msg or "pdftoppm" in msg:
                raise Exception(
                    "PDF processing error: Unable to get page count. "
                    "Please ensure poppler is installed at: "
                    r"C:\Users\Satyam.Jadhav\AppData\Local\Programs\poppler-25.12.0\Library\bin"
                )
            raise Exception(f"PDF processing error: {msg}")
    else:
        # Load image directly for JPG/PNG
        image = cv2.imread(abs_file_path)
        if image is None:
            raise Exception(f"Image not loaded: unable to read file at {abs_file_path}. Check file format (JPG/PNG) or integrity.")

    # resize
    h, w = image.shape[:2]
    if w < 1500:
        scale = 1500 / w
        image = cv2.resize(image, None, fx=scale, fy=scale)

    # Conservative preprocessing for better OCR quality
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply mild denoising
    gray = cv2.bilateralFilter(gray, 9, 15, 15)

    # Increase contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8,8))
    gray = clahe.apply(gray)

    # OCR bounding boxes
    boxes = extract_bounding_boxes(gray)

    # line grouping
    lines = group_by_lines(boxes)

    # structured lines
    text_lines = lines_to_text(lines)

    # DIV blocks
    blocks = group_into_blocks(text_lines)
    divs = blocks_to_divs(blocks)

    # raw text (keep structured)
    raw_text = "\n".join([line["text"] for line in text_lines])

    # clean text (remove extra whitespace and normalize)
    clean_text = " ".join([line["text"].strip() for line in text_lines if line["text"].strip()])

    # extraction (optional fallback)
    fields = extract_fields_from_divs(divs, raw_text, clean_text)
    

    result = {
        "file_path": file_path,
        "file_name": file_path.split("\\")[-1],
        "file_type": file_path.split(".")[-1],
        "raw_text": raw_text,
        "clean_text": raw_text,
        "layout_divs": divs,
        "extracted_fields": fields
    }

    return result


def process_document_no_llm(file_path):
    """Process document without LLM fallback for faster testing"""
    # Convert to image if PDF
    if file_path.lower().endswith('.pdf'):
        try:
            images = convert_from_path(file_path, poppler_path=r'C:\poppler-24.02.0\Library\bin')
            image = images[0]  # Use first page
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            return {"status": 500, "message": f"PDF conversion failed: {str(e)}"}
    else:
        image = cv2.imread(file_path)
        if image is None:
            return {"status": 400, "message": "Could not read image file"}

    # OCR
    text_lines = ocr_image(image)
    
    # Layout analysis
    divs = parse_layout(text_lines)
    
    # Extract fields
    fields = extract_fields_from_divs(divs)

    result = {
        "file_path": file_path,
        "file_name": file_path.split("\\")[-1],
        "file_type": file_path.split(".")[-1],
        "raw_text": "\n".join([line["text"] for line in text_lines]),
        "clean_text": "\n".join([line["text"] for line in text_lines]),
        "layout_divs": divs,
        "extracted_fields": fields
    }

    return result