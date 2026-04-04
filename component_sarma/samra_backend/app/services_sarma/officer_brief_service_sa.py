def build_officer_brief(category: str, expanded_text: str, track: str, recurring_count: int, poi_details: list) -> dict:
    cat = (category or "").lower().strip()
    text = (expanded_text or "").strip()

    # Situation (short excerpt)
    words = text.split()
    situation = " ".join(words[:18]) + ("..." if len(words) > 18 else "")
    if not situation:
        situation = "Citizen reported an issue that needs review."

    # Likely impact (non-technical tags)
    impact = []
    t = (expanded_text or "").lower()

    if cat == "garbage":
        impact.append("Public health & hygiene")
        if any(w in t for w in ["smell", "odor", "mosquito", "flies", "overflow", "dump"]):
            impact.append("Community nuisance")
    elif cat == "road":
        impact.append("Public safety")
        if any(w in t for w in ["accident", "danger", "risk", "pothole", "hole", "crack"]):
            impact.append("Travel disruption")
    else:
        impact.append("Service delivery impact")

    # POI hint -> still no tech words
    if poi_details:
        ptype = (poi_details[0].get("type") or "").lower()
        if "school" in ptype:
            impact.append("Sensitive area (school zone)")
        elif "hospital" in ptype:
            impact.append("Sensitive area (medical access)")
        elif "bus_station" in ptype or "station" in ptype:
            impact.append("High public movement area")

    # remove duplicates
    cleaned = []
    for x in impact:
        if x not in cleaned:
            cleaned.append(x)

    # Handling note
    if track == "Planning":
        handling_note = "May need planned intervention beyond routine field work."
    else:
        handling_note = "Routine field response is likely sufficient."

    # Officer check list
    checks = ["Confirm the location pin is correct on the map."]
    if recurring_count and recurring_count > 1:
        checks.append(f"Check earlier reports nearby (reported {recurring_count} times).")
    else:
        checks.append("Check if similar reports exist nearby.")

    if cat == "road":
        checks.append("Check if the issue creates a safety hazard or blocks access.")
        checks.append("Consider temporary safety measures if needed.")
    elif cat == "garbage":
        checks.append("Check whether collection was missed or delayed.")
        checks.append("Check if the issue affects nearby homes/shops or public areas.")
    else:
        checks.append("Confirm the affected service area and any immediate risk.")

    return {
        "situation": situation,
        "likely_impact": cleaned[:3],
        "handling_note": handling_note,
        "officer_check": checks[:4],
    }