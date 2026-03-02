"""Test database migration from old schema to new schema."""
import pytest
from coffee_finder import database
import os
import tempfile
import sqlite3


def test_migrate_existing_database(monkeypatch):
    """Test migration of existing database without username column."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    monkeypatch.setattr(database, '_DB_PATH', db_path)
    
    try:
        # Step 1: Create old schema (without username column)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE home_location (
                id INTEGER PRIMARY KEY,
                name TEXT,
                lat REAL NOT NULL,
                lng REAL NOT NULL,
                saved_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE saved_places (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                lat REAL NOT NULL,
                lng REAL NOT NULL,
                address TEXT,
                rating REAL,
                source TEXT,
                saved_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert some old data
        cursor.execute("INSERT INTO home_location (name, lat, lng) VALUES (?, ?, ?)",
                      ("Old Home", 40.0, -74.0))
        cursor.execute("INSERT INTO saved_places (name, lat, lng, address) VALUES (?, ?, ?, ?)",
                      ("Old Cafe", 41.0, -75.0, "123 Main St"))
        conn.commit()
        conn.close()
        
        # Step 2: Run migration
        database._init_db()
        
        # Step 3: Verify username column was added
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(home_location)")
        home_columns = [row[1] for row in cursor.fetchall()]
        assert 'username' in home_columns, "username column not added to home_location"
        
        cursor.execute("PRAGMA table_info(saved_places)")
        places_columns = [row[1] for row in cursor.fetchall()]
        assert 'username' in places_columns, "username column not added to saved_places"
        
        # Step 4: Verify old data was migrated (should have default_user as username)
        cursor.execute("SELECT COUNT(*) FROM home_location WHERE username = 'default_user'")
        count = cursor.fetchone()[0]
        assert count == 1, "Old home location data not migrated with default_user"
        
        cursor.execute("SELECT COUNT(*) FROM saved_places WHERE username = 'default_user'")
        count = cursor.fetchone()[0]
        assert count == 1, "Old saved place data not migrated with default_user"
        
        conn.close()
        
        # Step 5: Verify database functions still work
        home = database.get_home_location("default_user")
        assert home is not None
        assert home['lat'] == 40.0
        assert home['name'] == "Old Home"
        
        places = database.get_saved_places("default_user")
        assert len(places) == 1
        assert places[0]['name'] == "Old Cafe"
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
