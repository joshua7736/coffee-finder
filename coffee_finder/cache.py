"""Simple on-disk sqlite cache for query results."""
import os
import sqlite3
import json
import time
from typing import Any, Optional


def _cache_path() -> str:
    if os.name == "nt":
        base = os.getenv("LOCALAPPDATA") or os.path.expanduser("~")
    else:
        base = os.getenv("XDG_CACHE_HOME") or os.path.join(os.path.expanduser("~"), ".cache")
    d = os.path.join(base, "coffee_finder")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "cache.db")


_DB_PATH = _cache_path()


def _get_conn():
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS cache (k TEXT PRIMARY KEY, v TEXT, ts INTEGER)""")
    return conn


def cache_get(key: str, max_age_seconds: int = 24 * 3600) -> Optional[Any]:
    try:
        conn = _get_conn()
        cur = conn.execute("SELECT v, ts FROM cache WHERE k=?", (key,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        val, ts = row
        if int(time.time()) - int(ts) > max_age_seconds:
            return None
        return json.loads(val)
    except Exception:
        return None


def cache_set(key: str, value: Any) -> None:
    try:
        conn = _get_conn()
        conn.execute("REPLACE INTO cache (k, v, ts) VALUES (?, ?, ?)", (key, json.dumps(value), int(time.time())))
        conn.commit()
        conn.close()
    except Exception:
        pass
