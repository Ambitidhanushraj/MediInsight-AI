from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_service import retrieve_context
from app.services.openrouter_service import answer_report_question
from app.services.gemini_service import generate_medical_answer
from app.services.history_service import (
    save_chat_message,
    get_chat_history,
    clear_chat_history,
    get_report_list,
    get_report_analysis,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class ReportQuestionRequest(BaseModel):
    question: str
    report_text: str
    report_id: str | None = None
    doctor_mode: bool = False


@router.post("/ask-report")
def ask_report(request: ReportQuestionRequest):
    rag_context = retrieve_context(request.question)

    # Primary: OpenRouter (free model, natural language)
    answer = answer_report_question(
        request.question,
        request.report_text,
        rag_context,
        doctor_mode=request.doctor_mode,
    )
    model_used = "openrouter"

    # Fallback: Gemini
    if not answer:
        logger.warning("OpenRouter unavailable — falling back to Gemini")
        answer = generate_medical_answer(
            request.question,
            request.report_text,
            rag_context,
        )
        model_used = "gemini"

    # Last-resort: raw RAG context
    if not answer:
        logger.warning("Gemini unavailable — returning raw RAG context")
        answer = rag_context or "No relevant information found in the knowledge base."
        model_used = "rag"

    save_chat_message(
        report_id=request.report_id,
        context_type="report",
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


@router.get("/reports")
def list_reports(limit: int = 20):
    """Return list of previously uploaded reports for comparison picker."""
    return {"reports": get_report_list(limit=limit)}


@router.get("/reports/{report_id}/analysis")
def report_analysis(report_id: str):
    """Return stored analysis for a given report_id (used in comparison)."""
    data = get_report_analysis(report_id)
    if not data:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Report not found")
    return data


@router.get("/chat-history")
def chat_history(report_id: str | None = None, limit: int = 50):
    return {
        "items": get_chat_history(report_id=report_id, limit=limit)
    }


@router.delete("/chat-history")
def delete_chat_history(report_id: str | None = None):
    deleted = clear_chat_history(report_id=report_id)
    return {
        "deleted": deleted,
        "report_id": report_id,
    }