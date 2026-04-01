from multiprocessing import shared_memory
import pickle
from pathlib import Path
from datetime import datetime
from time import time

from sumo_core.History import History
from infra.persistence.annotated_serialiser import load_history_with_annotations
from infra.parser.parser2 import OUTPUT_DIR

from infra.config import EPOCH
from .config import VERSION


class LiveStore:
    """
    Live in-memory snapshot of the canonical History.

    The live store is a named shared-memory segment containing a pickled
    History object.

    Semantics:
    - The store may be replaced at any time.
    - Clients are not notified of updates.
    - Clients must reconnect if freshness matters.
    """

    def __init__(self, name: str):
        self.name = name
        self._shm = None

    def exists(self) -> bool:
        """Return True iff the shared-memory segment exists."""
        try:
            shm = shared_memory.SharedMemory(name=self.name)
            shm.close()
            return True
        except FileNotFoundError:
            return False
        except Exception as exc:
            print(f"[live_store] exists() error: {exc}")
            return False

    def connect(self) -> History | None:
        """
        Connect to the live store and return the unpickled History.

        Returns None if the store does not exist or cannot be read.
        """
        try:
            shm = shared_memory.SharedMemory(name=self.name)
            try:
                return pickle.loads(bytes(shm.buf))
            finally:
                shm.close()

        except FileNotFoundError:
            print(f"[live_store] '{self.name}' not found")
            return None

        except Exception as exc:
            print(f"[live_store] connect() error: {exc}")
            return None

    def init_live_store(self) -> bool:
        """
        Bootstrap the live store from the canonical zip.
        """
        try:
            zip_path = str(_canonical_zip_path())
            print(f"Loading {zip_path}.zip ...", end=" ", flush=True)
            history = load_history_with_annotations(zip_path)
            payload = pickle.dumps(history)
            self._replace_segment(payload)
            return True
        except Exception as exc:
            print(f"[live_store] init_live_store() failed: {exc}")
            return False

    def publish(self, h: History) -> bool:
        """
        Replace the live store with the supplied History.
        """
        try:
            payload = pickle.dumps(h)
            self._replace_segment(payload)
            return True
        except Exception as exc:
            print(f"[live_store] publish() failed: {exc}")
            return False

    def close(self) -> None:
        """
        Explicitly close and remove the live store owned by this object.
        """
        if self._shm is not None:
            try:
                self._shm.close()
                self._shm.unlink()
            except FileNotFoundError:
                pass
            finally:
                self._shm = None

    def _replace_segment(self, payload: bytes) -> None:
        """
        Replace the shared-memory segment with new payload.

        On Windows, the segment disappears when the last handle is closed,
        so this object keeps one handle alive in self._shm.
        """
        if self._shm is not None:
            try:
                self._shm.close()
                self._shm.unlink()
            except FileNotFoundError:
                pass
            finally:
                self._shm = None

        try:
            existing = shared_memory.SharedMemory(name=self.name)
            try:
                existing.close()
                existing.unlink()
            except FileNotFoundError:
                pass
        except FileNotFoundError:
            pass

        shm = shared_memory.SharedMemory(
            name=self.name,
            create=True,
            size=len(payload),
        )

        shm.buf[:len(payload)] = payload

        # Keep one handle alive so the segment continues to exist.
        self._shm = shm


def get_store() -> LiveStore:
    """
    Create the default live store, bootstrapping it from the canonical zip
    if necessary.

    This function is intended only for the case where no live store is
    currently loaded.
    """
    s = LiveStore(f"history{VERSION}")

    if not s.exists():
        if not s.init_live_store():
            raise RuntimeError("could not initialise live store")
    else:
        raise RuntimeError("initialised live store already exists!")

    return s


def _canonical_zip_path() -> Path:
    """
    Return the canonical History zip path.
    """
    start_year = int(EPOCH)
    end_year = _current_end_year()

    output_dir = Path(OUTPUT_DIR) / "Historys"
    filename = f"{start_year}_01 to {end_year}_11"
    return output_dir / filename


def _current_end_year() -> int:
    """
    Return the current canonical end year.
    """
    return datetime.now().year


if __name__ == "__main__":
    t0 = time()
    s = get_store()
    h = s.connect()
    if h:
        print(f"\nConnected to '{s.name}', {len(h)} basho in {time()-t0:.0f} seconds.")
