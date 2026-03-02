# Coffee Finder

This project was created with GitHub Copilot.

Find nearby coffee shops and cafes from your current location, an address, or lat/lng coordinates. Coffee Finder supports three interfaces: a command-line tool, graphical desktop app, and a system tray icon. It uses OpenStreetMap Overpass API by default and optionally integrates with Google Places for enhanced ratings and reviews.

## Features

- **User accounts**: Create an account with email, username, and password to store your preferences securely
- **Multiple interfaces**: CLI and GUI (Tkinter)
- **Flexible location input**: GPS coordinates, address, or auto-detect via IP geolocation
- **Dual data provider strategy**: 
  - OpenStreetMap Overpass API (free, no key required, with local caching)
  - Google Places API (optional, requires API key, returns ratings)
- **Persistent cache**: Results cached locally for 24 hours (configurable)
- **Configuration UI**: Adjust cache TTL and Google API key from settings dialog
- **Distance filtering**: Specify search radius in meters
- **Result limiting**: Control how many results to display
- **Map integration**: Double-click results in GUI to open in Google Maps

## Installation

### Requirements
- Python 3.8+
- pip

### Quick Start

1. Clone or download the project:
```bash
cd /path/to/coffee-finder
```

2. Install dependencies:
```bash
python -m pip install -r requirements.txt
```

3. (Optional) Install the package in editable mode for console commands:
```bash
python -m pip install -e .
```

### Standalone Executables (No Python Required)

For end users who don't have Python installed, you can build standalone executables using PyInstaller.

#### Windows

1. Install build dependencies:
```bash
python -m pip install -r requirements-dev.txt
```

2. Build executables:
```bash
build_installer.bat
```

This creates two .exe files in `dist/`:
- `coffee-finder.exe` - CLI with console
- `coffee-finder-gui.exe` - GUI application (main)

**Optional: Create a Windows installer (MSI/EXE)**

If you have Inno Setup installed (download from https://jrsoftware.org/):
```bash
iscc coffee-finder.iss
```

This creates `dist/coffee-finder-setup.exe` with uninstaller and start menu shortcuts.

#### macOS / Linux

1. Install build dependencies:
```bash
python -m pip install -r requirements-dev.txt
```

2. Build executables:
```bash
bash build_installer.sh
```

This creates standalone executables in `dist/`:
- `coffee-finder` - CLI
- `coffee-finder-gui` - GUI application (main)

**macOS App Bundle**

To create a proper macOS .app bundle:
```bash
python -m PyInstaller --onefile --windowed --name "Coffee Finder" coffee_finder/gui.py
```

The result will be in `dist/Coffee Finder.app`.

**Linux System-Wide Installation**

```bash
sudo cp dist/coffee-finder* /usr/local/bin/
```

Or create a .deb package with tools like `fpm`:
```bash
fpm -s dir -t deb -n coffee-finder -v 0.1.0 -C dist coffee-finder=/usr/local/bin/

## Usage

### Command-Line Interface (CLI)

Use the CLI for quick, scriptable coffee searches.

#### Auto-detect location (IP-based):
```bash
python -m coffee_finder
```

#### Search by coordinates:
```bash
python -m coffee_finder --latlng 40.7128,-74.0060 --radius 1500 --limit 5
```

#### Search by address (geocoded via Nominatim):
```bash
python -m coffee_finder --address "1600 Amphitheatre Parkway, Mountain View, CA" --limit 20
```

#### Search by explicit lat/lng:
```bash
python -m coffee_finder --lat 51.5074 --lng -0.1278 --radius 2000
```

#### Filter by minimum rating (Google Places only):
```bash
python -m coffee_finder --latlng 40.7128,-74.0060 --min-rating 4.0 --limit 10
```

#### CLI Options
```
--latlng LAT,LNG          Search location as "latitude,longitude"
--lat LAT --lng LNG       Alternative way to specify coordinates
--address ADDRESS         Address to geocode (uses Nominatim API)
--radius METERS           Search radius in meters (default: 1000)
--limit COUNT             Maximum results to return (default: 10)
--min-rating RATING       Minimum rating filter (Google Places only)
```

### Graphical User Interface (GUI)

A Tkinter-based desktop application with search and settings dialogs.

#### Launch the GUI:
```bash
python -m coffee_finder.gui
```

**Login & Registration:**
When you launch the GUI for the first time, you'll be prompted to create an account or log in:
- **Create Account**: Enter your email, choose a username (min 3 characters), and set a password (min 6 characters)
- **Login**: Use your username and password to access the app
- Your credentials are securely stored locally in the app's database
- Multi-user support: Each account maintains separate home location and saved places

**Main Features:**
- Input fields for lat/lng, address, radius, and result limit
- Real-time search with status updates
- Results displayed in a scrollable list
- Double-click any result to open location in Google Maps
- Right-click context menu on results to save or open in Maps

**Home Location Management:**
- **Load Home**: Quickly load your saved home location into the search field
- **Save as Home**: Save the current search location as your home for quick future access
- **Auto-load on startup**: Optional preference to automatically load home location when GUI starts

**Saved Favorites:**
- **Save Selected**: Save any coffee place from search results to your personal database
- **View Saved**: Browse all your favorite coffee places with an option to delete
- Access saved places from the results action buttons

**Settings Dialog:**
- **Cache TTL (hours)**: How long to cache Overpass results (default: 24)
- **Google Places API Key**: Optional key for better ratings and reviews
- **Auto-load home on startup**: Enable to automatically load home location on launch

### System Tray Integration

A minimal system tray icon with quick access to the GUI and settings.

#### Launch the tray app:
```bash
python -m coffee_finder.tray
```

**Login:**
On first launch, you'll be prompted to create an account or log in with your credentials.

**Tray Menu:**
- **Open**: Bring up the main GUI window
- **Settings**: Configure cache TTL and API key
- **Quit**: Exit the application

The app starts hidden; **right‑click** (or use the menu key) on the tray icon to access the menu. Left-click no longer launches the GUI directly, preventing accidental opens.

## Configuration

### User Accounts

Every user must create an account to use Coffee Finder's GUI.

**Account requirements:**
- **Email**: Valid email address (used to verify account uniqueness)
- **Username**: 3+ characters (must be unique)
- **Password**: 6+ characters (hashed and stored securely)

**Account management:**
- Each account has separate home location, saved places, and preferences
- Accounts are stored locally in `auth.db` in the app's data directory
- Passwords are hashed using SHA-256; plain-text passwords are never stored
- To delete your account and all associated data, delete the `auth.db` file and restart

**Data privacy:**
- All account data is stored locally on your machine
- No account information is transmitted to external servers
- The app is fully offline-capable after login

### Google Places API (Optional)

To enable Google Places features (ratings, reviews, better coverage):

1. [Create a Google Cloud project](https://console.cloud.google.com/)
2. Enable the "Places API"
3. Create an API key with appropriate restrictions
4. Set your key in one of two ways:

**Environment variable (CLI only):**
```bash
export GOOGLE_PLACES_API_KEY=your_api_key_here
python -m coffee_finder --latlng 40.7128,-74.0060
```

**Via settings dialog (GUI or System Tray):**
- Open the Settings menu
- Enter your API key in the "Google Places API Key" field
- Click Save

### Cache Configuration

Local query results are cached in:
- **Windows**: `%LOCALAPPDATA%\coffee_finder\cache.db`
- **Linux/macOS**: `~/.cache/coffee_finder/cache.db`

Configuration is stored in:
- **Windows**: `%LOCALAPPDATA%\coffee_finder\config.json`
- **Linux/macOS**: `~/.config/coffee_finder/config.json`

Adjust cache TTL via the settings dialog (default: 24 hours).

### User Database

Your home location, saved favorite coffee places, and preferences are stored in a local SQLite database:
- **Windows**: `%LOCALAPPDATA%\coffee_finder\user.db`
- **Linux/macOS**: `~/.local/share/coffee_finder/user.db`

**Data stored:**
- **Home location**: Your saved home address for quick access
- **Saved places**: Favorite coffee shops with names, locations, and ratings
- **Preferences**: UI preferences like auto-load home on startup

The database is fully private and stored locally on your machine—no data is ever sent to external servers.

To clear your saved data, delete the `user.db` file and restart the application.

## Examples

### Find top-rated cafes nearby:
```bash
python -m coffee_finder --min-rating 4.5 --limit 10
```
*(Requires Google Places API key)*

### Search a wider area:
```bash
python -m coffee_finder --address "Paris, France" --radius 5000 --limit 15
```

### Batch search multiple locations (scripting):
```bash
for addr in "New York" "Los Angeles" "Chicago"; do
  echo "=== $addr ==="
  python -m coffee_finder --address "$addr" --limit 3
done
```

## Screenshot Descriptions

The GUI provides:
- A search panel with fields for location input (coordinates, address, radius, limit)
- A Search button and Settings button in the toolbar
- A results list showing coffee shop names, distances, and addresses
- Double-click integration with Google Maps for each result

The tray icon appears in the system notification area with a coffee-bean silhouette and a three-item menu.

## Troubleshooting

### "No coffee places found"
- Try increasing the `--radius` (default is 1000 meters)
- Check internet connectivity
- Switch between providers (Overpass vs. Google Places)

### "Address not found"
- Nominatim geocoding is used for address resolution and may not recognize very local addresses
- Try rephrasing the address or use coordinates instead
- Check spelling and include city/country when needed

### Google Places API errors
- Verify your API key is valid and has Places API enabled
- Check that your Google Cloud project has billing enabled
- Ensure the key isn't restricted to specific IPs

### Slow searches
- Overpass API can be slow during heavy load; results are cached locally
- Cache is stored for 24 hours by default; adjust in Settings
- Google Places is generally faster if you have an API key

### Cache issues
- Delete `cache.db` to clear all cached results
- On **Windows**: Delete `%LOCALAPPDATA%\coffee_finder\cache.db`
- On **Linux/macOS**: Delete `~/.cache/coffee_finder/cache.db`

## Development

### Running Tests
```bash
pytest -v tests/
```

### Adding Features
The codebase is organized as:
- `coffee_finder/main.py` - CLI entry point
- `coffee_finder/gui.py` - Tkinter GUI
- `coffee_finder/tray.py` - System tray integration
- `coffee_finder/login.py` - Login/registration UI
- `coffee_finder/auth.py` - User authentication logic
- `coffee_finder/database.py` - User data persistence (home, favorites, preferences)
- `coffee_finder/providers.py` - Data providers (Overpass, Google Places)
- `coffee_finder/cache.py` - Local caching layer
- `coffee_finder/config.py` - Configuration persistence
- `coffee_finder/utils.py` - Utilities (distance calculation, parsing)

### Setting Up Development Environment
```bash
python -m pip install -r requirements.txt
python -m pytest tests/
```

## Notes

- **Overpass API**: Free, no API key required, but slower and no ratings
- **Google Places API**: Faster, includes ratings/reviews, but requires API key and may incur costs
- The app automatically prefers Google Places if an API key is available
- Results are cached locally to reduce API calls and improve responsiveness
- Distance calculations use the Haversine formula for accuracy
