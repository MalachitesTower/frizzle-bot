#TODO Adapt historic to look at last three years
# additional params not actually passed

import requests
import os
from dotenv import load_dotenv
from settings import DAYS_BACK, MAX_RESULTS
from utils import _build_stats

load_dotenv()
EBIRD_TOKEN = os.getenv("EBIRD_TOKEN")

BASE_URL = "https://api.ebird.org/v2"

def get_ebird_recent_obs(lat, lng, days_back: int = DAYS_BACK, max_results: int = MAX_RESULTS, stats_only: bool = False):
    """
    Fetch recent observations for a region.
    region_code: e.g. "US-CT"
    days_back: how many days to look back (max 30)
    max_results: cap the number of results returned
    stats_only: return summary statistics instead of raw observations
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

    if stats_only:
        return _build_stats(observations, {"lat": lat, "lng": lng, "days_back": days_back, "max_results": max_results}, "obsDt", "locName", response_url=response.url)

    return observations, None

def get_ebird_rare_birds(lat, lng, days_back: int = DAYS_BACK, max_results: int = MAX_RESULTS, stats_only: bool = False):
    """
    Fetch recent NOTABLE observations for a region.
    region_code: e.g. "US-CT"
    days_back: how many days to look back (max 30)
    max_results: cap the number of results returned
    stats_only: return summary statistics instead of raw observations
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

    if stats_only:
        return _build_stats(observations, {"lat": lat, "lng": lng, "days_back": days_back, "max_results": max_results}, "obsDt", "locName", response_url=response.url)

    return observations, None

def get_ebird_historic_birds(region_code: str, y: int, m: int, d: int, days_back: int = DAYS_BACK, max_results: int = MAX_RESULTS, stats_only: bool = False):
    """
    Fetch HISTORIC observations for a region.
    region_code: e.g. "US-CT"
    days_back: how many days to look back (max 30)
    max_results: cap the number of results returned
    stats_only: return summary statistics instead of raw observations
    """
    url = f"{BASE_URL}/data/obs/{region_code}/historic/{y}/{m}/{d}"
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


    if stats_only:
        return _build_stats(observations, {"region_code": region_code, "y": y, "m": m, "d": d, "days_back": days_back, "max_results": max_results}, "obsDt", "locName", response_url=response.url)

    return observations, None


def format_ebird_obs(observations: list, title: str = "Recent bird sightings (past 7 days)") -> str:
    """Turn raw eBird JSON into a readable Discord message."""
    if not observations:
        return "No recent observations found for your area."

    lines = [f"**{title}**\n"]
    for obs in observations:
        name = obs.get("comName", "Unknown")
        location = obs.get("locName", "Unknown location")
        date = obs.get("obsDt", "")
        count = obs.get("howMany", "")
        count_str = f" ({count})" if count else ""
        lines.append(f"- {name}{count_str} — {location} on {date}")

    return "\n".join(lines)






