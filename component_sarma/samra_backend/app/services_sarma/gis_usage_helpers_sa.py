from geopy.distance import geodesic

# ---POI SCORE-----------------------------
def _poi_score(lat, lon, poi_list):
    nearest = None
    score = 0

    for poi in poi_list:
        d = geodesic((lat, lon), (poi["lat"], poi["lon"])).meters
        if nearest is None or d < nearest:
            nearest = d

    if nearest:
        if nearest <= 200:
            score = 12
        elif nearest <= 500:
            score = 8
        elif nearest <= 1000:
            score = 4

    return score, {
        "nearest_poi_distance_m": round(nearest or 0, 1)
    }


# ---------ROAD IMPORTANCE-----------------------------
def _road_importance_score(road_class: str):
    mapping = {
        "motorway": 8,
        "trunk": 8,
        "primary": 6,
        "secondary": 4,
        "tertiary": 2,
        "residential": 1
    }
    return mapping.get(road_class, 2)


# ---CONNECTIVITY (BRIDGE LOGIC)-----------------------------
def _connectivity_score(alternate_routes_count: int, nearest_alt_crossing_km: float):
    if alternate_routes_count == 0:
        return 8
    if alternate_routes_count == 1:
        return 6
    if alternate_routes_count <= 3:
        return 4

    if nearest_alt_crossing_km >= 5:
        return 6
    if nearest_alt_crossing_km >= 3:
        return 4
    if nearest_alt_crossing_km >= 1:
        return 2

    return 0


# ----------CROWD USAGE PROXY-----------------------------
def _crowd_proxy_score(road_class: str, junction_density: int):
    score = 0

    if road_class in ["primary", "secondary", "trunk"]:
        score += 2

    if junction_density >= 4:
        score += 2
    elif junction_density >= 2:
        score += 1

    return min(score, 6)


# ---------COMPLAINT DENSITY-----------------------------
def _complaint_density_score(count: int):
    if count >= 10:
        return 6
    if count >= 6:
        return 4
    if count >= 3:
        return 2
    if count >= 1:
        return 1
    return 0


# --------SUMMARY (OFFICER FRIENDLY)-----------------------------
def _build_summary(poi_score, connect_score, density_score):
    if connect_score >= 6:
        return "This point is a key connector route; disruption may force long detours."
    if poi_score >= 8:
        return "Location is close to critical public facilities."
    if density_score >= 4:
        return "Multiple complaints reported near this location."
    return "No major GIS risk signals detected near this point."
