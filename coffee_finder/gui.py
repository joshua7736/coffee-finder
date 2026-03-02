"""Small Tkinter GUI for Coffee Finder.

Runable as module: `python -m coffee_finder.gui` or via script `coffee-finder-gui`.
"""
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import os
import webbrowser
from typing import Optional

from .config import get_cache_ttl, get_google_api_key, set_cache_ttl, set_google_api_key
from .database import get_home_location, set_home_location, save_place, get_saved_places, delete_saved_place
from .utils import parse_latlng
from .providers import choose_provider
from .login import show_login


def _open_map(lat: float, lng: float):
    url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
    webbrowser.open(url)


class CoffeeFinderGUI:
    def __init__(self, root: tk.Tk, username: str = "User"):
        self.root = root
        self.username = username
        root.title(f"Coffee Finder - {username}")

        frm = ttk.Frame(root, padding=12)
        frm.grid(sticky="nsew")

        ttk.Label(frm, text="Lat,Lng").grid(row=0, column=0, sticky="w")
        self.latlng_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.latlng_var, width=30).grid(row=0, column=1, sticky="ew")

        ttk.Label(frm, text="Address").grid(row=1, column=0, sticky="w")
        self.address_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.address_var, width=30).grid(row=1, column=1, sticky="ew")

        ttk.Label(frm, text="Radius (m)").grid(row=2, column=0, sticky="w")
        self.radius_var = tk.IntVar(value=1000)
        ttk.Entry(frm, textvariable=self.radius_var, width=10).grid(row=2, column=1, sticky="w")

        ttk.Label(frm, text="Limit").grid(row=3, column=0, sticky="w")
        self.limit_var = tk.IntVar(value=10)
        ttk.Entry(frm, textvariable=self.limit_var, width=10).grid(row=3, column=1, sticky="w")

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(8, 4))
        self.search_btn = ttk.Button(btn_frame, text="Search", command=self.on_search)
        self.search_btn.pack(side="left")
        home_btn = ttk.Button(btn_frame, text="Load Home", command=self.load_home)
        home_btn.pack(side="left", padx=(8,0))
        save_home_btn = ttk.Button(btn_frame, text="Save as Home", command=self.save_as_home)
        save_home_btn.pack(side="left", padx=(4,0))
        self.settings_btn = ttk.Button(btn_frame, text="Settings", command=self.open_settings)
        self.settings_btn.pack(side="left", padx=(8,0))

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(frm, textvariable=self.status_var).grid(row=5, column=0, columnspan=2, sticky="w")

        # results listbox
        self.results = tk.Listbox(frm, width=60, height=12)
        self.results.grid(row=6, column=0, columnspan=2, pady=(8, 0))
        self.results.bind("<Double-Button-1>", self.on_open_map)
        self.results.bind("<Button-3>", self.on_right_click)  # Right-click context menu

        # result action buttons
        result_btn_frame = ttk.Frame(frm)
        result_btn_frame.grid(row=7, column=0, columnspan=2, pady=(4, 0))
        ttk.Button(result_btn_frame, text="Save Selected", command=self.save_selected_place).pack(side="left")
        ttk.Button(result_btn_frame, text="View Saved", command=self.view_saved_places).pack(side="left", padx=(4,0))

        # make layout expand nicely
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        frm.columnconfigure(1, weight=1)

        self.places = []
        
        # Auto-load home on startup if preference is set
        from .database import get_preference_bool
        if get_preference_bool("auto_load_home", False):
            self.root.after(100, self.load_home)

    def set_status(self, text: str):
        self.status_var.set(text)

    def on_search(self):
        latlng = self.latlng_var.get().strip()
        address = self.address_var.get().strip()
        radius = self.radius_var.get()
        limit = self.limit_var.get()

        # determine callable args
        def worker():
            try:
                self.search_btn.config(state="disabled")
                self.set_status("Searching...")
                if latlng:
                    lat, lng = parse_latlng(latlng)
                elif address:
                    # pass address string to choose_provider via main codepath: use geocoding in main; here we will
                    # attempt to use Nominatim directly for geocoding to keep GUI self-contained.
                    import requests
                    q = requests.get("https://nominatim.openstreetmap.org/search", params={"q": address, "format": "json", "limit": 1}, headers={"User-Agent": "coffee-finder-gui"}, timeout=10)
                    q.raise_for_status()
                    res = q.json()
                    if not res:
                        raise RuntimeError("Address not found")
                    lat = float(res[0]["lat"]) ; lng = float(res[0]["lon"])
                else:
                    # fallback to ip detection
                    import requests
                    r = requests.get("https://ipinfo.io/json", timeout=5)
                    r.raise_for_status()
                    loc = r.json().get("loc")
                    if not loc:
                        raise RuntimeError("Could not detect location")
                    lat, lng = parse_latlng(loc)

                places = choose_provider(lat, lng, radius=radius, limit=limit)
                # update UI in main thread
                self.root.after(0, lambda: self.update_results(places))
                self.root.after(0, lambda: self.set_status(f"Found {len(places)} places"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Search error", str(e)))
                self.root.after(0, lambda: self.set_status("Error"))
            finally:
                self.root.after(0, lambda: self.search_btn.config(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

    def update_results(self, places):
        self.places = places
        self.results.delete(0, tk.END)
        for p in places:
            name = p.get("name")
            addr = p.get("address") or ""
            dist = p.get("distance_m")
            label = f"{name} - {int(dist) if dist else '?'} m - {addr}"
            self.results.insert(tk.END, label)

    def open_settings(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Settings")
        dlg.transient(self.root)
        dlg.grab_set()

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
            messagebox.showinfo("Saved", "Settings saved.")
            dlg.destroy()

        btn_save = ttk.Button(dlg, text="Save", command=on_save)
        btn_save.grid(row=2, column=0, columnspan=2, pady=(6,12))
        
        # Auto-load home preference
        from .database import get_preference_bool, set_preference_bool
        ttk.Label(dlg, text="Auto-load home on startup").grid(row=3, column=0, sticky="w", padx=8, pady=6)
        auto_home_var = tk.BooleanVar(value=get_preference_bool("auto_load_home", False))
        ttk.Checkbutton(dlg, variable=auto_home_var).grid(row=3, column=1, sticky="w", padx=8, pady=6)
        
        # Update on_save to also save preferences
        orig_on_save = on_save
        def on_save_with_prefs():
            orig_on_save()
            set_preference_bool("auto_load_home", auto_home_var.get())
        
        btn_save.config(command=on_save_with_prefs)

    def on_open_map(self, event):
        sel = self.results.curselection()
        if not sel:
            return
        idx = sel[0]
        p = self.places[idx]
        lat = p.get("lat")
        lng = p.get("lng")
        if lat and lng:
            _open_map(lat, lng)

    def load_home(self):
        """Load saved home location into search field."""
        home = get_home_location()
        if home:
            self.latlng_var.set(f"{home['lat']},{home['lng']}")
            self.address_var.set("")
            self.set_status(f"Loaded home: {home['name']}")
        else:
            messagebox.showinfo("No Home", "Home location not saved yet. Search and click 'Save as Home'.")

    def save_as_home(self):
        """Save current location in search field as home."""
        latlng = self.latlng_var.get().strip()
        address = self.address_var.get().strip()
        if not latlng and not address:
            messagebox.showwarning("No Location", "Enter location (lat,lng or address) first.")
            return
        try:
            if latlng:
                lat, lng = parse_latlng(latlng)
            elif address:
                import requests
                q = requests.get("https://nominatim.openstreetmap.org/search", params={"q": address, "format": "json", "limit": 1}, headers={"User-Agent": "coffee-finder-gui"}, timeout=10)
                q.raise_for_status()
                res = q.json()
                if not res:
                    raise RuntimeError("Address not found")
                lat = float(res[0]["lat"])
                lng = float(res[0]["lon"])
            set_home_location(lat, lng, address or latlng)
            messagebox.showinfo("Saved", f"Home location saved: {lat},{lng}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save home: {str(e)}")

    def save_selected_place(self):
        """Save selected result as favorite."""
        sel = self.results.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a coffee place first.")
            return
        idx = sel[0]
        p = self.places[idx]
        try:
            save_place(p.get("name"), p.get("lat"), p.get("lng"), 
                      address=p.get("address") or "", rating=p.get("rating"))
            messagebox.showinfo("Saved", f"Saved: {p.get('name')}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")

    def view_saved_places(self):
        """Show dialog with saved favorite places."""
        saved = get_saved_places()
        if not saved:
            messagebox.showinfo("No Saved Places", "No favorites yet. Save places from search results.")
            return
        
        dlg = tk.Toplevel(self.root)
        dlg.title("Saved Places")
        dlg.transient(self.root)
        dlg.resizable(True, True)
        
        # Listbox frame
        list_frame = ttk.Frame(dlg)
        list_frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        lb = tk.Listbox(list_frame, width=60, height=10)
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=lb.yview)
        lb.config(yscrollcommand=sb.set)
        lb.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        for p in saved:
            label = f"{p['name']} - {p['address'][:50] if p['address'] else 'N/A'}"
            lb.insert(tk.END, label)
        
        # Button frame
        btn_frame = ttk.Frame(dlg)
        btn_frame.pack(fill="x", padx=8, pady=4)
        
        def on_delete():
            sel = lb.curselection()
            if sel:
                idx = sel[0]
                delete_saved_place(saved[idx]['id'])
                lb.delete(idx)
                messagebox.showinfo("Deleted", "Place removed from favorites.")
        
        ttk.Button(btn_frame, text="Delete Selected", command=on_delete).pack(side="left")
        ttk.Button(btn_frame, text="Close", command=dlg.destroy).pack(side="right")

    def on_right_click(self, event):
        """Right-click context menu on results."""
        sel_idx = self.results.nearest(event.y)
        if sel_idx < 0 or sel_idx >= len(self.places):
            return
        self.results.selection_clear(0, tk.END)
        self.results.selection_set(sel_idx)
        
        menu = tk.Menu(self.root, tearoff=False)
        menu.add_command(label="Open in Maps", command=lambda: self._open_selected_map())
        menu.add_command(label="Save as Favorite", command=self.save_selected_place)
        menu.post(event.x_root, event.y_root)

    def _open_selected_map(self):
        """Open selected place in Google Maps."""
        sel = self.results.curselection()
        if sel:
            p = self.places[sel[0]]
            if p.get("lat") and p.get("lng"):
                _open_map(p.get("lat"), p.get("lng"))


def main(argv: Optional[list] = None):
    # Show login window
    authenticated, username, root = show_login()
    if not authenticated:
        return
    
    if root is None:
        root = tk.Tk()
    app = CoffeeFinderGUI(root, username)
    root.mainloop()


if __name__ == "__main__":
    main()
