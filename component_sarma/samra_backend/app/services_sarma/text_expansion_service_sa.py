def expand_complaint_text(category: str, text: str) -> str:
    base_intro = f"This complaint is related to {category} infrastructure."

    expanded = (
        f"{base_intro} "
        f"The citizen reports the following issue: {text.strip()}. "
        "This issue affects daily public usage and requires attention from authorities. "
        "The complaint has been submitted with location details for further analysis. "
        "The system will evaluate severity, recurrence, and impact to support officer decision-making."
    )

    return expanded
