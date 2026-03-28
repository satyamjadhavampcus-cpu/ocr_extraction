from app.services.llm_fallback import llm_extract
print('LLM function import successful')
try:
    result = llm_extract("test text", None, [])
    print('LLM function call successful')
except Exception as e:
    print(f'LLM function call failed: {e}')