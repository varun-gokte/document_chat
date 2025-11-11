import pdfplumber
from typing import List
import google.generativeai as genai
import numpy as np
from functools import lru_cache
import os

# 1️⃣ Extract raw text from PDF
def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# 2️⃣ Normalize the text
def normalize_text(text: str) -> str:
    # Remove extra whitespace and line breaks
    text = text.replace("\n", " ").replace("\r", " ")
    text = " ".join(text.split())  # remove extra spaces
    return text

# 3️⃣ Chunk the text
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
  """
  Split text into overlapping chunks with metadata.
  Returns a list of dicts: {"text": ..., "start": ..., "end": ..., "page": ...}
  """
  chunks = []
  start = 0
  page = 1  # optional: track page number if you know it from pdfplumber
  while start < len(text):
      end = start + chunk_size
      chunk_text = text[start:end]
      chunks.append({
          "text": chunk_text,
          "start": start,
          "end": end,
          "page": page
      })
      start += chunk_size - overlap
  return chunks

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
@lru_cache
def get_embedding_model():
    """Lazy-load and configure the Gemini Embedding API."""
    if not GEMINI_API_KEY:
        raise RuntimeError("Missing GENAI_API_KEY environment variable")

    genai.configure(api_key=GEMINI_API_KEY)
    return "models/text-embedding-004"

def generate_embeddings(chunks: List[str]) -> np.ndarray:
    model = get_embedding_model()
    response = genai.embed_content(
        model=model,
        input=chunks
    )
    embeddings = response["embedding"]  
    return embeddings

from qdrant_db import get_qdrant_collection, COLLECTION_NAME

def retrieve_relevant_chunks(question: str, k: int = 5):
    client = get_qdrant_collection()
    query_embedding = generate_embeddings([question])[0]

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=k
    )

    return [
        {
            "text": r.payload["text"],
            "start": r.payload.get("start"),
            "end": r.payload.get("end"),
            "page": r.payload.get("page")
        }
        for r in results
    ]
