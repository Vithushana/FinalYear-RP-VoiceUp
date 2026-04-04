# GIS score is hybrid because it combines multiple spatial factors, not a single rule.
from geopy.distance import geodesic

# CONFIG
# -----------------------------
MAX_GIS_SCORE = 30

# POI (point of interest) scoring tiers: within radius -> score
POI_RADIUS_TIERS = [
    (200, 12),
    (500, 8),
    (1000, 4),
]

ROAD_CLASS_WEIGHTS = {
    "primary": 10,
    "secondary": 7,
    "tertiary": 5,
    "residential": 2,
    "service": 1,
    "unknown": 2,
}

# REASONS GENERATION
# -----------------------------
def _build_professional_reasons(nearby_top_5: list):
    """Generates analytical justifications for the Officer View."""
    reasons = []
    if not nearby_top_5:
        return ["No major high-traffic landmarks detected within the primary impact zone."]

    primary = nearby_top_5[0]
    p_type = primary.get('type', 'POI')
    p_name = primary.get('name', 'Unknown')

    # Professional English Templates for Research Paper Standard
    if "railway:station" in p_type or "bus_station" in p_type:
        reasons.append(f"CRITICAL TRANSIT IMPACT: Incident is located near {p_name}, a major transportation hub. Road failure disrupts commuter flow and public transit access.")
    elif "school" in p_type or "university" in p_type:
        reasons.append(f"PUBLIC SAFETY RISK: Proximity to {p_name} increases vulnerability for students and high pedestrian traffic peaks.")
    elif "hospital" in p_type:
        reasons.append(f"EMERGENCY ACCESS ALERT: Proximity to {p_name} detected. Maintaining road integrity is vital for ambulance access.")
    else:
        reasons.append(f"STRATEGIC IMPACT: Landmark {p_name} ({p_type}) detected, indicating a high-activity urban zone.")

    return reasons



# MAIN ENTRY
# -----------------------------
def calculate_hybrid_gis_score(
    latitude: float,
    longitude: float,
    poi_list: list,
    road_class: str,
    alternate_routes_count: int,
    nearest_alt_crossing_km: float,
    junction_density: int,
    nearby_complaint_count: int,
    expanded_text: str = ""
) -> dict:
    # Use underscores consistently for internal helper calls
    poi_score, poi_info, poi_reasons = _poi_score(latitude, longitude, poi_list)
    road_score, road_reason = _road_importance_score(road_class)
    connect_score, connect_reason = _connectivity_score(
        alternate_routes_count,
        nearest_alt_crossing_km
    )
    crowd_score, crowd_reason = _crowd_proxy_score(road_class, junction_density)
    density_score, density_reason = _complaint_density_score(nearby_complaint_count)

    total = poi_score + road_score + connect_score + crowd_score + density_score
    total = min(total, MAX_GIS_SCORE)

    text_content = expanded_text.lower()

    # Reasons list for officer explanation
    reasons = []
    reasons.extend(poi_reasons)
    if road_reason:
        reasons.append(road_reason)
    if connect_reason:
        reasons.append(connect_reason)
    if crowd_reason:
        reasons.append(crowd_reason)
    if density_reason:
        reasons.append(density_reason)

    # Build a human-readable summary and professional reasons once
    summary_text = _build_summary(poi_info, alternate_routes_count, nearest_alt_crossing_km)
    professional_reasons = _build_professional_reasons(poi_info)

    # Build the detailed evidence string safely
    if poi_info:
        landmark_evidence = ", ".join([f"{p.get('name','Unknown')} ({p.get('distance','?')}m)" for p in poi_info])
    else:
        landmark_evidence = "None"

    # Final summary combining professional rationale and the summary/evidence
    full_gis_summary = (
        (" ".join(professional_reasons) if professional_reasons else summary_text)
        + f" | {summary_text} | Impacted Landmarks: {landmark_evidence}."
    )

    return {
        "gis_score": total,
        "gis_summary": full_gis_summary,
        "gis_reasons": reasons,
        "gis_breakdown": {
            "poi_score": poi_score,
            "road_score": road_score,
            "connectivity_score": connect_score,
            "crowd_score": crowd_score,
            "complaint_density_score": density_score,
            "why_this_priority": professional_reasons,
            "poi_details": poi_info,
            "road_class": road_class,
            "alternate_routes_count": alternate_routes_count,
            "nearest_alt_crossing_km": nearest_alt_crossing_km,
            "junction_density": junction_density,
            "nearby_complaint_count": nearby_complaint_count,
        }
    }

# HELPERS
# -----------------------------
def _poi_score(latitude: float, longitude: float, poi_list: list):
    user_loc = (latitude, longitude)
    
    # Define Traffic Scores for Analysis
    TRAFFIC_WEIGHTS = {
        "railway:station": 15.0,
        "amenity:bus_station": 12.0,
        "public_transport:station": 12.0,
        "amenity:marketplace": 10.0,
        "amenity:hospital": 9.0,
        "amenity:school": 8.0,
        "amenity:university": 8.0,
        "amenity:place_of_worship": 6.0,
        "shop:supermarket": 5.0,
        "poi": 1.0,
    }

    # 1. FIND AND SCORE PLACES
    scored_pois = []
    for p in poi_list:
        d = geodesic(user_loc, (p["lat"], p["lon"])).meters
        p_type = p.get("type", "POI")
        weight = TRAFFIC_WEIGHTS.get(p_type, 1.0)
        
        # Traffic Analysis: Priority = Distance / Weight
        traffic_priority = d / weight 
        
        scored_pois.append({
            "name": p.get("name", "Unknown"),
            "type": p_type,
            "distance": round(d),
            "priority": traffic_priority
        })

    # 2. ANALYZE AND SORT BY TRAFFIC IMPACT
    scored_pois.sort(key=lambda x: x["priority"])
    
    # 3. FILTER FIVE MAJOR PLACES
    seen_names = set()
    unique_major_places = []
    for p in scored_pois:
        # Use the full normalized name to group identical POIs and avoid
        # accidental grouping by the first word (which merges unrelated places).
        name = (p.get('name') or '').strip().lower()
        if not name:
            continue
        if name not in seen_names:
            unique_major_places.append(p)
            seen_names.add(name)

    # Output the top 5 major places based on analysis and within 1500m
    nearby_top_5 = [p for p in unique_major_places if p["distance"] <= 1500][:5]

    # Calculate GIS Score based on the primary major place found
    score = 0
    if nearby_top_5:
        closest_dist = nearby_top_5[0]["distance"]
        for radius, s in POI_RADIUS_TIERS:
            if closest_dist <= radius:
                score = s
                break

    return score, nearby_top_5, []

def _road_importance_score(road_class: str):
    """Calculates score based on road type"""
    rc = (road_class or "unknown").lower().strip()
    score = ROAD_CLASS_WEIGHTS.get(rc, ROAD_CLASS_WEIGHTS["unknown"])
    reason = None
    if rc in ["primary", "secondary"]:
        reason = f"Road type is {rc}, usually higher traffic."
    elif rc in ["residential", "service"]:
        reason = f"Road type is {rc}, usually lower traffic."
    return score, reason

def _connectivity_score(alternate_routes_count: int, nearest_alt_crossing_km: float):
    alt = max(alternate_routes_count or 0, 0)
    
    dist = nearest_alt_crossing_km if (nearest_alt_crossing_km and nearest_alt_crossing_km > 0) else 99.0
    score = 0
    reason = ""
    #    1. Score based on number of alternate routes (alt)
    if alt == 0:
        score += 6
        reason = "No alternate routes detected nearby (connectivity risk high)."
    elif alt <= 2:
        score += 3
        reason = "Few alternate routes available nearby."
    else:
        score += 1

    # 2. Score based on distance (dist)
    if dist >= 2:
        score += 4
        reason = (reason or "") + " Nearest alternate crossing is far or not detected."
    elif dist >= 1:
        score += 2

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
    reason = "Junction density suggests this area is a connector route." if score >= 6 else None
    return score, reason

def _complaint_density_score(nearby_complaint_count: int):
    c = max(nearby_complaint_count or 0, 0)
    if c >= 10: return 6, "High complaint density in this area."
    if c >= 5: return 4, "Moderate complaint density in this area."
    if c >= 2: return 2, "Some similar complaints nearby."
    return 0, None

def _build_summary(poi_info: list, alternate_routes_count: int, nearest_alt_crossing_km: float):
    parts = []
    if poi_info:
        place_strings = [f"{p.get('name','Unknown')} ({p.get('distance_m', p.get('distance', '?'))}m)" for p in poi_info]
        parts.append("Major high-traffic places: " + ", ".join(place_strings))
    alt = max(alternate_routes_count or 0, 0)
    parts.append(f"No alternate routes detected nearby" if alt == 0 else f"Alternate routes: {alt}")
    if nearest_alt_crossing_km is not None:
        parts.append(f"Nearest alternate crossing: {nearest_alt_crossing_km} km")
    return ". ".join(parts) if parts else "No significant GIS signals detected."