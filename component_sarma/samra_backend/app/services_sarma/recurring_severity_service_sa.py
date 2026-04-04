def calculate_recurring_severity(recurring_count: int) -> dict:
    if recurring_count <= 0:
        severity = 0
        reason = "No previous reports in this location."

    elif recurring_count <= 1:
        severity = 5
        reason = "This issue has been reported once in this location."
    elif 2 <= recurring_count <= 3:
        severity = 15
        reason = "This issue has been reported multiple times in this location."
    elif 4 <= recurring_count <= 6:
        severity = 25
        reason = "This is a frequently recurring problem in this location."
    else:
        severity = 30
        reason = "This is a chronic issue reported repeatedly in this location."

    return {
        "recurring_severity": severity,
        "recurring_reason": reason
    }
