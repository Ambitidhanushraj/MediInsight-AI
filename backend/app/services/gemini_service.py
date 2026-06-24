from google import genai
import logging
import os

logger = logging.getLogger(__name__)


def _get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def _generate_with_gemini(prompt: str):
    client = _get_client()
    if client is None:
        return None

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        logger.error("Gemini API error: %s", e)
        return None

def generate_medical_answer(
    question,
    report_text,
    rag_context
):

    prompt = f"""
You are an expert medical AI assistant.

Patient Report:
{report_text}

Medical Knowledge:
{rag_context}

User Question:
{question}

Provide:
1. Simple explanation
2. Possible causes
3. Recommendations

Keep response under 200 words.
"""

    answer = _generate_with_gemini(prompt)
    if answer:
        return answer

    return "AI explanation temporarily unavailable."


def generate_medical_summary(report_text):
    prompt = f"""
You are an expert medical AI assistant.

Patient Report:
{report_text}

Provide a brief medical summary in simple language.
Keep response under 120 words.
"""

    summary = _generate_with_gemini(prompt)
    if summary:
        return summary

    return "AI summary temporarily unavailable."