import math
import requests
import time   
from typing import Dict, List, Tuple

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.nchc.org.tw/api/interpreter",
]
    
# Sri Lanka bounding box for safety checks
SL_BBOX = {
    "min_lat": 5.7,
    "max_lat": 9.9,
    "min_lon": 79.4,
    "max_lon": 81.9,
}

# EXPANDED: Includes markets and commercial landuse for better strategic detection
POI_TAGS = [
    'amenity~"school|college|university|hospital|clinic|pharmacy|police|fire_station|place_of_worship|bus_station|marketplace"',
    'shop~"supermarket|mall|market|department_store"',
    'landuse~"commercial|retail"',
    'railway~"station"',
    'public_transport~"station"'
]

HEADERS = {
    "User-Agent": "sarma-backend/1.0 (University Research Project; contact: your-email)"
}

def _in_sri_lanka(lat: float, lon: float) -> bool:
    return (
        SL_BBOX["min_lat"] <= lat <= SL_BBOX["max_lat"]
        and SL_BBOX["min_lon"] <= lon <= SL_BBOX["max_lon"]
    )

def _haversine_m(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    lat1, lon1 = a
    lat2, lon2 = b
    R = 6371000.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(x))

def _overpass(query: str, timeout: int = 60) -> dict:
    last_err = None
    for url in OVERPASS_URLS:
        for attempt in range(3):
            try:
                r = requests.post(
                    url,
                    data={"data": query},
                    headers=HEADERS,
                    timeout=(10, timeout),
                )
                r.raise_for_status()
                return r.json()

            except Exception as e:
                last_err = e
                print(f"Overpass failed: {url} attempt={attempt+1} err={e}")
                time.sleep(2 * (attempt + 1))
    # If all servers fail
    print(f"All Overpass servers failed. Last error: {last_err}")
    return {"elements": []}


def _pick_name(tags: dict) -> str:
    return tags.get("name") or tags.get("name:en") or tags.get("name:si") or tags.get("name:ta") or "Unknown"

def _poi_type(tags: dict) -> str:
    for key in ["amenity", "shop", "tourism", "railway", "public_transport", "landuse"]:
        if key in tags:
            return f"{key}:{tags[key]}"
    return "poi"

def fetch_osm_features(lat: float, lon: float) -> Dict:
    overpass_ok = True
    nearest_alt_crossing_km = 99.0

    

    # 1. Location Validation
    if not _in_sri_lanka(lat, lon):
        return {
            "poi_list": [],
            "road_class": "unknown",
            "junction_density": 0,
            "alternate_routes_count": 0,
            "nearest_alt_crossing_km": 99.0, # Consistent research default
            "overpass_ok": False,
            "meta": {"note": "Outside Sri Lanka; OSM fetch skipped"}
        }

    # 2. Initialize research variables
    poi_list: List[dict] = []
    road_class = "unknown"
    junction_density = 0
    alternate_routes_count = 0
    nearest_alt_crossing_km = 99.0 # FIXED: Prevents 0.0km isolation bug
    unique_road_names = set()

    # 3. RESEARCH OPTIMIZATION: Combined Query to prevent 500 errors
    combined_query = f"""
    [out:json][timeout:35];
    (
      nwr["amenity"~"school|college|university|hospital|marketplace|bus_station"](around:2000,{lat},{lon});
      nwr["shop"~"market|supermarket|mall"](around:2000,{lat},{lon});
      nwr["landuse"~"commercial|retail"](around:2000,{lat},{lon});
      way["highway"](around:1200,{lat},{lon});
      nwr["bridge"](around:4000,{lat},{lon});
      node["highway"="crossing"](around:4000,{lat},{lon});
      node(around:400,{lat},{lon})["highway"~"junction|traffic_signals"];
    );
    out center tags;
    """

    try:
        data = _overpass(combined_query)
        elements = data.get("elements", [])
        
        best_road_dist = None
        best_bridge_dist = None

        best_bridge_lat = None
        best_bridge_lon = None
        best_bridge_name = None

        for el in elements:
            tags = el.get("tags", {})
            e_lat = el.get("lat") or (el.get("center") or {}).get("lat")
            e_lon = el.get("lon") or (el.get("center") or {}).get("lon")
            if e_lat is None: continue
            
            dist_m = _haversine_m((lat, lon), (e_lat, e_lon))

            # A. Strategic Landmark Extraction
            if any(k in tags for k in ["amenity", "shop", "landuse", "railway", "public_transport"]):
                poi_list.append({
                    "name": _pick_name(tags),
                    "type": _poi_type(tags),
                    "lat": float(e_lat), 
                    "lon": float(e_lon), 
                    "distance_m": round(dist_m, 1)
                })

            # B. Road Classification
            if "highway" in tags and tags["highway"] not in ["bridge", "crossing", "junction", "traffic_signals"]:
                if best_road_dist is None or dist_m < best_road_dist:
                    best_road_dist = dist_m
                    road_class = tags["highway"]

            # C. Junction Density (Proxy for traffic congestion)
            if tags.get("highway") in ["junction", "traffic_signals"]:
                junction_density += 1

            # D. Connectivity Analysis (Bridges/Crossings)
            if "bridge" in tags or tags.get("highway") == "crossing":
                name = tags.get("name")
                if name: unique_road_names.add(name)
                if best_bridge_dist is None or dist_m < best_bridge_dist:
                    best_bridge_dist = dist_m
                    best_bridge_lat = float(e_lat)
                    best_bridge_lon = float(e_lon)
                    best_bridge_name = tags.get("name")

        # E. Final Data Processing
        poi_list.sort(key=lambda x: x["distance_m"])
        print("DEBUG lat/lon:", lat, lon)
        print("DEBUG POI count:", len(poi_list))
        if poi_list[:3]:
            print("DEBUG sample POIs:", poi_list[:3])

        alternate_routes_count = len(unique_road_names)
        if best_bridge_dist and best_bridge_dist > 50:
            nearest_alt_crossing_km = round(best_bridge_dist / 1000, 2)
        else:
            # Stay at 99.0 if no real alternate is found
            nearest_alt_crossing_km = 99.0
        
    except Exception as e:
        print(f"OSM Combined Fetch Error: {e}")
        overpass_ok = False

    return {
        "poi_list": poi_list[:15], # Top 15 for hybrid score validation
        "road_class": road_class,
        "junction_density": junction_density,
        "alternate_routes_count": alternate_routes_count,
        "nearest_alt_crossing_km": nearest_alt_crossing_km,
        "nearest_alt_point_lat": best_bridge_lat,
        "nearest_alt_point_lon": best_bridge_lon,
        "nearest_alt_point_name": best_bridge_name,
        "overpass_ok": overpass_ok,
        "meta": {"source": "OSM/Overpass Combined"}
    }