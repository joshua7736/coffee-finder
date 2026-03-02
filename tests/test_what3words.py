"""Tests for what3words support."""
import os
import pytest
from unittest.mock import patch, MagicMock

from coffee_finder.utils import parse_what3words


@patch.dict(os.environ, {}, clear=True)
def test_parse_what3words_key_missing():
    """When no API key is set, a RuntimeError is raised."""
    with pytest.raises(RuntimeError, match="WHAT3WORDS_API_KEY"):
        parse_what3words("///anything.here.test")


def test_parse_what3words_valid():
    """Successful lookup using the official API."""
    fake_json = {"coordinates": {"lat": 51.5211, "lng": -0.2033}}
    with patch.dict(os.environ, {"WHAT3WORDS_API_KEY": "dummy"}):
        with patch("coffee_finder.utils.requests.get") as mock_get:
            mock_get.return_value.json.return_value = fake_json
            mock_get.return_value.raise_for_status = MagicMock()

            lat, lng = parse_what3words("///light.dog.cat")
            assert lat == 51.5211
            assert lng == -0.2033
            mock_get.assert_called_once()


def test_parse_what3words_strips_slashes_and_uses_key():
    """Leading slashes removed and key included in request."""
    fake_json = {"coordinates": {"lat": 1.0, "lng": 2.0}}
    with patch.dict(os.environ, {"WHAT3WORDS_API_KEY": "abc123"}):
        with patch("coffee_finder.utils.requests.get") as mock_get:
            mock_get.return_value.json.return_value = fake_json
            mock_get.return_value.raise_for_status = MagicMock()

            parse_what3words("///foo.bar.baz")
            called = mock_get.call_args[1]
            assert called["params"]["words"] == "foo.bar.baz"
            assert called["params"]["key"] == "abc123"


def test_parse_what3words_invalid_format():
    with pytest.raises(ValueError, match="Invalid what3words format"):
        parse_what3words("///")


def test_parse_what3words_api_error():
    fake_json = {"error": {"message": "Invalid address"}}
    with patch.dict(os.environ, {"WHAT3WORDS_API_KEY": "key"}):
        with patch("coffee_finder.utils.requests.get") as mock_get:
            mock_get.return_value.json.return_value = fake_json
            mock_get.return_value.raise_for_status = MagicMock()
            with pytest.raises(ValueError, match="what3words error"):
                parse_what3words("///foo.bar.baz")


def test_parse_what3words_missing_coordinates():
    fake_json = {"coordinates": {}}
    with patch.dict(os.environ, {"WHAT3WORDS_API_KEY": "key"}):
        with patch("coffee_finder.utils.requests.get") as mock_get:
            mock_get.return_value.json.return_value = fake_json
            mock_get.return_value.raise_for_status = MagicMock()
            with pytest.raises(ValueError, match="Could not convert"):
                parse_what3words("///foo.bar.baz")


def test_parse_what3words_network_error():
    import requests
    with patch.dict(os.environ, {"WHAT3WORDS_API_KEY": "key"}):
        with patch("coffee_finder.utils.requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("Network")
            with pytest.raises(RuntimeError, match="Failed to resolve"):
                parse_what3words("///foo.bar.baz")


def test_parse_what3words_timeout():
    import requests
    with patch.dict(os.environ, {"WHAT3WORDS_API_KEY": "key"}):
        with patch("coffee_finder.utils.requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout("Timeout")
            with pytest.raises(RuntimeError, match="Failed to resolve"):
                parse_what3words("///foo.bar.baz")

