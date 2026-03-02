"""System tray helper for Coffee Finder using pystray.

Reuses root window from login, creates a tray icon with menu.
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
    """Create a simple coffee-bean style icon."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # brown circle
    draw.ellipse((8, 8, size - 8, size - 8), fill=(88, 41, 0, 255))
    # highlight
    draw.ellipse((18, 18, size - 18, size - 18), fill=(140, 110, 90, 255))
    return img


class TrayApp:
    def __init__(self, username: str = "User", root: Optional[tk.Tk] = None):
        self.root = root
        self.username = username
        self.gui_window = None
        self.settings_window = None
    
    def _open_gui(self, icon=None, item=None):
        """Open the main GUI window."""
        if self.gui_window is None or not tk.Toplevel.winfo_exists(self.gui_window):
            self.gui_window = tk.Toplevel(self.root)
            app = CoffeeFinderGUI(self.gui_window, self.username)
        else:
            self.gui_window.lift()
            self.gui_window.focus()
    
    def _open_settings(self, icon=None, item=None):
        """Open settings dialog."""
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
        
        button_frame = ttk.Frame(dlg)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Save", command=on_save).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=lambda: dlg.destroy()).pack(side="left", padx=5)
        
        def on_close():
            self.settings_window = None
        
        dlg.protocol("WM_DELETE_WINDOW", on_close)
    
    def _quit(self, icon=None, item=None):
        """Quit the application."""
        if self.settings_window:
            try:
                self.settings_window.destroy()
            except Exception:
                pass
        if self.gui_window:
            try:
                self.gui_window.destroy()
            except Exception:
                pass
        if self.root:
            try:
                self.root.quit()
            except Exception:
                pass
    
    def run(self):
        """Start the tray application."""
        if self.root is None:
            self.root = tk.Tk()
        
        # Hide the root window
        self.root.withdraw()
        
        # Create tray menu
        menu = pystray.Menu(
            pystray.MenuItem("Open", self._open_gui),
            pystray.MenuItem("Settings", self._open_settings),
            pystray.MenuItem("Quit", self._quit),
        )
        
        # Create tray icon
        image = _make_image()
        icon = pystray.Icon("coffee-finder", image, "Coffee Finder", menu)
        
        # Run icon in a separate thread
        icon_thread = threading.Thread(target=icon.run, daemon=True)
        icon_thread.start()
        
        # Run root mainloop in main thread
        try:
            self.root.mainloop()
        except Exception:
            pass
        finally:
            try:
                icon.stop()
            except Exception:
                pass


def main(argv: Optional[list] = None):
    """Entry point for tray application."""
    # Show login window
    authenticated, username, root_window = show_login()
    if not authenticated:
        return
    
    app = TrayApp(username, root_window)
    app.run()


if __name__ == "__main__":
    main()
