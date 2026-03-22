import json
import os
from zipfile import ZipFile, ZIP_DEFLATED

# --- Import the new data model classes ---
from sumo_core.Banzuke import Banzuke, RikChii
from sumo_core.BashoState import BashoState
from sumo_core.History import History, Date, Year, Month
from sumo_core.BasicPrimitives import RikId

# --- Import the custom rank object that needs special handling ---
from sumo_core.Chii import Chii

# --- Import the original serialiser to reuse its stable methods ---
from .serialiser import SumoSerialiser
from .base_serialiser import BaseSerialiser

class NewSumoSerialiser(BaseSerialiser):
    """
    Handles serialisation of Sumo tournament data structures that include
    extended annotations via the Chii class.

    What's New:
    - It serialises the new (was `...WithAnnotations`) data structures.
    - The core change is the serialisation of `Chii` objects into their
      unique integer ordinals, and deserialisation back from those integers.
    - It reuses methods from the original `SumoSerialiser` for parts of
      the data model that have not changed (e.g., Summary, Riks, RikShikona),
      promoting code reuse and stability.
    """

    # --- Core Chii Serialisation Logic ---

    @classmethod
    def _serialise_new_foo(cls, foo: Chii) -> int:
        """Serialise a Chii object to its unique integer ordinal."""
        return foo.ordinal()

    @classmethod
    def _deserialise_new_foo(cls, ordinal: int) -> Chii:
        """Deserialise an integer ordinal back into a Chii object."""
        return Chii.from_ordinal(ordinal)

    # --- New Dictionary Mapping Logic ---

    @classmethod
    def _serialise_rikchii(cls, rikchii_map: RikChii) -> dict[str, int]:
        """Convert a RikChii mapping to a serialisable dictionary."""
        return {
            str(rid): cls._serialise_new_foo(foo)
            for rid, foo in rikchii_map.items()
        }

    @classmethod
    def _deserialise_rikchii(cls, data: dict[str, int]) -> RikChii:
        """Convert a dictionary back to a RikChii mapping object."""
        return RikChii({
            RikId(int(rid_str)): cls._deserialise_new_foo(ordinal)
            for rid_str, ordinal in data.items()
        })

    # --- New Banzuke Serialisation Logic ---

    @classmethod
    def _serialise_banzuke_with_ann(cls, banzuke: Banzuke) -> dict:
        """Convert a Banzuke object to a dictionary."""
        return {
            "riks": SumoSerialiser._serialise_riks(banzuke.riks),
            "rikchii": cls._serialise_rikchii(banzuke.rikchii),
            "rikshik": SumoSerialiser._serialise_rikshik(banzuke.rikshik)
        }

    @classmethod
    def _deserialise_banzuke_with_ann(cls, data: dict) -> Banzuke:
        """Convert a dictionary back to a Banzuke object."""
        return Banzuke(
            riks=SumoSerialiser._deserialise_riks(data["riks"]),
            rikchii=cls._deserialise_rikchii(data["rikchii"]),
            rikshik=SumoSerialiser._deserialise_rikshik(data["rikshik"])
        )

    # --- New BashoState Serialisation Logic ---

    @classmethod
    def _serialise_basho_state_with_ann(cls, state: BashoState) -> dict:
        """Convert a BashoState object to a dictionary."""
        return {
            "banzuke": cls._serialise_banzuke_with_ann(state.banzuke),
            # The Summary object has not changed, so we can reuse the old serialiser.
            "summary": SumoSerialiser._serialise_summary(state.summary)
        }

    @classmethod
    def deserialise_basho_state_with_ann(cls, data: dict) -> BashoState:
        """Convert a dictionary back to a BashoState object."""
        return BashoState(
            banzuke=cls._deserialise_banzuke_with_ann(data["banzuke"]),
            # Reuse the old deserialiser for the unchanged Summary part.
            summary=SumoSerialiser._deserialise_summary(data["summary"])
        )

    # --- New History Serialisation Logic ---

    @classmethod
    def _serialise_history_with_ann(cls, history: History) -> dict:
        """Convert a History object to a dictionary."""
        return {
            str(date): cls._serialise_basho_state_with_ann(bs)
            for date, bs in history.items()
        }

    @classmethod
    def deserialise_history_with_ann(cls, data: dict) -> History:
        """Convert a dictionary back to a History object."""
        result = History()
        for date_str, bs_data in data.items():
            year_str, month_str = date_str.split('/')
            date = Date(Year(int(year_str)), Month(int(month_str)))
            result[date] = cls.deserialise_basho_state_with_ann(bs_data)
        return result


# --- Top-Level Helper Functions for External Use ---

def save_history_with_annotations(history: History, filename: str) -> None:
    """
    Save a History object to a compressed JSON file.
    The filename should not include the .zip extension.
    """
    serialised_data = NewSumoSerialiser._serialise_history_with_ann(history)
    NewSumoSerialiser.save_to_zip(serialised_data, filename)
    print(f"Successfully saved history to {filename}.zip")

def load_history_with_annotations(filename: str) -> History:
    """
    Load a History object from a compressed JSON file.
    The filename should not include the .zip extension.
    """
    data = NewSumoSerialiser.load_from_zip(filename)
    return NewSumoSerialiser.deserialise_history_with_ann(data)
