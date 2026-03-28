#TODO Adapt historic to look at last three years
# additional params not actually passed

import requests
import os
from dotenv import load_dotenv

load_dotenv()
EBIRD_TOKEN = os.getenv("EBIRD_TOKEN")

BASE_URL = "https://api.ebird.org/v2"

def get_recent_observations(lat, lng, days_back: int = 7, max_results: int = 10):
    """
    Fetch recent observations for a region.
    region_code: e.g. "US-CT"
    days_back: how many days to look back (max 30)
    max_results: cap the number of results returned
    """
    url = f"{BASE_URL}/data/obs/geo/recent?lat={lat}&lng={lng}"
    headers = {"X-eBirdApiToken": EBIRD_TOKEN}
    params = {
        "back": days_back,
        "maxResults": max_results,
        "includeProvisional": False
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return None, f"eBird API error: {response.status_code}"
    
    if response.status_code == 429:
        return None, "eBird rate limit hit. Try again later."

    observations = response.json()

    if not observations:
        return [], None

    return observations, None

def get_rarebirds(lat, lng, days_back: int = 7, max_results: int = 10):
    """
    Fetch recent NOTABLE observations for a region.
    region_code: e.g. "US-CT"
    days_back: how many days to look back (max 30)
    max_results: cap the number of results returned
    """
    url = f"{BASE_URL}/data/obs/geo/recent/notable?lat={lat}&lng={lng}"
    headers = {"X-eBirdApiToken": EBIRD_TOKEN}
    params = {
        "back": days_back,
        "maxResults": max_results,
        "includeProvisional": False
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return None, f"eBird API error: {response.status_code}"

    if response.status_code == 429:
        return None, "eBird rate limit hit. Try again later."

    observations = response.json()

    if not observations:
        return [], None

    return observations, None

def get_historicbirds(region_code: str, y: int, m: int, d: int, days_back: int = 7, max_results: int = 10):
    """
    Fetch HISTORIC observations for a region.
    region_code: e.g. "US-CT"
    days_back: how many days to look back (max 30)
    max_results: cap the number of results returned
    """
    url = f"{BASE_URL}/data/obs/{region_code}/historic/{y}/{m}/{d}"
    print(url)
    headers = {"X-eBirdApiToken": EBIRD_TOKEN}
    params = {
        "back": days_back,
        "maxResults": max_results,
        "includeProvisional": False
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return None, f"eBird API error: {response.status_code}"

    if response.status_code == 429:
        return None, "eBird rate limit hit. Try again later."

    observations = response.json()

    if not observations:
        return [], None

    return observations, None


def format_observations(observations: list) -> str:
    """Turn raw eBird JSON into a readable Discord message."""
    if not observations:
        return "No recent observations found for your area."

    lines = [f"**Recent bird sightings (past 7 days)**\n"]
    for obs in observations:
        name = obs.get("comName", "Unknown")
        location = obs.get("locName", "Unknown location")
        date = obs.get("obsDt", "")
        count = obs.get("howMany", "")
        count_str = f" ({count})" if count else ""
        lines.append(f"- {name}{count_str} — {location} on {date}")

    return "\n".join(lines)






