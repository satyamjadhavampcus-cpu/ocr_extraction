try:
    from app.services.llm_fallback import llm_extract
    print('✅ LLM import successful')
except Exception as e:
    print(f'❌ LLM import failed: {e}')

try:
    from app.services.field_extractor import extract_fields_from_divs
    print('✅ Field extractor import successful')
except Exception as e:
    print(f'❌ Field extractor import failed: {e}')