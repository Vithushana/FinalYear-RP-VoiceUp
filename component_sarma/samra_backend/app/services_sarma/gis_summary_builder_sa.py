def build_gis_summary(osm_data: dict) -> str:
    if not osm_data.get("overpass_ok", True):
        return "OSM data unavailable right now. Using fallback GIS values."

    poi_list = osm_data.get("poi_list", [])
    road_class = osm_data.get("road_class", "unknown")
    junction_density = osm_data.get("junction_density", 0)
    alt_count = osm_data.get("alternate_routes_count", 0)
    nearest_km = osm_data.get("nearest_alt_crossing_km", 0.0)

    # New logic to list multiple places with their distances
    if poi_list:
        # Create a string like: "St. Joseph's College (146m), Hospital (450m), etc."
        place_strings = [f"{p['name']} ({p.get('distance_m', p.get('distance', '?'))}m)" for p in poi_list]
        poi_part = "Nearby critical places: " + ", ".join(place_strings) + "."
    else:
        poi_part = "No major mapped public places found nearby."

    # Road summary
    road_part = f"Nearest road type: {road_class}."

    # Junction summary
    if junction_density >= 8:
        j_part = "High junction density suggests busy/connected area."
    elif junction_density >= 3:
        j_part = "Moderate junction density."
    else:
        j_part = "Low junction density (less connected/remote area)."

    # Bridge / crossing summary
    if alt_count == 0:
        alt_part = "No alternate crossings/bridges detected within 3km."
    else:
        alt_part = f"{alt_count} crossings/bridges detected nearby; nearest is ~{nearest_km} km."

    return f"{poi_part} {road_part} {j_part} {alt_part}"
