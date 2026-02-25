from coffee_finder import config
import os
import tempfile
import json


def test_config_read_write(monkeypatch):
    # use a real temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_path = f.name

    try:
        # monkeypatch config module's file path
        monkeypatch.setattr(config, "_PATH", test_path)

        # test defaults on missing file
        cfg = config.read_config()
        assert cfg.get("cache_ttl_seconds") == 24 * 3600
        assert cfg.get("google_places_api_key") is None

        # test write and read back
        config.set_cache_ttl(3600)
        config.set_google_api_key("my-key")

        cfg = config.read_config()
        assert cfg.get("cache_ttl_seconds") == 3600
        assert cfg.get("google_places_api_key") == "my-key"
    finally:
        # cleanup
        if os.path.exists(test_path):
            os.remove(test_path)
