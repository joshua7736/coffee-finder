"""Tests for tray functionality (headless via monkeypatch)."""
import importlib
import time

import pytest


def test_tray_app_start_stop(monkeypatch):
    # prevent actual GUI loop by providing a dummy root
    class DummyRoot:
        def withdraw(self):
            pass
        def mainloop(self):
            # simulate short run
            return
        def quit(self):
            pass

    # stub Icon to avoid creating a real system tray icon
    class DummyIcon:
        def __init__(self, *args, **kwargs):
            self._running = False
        def run(self):
            self._running = True
            return
        def stop(self):
            self._running = False

    monkeypatch.setattr('pystray.Icon', DummyIcon)
    # stub out the login flow so we don't create real windows during the test
    import coffee_finder.login as login_mod
    monkeypatch.setattr(login_mod, 'show_login', lambda: (True, 'testuser'))

    tray = importlib.import_module('coffee_finder.tray')
    app = tray.TrayApp(root=DummyRoot())
    # run should return quickly due to DummyRoot.mainloop being no-op
    app.run()
    # if no exceptions, consider success
    assert True
