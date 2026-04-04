def determine_priority_track(category: str, expanded_text: str, is_recurring: bool) -> dict:
    text = (expanded_text or "").lower()
    category_clean = (category or "").lower().strip()

    # --- Category-specific keywords ---
    road_planning = [
        "need new", "construct", "build", "new road", "road should be built",
        "upgrade", "widen", "permanent solution", "drainage needed",
        "reconstruction", "development",
    ]
    road_operational = [
        "pothole", "hole", "crack", "urgent repair", "danger", "accident",
        "temporary", "patch", "blocked drain", "drain blocked", "fallen tree",
        "road blocked", "repair immediately",
    ]

    garbage_planning = [
        "need more bins", "need bin", "collection point",
        "waste collection center", "future planning", "permanent solution",
    ]
    garbage_operational = [
        "not collected", "missed pickup", "overflow", "clean immediately",
        "blocked", "garbage blocks", "remove garbage", "maintenance",
        "clogged", "smell",
    ]

    # --- Decide which keyword set to use ---
    if category_clean == "road":
        planning_keywords = road_planning
        operational_keywords = road_operational
        operational_unit = "Municipal Council / PS – Engineering Works Unit"
        planning_unit = "Municipal Council – Engineering Division (Planning) / Provincial Road Unit"
        op_action = "Field inspection + patch/repair + hazard removal"
        plan_action = "Engineering inspection + budget/repair plan (long-term fix)"
    else:
        # default -> garbage
        planning_keywords = garbage_planning
        operational_keywords = garbage_operational
        operational_unit = "Municipal Council / PS – Solid Waste Management Unit"
        planning_unit = "Municipal Council – Waste Management Planning / Procurement"
        op_action = "Immediate collection + hotspot cleanup"
        plan_action = "Plan additional bins/collection point + route adjustment"

    # --- Decision Logic ---
    why = []

    if any(k in text for k in planning_keywords):
        track = "Planning"
        why.append("Planning keywords detected in complaint text.")
    elif any(k in text for k in operational_keywords):
        track = "Operational"
        why.append("Operational/maintenance keywords detected in complaint text.")
    else:
        if is_recurring:
            track = "Planning"
            why.append("Recurring issue → long-term fix recommended.")
        else:
            track = "Operational"
            why.append("No strong keywords → default operational maintenance flow.")

    # --- Attach gov-style unit + SLA ---
    if track == "Operational":
        responsible_unit = operational_unit
        suggested_action = op_action
    else:
        responsible_unit = planning_unit
        suggested_action = plan_action
    
    track_reason = " | ".join(why) if why else "Track decision generated."
    return {
        "track": track,
        "track_reason": track_reason,
        "responsible_unit": responsible_unit,
        "suggested_action": suggested_action,
        "why": why
    }