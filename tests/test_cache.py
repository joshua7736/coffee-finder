import time
from coffee_finder import cache


def test_cache_set_get():
    key = f"test:key:{int(time.time())}"
    value = {"a": 1, "b": [1, 2, 3]}
    cache.cache_set(key, value)
    got = cache.cache_get(key)
    assert got == value


def test_cache_expiry(monkeypatch):
    key = f"test:expiry:{int(time.time())}"
    value = {"x": 42}
    # set normally
    cache.cache_set(key, value)

    # simulate time in the far future so the entry is considered expired
    real_time = time.time()

    def fake_time():
        return real_time + 3600 * 24 * 2

    monkeypatch.setattr(cache.time, "time", fake_time)
    got = cache.cache_get(key, max_age_seconds=60)
    assert got is None
