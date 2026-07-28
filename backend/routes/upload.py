import os
import time
import uuid
import tempfile
import asyncio

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.concurrency import run_in_threadpool
from qdrant_client.http import models

from constants import CHUNK_SIZE, CHUNK_OVERLAP, DOCUMENT_TTL_SECONDS, SUMMARY_MAX_INPUT_CHARS
from qdrant_db import get_qdrant_collection, COLLECTION_NAME, cleanup_old_documents
from summary_store import save_summary, cleanup_old_summaries
from services.pdf_processing import extract_text_from_pdf, normalize_text, chunk_text
from services.embeddings import generate_embeddings
from services.llm import generate_document_summary, build_summary_input

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files are supported")

    cleanup_old_documents()
    cleanup_old_summaries(DOCUMENT_TTL_SECONDS)

    document_id = str(uuid.uuid4())
    uploaded_at = time.time()

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        temp_path = tmp.name
        content = await file.read()
        if not content:
            raise HTTPException(400, "Uploaded file is empty")
        tmp.write(content)

    try:
        raw_pages = await run_in_threadpool(extract_text_from_pdf, temp_path)
        normalized_pages = normalize_text(raw_pages)
        chunks_with_metadata = chunk_text(
            normalized_pages, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP
        )

        if not chunks_with_metadata:
            raise HTTPException(422, "No extractable text found in PDF")
        
        summary_input = build_summary_input(chunks_with_metadata, max_chars=SUMMARY_MAX_INPUT_CHARS)

        embeddings, summary = await asyncio.gather(
            run_in_threadpool(generate_embeddings, [c["text"] for c in chunks_with_metadata], "RETRIEVAL_DOCUMENT"),
            run_in_threadpool(generate_document_summary, summary_input),
        )
        save_summary(document_id, summary, uploaded_at)

        # --- Store chunks in Qdrant ---
        client = get_qdrant_collection()
        ids = [str(uuid.uuid4()) for _ in range(len(chunks_with_metadata))]

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=ids[i],
                    vector=embeddings[i],
                    payload={
                        "document_id": document_id,
                        "uploaded_at": uploaded_at,
                        "filename": file.filename,
                        "text": chunks_with_metadata[i]["text"],
                        "chunk_index": i,
                        "start": chunks_with_metadata[i]["start"],
                        "end": chunks_with_metadata[i]["end"],
                        "page": chunks_with_metadata[i]["page"],
                    },
                )
                for i in range(len(chunks_with_metadata))
            ],
        )
    finally:
        os.remove(temp_path)

    return {
        "document_id": document_id,
        "filename": file.filename,
        "num_chunks": len(chunks_with_metadata),
        "summary": summary,
        "first_chunk_preview": chunks_with_metadata[0]["text"][:200],
    }