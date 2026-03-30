import requests
import time
from datetime import date, timedelta
from settings import DAYS_BACK, MAX_RESULTS, RADIUS_KM
from utils import _build_stats

BASE_URL = "https://api.inaturalist.org/v1"


def _fetch_inat_paginated(url, params, paginate=True, max_results=MAX_RESULTS, max_pages=5):
    """
    Execute one or more iNaturalist API requests and return collected results.
    Returns (observations, total_results, last_response_url, pages_fetched, error_string).
    """
    if not paginate:
        response = requests.get(url, params=params)

        if response.status_code == 429:
            return None, 0, None, 1, "iNaturalist rate limit hit. Try again later."
        if response.status_code != 200:
            return None, 0, None, 1, f"iNaturalist API error: {response.status_code}"

        data = response.json()
        total_results = data.get("total_results", 0)
        print(f"Total results available: {total_results}")
        return data.get("results", []), total_results, response.url, 1, None
    if max_pages < max_results/200: #200 is hard coded max per page result
        max_pages_temp = round(max_results/200)
    else: 
        max_pages_temp = max_pages

    paged_params = dict(params)
    all_observations = []
    total_results = 0
    page = 0
    for page in range(1, max_pages + 1):
        paged_params["page"] = page
        response = requests.get(url, params=paged_params)

        if response.status_code == 429:
            return None, 0, None, page, "iNaturalist rate limit hit. Try again later."
        if response.status_code != 200:
            return None, 0, None, page, f"iNaturalist API error: {response.status_code}"

        data = response.json()
        total_results = data.get("total_results", 0)
        if page == 1:
            print(f"Total results available: {total_results}")

        all_observations.extend(data.get("results", []))

        if len(all_observations) >= total_results:
            break
        time.sleep(1)

    return all_observations, total_results, response.url, page, None


def get_inat_recent_obs(lat, lng, radius_km: int = RADIUS_KM, days_back: int = DAYS_BACK, stats_only: bool = False, paginate: bool = True):
    """
    Fetch recent observations near a location from iNaturalist.
    lat/lng: coordinates
    radius_km: search radius in kilometers
    days_back: how many days to look back
    max_results: cap the number of results returned
    stats_only: return summary statistics instead of raw observations
    paginate: if True, fetch all pages up to max_pages=5
    """
    d1 = (date.today() - timedelta(days=days_back)).isoformat()

    url = f"{BASE_URL}/observations"
    params = {
        "lat": lat,
        "lng": lng,
        "radius": radius_km,
        "d1": d1,
        "per_page": 200,
        "order": "desc",
        "order_by": "observed_on",
        "quality_grade": "research",
    }

    observations, total_results, response_url, pages_fetched, err = _fetch_inat_paginated(url, params, paginate=paginate)
    if err:
        return None, err

    if stats_only:
        return _build_stats(observations, {"lat": lat, "lng": lng, "radius_km": radius_km, "days_back": days_back, "max_results": MAX_RESULTS}, "observed_on", "place_guess", response_url=response_url, pages_fetched=pages_fetched)

    return observations, None


def get_inat_rare_obs(lat, lng, radius_km: int = RADIUS_KM, days_back: int = DAYS_BACK, stats_only: bool = False, paginate: bool = True):
    """
    Fetch recent threatened species observations near a location from iNaturalist.
    lat/lng: coordinates
    radius_km: search radius in kilometers
    days_back: how many days to look back
    max_results: cap the number of results returned
    stats_only: return summary statistics instead of raw observations
    paginate: if True, fetch all pages up to max_pages=5
    """
    d1 = (date.today() - timedelta(days=days_back)).isoformat()

    url = f"{BASE_URL}/observations"
    params = {
        "lat": lat,
        "lng": lng,
        "radius": radius_km,
        "d1": d1,
        "per_page": 200,
        "order": "desc",
        "order_by": "observed_on",
        "quality_grade": "research",
        "threatened": "true",
    }

    observations, total_results, response_url, pages_fetched, err = _fetch_inat_paginated(url, params, paginate=paginate)
    if err:
        return None, err

    if stats_only:
        return _build_stats(observations, {"lat": lat, "lng": lng, "radius_km": radius_km, "days_back": days_back, "max_results": MAX_RESULTS}, "observed_on", "place_guess", response_url=response_url, pages_fetched=pages_fetched)

    return observations, None


def get_inat_historic_obs(lat, lng, radius_km: int = RADIUS_KM, days_back: int = DAYS_BACK, stats_only: bool = False, paginate: bool = True):
    """
    Fetch research-grade observations from the same week one year ago near a location.
    lat/lng: coordinates
    radius_km: search radius in kilometers
    days_back: width of the date window (default 7)
    max_results: cap the number of results returned
    stats_only: return summary statistics instead of raw observations
    paginate: if True, fetch all pages up to max_pages=5
    """
    today = date.today()
    try:
        d2 = today.replace(year=today.year - 1)
    except ValueError:
        d2 = today.replace(year=today.year - 1, day=28)
    d1 = (d2 - timedelta(days=days_back)).isoformat()
    d2 = d2.isoformat()

    url = f"{BASE_URL}/observations"
    params = {
        "lat": lat,
        "lng": lng,
        "radius": radius_km,
        "d1": d1,
        "d2": d2,
        "per_page": 200,
        "order": "desc",
        "order_by": "observed_on",
        "quality_grade": "research",
    }

    observations, total_results, response_url, pages_fetched, err = _fetch_inat_paginated(url, params, paginate=paginate)
    if err:
        return None, err

    if stats_only:
        return _build_stats(observations, {"lat": lat, "lng": lng, "radius_km": radius_km, "d1": d1, "d2": d2, "max_results": MAX_RESULTS}, "observed_on", "place_guess", response_url=response_url, pages_fetched=pages_fetched)

    return observations, None


def format_inat_obs(observations: list, title: str = "Recent nature observations near you") -> str:
    """Turn raw iNaturalist JSON into a readable Discord message."""
    if not observations:
        return "No recent observations found for your area."

    lines = [f"**{title}**\n"]
    for obs in observations:
        taxon = obs.get("taxon") or {}
        name = taxon.get("preferred_common_name") or taxon.get("name", "Unknown species")
        location = obs.get("place_guess", "Unknown location")
        observed_on = obs.get("observed_on", "")
        lines.append(f"- {name} — {location} on {observed_on}")

    return "\n".join(lines)
