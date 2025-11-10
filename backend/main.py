from helpers import extract_text_from_pdf, normalize_text,chunk_text, generate_embeddings, retrieve_relevant_chunks
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
from qdrant_db import get_qdrant_collection
from qdrant_client.http import models
import uuid

load_dotenv()
app = FastAPI()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_ENDPOINT = "https://generativeai.googleapis.com/v1beta2/models/text-bison-001:generate--"

# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# virtual/Scripts/activate

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
genai.configure(api_key=os.getenv("GENAI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://querydocs.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Save file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    # Extract, normalize, chunk
    raw_text = extract_text_from_pdf(temp_path)
    normalized_text = normalize_text(raw_text)
    chunks_with_metadata = chunk_text(normalized_text, chunk_size=500, overlap=50)
    embeddings = generate_embeddings([c["text"] for c in chunks_with_metadata])

    client = get_qdrant_collection()

    ids = [str(uuid.uuid4()) for _ in range(len(chunks_with_metadata))]

    client.upsert(
        collection_name="document_chunks",
        points=[
            models.PointStruct(
                id=ids[i],
                vector=embeddings[i],
                payload={
                    "text": chunks_with_metadata[i]["text"],
                    "chunk_index": i,
                    "start": chunks_with_metadata[i]["start"],
                    "end": chunks_with_metadata[i]["end"],
                    "page": chunks_with_metadata[i]["page"],
                },
            )
            for i in range(len(chunks_with_metadata))
        ]
    )
    os.remove(temp_path)

    return {
        "filename": file.filename,
        "num_chunks": len(chunks_with_metadata),
        "first_chunk_preview": chunks_with_metadata[0] if chunks_with_metadata else ""
    }

class AskRequest(BaseModel):
    question: str
    pdfUrl: str  # Or a unique document identifier

@app.post("/ask")
async def ask(request: AskRequest):
    try:
        chunks = retrieve_relevant_chunks(request.question)
        if not chunks:
            return {"answer": "No relevant information found."}

        # Build prompt for Gemini
        context = "\n\n".join([c["text"] for c in chunks])
        prompt = f"Answer the following question using only the context below:\n\nContext:\n{context}\n\nQuestion: {request.question}\nAnswer:"

        response = model.generate_content(prompt)

        # Return both answer and metadata
        return {
            "answer": response.text,
            "sources": [{"page": c["page"], "start": c["start"], "end": c["end"]} for c in chunks]
        }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
