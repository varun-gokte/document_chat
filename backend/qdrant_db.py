# qdrant_db.py
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

# 👇 Define this at the top
COLLECTION_NAME = "document_chunks"

def get_qdrant_collection():
    client = QdrantClient(path="./qdrant_db")

    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,  # embedding dimension for all-MiniLM-L6-v2
            distance=Distance.COSINE
        )
    )

    return client
