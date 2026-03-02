import math
from typing import Tuple
import requests


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in meters between two lat/lon points using haversine."""
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def parse_latlng(value: str) -> Tuple[float, float]:
    """Parse a 'lat,lon' string into floats."""
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != 2:
        raise ValueError("Expected 'lat,lon' format")
    return float(parts[0]), float(parts[1])


def parse_what3words(value: str) -> Tuple[float, float]:
    """Parse a what3words location (e.g., '///light.dog.cat') and return (lat, lng).
    
    Uses the free what3words API (limited to 60 requests/minute without API key).
    """
    # normalize input: remove leading /// if present
    words = value.lstrip('/').strip()
    if not words:
        raise ValueError("Invalid what3words format")
    
    try:
        # Call what3words API (free tier, no key required but rate-limited)
        response = requests.get(
            "https://api.what3words.com/v3/convert-to-coordinates",
            params={"words": words, "key": "fallback"},  # fallback key for free tier
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            raise ValueError(f"what3words error: {data['error'].get('message', 'invalid location')}")
        
        coordinates = data.get("coordinates", {})
        lat = coordinates.get("lat")
        lng = coordinates.get("lng")
        
        if lat is None or lng is None:
            raise ValueError("Could not convert what3words to coordinates")
        
        return float(lat), float(lng)
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to resolve what3words location: {e}")

