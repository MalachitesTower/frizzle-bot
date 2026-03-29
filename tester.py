from ebird import get_ebird_recent_obs, get_ebird_rare_birds, get_ebird_historic_birds, format_ebird_obs
from inat import get_inat_recent_obs, get_inat_historic_obs, format_inat_obs
from synthesize import synthesize_ebird
from datetime import date, datetime
from settings import RADIUS_KM

lat, lng = 41.85851607776688, -72.86318880283952
region = "US-CT"
today = date.today()
sections = []

obs, err = get_ebird_recent_obs(lat, lng)
sections.append(format_ebird_obs(obs, title="Recent bird observations near you (past 7 days)") if not err else f"Recent sightings unavailable: {err}")

raw = "\n\n".join(sections)
synthesized = synthesize_ebird(raw)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_path = f"test_output_{timestamp}.txt"

with open(log_path, "w", encoding="utf-8") as f:
    f.write("=" * 60 + "\n")
    f.write("RAW OBSERVATIONS\n")
    f.write("=" * 60 + "\n\n")
    f.write(raw)
    f.write("\n\n")
    f.write("=" * 60 + "\n")
    f.write("SYNTHESIZED OUTPUT\n")
    f.write("=" * 60 + "\n\n")
    f.write(synthesized)
    f.write(f"\n\nCharacter count: {len(synthesized)}\n")

print(f"Log written to {log_path}")
