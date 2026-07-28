from functools import lru_cache
import os

from google import genai
from qdrant_client.models import Filter, FieldCondition, MatchValue

from qdrant_db import get_qdrant_collection
from .embeddings import generate_embeddings
from constants import CHAT_MODEL
from qdrant_db import COLLECTION_NAME

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@lru_cache
def get_genai_client():
    """Lazy-load and cache the Gemini client."""
    if not GEMINI_API_KEY:
        raise RuntimeError("Missing GEMINI_API_KEY environment variable")
    return genai.Client(api_key=GEMINI_API_KEY)


def retrieve_relevant_chunks(question: str, document_id: str, k: int = 5):
    client = get_qdrant_collection()
    query_embedding = generate_embeddings([question], task_type="RETRIEVAL_QUERY")[0]

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        query_filter=Filter(
            must=[
                FieldCondition(key="document_id", match=MatchValue(value=document_id))
            ]
        ),
        limit=k,
    ).points
    print (f"Retrieved {len(results)} relevant chunks for document_id {document_id}")
    return [
        {
            "text": r.payload["text"],
            "start": r.payload.get("start"),
            "end": r.payload.get("end"),
            "page": r.payload.get("page"),
        }
        for r in results
    ]

def generate_document_summary(text: str) -> str:
    """Generate a short summary describing what the document is."""
    client = get_genai_client()
    prompt = (
        "In 2-3 sentences, describe what kind of document this is and "
        "who or what it's about. Be specific (e.g. 'a resume for a "
        "software developer', not just 'a document').\n\n"
        f"{text}"
    )
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text.strip()

def build_summary_input(chunks_with_metadata: list[dict], max_chars: int = 12000) -> str:
    """
    Build a bounded-size sample of the document for summarization.
    Small documents: use everything. Large documents: sample evenly
    across the full length so the summary reflects the whole document.
    """
    full_text = " ".join(c["text"] for c in chunks_with_metadata)

    if len(full_text) <= max_chars:
        return full_text

    num_chunks = len(chunks_with_metadata)
    sample_count = max(1, max_chars // 500)
    step = max(1, num_chunks // sample_count)

    sampled = chunks_with_metadata[::step]
    sample_text = " ".join(c["text"] for c in sampled)
    return sample_text[:max_chars]

