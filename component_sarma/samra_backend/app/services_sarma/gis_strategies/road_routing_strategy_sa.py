# app/services_sarma/gis_strategies/road_routing_strategy_sa.py
import requests
from geopy.distance import geodesic

POI_RADIUS_TIERS = [(200, 12), (500, 8), (1000, 4)]
TRAFFIC_WEIGHTS = {
    "railway:station": 15.0, "amenity:bus_station": 12.0, "public_transport:station": 12.0,
    "amenity:marketplace": 10.0, "amenity:hospital": 9.0, "amenity:clinic": 9.0,
    "amenity:school": 8.0, "amenity:college": 8.0, "amenity:university": 8.0,
    "amenity:place_of_worship": 6.0, "shop:supermarket": 5.0, "poi": 1.0,
}

def analyze_road_pois(latitude: float, longitude: float, poi_list: list):
    """
    Road Specific Analysis: Uses OSRM Network Distance.
    Commuter impact follows the actual road network.
    """
    user_loc = (latitude, longitude)
    scored_pois = []

    for p in poi_list:
        p_type = p.get("type", "POI")
        weight = TRAFFIC_WEIGHTS.get(p_type, 1.0)
        
        # 1. Try OSRM
        actual_dist = None
        try:
            url = f"http://router.project-osrm.org/route/v1/walking/{longitude},{latitude};{p['lon']},{p['lat']}?overview=false"
            res = requests.get(url, timeout=3).json()
            if res.get("code") == "Ok":
                actual_dist = res["routes"][0]["distance"]
        except:
            pass
            
        # 2. Fallback to Radial if OSRM fails
        if actual_dist is None:
            actual_dist = geodesic(user_loc, (p["lat"], p["lon"])).meters
            dist_type = "Road Network (Fallback to Radial)"
        else:
            dist_type = "Road Network (OSRM Walking)"

        scored_pois.append({
            "name": p.get("name", "Unknown"),
            "type": p_type,
            "distance": round(actual_dist),
            "distance_type": dist_type,
            "priority": actual_dist / weight,
            "lat": p["lat"], "lon": p["lon"]
        })

    scored_pois.sort(key=lambda x: x["priority"])
    
    seen_names = set()
    unique_major_places = []
    for p in scored_pois:
        name = (p.get("name") or "").strip().lower()
        if not name or name in seen_names: continue
        unique_major_places.append(p)
        seen_names.add(name)

    nearby_top_5 = [p for p in unique_major_places if p["distance"] <= 1500][:5]

    score = 0
    if nearby_top_5:
        closest_dist = nearby_top_5[0]["distance"]
        for radius, s in POI_RADIUS_TIERS:
            if closest_dist <= radius:
                score = s; break

    return score, nearby_top_5, []