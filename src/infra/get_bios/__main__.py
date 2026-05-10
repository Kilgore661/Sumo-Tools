# src/infra/get_bios/__main__.py

from pathlib import Path
from time import sleep
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

from ..live_store.api import get_history
from ..parser.parser2 import OUTPUT_DIR


BIO_DIR = Path(OUTPUT_DIR) / "infra" / "rikishi"

DOWNLOAD_TIMEOUT_SECONDS = 1
MINIMUM_FILE_SIZE_BYTES = 6 * 1024
MAX_CONSECUTIVE_GLITCHES = 6

URL_TEMPLATE = "https://sumodb.sumogames.de/Rikishi.aspx?r={}"


def existing_rikishi_ids() -> set[int]:
    """
    Return all rikishi ids already present in the bio directory.
    """
    if not BIO_DIR.exists():
        return set()

    result = set()

    for path in BIO_DIR.glob("*.html"):
        try:
            result.add(int(path.stem))
        except ValueError:
            pass

    return result


def all_history_rikishi_ids() -> set[int]:
    """
    Extract all rikishi ids from the live-store history.
    """
    history = get_history()

    result = set()

    for basho_state in history.values():
        result.update(int(rid) for rid in basho_state.banzuke.riks)

    return result


def download_bio(rik_id: int) -> bytes | None:
    """
    Download a rikishi bio page.

    Returns:
        bytes on success
        None on failure/glitch
    """
    url = URL_TEMPLATE.format(rik_id)

    try:
        with urlopen(url, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
            data = response.read()

    except (URLError, HTTPError, TimeoutError, OSError) as exc:
        print(f"{rik_id}: glitch ({exc})")
        return None

    if len(data) < MINIMUM_FILE_SIZE_BYTES:
        print(f"{rik_id}: glitch (too small: {len(data)} bytes)")
        return None

    return data


def save_bio(rik_id: int, data: bytes) -> None:
    """
    Save downloaded bio HTML.
    """
    BIO_DIR.mkdir(parents=True, exist_ok=True)

    output_file = BIO_DIR / f"{rik_id:05d}.html"

    with open(output_file, "wb") as f:
        f.write(data)


def main() -> None:
    existing = existing_rikishi_ids()
    history_ids = all_history_rikishi_ids()

    missing_ids = sorted(history_ids - existing)

    print(f"{len(existing)} existing bio files.")
    print(f"{len(missing_ids)} rikishi bio files to fetch.\n")

    glitches = 0

    for rik_id in missing_ids:

        data = download_bio(rik_id)

        if data is None:
            glitches += 1

            print(
                f"{rik_id}: glitch "
                f"({glitches}/{MAX_CONSECUTIVE_GLITCHES} consecutive)"
            )

            if glitches >= MAX_CONSECUTIVE_GLITCHES:
                print("\nToo many consecutive glitches. Quitting.")
                return

            continue

        save_bio(rik_id, data)

        glitches = 0

        print(f"{rik_id:05d}: saved ({len(data)} bytes)")

        # Be polite to the server.
        sleep(1)

    print("\nComplete.")


if __name__ == "__main__":
    main()
