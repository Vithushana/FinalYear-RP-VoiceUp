#The system explains why a priority is assigned, not just the score.

from app.services_sarma.text_severity_service_sa import calculate_text_severity
from app.services_sarma.gis_usage_service_sa import calculate_hybrid_gis_score
from app.services_sarma.recurring_severity_service_sa import calculate_recurring_severity
from app.services_sarma.priority_scoring_service_sa import calculate_priority_score
from app.services_sarma.priority_level_service_sa import determine_priority_level
from app.services_sarma.track_decision_service_sa import determine_priority_track

from app.services_sarma.reverse_geocode_service_sa import get_place_hint
from app.services_sarma.officer_brief_service_sa import build_officer_brief


def build_officer_output(
    complaint_id: int,
    category: str,
    expanded_text: str,
    latitude: float,
    longitude: float,
    location_link: str | None,

    recurring_count: int,
    is_recurring: bool,

    poi_list: list,
    road_class: str,
    alternate_routes_count: int,
    nearest_alt_crossing_km: float,
    junction_density: int,
    nearby_complaint_count: int,

    ml_result: dict
) -> dict:

    # 1) Text severity
    text_scores = calculate_text_severity(expanded_text)

    # 2) Hybrid GIS
    gis_result = calculate_hybrid_gis_score(
        latitude=latitude,
        longitude=longitude,
        poi_list=poi_list,
        road_class=road_class,
        alternate_routes_count=alternate_routes_count,
        nearest_alt_crossing_km=nearest_alt_crossing_km,
        junction_density=junction_density,
        nearby_complaint_count=nearby_complaint_count,
        expanded_text=expanded_text
    )
    gis_breakdown = gis_result.get("gis_breakdown", {}) or {}
    poi_details = gis_breakdown.get("poi_details", []) or []
    gis_score = int(gis_result.get("gis_score", 0))

    # 3) Recurring severity
    recurring_scores = calculate_recurring_severity(recurring_count)

    # 4) Final priority score
    score_result = calculate_priority_score(
        text_severity=text_scores["text_severity"],
        gis_severity=gis_score,
        recurring_severity=recurring_scores["recurring_severity"]
    )

    # 5) Priority level
    level_result = determine_priority_level(score_result["priority_score"])

    # 6) Track
    track_result = determine_priority_track(category, expanded_text, is_recurring)

    # 7) Action time
    if level_result["priority_level"] == 1:
        action_time = "Immediate (0–24 hours)"
        risk_category = "Critical"
    elif level_result["priority_level"] == 2:
        action_time = "Soon (1–3 days)"
        risk_category = "Moderate"
    else:
        action_time = "Planned (within 1–2 weeks)"
        risk_category = "Low"

    # 8) Why list (short)
    why_list = []
    if text_scores.get("urgency_score", 0) >= 15:
        why_list.append("Text indicates high urgency.")
    if text_scores.get("impact_score", 0) >= 15:
        why_list.append("Text indicates high public impact.")
    if text_scores.get("frequency_score", 0) >= 10:
        why_list.append("Text indicates the issue is frequent or recurring.")

    # Include GIS analysis in structured `gis` object only; avoid duplicating the
    # full summary in the short 'why' list presented at the top-level.
    # If a short note is useful, add a concise entry instead.
    if gis_result.get("gis_score", 0) > 0:
        why_list.append(f"GIS impact detected (score: {int(gis_result.get('gis_score',0))}).")
    why_list.append(recurring_scores.get("recurring_reason", "Recurring analysis completed."))

    # 9) AI note
    conf = float(ml_result.get("confidence", 0))
    note = "AI is supporting info only. Final decision is based on Hybrid score (Text + GIS + Recurring)."
    if conf < 0.70:
        note = "AI confidence is moderate/low. Final decision is based on Hybrid score (Text + GIS + Recurring)."

    # 10) Place hint    
    place_hint = get_place_hint(latitude, longitude)

    if not place_hint and poi_details:
        place_hint = f"Near {poi_details[0].get('name','')}".strip() or None
    
    officer_brief = build_officer_brief(
        category=category,
        expanded_text=expanded_text,
        track=track_result.get("track", ""),
        recurring_count=recurring_count,
        poi_details=poi_details,
    )

    #  Clean structured output
    return {
        "summary": {
            "complaint_id": complaint_id,
            "category": category,
            "priority_level": level_result["priority_level"],
            "priority_label": level_result["priority_label"],
            "priority_score": score_result["priority_score"],
            "risk_category": risk_category,
            "recommended_action_time": action_time
        },

        "complaint": {
            "expanded_text": expanded_text
        },

        "location": {
            "place_hint": place_hint,
            "latitude": latitude,
            "longitude": longitude,
            "location_link": location_link
        },

        "why_this_priority": why_list,

        "officer_brief": officer_brief,

        "gis": {
            "gis_score": gis_score,
            "gis_summary": gis_result.get("gis_summary", ""),

            "officer_display_summary": (
                (gis_result.get("gis_summary", "") or "").split("|")[0].strip()
                or "GIS context processed."
            ),
            "details_for_popup": {
                "poi_score": gis_breakdown.get("poi_score", 0),
                "road_score": gis_breakdown.get("road_score", 0),
                "connectivity_score": gis_breakdown.get("connectivity_score", 0),
                "crowd_score": gis_breakdown.get("crowd_score", 0),
                "complaint_density_score": gis_breakdown.get("complaint_density_score", 0),
            },

            "poi_details": poi_details,

            "alternate_routes_count": alternate_routes_count,
            "nearest_alt_crossing_km": nearest_alt_crossing_km,
            "junction_density": junction_density,
        },

        "recurring": {
            "recurring_count": recurring_count,
            "is_recurring": is_recurring,
            "recurring_reason": recurring_scores.get("recurring_reason", "")
        },

        "ai_suggestion": {
            "priority_level_ml": ml_result.get("priority_level_ml"),
            "confidence": conf,
            "note": note
        },

        "track": {
            "track": track_result["track"],
            "reason": track_result["track_reason"],
            "responsible_unit": track_result.get("responsible_unit"),
            "suggested_action": track_result.get("suggested_action"),
            "why": track_result.get("why", []),
        }
    }
