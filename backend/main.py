import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routes.upload import router as upload_router
from routes.ask import router as ask_router

load_dotenv()
app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://rag-app-varun.netlify.app"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    return {"status": "ok"}

app.include_router(upload_router)
app.include_router(ask_router)

# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# virtual/Scripts/activate

# Start backend: python -m uvicorn main:app --reload
# Qdrant run command: docker run -p 6333:6333 -p 6334:6334 -v "${PWD}:/qdrant/storage" qdrant/qdrant 