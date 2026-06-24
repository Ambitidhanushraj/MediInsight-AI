import re

def extract_parameters(text: str):

    results = {}

    hemoglobin = re.search(
        r"Hemoglobin\s*[:\-]?\s*(\d+\.?\d*)",
        text,
        re.IGNORECASE
    )

    if hemoglobin:
        results["Hemoglobin"] = float(
            hemoglobin.group(1)
        )

    return results