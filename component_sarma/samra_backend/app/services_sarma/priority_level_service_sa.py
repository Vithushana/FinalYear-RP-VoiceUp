
def determine_priority_level(priority_score: int) -> dict:
    """
    Converts priority score (0–100) into Priority Level (1 / 2 / 3)
    """

    if priority_score >= 70:
        level = 1
        label = "High Priority"
    elif priority_score >= 40:
        level = 2
        label = "Medium Priority"
    else:
        level = 3
        label = "Low Priority"

    return {
        "priority_level": level,
        "priority_label": label
    }
