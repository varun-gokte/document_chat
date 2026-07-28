import time

# document_id -> {"summary": str, "uploaded_at": float}
document_summaries: dict[str, dict] = {}

def save_summary(document_id: str, summary: str, uploaded_at: float) -> None:
    document_summaries[document_id] = {"summary": summary, "uploaded_at": uploaded_at}

def get_document_summary(document_id: str) -> str | None:
    entry = document_summaries.get(document_id)
    return entry["summary"] if entry else None

def cleanup_old_summaries(max_age_seconds: int) -> None:
    """Remove summaries older than max_age_seconds. Call alongside cleanup_old_documents."""
    cutoff = time.time() - max_age_seconds
    expired_ids = [
        doc_id for doc_id, entry in document_summaries.items()
        if entry["uploaded_at"] < cutoff
    ]
    for doc_id in expired_ids:
        del document_summaries[doc_id]