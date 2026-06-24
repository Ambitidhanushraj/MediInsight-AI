def generate_summary(analysis):

    normal = []
    low = []
    high = []

    for parameter, details in analysis.items():

        status = details["status"]

        if status == "Normal":
            normal.append(parameter)

        elif status == "Low":
            low.append(parameter)

        elif status == "High":
            high.append(parameter)

    summary = []

    if normal:
        summary.append(
            f"Normal parameters: {', '.join(normal)}."
        )

    if low:
        summary.append(
            f"Low parameters: {', '.join(low)}."
        )

    if high:
        summary.append(
            f"High parameters: {', '.join(high)}."
        )

    if not low and not high:
        summary.append(
            "No abnormal values detected."
        )

    return " ".join(summary)