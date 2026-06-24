from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.services.pdf_service import extract_text_from_pdf
from app.services.ocr_service import extract_text_from_image
from app.services.classification_service import classify_report
from app.services.report_parser import extract_health_parameters
from app.services.analysis_service import analyze_parameter, has_critical_values
from app.services.summary_service import generate_summary
from app.services.recommendation_service import generate_recommendations
from app.services.risk_service import calculate_risk
from app.services.gemini_service import generate_medical_summary
from app.services.history_service import save_report, save_report_analysis
from app.services.classification_service import classify_report, confidence_score
from app.config.config import UPLOAD_DIR, MAX_UPLOAD_SIZE, ALLOWED_EXTENSIONS
import logging
import os
import uuid
import json

logger = logging.getLogger(__name__)

router = APIRouter()

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Valid file magic bytes
_MAGIC = {
    b"%PDF": ".pdf",
    b"\xff\xd8\xff": ".jpg",
    b"\x89PNG": ".png",
}


def _detect_type(file_path: str) -> str | None:
    """Return extension based on magic bytes, or None if unrecognised."""
    with open(file_path, "rb") as f:
        header = f.read(4)
    for magic, ext in _MAGIC.items():
        if header.startswith(magic):
            return ext
    return None


def is_pdf_file(file_path: str) -> bool:
    return _detect_type(file_path) == ".pdf"


@router.post("/upload-report")
async def upload_report(
    file: UploadFile = File(...),
    age: int = Form(None),
    sex: str = Form(None),
):

    # Extension allow-list
    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail=f"Only {', '.join(ALLOWED_EXTENSIONS)} files are allowed"
        )

    # Read file into memory first so we can size-check before writing
    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE // (1024*1024)} MB"
        )

    # Save with UUID name to prevent path traversal / name collisions
    ext = os.path.splitext(file.filename)[1].lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    # Validate actual file type via magic bytes
    detected = _detect_type(file_path)
    if detected is None:
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail="File content does not match a supported type (PDF, JPEG, PNG)"
        )

    logger.info("Uploaded file %s saved as %s (%d bytes)", file.filename, safe_name, len(contents))

    extracted_text = ""

    # PDF Processing
    if is_pdf_file(file_path):

        extracted_text = extract_text_from_pdf(
            file_path
        )

        # OCR fallback for scanned PDFs
        if not extracted_text.strip():

            from app.services.pdf_ocr_service import (
                extract_text_with_ocr
            )

            extracted_text = extract_text_with_ocr(
                file_path
            )

    # Image Processing
    else:

        extracted_text = extract_text_from_image(
            file_path
        )

    report_type = classify_report(
        extracted_text
    )

    parameters = extract_health_parameters(
        extracted_text
    )

    analysis = {}

    for name, value in parameters.items():

        analysis[name] = {
            "value": value,
            "status": analyze_parameter(
                name,
                value,
                sex=sex,
                age=age,
            )
        }

    summary = generate_summary(
        analysis
    )

    recommendations = generate_recommendations(
        analysis
    )

    risk_level = calculate_risk(
        analysis
    )

    # Gemini AI Summary
    try:
        ai_summary = generate_medical_summary(
            extracted_text
        )
    except Exception as e:
        logger.error("Gemini summary error: %s", e)
        ai_summary = "AI summary temporarily unavailable."

    report_id = uuid.uuid4().hex
    save_report(
        report_id=report_id,
        filename=file.filename,
        report_type=report_type,
        risk_level=risk_level,
        summary=summary,
    )
    save_report_analysis(report_id, json.dumps(analysis))

    conf = confidence_score(report_type, parameters)

    return {
        "report_id": report_id,
        "filename": file.filename,
        "report_type": report_type,
        "risk_level": risk_level,
        "has_critical": has_critical_values(analysis),
        "critical_parameters": [
            name for name, d in analysis.items()
            if d.get("status", "").startswith("Critical")
        ],
        "confidence": conf,
        "analysis": analysis,
        "summary": summary,
        "ai_summary": ai_summary,
        "recommendations": recommendations,
        "text_preview": extracted_text[:1000]
    }