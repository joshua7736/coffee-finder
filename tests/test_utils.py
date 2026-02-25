import math
from coffee_finder.utils import haversine_distance, parse_latlng


def test_haversine_zero():
    d = haversine_distance(0.0, 0.0, 0.0, 0.0)
    assert math.isclose(d, 0.0, abs_tol=1e-6)


def test_parse_latlng():
    lat, lng = parse_latlng("40.0, -74.0")
    assert lat == 40.0
    assert lng == -74.0


def test_parse_latlng_bad():
    import pytest
    with pytest.raises(ValueError):
        parse_latlng("not-a-pair")
