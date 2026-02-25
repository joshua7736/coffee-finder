import threading
import time
import importlib


def test_tray_app_start_stop(monkeypatch):
    # Import the tray module
    tray = importlib.import_module('coffee_finder.tray')

    # Fake Tk so mainloop returns immediately and methods exist
    class DummyTk:
        def __init__(self):
            self.withdrawn = False
            self.deiconified = False
            self._quit = False

        def withdraw(self):
            self.withdrawn = True

        def deiconify(self):
            self.deiconified = True

        def lift(self):
            pass

        def mainloop(self):
            # return quickly to allow run() to proceed
            return

        def quit(self):
            self._quit = True

    monkeypatch.setattr(tray.tk, 'Tk', DummyTk)

    # Fake Icon for pystray to avoid system tray interaction
    class FakeIcon:
        def __init__(self, name, image, title, menu):
            self.name = name
            self.image = image
            self.title = title
            self.menu = menu
            self._stopped = False
            self.started = False

        def run(self):
            self.started = True
            # wait until stopped
            while not self._stopped:
                time.sleep(0.01)

        def stop(self):
            self._stopped = True

    monkeypatch.setattr(tray.pystray, 'Icon', FakeIcon)

    app = tray.TrayApp()

    # run in thread to ensure it doesn't block the test (mainloop returns quickly)
    t = threading.Thread(target=app.run, daemon=True)
    t.start()
    # give it a moment to start and for the icon thread to be created
    time.sleep(0.2)

    # after run completes, icon.stop should have been called and thread should exit
    # ensure thread finished
    t.join(timeout=2)
    assert not t.is_alive()
