import json
import os
import re
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from timezonefinder import TimezoneFinder

LOCATION_FILE = "user_location.json"
geolocoder = Nominatim(user_agent="frizzle-bot")
tf = TimezoneFinder()

def _parse_input(raw: str):
    """
    Accept coordinates, zip, or place name.
    Always returns a geopy Location object or None.
    """
    raw = raw.strip()

    # Check for coordinate format: 41.76,-72.68 or 41.76 -72.68
    coord_pattern = r'^(-?\d+\.?\d*)[,\s]+(-?\d+\.?\d*)$'
    match = re.match(coord_pattern, raw)
    if match:
        lat, lng = float(match.group(1)), float(match.group(2))
        # reverse geocode to get a display name
        try:
            location = geolocoder.reverse((lat, lng), language="en")
            return location
        except (GeocoderTimedOut, GeocoderServiceError):
            return None

    # Everything else (city, zip, state) goes through forward geocoding
    try:
        location = geolocoder.geocode(raw, addressdetails=True, language="en")
        return location
    except (GeocoderTimedOut, GeocoderServiceError):
        return None

def _extract_state_code(raw_address: dict) -> str:
    """Pull two-letter state code from geopy address details."""
    state = raw_address.get("state", "")
    # geopy returns full state name, so we map it
    state_map = {
          "Alabama": "AL",
          "Alaska": "AK",
          "Arizona": "AZ",
          "Arkansas": "AR",
          "California": "CA",
          "Colorado": "CO",
          "Connecticut": "CT",
          "Delaware": "DE",
          "Florida": "FL",
          "Georgia": "GA",
          "Hawaii": "HI",
          "Idaho": "ID",
          "Illinois": "IL",
          "Indiana": "IN",
          "Iowa": "IA",
          "Kansas": "KS",
          "Kentucky": "KY",
          "Louisiana": "LA",
          "Maine": "ME",
          "Maryland": "MD",
          "Massachusetts": "MA",
          "Michigan": "MI",
          "Minnesota": "MN",
          "Mississippi": "MS",
          "Missouri": "MO",
          "Montana": "MT",
          "Nebraska": "NE",
          "Nevada": "NV",
          "New Hampshire": "NH",
          "New Jersey": "NJ",
          "New Mexico": "NM",
          "New York": "NY",
          "North Carolina": "NC",
          "North Dakota": "ND",
          "Ohio": "OH",
          "Oklahoma": "OK",
          "Oregon": "OR",
          "Pennsylvania": "PA",
          "Rhode Island": "RI",
          "South Carolina": "SC",
          "South Dakota": "SD",
          "Tennessee": "TN",
          "Texas": "TX",
          "Utah": "UT",
          "Vermont": "VT",
          "Virginia": "VA",
          "Washington": "WA",
          "West Virginia": "WV",
          "Wisconsin": "WI",
          "Wyoming": "WY"}
    return state_map.get(state, state[:2].upper())

def resolve_location(raw_input: str):
    """
    Main entry point. Takes any location string, returns a 
    normalized dict or an error string.
    """
    location = _parse_input(raw_input)

    if location is None:
        return None, f"Could not resolve '{raw_input}' to a location. Try a city name, ZIP code, or coordinates."

    lat = location.latitude
    lng = location.longitude
    address = location.raw.get("address", {})

    # build display name
    city = address.get("city") or address.get("town") or address.get("village", "")
    state = address.get("state", "")
    country_code = address.get("country_code", "").upper()
    display = ", ".join(filter(None, [city, state, country_code if country_code != "US" else ""]))
    if not display:
        display = location.address.split(",")[0]

    # derive timezone from coordinates
    timezone = tf.timezone_at(lat=lat, lng=lng)

    # derive state code for eBird-style region codes
    state_code = _extract_state_code(address)

    normalized = {
        "display": display,
        "lat": round(lat, 4),
        "lng": round(lng, 4),
        "timezone": timezone,
        "state": state_code,
        "country": country_code,
        "raw_address": address  # keep this for debugging
    }

    return normalized, None

def save_location(user_id: int, raw_input: str):
    """Resolve and save a user's location. Returns (success, message)."""
    normalized, error = resolve_location(raw_input)
    if error:
        return False, error

    data = {}
    if os.path.exists(LOCATION_FILE):
        with open(LOCATION_FILE, "r") as f:
            data = json.load(f)

    data[str(user_id)] = normalized

    with open(LOCATION_FILE, "w") as f:
        json.dump(data, f, indent=2)

    return True, f"Location set to **{normalized['display']}** (timezone: {normalized['timezone']})"

def get_location(user_id: int):
    """Retrieve stored location dict for a user, or None."""
    if not os.path.exists(LOCATION_FILE):
        return None
    with open(LOCATION_FILE, "r") as f:
        data = json.load(f)
    return data.get(str(user_id))

# --- Converters for specific APIs ---

def to_ebird_region(loc: dict) -> str:
    """Returns eBird region code. Country-level if no state."""
    if loc.get("state") and loc.get("country") == "US":
        return f"US-{loc['state']}"
    return loc.get("country", "US")

def to_latlng(loc: dict) -> tuple:
    """Returns (lat, lng) tuple."""
    return (loc["lat"], loc["lng"])

def to_timezone(loc: dict) -> str:
    """Returns IANA timezone string."""
    return loc.get("timezone", "America/New_York")

def to_inaturalist_params(loc: dict, radius_km: int = 50) -> dict:
    """Returns iNaturalist API params for location-based queries."""
    return {
        "lat": loc["lat"],
        "lng": loc["lng"],
        "radius": radius_km
    }
