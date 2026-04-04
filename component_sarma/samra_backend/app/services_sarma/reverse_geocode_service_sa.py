import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
HEADERS = {"User-Agent": "voiceup-research/1.0 (contact: your-email)"}

def get_place_hint(lat: float, lon: float) -> str | None:
    try:
        params = {
            "format": "json",
            "lat": lat,
            "lon": lon,
            "zoom": 16,
            "addressdetails": 1
        }
        r = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        addr = data.get("address", {}) or {}

        # Local area (may be missing sometimes)
        local = addr.get("village") or addr.get("suburb") or addr.get("neighbourhood")

        # City/Town (Moratuwa)
        city = addr.get("city") or addr.get("town") or addr.get("municipality")

        # District + Province
        district = addr.get("state_district") or addr.get("county")
        province = addr.get("state") or addr.get("region")

        # Build parts in order
        parts = []
        if local:
            parts.append(local)
        if city and city not in parts:
            parts.append(city)
        if district and district not in parts:
            parts.append(district)
        if province and province not in parts:
            parts.append(province)

        # Optional: shorten "Colombo District" -> "Colombo"
        parts = [p.replace(" District", "") for p in parts]

        return " - ".join(parts) if parts else None

    except Exception:
        return None