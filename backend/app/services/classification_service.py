# Expected parameters per report type — used for confidence score
EXPECTED_PARAMS: dict[str, list[str]] = {
    "CBC": ["Hemoglobin", "Hematocrit", "RBC", "WBC", "Platelets",
            "MCV", "MCH", "MCHC", "RDW", "Neutrophils", "Lymphocytes",
            "Monocytes", "Eosinophils", "Basophils"],
    "Diabetes": ["Glucose", "HbA1c"],
    "Lipid Profile": ["Total Cholesterol", "LDL", "HDL", "Triglycerides"],
    "Thyroid": ["TSH", "T3", "T4"],
    "Vitamin Report": ["Vitamin D", "Vitamin B12"],
    "Unknown": [],
}


def classify_report(text: str) -> str:

    text = text.lower()

    if "hemoglobin" in text and "rbc" in text:
        return "CBC"

    elif "hba1c" in text:
        return "Diabetes"

    elif "cholesterol" in text:
        return "Lipid Profile"

    elif "tsh" in text:
        return "Thyroid"

    elif "vitamin d" in text:
        return "Vitamin Report"

    return "Unknown"


def confidence_score(report_type: str, extracted: dict) -> dict:
    """Return extraction count, expected count, score % and missing parameters."""
    expected = EXPECTED_PARAMS.get(report_type, [])
    if not expected:
        return {"extracted": len(extracted), "expected": 0, "score": 100, "missing": []}
    found = [p for p in expected if p in extracted]
    missing = [p for p in expected if p not in extracted]
    score = round(len(found) / len(expected) * 100)
    return {
        "extracted": len(found),
        "expected": len(expected),
        "score": score,
        "missing": missing,
    }