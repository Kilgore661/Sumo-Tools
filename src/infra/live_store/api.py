"""
Live store access API.

This module provides the canonical entry point for applications that need
access to the current in-memory sumo History.

Usage:

    from infra.live_store.api import get_history

    h = get_history()

The live store is published by the tracker as a named shared-memory segment.
The name of the current segment is written to a well-known file.

This module implements the client-side protocol:

1. Read the published-name file.
2. Extract the shared-memory segment name.
3. Connect to that segment and return the History.

If any step fails, the process terminates.

Design principles:

- Applications are consumers only; they do not create or repair the live store.
- The tracker (via the live store module) is solely responsible for publication.
- No attempt is made to recover from missing or stale state.
- Freshness is not guaranteed; clients must tolerate replacement of the store.

This keeps the interface simple and avoids coupling applications to internal
details such as shared-memory naming or versioning.
"""

import sys
from time import time
from pathlib import Path

from ...sumo_core.History import History

from .LiveStore import LiveStore
from .config import PUBLISHED_NAME_FILE

def get_history() -> History:
    """
    Return the currently published History from the live store.

    This function terminates if:
    - no published-name file exists
    - the file cannot be read
    - the file is empty
    - the named shared-memory segment cannot be connected to
    """
    t0 = time()
    if not PUBLISHED_NAME_FILE.exists():
        sys.exit("[live_store.api] no published live store name-file found. Use:\n\n    py -m src.infra.tracker.tracker\n\nfrom X:\\Sumo\\Sumo-Tools.")

    try:
        name = PUBLISHED_NAME_FILE.read_text(encoding="utf-8").strip()
    except Exception as exc:
        sys.exit(f"[live_store.api] could not read live store name-file: {exc}")

    if not name:
        sys.exit("[live_store.api] live store name-file is empty")

    store = LiveStore(name)
    history = store.connect()

    if history is None:
        sys.exit(f"[live_store.api] could not connect to published live store '{name}'")
    print( f'Connection made in {time()-t0:.0f} seconds.' )

    return history

def published_name_file() -> Path:
    return PUBLISHED_NAME_FILE


def clear_published_name() -> None:
    try:
        PUBLISHED_NAME_FILE.unlink()
    except FileNotFoundError:
        pass


def write_published_name(name: str) -> None:
    PUBLISHED_NAME_FILE.parent.mkdir(parents=True, exist_ok=True)
    PUBLISHED_NAME_FILE.write_text(name, encoding="utf-8")
