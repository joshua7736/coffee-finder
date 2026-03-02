import math
from typing import Tuple
import os
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
    """Convert a what3words address into latitude and longitude.

    This function requires an API key from what3words.  Set the key in the
    environment variable ``WHAT3WORDS_API_KEY`` before calling.  The free
    developer plan is sufficient for casual use; see
    https://developer.what3words.com for details.  Without a key a
    :class:`RuntimeError` is raised.

    The input may include leading slashes (e.g. ``///index.home.raft``); they
    are stripped automatically.  A ``ValueError`` is raised if the format is
    clearly invalid or the API returns no coordinates.
    """
    # normalize input: remove leading slashes
    words = value.lstrip('/').strip()
    if not words:
        raise ValueError("Invalid what3words format")

    api_key = os.getenv("WHAT3WORDS_API_KEY")
    if not api_key:
        raise RuntimeError(
            "what3words API key not set; please export WHAT3WORDS_API_KEY"
        )

    try:
        response = requests.get(
            "https://api.what3words.com/v3/convert-to-coordinates",
            params={"words": words, "key": api_key},
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            # propagate error message for debugging
            raise ValueError(f"what3words error: {data['error'].get('message')}")

        coords = data.get("coordinates", {})
        lat = coords.get("lat")
        lng = coords.get("lng")
        if lat is None or lng is None:
            raise ValueError("Could not convert what3words to coordinates")
        return float(lat), float(lng)
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to resolve what3words location: {exc}")


