import pytest
from coffee_finder import database
import os
import tempfile


def test_home_location(monkeypatch):
    """Test saving and retrieving home location."""
    # Use temp DB for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    monkeypatch.setattr(database, '_DB_PATH', db_path)
    database._init_db()
    
    try:
        # Test no home initially
        home = database.get_home_location("testuser")
        assert home is None
        
        # Save home
        database.set_home_location(40.7128, -74.0060, "testuser", "NYC Home")
        home = database.get_home_location("testuser")
        assert home is not None
        assert home['lat'] == 40.7128
        assert home['lng'] == -74.0060
        assert home['name'] == "NYC Home"
        
        # Clear home
        database.clear_home_location("testuser")
        home = database.get_home_location("testuser")
        assert home is None
        
        # Test user isolation: other user should have no home
        home = database.get_home_location("otheruser")
        assert home is None
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_saved_places(monkeypatch):
    """Test saving and retrieving coffee places."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    monkeypatch.setattr(database, '_DB_PATH', db_path)
    database._init_db()
    
    try:
        # Test empty initially
        places = database.get_saved_places("testuser")
        assert len(places) == 0
        
        # Save place for testuser
        database.save_place("My Cafe", 40.0, -74.0, "testuser", "123 Main St", 4.5, "user")
        places = database.get_saved_places("testuser")
        assert len(places) == 1
        assert places[0]['name'] == "My Cafe"
        assert places[0]['rating'] == 4.5
        
        # Save another for testuser
        database.save_place("Other Cafe", 41.0, -75.0, "testuser", "456 Oak St")
        places = database.get_saved_places("testuser")
        assert len(places) == 2
        
        # Save place for different user
        database.save_place("Third Cafe", 42.0, -76.0, "otheruser", "789 Pine St")
        places = database.get_saved_places("otheruser")
        assert len(places) == 1
        assert places[0]['name'] == "Third Cafe"
        
        # testuser still has 2 places
        places = database.get_saved_places("testuser")
        assert len(places) == 2
        
        # Delete first place for testuser
        place_id = places[0]['id']
        database.delete_saved_place(place_id, "testuser")
        places = database.get_saved_places("testuser")
        assert len(places) == 1
        assert places[0]['name'] == "Other Cafe"
        
        # otheruser still has 1 place
        places = database.get_saved_places("otheruser")
        assert len(places) == 1
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_preferences(monkeypatch):
    """Test saving and retrieving preferences."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    monkeypatch.setattr(database, '_DB_PATH', db_path)
    database._init_db()
    
    try:
        # Test string preference
        database.set_preference("test_key", "test_value")
        val = database.get_preference("test_key")
        assert val == "test_value"
        
        # Test default
        val = database.get_preference("nonexistent", "default")
        assert val == "default"
        
        # Test boolean preference
        database.set_preference_bool("auto_load", True)
        is_true = database.get_preference_bool("auto_load")
        assert is_true is True
        
        # Test boolean false
        database.set_preference_bool("auto_load", False)
        is_false = database.get_preference_bool("auto_load")
        assert is_false is False
        
        # Test get all
        database.set_preference("key1", "val1")
        database.set_preference("key2", "val2")
        all_prefs = database.get_all_preferences()
        assert "key1" in all_prefs
        assert all_prefs["key1"] == "val1"
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
