from pathlib import Path

OUTPUT_DIR = Path("files/output/standings/engine")
CACHE_FILE = OUTPUT_DIR / "totals_cache.csv"

LATEST_STANDINGS_FILE = OUTPUT_DIR / "standings.csv"
LATEST_RUN_FILE = OUTPUT_DIR / "last_run.txt"

PUBLISHER_LATEST_DATA = Path("files/output/standings/publisher/latest_data")

LEGACY_QUALIFIED_SHIKONA = Path(__file__).resolve().parent / "files" / "full_shiks.pkl"
