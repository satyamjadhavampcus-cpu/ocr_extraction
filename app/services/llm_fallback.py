import json
import re
from transformers import pipeline
from models.response_schema import CertificateData
from typing import Optional

# We can initialize the pipeline lazily to save resources on startup
_llm_pipeline = None

def get_pipeline():
    global _llm_pipeline
    if _llm_pipeline is None:
        model_id = "Qwen/Qwen2.5-0.5B-Instruct"  # 3x smaller, very fast on CPU
        print(f"Loading local model {model_id} (This may take a few minutes to download the first time)...")
        _llm_pipeline = pipeline(
            "text-generation",
            model=model_id,
            device_map="auto"
        )
        print("Model loaded successfully.")
    return _llm_pipeline

class LLMExtractor:
    def __init__(self):
        pass  # Pipeline initialized lazily

    def extract(self, raw_text, clean_text, layout_divs):
        # Combine inputs into a single OCR text
        layout_text = "\n".join([f"Block {i}: {div.get('content', '')}" for i, div in enumerate(layout_divs)])
        ocr_text = f"Raw Text:\n{raw_text}\n\nClean Text:\n{clean_text}\n\nLayout Blocks:\n{layout_text}"

        pipe = get_pipeline()
        
        messages = [
            {"role": "system", "content": "You are a highly precise data extraction assistant. Your ONLY job is to extract requested fields from the given text and output them in valid JSON format. Do NOT invent or hallucinate any data. Only extract information that is explicitly present in the text. If a field is not found, set it to null or empty as appropriate. Think step-by-step inside the `_thinking` field before outputting."},
            {"role": "user", "content": f"Extract the following fields from the OCR text into JSON. The text may be tab-separated `|` representing columns. Look closely at dates next to their labels.\n- \"_thinking\" (string): Analyze the document text row by row. Identify the exact substrings that correspond to the requested fields and justify your extraction. If a field is not present, state that clearly. Put this before any other field.\n- \"certificate_number\" (string): The unique certification number (e.g., 'Nwos277'). Look for 'Number', 'Certificate', etc. Return as a single string, not a list.\n- \"organization\" (string): The name of the organization receiving the certification. Return as a single string, not a list.\n- \"expiry_date\" (string): The expiration date as a single date string (e.g., '05/31/2022'). Return as a single string, not a list.\n- \"issued_date\" (string): The issue date as a single date string (e.g., '05/31/2021'). Return as a single string, not a list.\n- \"naics\" (list of strings): Any NAICS codes found in the text. If no NAICS codes are present, return an empty list [].\n- \"unspsc\" (list of strings): Any UNSPSC codes found in the text. If no UNSPSC codes are present, return an empty list [].\n\nOCR Text:\n```\n{ocr_text}\n```\n\nOutput only a single JSON object with the exact field names above."}
        ]
        
        outputs = pipe(
            messages,
            max_new_tokens=400,
            do_sample=False,  
            temperature=0.0,
        )
        
        generated_text = outputs[0]["generated_text"][-1]["content"].strip()
        
        # Try to parse the response as JSON
        # Frequently, LLMs wrap JSON in ```json ... ``` blocks
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', generated_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = generated_text
            
        try:
            parsed_data = json.loads(json_str)
            # Remove _thinking if present
            parsed_data.pop('_thinking', None)
            
            # Post-process to handle common LLM mistakes
            for field in ['organization', 'certificate_number', 'issued_date', 'expiry_date']:
                value = parsed_data.get(field)
                if isinstance(value, list):
                    # If it's a list, take the first string element or join them
                    if value and isinstance(value[0], str):
                        parsed_data[field] = value[0] if len(value) == 1 else ' '.join(value)
                    else:
                        parsed_data[field] = None
                elif not isinstance(value, str) and value is not None:
                    parsed_data[field] = str(value)
            
            # Ensure all expected fields are present
            expected_fields = ['organization', 'certificate_number', 'issued_date', 'expiry_date', 'naics', 'unspsc']
            for field in expected_fields:
                if field not in parsed_data:
                    parsed_data[field] = [] if field in ['naics', 'unspsc'] else None
            
            # Validate against the Pydantic model to ensure accurate structure
            valid_data = CertificateData(**parsed_data)
            return valid_data.model_dump()
        except Exception as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Raw output: {generated_text}")
            # Return fallback empty structure
            return CertificateData().model_dump()

# Module-level instance and wrapper function for backward compatibility
_extractor = LLMExtractor()


def llm_extract(raw_text, clean_text=None, layout_divs=None):
    """Wrapper function to maintain API compatibility with existing imports."""
    if layout_divs is None:
        layout_divs = []
    if clean_text is None:
        clean_text = raw_text
    return _extractor.extract(raw_text, clean_text, layout_divs)

