"""System tray helper for Coffee Finder using pystray.

Simple, robust tray implementation: shows login, then creates a hidden root
and a tray icon. The GUI opens only from the tray menu.
"""
import threading
import tkinter as tk
from typing import Optional
import pystray
from PIL import Image, ImageDraw
import os

from .gui import CoffeeFinderGUI
from .config import get_cache_ttl, get_google_api_key, set_cache_ttl, set_google_api_key
from .login import show_login


def _make_image():
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((8, 8, size - 8, size - 8), fill=(88, 41, 0, 255))
    d.ellipse((18, 18, size - 18, size - 18), fill=(140, 110, 90, 255))
    return img


class TrayApp:
    def __init__(self, username: str = "User", root: Optional[tk.Tk] = None):
        self.root = root
        self.username = username
        self.gui_window: Optional[tk.Toplevel] = None
        self.settings_window: Optional[tk.Toplevel] = None
        self.icon: Optional[pystray.Icon] = None
        self._icon_thread: Optional[threading.Thread] = None

    def _open_gui(self, icon=None, item=None):
        if self.gui_window is None or not tk.Toplevel.winfo_exists(self.gui_window):
            self.gui_window = tk.Toplevel(self.root)
            CoffeeFinderGUI(self.gui_window, self.username)
        else:
            try:
                self.gui_window.lift()
                self.gui_window.focus_force()
            except Exception:
                pass

    def _open_settings(self, icon=None, item=None):
        if self.settings_window is not None:
            try:
                self.settings_window.lift()
                return
            except Exception:
                pass
        if self.root is None:
            return
        dlg = tk.Toplevel(self.root)
        dlg.title("Settings")
        self.settings_window = dlg

        import tkinter.ttk as ttk
        ttk.Label(dlg, text="Cache TTL (hours)").grid(row=0, column=0, padx=6, pady=6)
        ttl = tk.DoubleVar(value=get_cache_ttl() / 3600.0)
        ttk.Entry(dlg, textvariable=ttl).grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(dlg, text="Google Places API Key").grid(row=1, column=0, padx=6, pady=6)
        api = tk.StringVar(value=get_google_api_key() or os.environ.get("GOOGLE_PLACES_API_KEY") or "")
        ttk.Entry(dlg, textvariable=api, width=40).grid(row=1, column=1, padx=6, pady=6)

        def on_save():
            try:
                hours = float(ttl.get())
            except Exception:
                import tkinter.messagebox as messagebox
                messagebox.showerror("Invalid TTL", "Cache TTL must be a number")
                return
            set_cache_ttl(int(max(0, hours * 3600)))
            key = api.get().strip() or None
            set_google_api_key(key)
            if key:
                os.environ["GOOGLE_PLACES_API_KEY"] = key
            else:
                os.environ.pop("GOOGLE_PLACES_API_KEY", None)
            import tkinter.messagebox as messagebox
            messagebox.showinfo("Saved", "Settings saved")
            dlg.destroy()
            self.settings_window = None

        frame = tk.Frame(dlg)
        frame.grid(row=2, column=0, columnspan=2, pady=8)
        ttk.Button(frame, text="Save", command=on_save).pack(side="left", padx=4)
        ttk.Button(frame, text="Cancel", command=lambda: dlg.destroy()).pack(side="left", padx=4)

        def on_close():
            self.settings_window = None
            dlg.destroy()
        dlg.protocol("WM_DELETE_WINDOW", on_close)

    def _quit(self, icon=None, item=None):
        def _do_quit():
            try:
                if self.icon:
                    try:
                        self.icon.stop()
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                if self.gui_window:
                    try:
                        self.gui_window.destroy()
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                if self.root:
                    try:
                        self.root.quit()
                    except Exception:
                        pass
            except Exception:
                pass

        # Ensure shutdown runs on Tk main thread
        if self.root:
            try:
                self.root.after(0, _do_quit)
            except Exception:
                _do_quit()
        else:
            _do_quit()

    def run(self):
        # show login first
        auth_result = show_login()
        if isinstance(auth_result, tuple) and len(auth_result) >= 2:
            authenticated, username = auth_result[0], auth_result[1]
        else:
            authenticated, username = False, None
        if not authenticated:
            return
        self.username = username or self.username

        if self.root is None:
            self.root = tk.Tk()
        # hide the root: we use Toplevel windows to display GUI on demand
        self.root.withdraw()

        menu = pystray.Menu(
            pystray.MenuItem("Open", self._open_gui),
            pystray.MenuItem("Settings", self._open_settings),
            pystray.MenuItem("Quit", self._quit),
        )
        image = _make_image()
        self.icon = pystray.Icon("coffee-finder", image, "Coffee Finder", menu)

        # start icon in separate thread, keep tk mainloop on main thread
        t = threading.Thread(target=self.icon.run, daemon=True)
        t.start()
        self._icon_thread = t

        try:
            self.root.mainloop()
        finally:
            try:
                if self.icon:
                    self.icon.stop()
            except Exception:
                pass


def main(argv: Optional[list] = None):
    app = TrayApp()
    app.run()


if __name__ == "__main__":
    main()
