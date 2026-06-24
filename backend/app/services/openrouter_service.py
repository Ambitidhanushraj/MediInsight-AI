"""
OpenRouter LLM service — free tier model: mistralai/mistral-7b-instruct:free
Docs: https://openrouter.ai/docs
Get free key: https://openrouter.ai/keys
"""
import logging
import os

import httpx
from app.config.config import OPENROUTER_API_KEY

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# Free model — no billing needed.  Change to any model slug from openrouter.ai/models
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct:free")


def _call_openrouter(system_prompt: str, user_prompt: str, doctor_mode: bool = False) -> str | None:
    """
    Call OpenRouter with a system + user message pair.
    Returns the assistant text or None on failure.
    """
    if not OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not set — skipping OpenRouter call")
        return None

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5173",   # required by OpenRouter
        "X-Title": "MediInsight AI",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "max_tokens": 700 if doctor_mode else 450,
        "temperature": 0.2 if doctor_mode else 0.4,
    }

    try:
        response = httpx.post(
            OPENROUTER_URL,
            json=payload,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except httpx.HTTPStatusError as e:
        logger.error("OpenRouter HTTP error %s: %s", e.response.status_code, e.response.text)
    except Exception as e:
        logger.error("OpenRouter error: %s", e)

    return None


def answer_report_question(
    question: str,
    report_text: str,
    rag_context: str,
    doctor_mode: bool = False,
) -> str:
    """
    Use OpenRouter to answer a question about an uploaded report.
    doctor_mode=True uses clinical terminology + differential + follow-up suggestions.
    """
    if doctor_mode:
        system_prompt = (
            "You are a clinical decision support assistant advising a physician. "
            "Always use precise medical terminology. Never simplify for a lay audience."
        )
        user_prompt = f"""Patient Report:
{report_text}

Knowledge Base:
{rag_context}

Clinician Question: {question}

Respond in clinical format:
1. Clinical Interpretation (use medical terminology, reference ranges where relevant)
2. Differential Diagnoses (list with brief rationale for each)
3. Recommended Investigations (labs, imaging, or referrals)
4. Management Considerations (pharmacological or non-pharmacological)

Be concise. Do not issue a definitive diagnosis. Max 350 words."""
    else:
        system_prompt = (
            "You are MediInsight AI, a friendly health assistant for patients. "
            "Use simple, everyday language a non-medical person can understand. "
            "Avoid medical jargon. Always suggest seeing a doctor for confirmation."
        )
        user_prompt = f"""My medical report:
{report_text}

Extra context:
{rag_context}

My question: {question}

Please explain in plain language:
1. What this result means in simple terms
2. Common reasons this might happen
3. What I should do next

Keep it friendly and under 200 words. Remind me to speak with my doctor."""

    return _call_openrouter(system_prompt, user_prompt, doctor_mode=doctor_mode)


def answer_medical_question(
    question: str,
    rag_context: str,
    doctor_mode: bool = False,
) -> str | None:
    """
    Use OpenRouter to answer a general medical question using RAG context.
    """
    if doctor_mode:
        system_prompt = (
            "You are a clinical decision support assistant advising a physician. "
            "Always use precise medical terminology. Never simplify for a lay audience."
        )
        user_prompt = f"""Knowledge Base:
{rag_context}

Clinician Question: {question}

Respond in clinical format:
1. Pathophysiology / Mechanism
2. Differential Diagnoses with brief rationale
3. Evidence-based investigations or management
4. Relevant clinical pearls or guidelines

Be concise. Max 300 words."""
    else:
        system_prompt = (
            "You are MediInsight AI, a friendly health assistant for patients. "
            "Use simple, everyday language a non-medical person can understand. "
            "Avoid jargon. Always suggest seeing a doctor."
        )
        user_prompt = f"""Health information:
{rag_context}

My question: {question}

Please explain in simple terms. Keep it under 150 words and remind me to see a doctor."""

    return _call_openrouter(system_prompt, user_prompt, doctor_mode=doctor_mode)
