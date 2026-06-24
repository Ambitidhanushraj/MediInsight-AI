def calculate_risk(analysis: dict) -> str:
    """Weight: Critical = 3 pts, High/Low = 1 pt each."""
    risk_score = 0

    for parameter, details in analysis.items():
        status = details.get("status", "Normal")
        if status in ("Critical Low", "Critical High"):
            risk_score += 3
        elif status in ("Low", "High"):
            risk_score += 1

    if risk_score == 0:
        return "Low Risk"
    if risk_score <= 2:
        return "Moderate Risk"
    return "High Risk"