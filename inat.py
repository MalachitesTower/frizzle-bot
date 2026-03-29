import requests
from datetime import date, timedelta
from settings import DAYS_BACK, MAX_RESULTS, RADIUS_KM

BASE_URL = "https://api.inaturalist.org/v1"

def get_inat_recent_obs(lat, lng, radius_km: int = RADIUS_KM, days_back: int = DAYS_BACK, max_results: int = MAX_RESULTS, stats_only: bool = False):
    """
    Fetch recent observations near a location from iNaturalist.
    lat/lng: coordinates
    radius_km: search radius in kilometers
    days_back: how many days to look back
    max_results: cap the number of results returned
    stats_only: return summary statistics instead of raw observations
    """
    d1 = (date.today() - timedelta(days=days_back)).isoformat()

    url = f"{BASE_URL}/observations"
    params = {
        "lat": lat,
        "lng": lng,
        "radius": radius_km,
        "d1": d1,
        "per_page": max_results,
        "order": "desc",
        "order_by": "observed_on",
        "quality_grade": "research",
    }

    response = requests.get(url, params=params)

    if response.status_code == 429:
        return None, "iNaturalist rate limit hit. Try again later."

    if response.status_code != 200:
        return None, f"iNaturalist API error: {response.status_code}"

    data = response.json()
    observations = data.get("results", [])

    if stats_only:
        print(f"URL: {response.url}")
        print(f"Results returned: {len(observations)}") 
        dates = sorted(obs.get("observed_on", "") for obs in observations if obs.get("observed_on"))
        locations = {obs.get("place_guess") for obs in observations if obs.get("place_guess")}
        return {
            "params": {"lat": lat, "lng": lng, "radius_km": radius_km, "days_back": days_back, "max_results": max_results},
            "num_observations": len(observations),
            "num_locations": len(locations),
            "date_range": {"earliest": dates[0], "latest": dates[-1]} if dates else {}
        }, None

    return observations, None


def get_inat_historic_obs(lat, lng, radius_km: int = RADIUS_KM, days_back: int = DAYS_BACK, max_results: int = MAX_RESULTS, stats_only: bool = False):
    """
    Fetch research-grade observations from the same week one year ago near a location.
    lat/lng: coordinates
    radius_km: search radius in kilometers
    days_back: width of the date window (default 7)
    max_results: cap the number of results returned
    stats_only: return summary statistics instead of raw observations
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
        "per_page": max_results,
        "order": "desc",
        "order_by": "observed_on",
        "quality_grade": "research",
    }

    response = requests.get(url, params=params)

    if response.status_code == 429:
        return None, "iNaturalist rate limit hit. Try again later."

    if response.status_code != 200:
        return None, f"iNaturalist API error: {response.status_code}"

    data = response.json()
    observations = data.get("results", [])

    if stats_only:
        print(f"URL: {response.url}")
        print(f"Results returned: {len(observations)}")
        dates = sorted(obs.get("observed_on", "") for obs in observations if obs.get("observed_on"))
        locations = {obs.get("place_guess") for obs in observations if obs.get("place_guess")}
        return {
            "params": {"lat": lat, "lng": lng, "radius_km": radius_km, "d1": d1, "d2": d2, "max_results": max_results},
            "num_observations": len(observations),
            "num_locations": len(locations),
            "date_range": {"earliest": dates[0], "latest": dates[-1]} if dates else {}
        }, None

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
