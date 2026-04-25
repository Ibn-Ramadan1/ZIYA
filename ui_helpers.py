def get_confidence_badge(confidence):
    if confidence == "High Confidence":
        return "🟢 High Confidence"
    elif confidence == "Moderate Confidence":
        return "🟡 Moderate Confidence"
    else:
        return "🟠 Exploratory Candidate"


def get_toxicity_badge(toxicity):
    if toxicity == "High":
        return "🔴 High"
    elif toxicity == "Medium":
        return "🟡 Medium"
    else:
        return "🟢 Low"