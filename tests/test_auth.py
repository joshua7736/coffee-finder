"""Unit tests for authentication module."""
import pytest
import tempfile
import os
from coffee_finder import auth


def test_register_user_valid(monkeypatch):
    """Test registering a valid user."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    monkeypatch.setattr(auth, "_AUTH_DB", db_path)
    auth._init_auth_db()
    
    try:
        success, msg = auth.register_user("john_doe", "john@example.com", "password123")
        assert success is True
        assert "successfully" in msg.lower()
        
        # Verify user can be retrieved
        user = auth.get_user_by_username("john_doe")
        assert user is not None
        assert user["username"] == "john_doe"
        assert user["email"] == "john@example.com"
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_register_user_invalid_username(monkeypatch):
    """Test registering with invalid username."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    monkeypatch.setattr(auth, "_AUTH_DB", db_path)
    auth._init_auth_db()
    
    try:
        success, msg = auth.register_user("ab", "test@example.com", "password123")
        assert success is False
        assert "at least 3" in msg.lower()
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_register_user_invalid_email(monkeypatch):
    """Test registering with invalid email."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    monkeypatch.setattr(auth, "_AUTH_DB", db_path)
    auth._init_auth_db()
    
    try:
        success, msg = auth.register_user("username", "invalid-email", "password123")
        assert success is False
        assert "email" in msg.lower()
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_register_user_short_password(monkeypatch):
    """Test registering with short password."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    monkeypatch.setattr(auth, "_AUTH_DB", db_path)
    auth._init_auth_db()
    
    try:
        success, msg = auth.register_user("username", "test@example.com", "short")
        assert success is False
        assert "at least 6" in msg.lower()
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_register_duplicate_username(monkeypatch):
    """Test registering with duplicate username."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    monkeypatch.setattr(auth, "_AUTH_DB", db_path)
    auth._init_auth_db()
    
    try:
        auth.register_user("john", "john@example.com", "password123")
        success, msg = auth.register_user("john", "john2@example.com", "password123")
        assert success is False
        assert "already taken" in msg.lower()
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_register_duplicate_email(monkeypatch):
    """Test registering with duplicate email."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    monkeypatch.setattr(auth, "_AUTH_DB", db_path)
    auth._init_auth_db()
    
    try:
        auth.register_user("john", "john@example.com", "password123")
        success, msg = auth.register_user("jane", "john@example.com", "password123")
        assert success is False
        assert "already registered" in msg.lower()
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_login_user_success(monkeypatch):
    """Test successful login."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    monkeypatch.setattr(auth, "_AUTH_DB", db_path)
    auth._init_auth_db()
    
    try:
        auth.register_user("john", "john@example.com", "password123")
        success, msg = auth.login_user("john", "password123")
        assert success is True
        assert "successful" in msg.lower()
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_login_user_wrong_password(monkeypatch):
    """Test login with wrong password."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    monkeypatch.setattr(auth, "_AUTH_DB", db_path)
    auth._init_auth_db()
    
    try:
        auth.register_user("john", "john@example.com", "password123")
        success, msg = auth.login_user("john", "wrongpassword")
        assert success is False
        assert "invalid" in msg.lower()
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_login_user_nonexistent(monkeypatch):
    """Test login with nonexistent user."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    monkeypatch.setattr(auth, "_AUTH_DB", db_path)
    auth._init_auth_db()
    
    try:
        success, msg = auth.login_user("nonexistent", "password123")
        assert success is False
        assert "invalid" in msg.lower()
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_user_exists(monkeypatch):
    """Test user_exists function."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    monkeypatch.setattr(auth, "_AUTH_DB", db_path)
    auth._init_auth_db()
    
    try:
        assert auth.user_exists("john") is False
        auth.register_user("john", "john@example.com", "password123")
        assert auth.user_exists("john") is True
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
