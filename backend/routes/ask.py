from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
import logging

from summary_store import get_document_summary
from services.llm import get_genai_client,retrieve_relevant_chunks
from constants import CHAT_MODEL

logger = logging.getLogger(__name__)
router = APIRouter()


class AskRequest(BaseModel):
    question: str
    document_id: str
    history: list[dict] = [] 

@router.post("/ask")
async def ask(request: AskRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        chunks = await run_in_threadpool(
            retrieve_relevant_chunks, request.question, request.document_id
        )
        # summary = get_document_summary(request.document_id)

        if not chunks:# and not summary:
            return {"answer": "No relevant information found."}

        context_parts = []
        # if summary:
        #     context_parts.append(f"Document summary: {summary}")
        if chunks:
            context_parts.append("\n\n".join(c["text"] for c in chunks))
        context = "\n\n".join(context_parts)

        history_text = "\n".join(f"{m['role']}: {m['text']}" for m in request.history[-6:])

        prompt = (
            "You are answering questions about a single document. "
            "Use only the information in the context below — do not use outside knowledge. "
            "If the answer isn't in the context, say so explicitly rather than guessing.\n\n"
            f"Context:\n{context}\n\n"
            f"Conversation so far:\n{history_text}\n\n"
            f"Question: {request.question}\n\n"
            "Answer:"
        )

        client = get_genai_client()
        response = await run_in_threadpool(
            client.models.generate_content,
            model=CHAT_MODEL,
            contents=prompt,
        )

        return {
            "answer": response.text,
            "sources": [
                {"page": c["page"], "start": c["start"], "end": c["end"]} for c in chunks
            ],
        }

    except Exception as e:
        logger.exception("Failed to answer question")
        raise HTTPException(
            status_code=500, detail="Something went wrong answering your question"
        )