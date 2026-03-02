"""Tests for what3words support."""
import pytest
from unittest.mock import patch, MagicMock

from coffee_finder.utils import parse_what3words


def test_parse_what3words_valid():
    """Test parsing valid what3words location."""
    # Mock successful API response
    mock_response = {
        "coordinates": {
            "lat": 51.5211,
            "lng": -0.2033
        }
    }
    
    with patch("coffee_finder.utils.requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = MagicMock()
        
        lat, lng = parse_what3words("///light.dog.cat")
        
        assert lat == 51.5211
        assert lng == -0.2033
        mock_get.assert_called_once()


def test_parse_what3words_strips_slashes():
    """Test that leading slashes are stripped from input."""
    mock_response = {
        "coordinates": {
            "lat": 51.5211,
            "lng": -0.2033
        }
    }
    
    with patch("coffee_finder.utils.requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = MagicMock()
        
        parse_what3words("///light.dog.cat")
        
        # Should pass words without slashes
        call_args = mock_get.call_args
        assert "light.dog.cat" in str(call_args)


def test_parse_what3words_invalid_format():
    """Test that invalid what3words format raises error."""
    with pytest.raises(ValueError, match="Invalid what3words format"):
        parse_what3words("///")


def test_parse_what3words_api_error():
    """Test handling of API error responses."""
    mock_response = {
        "error": {
            "message": "Invalid what3words address"
        }
    }
    
    with patch("coffee_finder.utils.requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = MagicMock()
        
        with pytest.raises(ValueError, match="what3words error"):
            parse_what3words("///invalid.words.here")


def test_parse_what3words_missing_coordinates():
    """Test handling when API returns no coordinates."""
    mock_response = {"coordinates": {}}
    
    with patch("coffee_finder.utils.requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = MagicMock()
        
        with pytest.raises(ValueError, match="Could not convert what3words"):
            parse_what3words("///test.words.here")


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
