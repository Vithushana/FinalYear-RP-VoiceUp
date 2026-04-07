import re
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

URL_PATTERNS = [
    r"@(-?\d+\.\d+),(-?\d+\.\d+)",
    r"[?&]q=(-?\d+\.\d+),(-?\d+\.\d+)",
    r"[?&]ll=(-?\d+\.\d+),(-?\d+\.\d+)",
]

HTML_PATTERNS = [
    r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)",
    r"center=(-?\d+\.\d+)%2C(-?\d+\.\d+)",
    r"@(-?\d+\.\d+),(-?\d+\.\d+)",
]

def _extract_latlon(text: str):
    for p in URL_PATTERNS:
        m = re.search(p, text)
        if m:
            return float(m.group(1)), float(m.group(2))
    for p in HTML_PATTERNS:
        m = re.search(p, text)
        if m:
            return float(m.group(1)), float(m.group(2))
    return None

def get_lat_lon_from_maps_link(location_link: str, timeout: int = 8):
    if not location_link:
        raise ValueError("Empty location link")

    # 1) Try direct parse
    coords = _extract_latlon(location_link)
    if coords:
        return coords

    # 2) Follow redirects + parse final url/html
    r = requests.get(location_link, allow_redirects=True, timeout=timeout, headers=HEADERS)
    final_url = r.url

    coords = _extract_latlon(final_url)
    if coords:
        return coords

    coords = _extract_latlon(r.text or "")
    if coords:
        return coords

    raise ValueError("Could not extract latitude/longitude from the link")
