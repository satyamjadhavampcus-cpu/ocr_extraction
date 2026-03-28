from fastapi import FastAPI
from app.routes.upload import router
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Certificate OCR AI")

app.include_router(router)