from ebird import get_recent_observations, get_rarebirds, get_historicbirds, format_observations
from datetime import date

lat, lng = 41.85851607776688, -72.86318880283952
m = date.today().month
d = date.today().day
y = date.today().year
isinstance(lat, int)

observations, error = get_recent_observations(lat, lng, days_back=7, max_results=10)
if error:
    print(f"Error: {error}")
else:
    print(format_observations(observations))

observations, error = get_rarebirds(lat, lng, days_back=7, max_results=10)
if error:
    print(f"Error: {error}")
else:
    print(format_observations(observations))
    
observations, error = get_historicbirds("US-CT", y-1, m, d, days_back=7, max_results=10)
if error:
    print(f"Error: {error}")
else:
    print(format_observations(observations))

