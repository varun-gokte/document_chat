from functools import lru_cache
import os
import numpy as np
from google import genai
from google.genai import types

from constants import EMBEDDING_MODEL

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@lru_cache
def get_embedding_client():
    """Lazy-load and cache the Gemini client."""
    if not GEMINI_API_KEY:
        raise RuntimeError("Missing GEMINI_API_KEY environment variable")
    return genai.Client(api_key=GEMINI_API_KEY)


def generate_embeddings(chunks: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> np.ndarray:
    """
    Embed a list of text chunks.
    task_type: "RETRIEVAL_DOCUMENT" for chunks being indexed,
               "RETRIEVAL_QUERY" for a user's search question.
    """
    client = get_embedding_client()
    batch_size = 100

    all_embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        try:
            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=batch,
                config=types.EmbedContentConfig(task_type=task_type),
            )
        except Exception as e:
            raise RuntimeError(f"Embedding generation failed: {e}") from e
        all_embeddings.extend(e.values for e in response.embeddings)

    return np.array(all_embeddings)