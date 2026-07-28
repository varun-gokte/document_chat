import os
import time
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import time
from qdrant_client.models import Filter, FieldCondition, Range
from constants import EMBEDDING_DIM, DOCUMENT_TTL_SECONDS
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "document_chunks")

_client = None
_collection_ready = False

def get_qdrant_client() -> QdrantClient:
    """Lazy-initialize and return the Qdrant client."""
    global _client
    if _client is None:
        if not QDRANT_URL:
            raise RuntimeError("Missing QDRANT_URL environment variable")
        _client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    return _client


def get_qdrant_collection() -> QdrantClient:
    """
    Ensure Qdrant client is initialized and collection exists.
    Returns the client (ready for upsert/search).
    """
    global _collection_ready
    client = get_qdrant_client()

    if not _collection_ready:
        existing_collections = [c.name for c in client.get_collections().collections]
        if COLLECTION_NAME not in existing_collections:
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=EMBEDDING_DIM,
                    distance=models.Distance.COSINE,
                ),
            )

            # Wait until Qdrant confirms the collection exists, with a timeout
            max_wait_seconds = 10
            waited = 0.0
            while waited < max_wait_seconds:
                collections = [c.name for c in client.get_collections().collections]
                if COLLECTION_NAME in collections:
                    break
                time.sleep(0.2)
                waited += 0.2
            else:
                raise RuntimeError(
                    f"Timed out waiting for Qdrant collection '{COLLECTION_NAME}' to be created"
                )

        _collection_ready = True

    return client


def cleanup_old_documents(max_age_seconds: int = DOCUMENT_TTL_SECONDS):
    """
    Delete all chunks belonging to documents uploaded more than
    max_age_seconds ago. Safe to call anytime — only removes points
    whose uploaded_at timestamp is older than the cutoff.
    """
    client = get_qdrant_collection()
    cutoff = time.time() - max_age_seconds

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="uploaded_at",
                    range=Range(lt=cutoff),
                )
            ]
        ),
    )