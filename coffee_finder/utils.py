import math
from typing import Tuple


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
