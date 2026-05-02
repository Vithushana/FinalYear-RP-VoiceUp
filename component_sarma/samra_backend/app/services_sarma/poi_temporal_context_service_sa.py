# nearby POIs edukkum
# zone/group classify pannum
# current day/time base-la activity estimate pannum
# temporal multiplier + reason return pannum

# poi_temporal_context_service_sa.py

from datetime import datetime
from zoneinfo import ZoneInfo


SL_TZ = ZoneInfo("Asia/Colombo")


def get_current_sl_datetime() -> datetime:
    return datetime.now(SL_TZ)


def get_day_type(dt: datetime) -> str:
    # Monday=0 ... Sunday=6
    return "weekend" if dt.weekday() >= 5 else "weekday"


def get_minutes(dt: datetime) -> int:
    return dt.hour * 60 + dt.minute


def in_window(now_min: int, start_h: int, start_m: int, end_h: int, end_m: int) -> bool:
    start = start_h * 60 + start_m
    end = end_h * 60 + end_m
    return start <= now_min <= end


def classify_poi_group(poi_type: str) -> str:
    t = (poi_type or "").lower()

    if "school" in t or "college" in t or "university" in t:
        return "education"
    if "hospital" in t or "clinic" in t or "pharmacy" in t:
        return "health"
    if "bus_station" in t or "station" in t or "railway" in t or "public_transport" in t:
        return "transport"
    if "marketplace" in t or "supermarket" in t or "mall" in t or "commercial" in t or "retail" in t:
        return "commercial"
    if "place_of_worship" in t:
        return "religious"
    if "police" in t or "fire_station" in t:
        return "emergency_service"

    return "other"


def get_group_weight(group: str) -> int:
    weights = {
        "education": 4,
        "health": 5,
        "transport": 4,
        "commercial": 3,
        "religious": 2,
        "emergency_service": 5,
        "other": 1,
    }
    return weights.get(group, 1)


def get_temporal_profile(group: str, dt: datetime) -> dict:
    day_type = get_day_type(dt)
    now_min = get_minutes(dt)

    # default profile
    activity_level = "medium"
    multiplier = 1.0
    reason = "Generic temporal profile applied."
    confidence = "medium"

    if group == "education":
        if day_type == "weekend":
            activity_level = "low"
            multiplier = 0.35
            reason = "Weekend: education-related movement is usually lower."
            confidence = "medium"
        else:
            if in_window(now_min, 7, 0, 8, 30) or in_window(now_min, 12, 0, 14, 0):
                activity_level = "high"
                multiplier = 1.30
                reason = "Weekday school peak period."
                confidence = "medium"
            else:
                activity_level = "medium"
                multiplier = 0.75
                reason = "Weekday but outside main school peak window."
                confidence = "medium"

    elif group == "health":
        activity_level = "high"
        multiplier = 1.20
        reason = "Healthcare locations are treated as continuously sensitive."
        confidence = "high"

    elif group == "transport":
        if in_window(now_min, 6, 30, 9, 0) or in_window(now_min, 16, 0, 19, 0):
            activity_level = "high"
            multiplier = 1.25
            reason = "Transport commute peak period."
            confidence = "medium"
        else:
            activity_level = "medium"
            multiplier = 1.00
            reason = "Transport location outside main commute peak."
            confidence = "medium"

    elif group == "commercial":
        if day_type == "weekend":
            activity_level = "medium"
            multiplier = 1.00
            reason = "Weekend commercial activity is usually moderate."
            confidence = "low"
        else:
            if in_window(now_min, 8, 0, 18, 0):
                activity_level = "medium"
                multiplier = 1.05
                reason = "Normal business-hour commercial activity."
                confidence = "low"
            else:
                activity_level = "low"
                multiplier = 0.60
                reason = "Outside common business hours."
                confidence = "low"

    elif group == "religious":
        activity_level = "low"
        multiplier = 0.80
        reason = "Religious locations are time-sensitive, but exact event timing is uncertain."
        confidence = "low"

    elif group == "emergency_service":
        activity_level = "high"
        multiplier = 1.15
        reason = "Emergency service locations are treated as continuously important."
        confidence = "high"

    else:
        activity_level = "low-medium"
        multiplier = 0.90
        reason = "No strong temporal profile available for this place type."
        confidence = "low"

    return {
        "day_type": day_type,
        "activity_level": activity_level,
        "multiplier": multiplier,
        "reason": reason,
        "confidence": confidence,
        "time_window": dt.strftime("%H:%M"),
    }


def build_temporal_context(poi_details: list) -> dict:
    """
    Input:
        poi_details = [
            {"name": "...", "type": "...", "distance": 123, ...},
            ...
        ]

    Output:
        dominant zone + temporal activity summary + enriched poi details
    """
    dt = get_current_sl_datetime()

    if not poi_details:
        return {
            "dominant_zone": "No Significant Zone",
            "secondary_zone": None,
            "activity_level_now": "low",
            "effective_zone_relevance_now": "low",
            "confidence": "low",
            "reason": "No major nearby places detected for temporal analysis.",
            "effective_temporal_multiplier": 1.0,
            "zone_breakdown": {},
            "poi_details_enriched": [],
            "current_time_context": {
                "day_type": get_day_type(dt),
                "time_window": dt.strftime("%H:%M"),
            }
        }

    zone_scores = {}
    enriched = []

    for p in poi_details:
        poi_type = str(p.get("type", ""))
        group = classify_poi_group(poi_type)
        base_weight = get_group_weight(group)
        profile = get_temporal_profile(group, dt)

        effective_weight = round(base_weight * profile["multiplier"], 2)

        zone_scores[group] = zone_scores.get(group, 0) + effective_weight

        item = dict(p)
        item["zone_group"] = group
        item["activity_level_now"] = profile["activity_level"]
        item["activity_reason"] = profile["reason"]
        item["activity_confidence"] = profile["confidence"]
        item["temporal_multiplier"] = profile["multiplier"]
        item["effective_weight_now"] = effective_weight
        enriched.append(item)

    sorted_zones = sorted(zone_scores.items(), key=lambda x: x[1], reverse=True)
    dominant_zone = sorted_zones[0][0] if sorted_zones else "other"
    secondary_zone = sorted_zones[1][0] if len(sorted_zones) > 1 else None

    dominant_score = sorted_zones[0][1] if sorted_zones else 0

    if dominant_score >= 8:
        effective_zone_relevance_now = "high"
        activity_level_now = "high"
    elif dominant_score >= 4:
        effective_zone_relevance_now = "medium"
        activity_level_now = "medium"
    else:
        effective_zone_relevance_now = "low"
        activity_level_now = "low"

    reason = f"Nearby place mix is currently dominated by the {dominant_zone} zone."
    if secondary_zone:
        reason += f" Secondary influence comes from the {secondary_zone} zone."

    return {
        "dominant_zone": dominant_zone,
        "secondary_zone": secondary_zone,
        "activity_level_now": activity_level_now,
        "effective_zone_relevance_now": effective_zone_relevance_now,
        "confidence": "medium",
        "reason": reason,
        "effective_temporal_multiplier": round(
            max([p["temporal_multiplier"] for p in enriched], default=1.0), 2
        ),
        "zone_breakdown": zone_scores,
        "poi_details_enriched": enriched,
        "current_time_context": {
            "day_type": get_day_type(dt),
            "time_window": dt.strftime("%H:%M"),
        }
    }