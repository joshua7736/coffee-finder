"""Provider implementations: Google Places (optional) and OpenStreetMap Overpass fallback."""
from typing import List, Dict, Optional
import os
import requests

from .utils import haversine_distance
from .cache import cache_get, cache_set
from .config import get_cache_ttl, get_google_api_key


def _distance_from(center_lat, center_lng, lat, lng) -> float:
    return haversine_distance(center_lat, center_lng, lat, lng)


def search_overpass(lat: float, lng: float, radius: int = 1000, limit: int = 20) -> List[Dict]:
    """Search Overpass API for cafes/coffee shops near the point.

    Returns list of dicts: name, lat, lng, address, distance_m, source
    """
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    # query nodes and ways with amenity=cafe or shop=coffee
    q = f"""
[out:json][timeout:25];
(
  node(around:{radius},{lat},{lng})[amenity=cafe];
  node(around:{radius},{lat},{lng})[shop=coffee];
  way(around:{radius},{lat},{lng})[amenity=cafe];
  way(around:{radius},{lat},{lng})[shop=coffee];
);
out center {limit};
"""
    # check cache first (respect configured TTL)
    cache_key = f"overpass:{lat:.6f}:{lng:.6f}:{radius}"
    cached = cache_get(cache_key, max_age_seconds=get_cache_ttl())
    if cached:
        return cached[:limit]

    r = requests.post(OVERPASS_URL, data={"data": q.strip() }, timeout=30)
    r.raise_for_status()
    data = r.json()
    results = []
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("brand")
        if not name:
            continue
        # node has lat/lon, way has center
        if el.get("type") == "node":
            el_lat = el.get("lat")
            el_lon = el.get("lon")
        else:
            center = el.get("center") or {}
            el_lat = center.get("lat")
            el_lon = center.get("lon")
        address_parts = []
        for k in ("addr:housenumber","addr:street","addr:city","addr:postcode","addr:country"):
            if tags.get(k):
                address_parts.append(tags.get(k))
        address = ", ".join(address_parts) if address_parts else tags.get("addr:full") or ""
        dist = _distance_from(lat, lng, el_lat, el_lon) if el_lat and el_lon else None
        results.append({
            "name": name,
            "lat": el_lat,
            "lng": el_lon,
            "address": address,
            "distance_m": dist,
            "rating": None,
            "source": "overpass",
        })
    # sort by distance
    results = [r for r in results if r.get("distance_m") is not None]
    results.sort(key=lambda x: x["distance_m"])
    # store in cache
    try:
        cache_set(cache_key, results)
    except Exception:
        pass
    return results[:limit]


def search_google_places(api_key: str, lat: float, lng: float, radius: int = 1000, limit: int = 20) -> List[Dict]:
    """Search Google Places Nearby Search for coffee/cafe. Requires API key."""
    URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "keyword": "coffee",
        "type": "cafe",
        "key": api_key,
    }
    results = []
    next_page = None
    while True:
        resp = requests.get(URL, params=params, timeout=10)
        resp.raise_for_status()
        j = resp.json()
        for p in j.get("results", []):
            name = p.get("name")
            loc = p.get("geometry", {}).get("location", {})
            plat = loc.get("lat")
            plng = loc.get("lng")
            rating = p.get("rating")
            vicinity = p.get("vicinity") or p.get("formatted_address")
            dist = _distance_from(lat, lng, plat, plng) if plat and plng else None
            results.append({
                "name": name,
                "lat": plat,
                "lng": plng,
                "address": vicinity,
                "distance_m": dist,
                "rating": rating,
                "source": "google",
            })
            if len(results) >= limit:
                return results[:limit]
        # paging
        next_page = j.get("next_page_token")
        if not next_page:
            break
        params = {"pagetoken": next_page, "key": api_key}
    return results[:limit]


def choose_provider(lat: float, lng: float, radius: int = 1000, limit: int = 20, min_rating: Optional[float] = None) -> List[Dict]:
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY") or get_google_api_key()
    if api_key:
        try:
            res = search_google_places(api_key, lat, lng, radius=radius, limit=limit)
            if res:
                return res
        except Exception:
            pass
    # fallback to overpass
    return search_overpass(lat, lng, radius=radius, limit=limit)
