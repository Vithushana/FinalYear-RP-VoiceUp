# app/services_sarma/gis_usage_service_sa.py

from app.services_sarma.poi_temporal_context_service_sa import build_temporal_context
from app.services_sarma.gis_strategies.road_routing_strategy_sa import analyze_road_pois
from app.services_sarma.gis_strategies.garbage_radial_strategy_sa import analyze_garbage_pois

MAX_GIS_SCORE = 30
ROAD_CLASS_WEIGHTS = {"primary": 10, "secondary": 7, "tertiary": 5, "residential": 2, "service": 1, "unknown": 2}

def calculate_hybrid_gis_score(
    latitude: float,
    longitude: float,
    poi_list: list,
    road_class: str,
    alternate_routes_count: int,
    nearest_alt_crossing_km: float,
    junction_density: int,
    nearby_complaint_count: int,
    category: str, 
    expanded_text: str = ""
) -> dict:

    # 1. DELEGATE TO STRATEGY FILES BASED ON CATEGORY
    if category.lower() == "road":
        poi_score, poi_info, poi_reasons = analyze_road_pois(latitude, longitude, poi_list)
    else:
        poi_score, poi_info, poi_reasons = analyze_garbage_pois(latitude, longitude, poi_list)
    
    # 2. TEMPORAL CONTEXT FIX
    temporal_context = build_temporal_context(poi_info)
    temporal_multiplier = temporal_context.get("effective_temporal_multiplier", 1.0)
    adjusted_poi_score = int(round(poi_score * temporal_multiplier))

    # 3. OTHER CORE CONCEPTS
    road_score, road_reason = _road_importance_score(road_class)
    connect_score, connect_reason = _connectivity_score(alternate_routes_count, nearest_alt_crossing_km)
    crowd_score, crowd_reason = _crowd_proxy_score(road_class, junction_density)
    density_score, density_reason = _complaint_density_score(nearby_complaint_count)

    total = adjusted_poi_score + road_score + connect_score + crowd_score + density_score
    total = min(total, MAX_GIS_SCORE)

    reasons = []
    reasons.extend(poi_reasons)
    if road_reason: reasons.append(road_reason)
    if connect_reason: reasons.append(connect_reason)
    if crowd_reason: reasons.append(crowd_reason)
    if density_reason: reasons.append(density_reason)

    poi_details_enriched = temporal_context.get("poi_details_enriched", poi_info)
    summary_text = _build_summary(poi_info, alternate_routes_count, nearest_alt_crossing_km)
    professional_reasons = _build_professional_reasons(poi_info)

    if poi_details_enriched:
        landmark_evidence = ", ".join([f"{p.get('name', 'Unknown')} ({p.get('distance', '?')}m, {p.get('activity_level_now', 'unknown')} now)" for p in poi_details_enriched])
    else:
        landmark_evidence = "None"

    temporal_summary = f"Current area context: {temporal_context.get('dominant_zone', 'Unknown Zone')} | Activity now: {temporal_context.get('activity_level_now', 'unknown')} | Reason: {temporal_context.get('reason', 'No temporal explanation available.')}"
    
    full_gis_summary = (
        (" ".join(professional_reasons) if professional_reasons else summary_text)
        + f" | {summary_text} | {temporal_summary} | Impacted Landmarks: {landmark_evidence}."
    )

    return {
        "gis_score": total,
        "gis_summary": full_gis_summary,
        "gis_reasons": reasons,
        "temporal_context": {
            "dominant_zone": temporal_context.get("dominant_zone"),
            "secondary_zone": temporal_context.get("secondary_zone"),
            "activity_level_now": temporal_context.get("activity_level_now"),
            "effective_zone_relevance_now": temporal_context.get("effective_zone_relevance_now"),
            "confidence": temporal_context.get("confidence"),
            "reason": temporal_context.get("reason"),
            "effective_temporal_multiplier": temporal_multiplier,
            "zone_breakdown": temporal_context.get("zone_breakdown", {}),
            "current_time_context": temporal_context.get("current_time_context", {}),
        },
        "gis_breakdown": {
            "poi_score": adjusted_poi_score,
            "road_score": road_score,
            "connectivity_score": connect_score,
            "crowd_score": crowd_score,
            "complaint_density_score": density_score,
            "why_this_priority": professional_reasons,
            "poi_details": poi_details_enriched,
            "road_class": road_class,
            "alternate_routes_count": alternate_routes_count,
            "nearest_alt_crossing_km": nearest_alt_crossing_km,
            "junction_density": junction_density,
            "nearby_complaint_count": nearby_complaint_count,
        }
    }

# -----------------------------
# HELPERS (Remaining code)
# -----------------------------
def _build_professional_reasons(nearby_top_5: list):
    reasons = []
    if not nearby_top_5: return ["No major high-traffic landmarks detected within the primary impact zone."]
    primary = nearby_top_5[0]
    p_type = primary.get("type", "POI")
    p_name = primary.get("name", "Unknown")

    if "railway:station" in p_type or "bus_station" in p_type: reasons.append(f"CRITICAL TRANSIT IMPACT: Incident is located near {p_name}, a major transportation hub. Road failure may disrupt commuter flow and public transit access.")
    elif "school" in p_type or "university" in p_type or "college" in p_type: reasons.append(f"PUBLIC SAFETY RISK: Proximity to {p_name} increases potential exposure to students and pedestrians.")
    elif "hospital" in p_type or "clinic" in p_type: reasons.append(f"EMERGENCY ACCESS ALERT: Proximity to {p_name} detected. Maintaining road integrity is important for emergency access.")
    else: reasons.append(f"STRATEGIC IMPACT: Landmark {p_name} ({p_type}) indicates an active public-use area.")
    return reasons

def _road_importance_score(road_class: str):
    rc = (road_class or "unknown").lower().strip()
    score = ROAD_CLASS_WEIGHTS.get(rc, ROAD_CLASS_WEIGHTS["unknown"])
    reason = f"Road type is {rc}, usually associated with higher public movement." if rc in ["primary", "secondary"] else (f"Road type is {rc}, usually associated with lower public movement." if rc in ["residential", "service"] else None)
    return score, reason

def _connectivity_score(alternate_routes_count: int, nearest_alt_crossing_km: float):
    alt = max(alternate_routes_count or 0, 0)
    dist = nearest_alt_crossing_km if (nearest_alt_crossing_km and nearest_alt_crossing_km > 0) else 99.0
    score, reason = 0, ""
    if alt == 0: score += 6; reason = "No alternate routes detected nearby (connectivity risk high)."
    elif alt <= 2: score += 3; reason = "Few alternate routes available nearby."
    else: score += 1
    if dist >= 2: score += 4; reason = (reason + " Nearest alternate crossing is far or not detected.").strip()
    elif dist >= 1: score += 2
    return min(score, 10), (reason.strip() if reason else None)

def _crowd_proxy_score(road_class: str, junction_density: int):
    rc = (road_class or "unknown").lower().strip()
    jd = max(junction_density or 0, 0)
    score = 0
    if rc in ["primary", "secondary"]: score += 5
    elif rc in ["tertiary"]: score += 3
    else: score += 1
    if jd >= 10: score += 5
    elif jd >= 5: score += 3
    elif jd >= 2: score += 1
    score = min(score, 8)
    return score, "Junction density suggests this area is a connector route." if score >= 6 else None

def _complaint_density_score(nearby_complaint_count: int):
    c = max(nearby_complaint_count or 0, 0)
    if c >= 10: return 6, "High complaint density in this area."
    if c >= 5: return 4, "Moderate complaint density in this area."
    if c >= 2: return 2, "Some similar complaints nearby."
    return 0, None

def _build_summary(poi_info: list, alternate_routes_count: int, nearest_alt_crossing_km: float):
    parts = []
    if poi_info: parts.append("Major nearby places: " + ", ".join([f"{p.get('name', 'Unknown')} ({p.get('distance_m', p.get('distance', '?'))}m)" for p in poi_info]))
    alt = max(alternate_routes_count or 0, 0)
    parts.append("No alternate routes detected nearby" if alt == 0 else f"Alternate routes: {alt}")
    if nearest_alt_crossing_km is not None: parts.append(f"Nearest alternate crossing: {nearest_alt_crossing_km} km")
    return ". ".join(parts) if parts else "No significant GIS signals detected."