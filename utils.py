def _build_stats(observations, params, date_field, location_field, response_url=None, pages_fetched=None):
    """
    Build a stats dict from a list of observations.
    date_field: key used to extract observation date (e.g. 'obsDt' or 'observed_on')
    location_field: key used to extract location name (e.g. 'locName' or 'place_guess')
    response_url: the final request URL, printed for debugging
    pages_fetched: included in output only when provided (iNaturalist paginated calls)
    Returns (stats_dict, None).
    """
    print(f"URL: {response_url}")
    if pages_fetched is not None:
        print(f"Pages fetched: {pages_fetched}")
    print(f"Results returned: {len(observations)}")

    dates = sorted(obs.get(date_field, "") for obs in observations if obs.get(date_field))
    locations = {obs.get(location_field) for obs in observations if obs.get(location_field)}

    stats = {
        "params": params,
        "num_observations": len(observations),
        "num_locations": len(locations),
        "date_range": {"earliest": dates[0], "latest": dates[-1]} if dates else {}
    }
    if pages_fetched is not None:
        stats["pages_fetched"] = pages_fetched

    return stats, None
