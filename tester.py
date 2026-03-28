from ebird import get_recent_observations, get_rarebirds, get_historicbirds, format_observations
from datetime import date
from synthesize import synthesize_ebird

lat, lng = 41.85851607776688, -72.86318880283952
m = date.today().month
d = date.today().day
y = date.today().year

observations, error = get_recent_observations(lat, lng, days_back=7, max_results=10)
if error:
    print(f"Error: {error}")
else:
    summary = synthesize_ebird(observations, "Recent observation in Hartford, CT")
    print(summary)
    print(f"\nCharacter count: {len(summary)}")

observations, error = get_rarebirds(lat, lng, days_back=7, max_results=10)
if error:
    print(f"Error: {error}")
else:
    summary = synthesize_ebird(observations, "Rare birds observed in Hartford, CT")
    print(summary)
    print(f"\nCharacter count: {len(summary)}")

observations, error = get_historicbirds("US-CT", y-1, m, d, days_back=7, max_results=10)
if error:
    print(f"Error: {error}")
else:
    summary = synthesize_ebird(observations, "Birds observed on this date last year in Hartford, CT")
    print(summary)
    print(f"\nCharacter count: {len(summary)}")