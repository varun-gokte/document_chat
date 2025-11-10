import pdfplumber
from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np
from functools import lru_cache

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

@lru_cache
def get_embedder():
    return SentenceTransformer("all-MiniLM-L6-v2")

def generate_embeddings(chunks: List[str]) -> np.ndarray:
    """
    Generate embeddings for a list of text chunks using SentenceTransformers.

    Args:
        chunks (List[str]): List of text chunks

    Returns:
        np.ndarray: Array of embeddings with shape (num_chunks, embedding_dim)
    """
    embedder = get_embedder()
    embeddings = embedder.encode(chunks, convert_to_numpy=True)
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
