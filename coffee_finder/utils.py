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
    
    Uses OpenStreetMap Nominatim API which supports what3words format for free.
    """
    # normalize input: remove leading /// if present
    words = value.lstrip('/').strip()
    if not words:
        raise ValueError("Invalid what3words format")
    
    # Ensure proper format for nominatim
    query = f"///{words}" if not words.startswith("///") else words
    
    try:
        # Nominatim supports what3words format natively (free API)
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": query,
                "format": "json",
                "limit": 1
            },
            headers={"User-Agent": "coffee-finder-app"},
            timeout=10
        )
        response.raise_for_status()
        results = response.json()
        
        if not results:
            raise ValueError(f"what3words location not found: {query}")
        
        result = results[0]
        lat = float(result.get("lat"))
        lng = float(result.get("lon"))
        
        return lat, lng
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to resolve what3words location: {e}")


