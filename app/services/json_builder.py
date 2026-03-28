import os

def build_json(file_path, raw_text, clean_text, fields):
    return {
        "file_path": file_path,
        "file_name": os.path.basename(file_path),
        "file_type": file_path.split(".")[-1],
        "raw_text": raw_text,
        "clean_text": clean_text,
        "extracted_fields": fields
    }