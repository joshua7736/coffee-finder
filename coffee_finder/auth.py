"""User authentication module for Coffee Finder.

Handles user registration, login, and password hashing.
"""
import sqlite3
import hashlib
import os
from typing import Tuple, Optional
from datetime import datetime

def _get_auth_db():
    """Get database connection for authentication."""
    from .database import _db_path
    # Use same directory as user database
    db_dir = os.path.dirname(_db_path())
    db_file = os.path.join(db_dir, "auth.db")
    return db_file

_AUTH_DB = _get_auth_db()

def _get_conn():
    """Get database connection."""
    conn = sqlite3.connect(_AUTH_DB)
    conn.row_factory = sqlite3.Row
    return conn

def _init_auth_db():
    """Initialize authentication database schema."""
    conn = _get_conn()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize on import
_init_auth_db()

def _hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(username: str, email: str, password: str) -> Tuple[bool, str]:
    """Register a new user.
    
    Returns: (success: bool, message: str)
    """
    # Validate inputs
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    if not email or '@' not in email:
        return False, "Invalid email address"
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    # Check for existing user
    conn = _get_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already taken"
    
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return False, "Email already registered"
    
    # Create user
    try:
        password_hash = _hash_password(password)
        cursor.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        """, (username, email, password_hash))
        conn.commit()
        conn.close()
        return True, "Account created successfully"
    except Exception as e:
        conn.close()
        return False, f"Registration error: {str(e)}"

def login_user(username: str, password: str) -> Tuple[bool, str]:
    """Authenticate a user.
    
    Returns: (success: bool, message: str)
    """
    if not username or not password:
        return False, "Username and password required"
    
    conn = _get_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return False, "Invalid username or password"
    
    password_hash = _hash_password(password)
    if row['password_hash'] != password_hash:
        return False, "Invalid username or password"
    
    return True, "Login successful"

def user_exists(username: str) -> bool:
    """Check if user exists."""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def get_user_by_username(username: str) -> Optional[dict]:
    """Get user details by username."""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, created_at FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
