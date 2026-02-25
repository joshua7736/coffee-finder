import os
from coffee_finder import providers


def test_choose_provider_uses_overpass_when_no_key(monkeypatch):
    # ensure no API key
    monkeypatch.delenv("GOOGLE_PLACES_API_KEY", raising=False)

    sample = [{"name": "Test Cafe", "lat": 1.0, "lng": 2.0, "distance_m": 100, "source": "overpass"}]

    def fake_overpass(lat, lng, radius=1000, limit=20):
        return sample

    monkeypatch.setattr(providers, "search_overpass", fake_overpass)

    res = providers.choose_provider(1.0, 2.0, radius=500, limit=5)
    assert res == sample


def test_choose_provider_prefers_google_if_key(monkeypatch):
    monkeypatch.setenv("GOOGLE_PLACES_API_KEY", "fake-key")

    sample_google = [{"name": "G Cafe", "lat": 1.0, "lng": 2.0, "distance_m": 50, "source": "google"}]

    def fake_google(key, lat, lng, radius=1000, limit=20):
        return sample_google

    # monkeypatch the google search function used internally
    monkeypatch.setattr(providers, "search_google_places", fake_google)
    res = providers.choose_provider(1.0, 2.0, radius=500, limit=5)
    assert res == sample_google
