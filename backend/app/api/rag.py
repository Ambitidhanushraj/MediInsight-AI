from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_service import retrieve_context
from app.services.openrouter_service import answer_medical_question
from app.services.history_service import save_chat_message
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class QuestionRequest(BaseModel):
    question: str
    doctor_mode: bool = False


@router.post("/ask-medical")
def ask_medical(request: QuestionRequest):
    rag_context = retrieve_context(request.question)

    # Primary: OpenRouter LLM with RAG context
    answer = answer_medical_question(
        request.question,
        rag_context,
        doctor_mode=request.doctor_mode,
    )
    model_used = "openrouter"

    # Fallback: raw RAG chunks
    if not answer:
        logger.warning("OpenRouter unavailable — returning raw RAG context")
        answer = rag_context or "No relevant information found in the knowledge base."
        model_used = "rag"

    save_chat_message(
        report_id=None,
        context_type="general",
        question=request.question,
        answer=answer,
        model=model_used,
    )

    return {
        "question": request.question,
        "answer": answer,
        "model": model_used,
        "doctor_mode": request.doctor_mode,
    }