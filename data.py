import json
import os
import pandas as pd
from datetime import datetime
import pytz

LOCATION_FILE = "user_location.json"

def save_location(user_id, timezone_str):
    """Save a user's timezone. Example timezone_str: 'America/New_York'"""
    try:
        pytz.timezone(timezone_str)  # validates the timezone
    except pytz.exceptions.UnknownTimeZoneError:
        return False, f"Unknown timezone: {timezone_str}. Use a format like America/New_York"
    
    data = {}
    if os.path.exists(LOCATION_FILE):
        with open(LOCATION_FILE, "r") as f:
            data = json.load(f)
    
    data[str(user_id)] = timezone_str
    
    with open(LOCATION_FILE, "w") as f:
        json.dump(data, f)
    
    return True, f"Location set to {timezone_str}"

def get_location(user_id):
    """Retrieve a user's saved timezone."""
    if not os.path.exists(LOCATION_FILE):
        return None
    with open(LOCATION_FILE, "r") as f:
        data = json.load(f)
    return data.get(str(user_id))
