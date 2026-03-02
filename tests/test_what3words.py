"""Tests for what3words support."""
import pytest
from unittest.mock import patch, MagicMock

from coffee_finder.utils import parse_what3words


def test_parse_what3words_valid():
    """Test parsing valid what3words location via Nominatim."""
    mock_response = [{
        "lat": "51.5211",
        "lon": "-0.2033",
        "name": "light.dog.cat"
    }]
    
    with patch("coffee_finder.utils.requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = MagicMock()
        
        lat, lng = parse_what3words("///light.dog.cat")
        
        assert lat == 51.5211
        assert lng == -0.2033
        mock_get.assert_called_once()


def test_parse_what3words_strips_slashes():
    """Test that leading slashes are stripped from input."""
    mock_response = [{
        "lat": "51.5211",
        "lon": "-0.2033"
    }]
    
    with patch("coffee_finder.utils.requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = MagicMock()
        
        parse_what3words("///light.dog.cat")
        
        # Should call nominatim with proper format
        call_args = mock_get.call_args
        assert "nominatim.openstreetmap.org" in str(call_args)


def test_parse_what3words_invalid_format():
    """Test that invalid what3words format raises error."""
    with pytest.raises(ValueError, match="Invalid what3words format"):
        parse_what3words("///")


def test_parse_what3words_not_found():
    """Test handling when location is not found."""
    mock_response = []
    
    with patch("coffee_finder.utils.requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = MagicMock()
        
        with pytest.raises(ValueError, match="what3words location not found"):
            parse_what3words("///invalid.words.here")


def test_parse_what3words_network_error():
    """Test handling of network errors."""
    import requests
    
    with patch("coffee_finder.utils.requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException("Network error")
        
        with pytest.raises(RuntimeError, match="Failed to resolve what3words"):
            parse_what3words("///light.dog.cat")


def test_parse_what3words_timeout():
    """Test handling of request timeout."""
    import requests
    
    with patch("coffee_finder.utils.requests.get") as mock_get:
        mock_get.side_effect = requests.Timeout("Request timeout")
        
        with pytest.raises(RuntimeError, match="Failed to resolve what3words"):
            parse_what3words("///light.dog.cat")


def test_parse_what3words_nominatim_called_correctly():
    """Test that Nominatim is called with correct parameters."""
    mock_response = [{
        "lat": "40.7128",
        "lon": "-74.0060"
    }]
    
    with patch("coffee_finder.utils.requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = MagicMock()
        
        parse_what3words("light.dog.cat")
        
        # Verify Nominatim endpoint is called
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["params"]["format"] == "json"
        assert "///light.dog.cat" in call_kwargs["params"]["q"]
        assert "coffee-finder-app" in call_kwargs["headers"]["User-Agent"]

