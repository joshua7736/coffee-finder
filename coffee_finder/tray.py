"""System tray helper for Coffee Finder using pystray.

Starts hidden GUI and provides tray icon with Open/Quit/Settings actions.
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
    # create a simple coffee-bean style icon
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # brown circle
    draw.ellipse((8, 8, size - 8, size - 8), fill=(88, 41, 0, 255))
    # highlight
    draw.ellipse((18, 18, size - 18, size - 18), fill=(140, 110, 90, 255))
    return img


class TrayApp:
    def __init__(self, username: str = "User"):
        self.root: Optional[tk.Tk] = None
        self.icon: Optional[pystray.Icon] = None
        self.settings_window: Optional[tk.Toplevel] = None
        self.username = username

    def _open_gui(self, icon=None, item=None):
        if self.root is None:
            # This shouldn't happen, but handle gracefully
            return
        
        # Create a new window for the GUI
        gui_window = tk.Toplevel(self.root)
        app = CoffeeFinderGUI(gui_window, self.username)
        gui_window.deiconify()

    def _get_hidden_root(self):
        """Get or create the hidden root window."""
        if self.root is None:
            self.root = tk.Tk()
            self.root.withdraw()
        return self.root

    def _open_settings(self, icon=None, item=None):
        """Open settings dialog from tray menu."""
        if self.settings_window is not None:
            try:
                self.settings_window.lift()
                return
            except Exception:
                pass

        if self.root is None:
            return

        dlg = tk.Toplevel(self.root)
        dlg.title("Coffee Finder Settings")
        self.settings_window = dlg

        import tkinter.ttk as ttk

        ttk.Label(dlg, text="Cache TTL (hours)").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttl_hours = tk.DoubleVar(value=get_cache_ttl() / 3600.0)
        ttk.Entry(dlg, textvariable=ttl_hours).grid(row=0, column=1, padx=8, pady=6)

        ttk.Label(dlg, text="Google Places API Key").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        api_var = tk.StringVar(value=get_google_api_key() or os.environ.get("GOOGLE_PLACES_API_KEY") or "")
        ttk.Entry(dlg, textvariable=api_var, width=40).grid(row=1, column=1, padx=8, pady=6)

        def on_save():
            try:
                hours = float(ttl_hours.get())
            except Exception:
                import tkinter.messagebox as messagebox
                messagebox.showerror("Invalid TTL", "Cache TTL must be a number (hours).")
                return
            seconds = int(max(0, hours * 3600))
            set_cache_ttl(seconds)
            key = api_var.get().strip() or None
            set_google_api_key(key)
            if key:
                os.environ["GOOGLE_PLACES_API_KEY"] = key
            else:
                os.environ.pop("GOOGLE_PLACES_API_KEY", None)
            import tkinter.messagebox as messagebox
            messagebox.showinfo("Saved", "Settings saved.")
            dlg.destroy()
            self.settings_window = None

        def on_close():
            dlg.destroy()
            self.settings_window = None

        btn_save = ttk.Button(dlg, text="Save", command=on_save)
        btn_save.grid(row=2, column=0, columnspan=2, pady=(6, 6))

        dlg.protocol("WM_DELETE_WINDOW", on_close)

    def _quit(self, icon=None, item=None):
        if self.settings_window:
            try:
                self.settings_window.destroy()
            except Exception:
                pass
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
        if self.root:
            try:
                self.root.quit()
            except Exception:
                pass

    def run(self):
        # initialize hidden root
        self.root = tk.Tk()
        self.root.withdraw()

        image = _make_image()
        menu = pystray.Menu(
            pystray.MenuItem("Open", self._open_gui),
            pystray.MenuItem("Settings", self._open_settings),
            pystray.MenuItem("Quit", self._quit),
        )
        self.icon = pystray.Icon("coffee-finder", image, "Coffee Finder", menu)

        # run the tray icon; keep GUI mainloop as main thread by running icon in separate thread
        t = threading.Thread(target=self.icon.run, daemon=True)
        t.start()

        # run tk mainloop in main thread
        try:
            self.root.mainloop()
        finally:
            try:
                if self.icon:
                    self.icon.stop()
            except Exception:
                pass


def main(argv: Optional[list] = None):
    # Show login window
    authenticated, username = show_login()
    if not authenticated:
        return
    
    app = TrayApp(username)
    app.run()


if __name__ == "__main__":
    main()
