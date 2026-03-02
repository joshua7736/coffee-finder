"""CLI entry and orchestration for Coffee Finder."""
import os
import argparse
from typing import List
import requests

from .providers import choose_provider, search_google_places
from .utils import parse_latlng


def detect_location_by_ip() -> tuple:
    try:
        r = requests.get("https://ipinfo.io/json", timeout=5)
        r.raise_for_status()
        j = r.json()
        loc = j.get("loc")
        if loc:
            lat, lng = parse_latlng(loc)
            return lat, lng
    except Exception:
        pass
    raise RuntimeError("Could not detect location. Provide --latlng or --lat and --lng.")


def format_place(p: dict) -> str:
    parts = [f"{p.get('name')}"]
    if p.get("rating"):
        parts.append(f"(rating: {p.get('rating')})")
    if p.get("distance_m") is not None:
        parts.append(f"{int(p.get('distance_m'))} m")
    if p.get("address"):
        parts.append(f"- {p.get('address')}")
    return " ".join(parts)


def main(argv: List[str] = None):
    parser = argparse.ArgumentParser(prog="coffee-finder")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--latlng", help="Latitude,Longitude (e.g. 40.7128,-74.0060)")
    group.add_argument("--address", help="Address to geocode (uses Nominatim)")
    parser.add_argument("--lat", type=float, help="Latitude (use with --lng)")
    parser.add_argument("--lng", type=float, help="Longitude (use with --lat)")
    parser.add_argument("--radius", type=int, default=1000, help="Search radius in meters (default 1000)")
    parser.add_argument("--limit", type=int, default=10, help="Max results (default 10)")
    parser.add_argument("--min-rating", type=float, help="Minimum rating to include (Google only)")
    args = parser.parse_args(argv)

    if args.latlng:
        lat, lng = parse_latlng(args.latlng)
    elif args.lat is not None and args.lng is not None:
        lat, lng = args.lat, args.lng
    elif args.address:
        # geocode via Nominatim
        q = requests.get("https://nominatim.openstreetmap.org/search", params={"q": args.address, "format": "json", "limit": 1}, headers={"User-Agent": "coffee-finder-app"}, timeout=10)
        q.raise_for_status()
        res = q.json()
        if not res:
            raise RuntimeError("Address not found")
        lat = float(res[0]["lat"]) ; lng = float(res[0]["lon"])
    else:
        lat, lng = detect_location_by_ip()

    # prefer Google if API key is set
    places = choose_provider(lat, lng, radius=args.radius, limit=args.limit, min_rating=args.min_rating)
    # filter by min-rating if provided
    if args.min_rating is not None:
        places = [p for p in places if (p.get("rating") is not None and p.get("rating") >= args.min_rating)]

    if not places:
        print("No coffee places found within radius.")
        return

    print(f"Found {len(places)} places near {lat},{lng} (radius {args.radius} m):\n")
    for i, p in enumerate(places, start=1):
        print(f"{i}. {format_place(p)}")


if __name__ == "__main__":
    main()
