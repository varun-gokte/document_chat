import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "document_chunks")

_client = None     # Lazy-initialized client
_collection_ready = False  # Tracks if collection is created

def get_qdrant_client() -> QdrantClient:
    """Lazy-initialize and return the Qdrant client."""
    global _client
    if _client is None:
        _client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )
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
                    size=768,
                    distance=models.Distance.COSINE,
                )
            )

            # ✅ Wait until Qdrant confirms the collection exists
            import time
            while True:
                collections = [c.name for c in client.get_collections().collections]
                if COLLECTION_NAME in collections:
                    break
                time.sleep(0.2)

        _collection_ready = True

    return client
