"""User database for Coffee Finder.

Stores home location, saved coffee places, and user preferences.
Uses SQLite for local persistence.
"""
import sqlite3
import os
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime

def _db_path() -> str:
    if os.name == "nt":
        base = os.getenv("LOCALAPPDATA") or os.path.expanduser("~")
    else:
        base = os.getenv("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local/share")
    d = os.path.join(base, "coffee_finder")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "user.db")

_DB_PATH = _db_path()

def _get_conn():
    """Get or create database connection."""
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _migrate_db():
    """Migrate database schema if needed."""
    conn = _get_conn()
    cursor = conn.cursor()
    
    # Check if home_location table exists and has username column
    try:
        cursor.execute("PRAGMA table_info(home_location)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'username' not in columns:
            # Add username column to home_location
            cursor.execute("ALTER TABLE home_location ADD COLUMN username TEXT DEFAULT 'default_user'")
            conn.commit()
    except Exception:
        pass
    
    # Check if saved_places table exists and has username column
    try:
        cursor.execute("PRAGMA table_info(saved_places)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'username' not in columns:
            # Add username column to saved_places
            cursor.execute("ALTER TABLE saved_places ADD COLUMN username TEXT DEFAULT 'default_user'")
            conn.commit()
    except Exception:
        pass
    
    conn.close()

def _init_db():
    """Initialize database schema if needed."""
    conn = _get_conn()
    cursor = conn.cursor()
    
    # Home location (per user)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS home_location (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            name TEXT,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            saved_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(username)
        )
    """)
    
    # Saved coffee places (per user)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_places (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            name TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            address TEXT,
            rating REAL,
            source TEXT,
            saved_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # User preferences
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    
    # Run migrations after creating tables
    _migrate_db()

# Initialize on import
_init_db()

# ===== Home Location =====

def set_home_location(lat: float, lng: float, username: str, name: str = "Home") -> None:
    """Save home location for a specific user."""
    conn = _get_conn()
    cursor = conn.cursor()
    # Delete existing home location for this user, then insert new one
    cursor.execute("DELETE FROM home_location WHERE username = ?", (username,))
    cursor.execute("INSERT INTO home_location (username, name, lat, lng) VALUES (?, ?, ?, ?)", 
                   (username, name, lat, lng))
    conn.commit()
    conn.close()

def get_home_location(username: str) -> Optional[Dict]:
    """Retrieve home location for a specific user."""
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT name, lat, lng, saved_at FROM home_location WHERE username = ? LIMIT 1", 
                      (username,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None
    except Exception:
        return None

def clear_home_location(username: str) -> None:
    """Clear saved home location for a specific user."""
    conn = _get_conn()
    conn.execute("DELETE FROM home_location WHERE username = ?", (username,))
    conn.commit()
    conn.close()

# ===== Saved Places =====

def save_place(name: str, lat: float, lng: float, username: str, address: str = "", 
               rating: Optional[float] = None, source: str = "user") -> None:
    """Save a coffee place for a specific user."""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO saved_places (username, name, lat, lng, address, rating, source)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (username, name, lat, lng, address, rating, source))
    conn.commit()
    conn.close()

def get_saved_places(username: str) -> List[Dict]:
    """Retrieve all saved coffee places for a specific user."""
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, lat, lng, address, rating, source, saved_at 
            FROM saved_places 
            WHERE username = ?
            ORDER BY saved_at DESC
        """, (username,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception:
        return []

def delete_saved_place(place_id: int, username: str) -> None:
    """Delete a saved place by ID (must belong to the user)."""
    conn = _get_conn()
    conn.execute("DELETE FROM saved_places WHERE id = ? AND username = ?", (place_id, username))
    conn.commit()
    conn.close()

# ===== Preferences =====

def set_preference(key: str, value: str) -> None:
    """Set a user preference."""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()
    conn.close()

def get_preference(key: str, default: str = "") -> str:
    """Get a user preference."""
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default
    except Exception:
        return default

def get_all_preferences() -> Dict[str, str]:
    """Get all preferences."""
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM preferences")
        rows = cursor.fetchall()
        conn.close()
        return {row[0]: row[1] for row in rows}
    except Exception:
        return {}

def set_preference_bool(key: str, value: bool) -> None:
    """Set a boolean preference."""
    set_preference(key, "1" if value else "0")

def get_preference_bool(key: str, default: bool = False) -> bool:
    """Get a boolean preference."""
    val = get_preference(key, "0" if not default else "1")
    return val == "1"
