from pathlib import Path

OUTPUT_DIR = Path("files/output/standings/engine")
CACHE_FILE = OUTPUT_DIR / "totals_cache.csv"

LATEST_STANDINGS_FILE = OUTPUT_DIR / "standings.csv"
LATEST_RUN_FILE = OUTPUT_DIR / "last_run.txt"

PUBLISHER_LATEST_DATA = Path("files/output/standings/publisher/latest_data")

# Brittle link to legacy code:
LEGACY_QUALIFIED_SHIKONA = Path("H:/Code/Sumo/Elo/v. 9/files/output/mirror/cgi-bin/files/input/data/full_shiks.pkl")
