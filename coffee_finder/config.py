"""Persistent configuration storage for Coffee Finder."""
import json
import os
from typing import Any, Dict


def _config_path() -> str:
    if os.name == "nt":
        base = os.getenv("LOCALAPPDATA") or os.path.expanduser("~")
    else:
        base = os.getenv("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    d = os.path.join(base, "coffee_finder")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "config.json")


_PATH = _config_path()


def _default_config() -> Dict[str, Any]:
    return {
        "cache_ttl_seconds": 24 * 3600,
        "google_places_api_key": None,
    }


def read_config() -> Dict[str, Any]:
    try:
        if not os.path.exists(_PATH):
            return _default_config()
        with open(_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        cfg = _default_config()
        cfg.update({k: data.get(k, v) for k, v in cfg.items()})
        return cfg
    except Exception:
        return _default_config()


def write_config(data: Dict[str, Any]) -> None:
    try:
        with open(_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def get_cache_ttl() -> int:
    return int(read_config().get("cache_ttl_seconds", 24 * 3600))


def set_cache_ttl(seconds: int) -> None:
    cfg = read_config()
    cfg["cache_ttl_seconds"] = int(seconds)
    write_config(cfg)


def get_google_api_key() -> Any:
    return read_config().get("google_places_api_key")


def set_google_api_key(key: Any) -> None:
    cfg = read_config()
    cfg["google_places_api_key"] = key
    write_config(cfg)
