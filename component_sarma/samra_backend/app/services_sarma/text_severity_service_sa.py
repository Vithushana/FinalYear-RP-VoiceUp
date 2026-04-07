
def calculate_text_severity(expanded_text: str) -> dict:
    text = (expanded_text or "").lower()
    
    # ----------------------
    # URGENCY SCORE (0–15)
    # ----------------------
    urgency_high = [
        "urgent", "immediately", "danger", "accident",
        "emergency", "risk", "serious"
    ]

    urgency_medium = [
        "soon", "important", "attention", "problem"
    ]

    urgency_score = 0
    if any(word in text for word in urgency_high):
        urgency_score = 15
    elif any(word in text for word in urgency_medium):
        urgency_score = 8

    # ----------------------
    # IMPACT SCORE (0–15)
    # ----------------------
    impact_high = [
        "cannot pass", "blocked", "health risk",
        "children", "ambulance", "school", "hospital"
    ]

    impact_medium = [
        "traffic", "difficult", "inconvenience"
    ]

    impact_low = [
        "issue", "problem", "complaint"
    ]

    impact_score = 0
    if any(word in text for word in impact_high):
        impact_score = 15
    elif any(word in text for word in impact_medium):
        impact_score = 10
    elif any(word in text for word in impact_low):
        impact_score = 5

    # ----------------------
    # FREQUENCY SCORE (0–10)
    # ----------------------
    frequency_high = [
        "every day", "daily", "always",
        "repeated", "again and again", "every week"
    ]

    frequency_medium = [
        "often", "sometimes", "frequently"
    ]

    frequency_score = 0
    if any(word in text for word in frequency_high):
        frequency_score = 10
    elif any(word in text for word in frequency_medium):
        frequency_score = 6
    else:
        frequency_score = 2

    # ----------------------
    # FINAL TEXT SEVERITY
    # ----------------------
    text_severity = urgency_score + impact_score + frequency_score
    text_severity = min(text_severity, 40)

    return {
        "urgency_score": urgency_score,
        "impact_score": impact_score,
        "frequency_score": frequency_score,
        "text_severity": text_severity
    }
