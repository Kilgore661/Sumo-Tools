import json
import os
from zipfile import ZipFile, ZIP_DEFLATED

# --- Import the new data model classes ---
from ..parser.parser2_new_model import (
    BanzukeWithAnnotations, BashoStateWithAnnotations, HistoryWithAnnotations, RikNewFoo
)

# --- Import the custom rank object that needs special handling ---
from ..parser.parser_UrChii import NewFoo

# --- Import the original serializer to reuse its stable methods ---
from infrastructure.persistence.sumo_serializer import SumoSerializer
from infrastructure.persistence.base_serializer import BaseSerializer

# --- Import core types for deserialization ---
from core.model.common.History import Date, Year, Month
from core.model.common.BasicPrimitives import RikId

class NewSumoSerializer(BaseSerializer):
    """
    Handles serialization of Sumo tournament data structures that include
    extended annotations via the NewFoo class.

    What's New:
    - It serializes the new `...WithAnnotations` data structures.
    - The core change is the serialization of `NewFoo` objects into their
      unique integer ordinals, and deserialization back from those integers.
    - It reuses methods from the original `SumoSerializer` for parts of
      the data model that have not changed (e.g., Summary, Riks, RikShikona),
      promoting code reuse and stability.
    """

    # --- Core NewFoo Serialization Logic ---

    @classmethod
    def _serialize_new_foo(cls, foo: NewFoo) -> int:
        """Serialize a NewFoo object to its unique integer ordinal."""
        return foo.ordinal()

    @classmethod
    def _deserialize_new_foo(cls, ordinal: int) -> NewFoo:
        """Deserialize an integer ordinal back into a NewFoo object."""
        return NewFoo.from_ordinal(ordinal)

    # --- New Dictionary Mapping Logic ---

    @classmethod
    def _serialize_rikchii(cls, rikchii_map: RikNewFoo) -> dict[str, int]:
        """Convert a RikNewFoo mapping to a serializable dictionary."""
        return {
            str(rid): cls._serialize_new_foo(foo)
            for rid, foo in rikchii_map.items()
        }

    @classmethod
    def _deserialize_rikchii(cls, data: dict[str, int]) -> RikNewFoo:
        """Convert a dictionary back to a RikNewFoo mapping object."""
        return RikNewFoo({
            RikId(int(rid_str)): cls._deserialize_new_foo(ordinal)
            for rid_str, ordinal in data.items()
        })

    # --- New Banzuke Serialization Logic ---

    @classmethod
    def _serialize_banzuke_with_ann(cls, banzuke: BanzukeWithAnnotations) -> dict:
        """Convert a BanzukeWithAnnotations object to a dictionary."""
        return {
            "riks": SumoSerializer._serialize_riks(banzuke.riks),
            "rikchii": cls._serialize_rikchii(banzuke.rikchii),
            "rikshik": SumoSerializer._serialize_rikshik(banzuke.rikshik)
        }

    @classmethod
    def _deserialize_banzuke_with_ann(cls, data: dict) -> BanzukeWithAnnotations:
        """Convert a dictionary back to a BanzukeWithAnnotations object."""
        return BanzukeWithAnnotations(
            riks=SumoSerializer._deserialize_riks(data["riks"]),
            rikchii=cls._deserialize_rikchii(data["rikchii"]),
            rikshik=SumoSerializer._deserialize_rikshik(data["rikshik"])
        )

    # --- New BashoState Serialization Logic ---

    @classmethod
    def _serialize_basho_state_with_ann(cls, state: BashoStateWithAnnotations) -> dict:
        """Convert a BashoStateWithAnnotations object to a dictionary."""
        return {
            "banzuke": cls._serialize_banzuke_with_ann(state.banzuke),
            # The Summary object has not changed, so we can reuse the old serializer.
            "summary": SumoSerializer._serialize_summary(state.summary)
        }

    @classmethod
    def deserialize_basho_state_with_ann(cls, data: dict) -> BashoStateWithAnnotations:
        """Convert a dictionary back to a BashoStateWithAnnotations object."""
        return BashoStateWithAnnotations(
            banzuke=cls._deserialize_banzuke_with_ann(data["banzuke"]),
            # Reuse the old deserializer for the unchanged Summary part.
            summary=SumoSerializer._deserialize_summary(data["summary"])
        )

    # --- New History Serialization Logic ---

    @classmethod
    def _serialize_history_with_ann(cls, history: HistoryWithAnnotations) -> dict:
        """Convert a HistoryWithAnnotations object to a dictionary."""
        return {
            str(date): cls._serialize_basho_state_with_ann(bs)
            for date, bs in history.items()
        }

    @classmethod
    def deserialize_history_with_ann(cls, data: dict) -> HistoryWithAnnotations:
        """Convert a dictionary back to a HistoryWithAnnotations object."""
        result = HistoryWithAnnotations()
        for date_str, bs_data in data.items():
            year_str, month_str = date_str.split('/')
            date = Date(Year(int(year_str)), Month(int(month_str)))
            result[date] = cls.deserialize_basho_state_with_ann(bs_data)
        return result


# --- Top-Level Helper Functions for External Use ---

def save_history_with_annotations(history: HistoryWithAnnotations, filename: str) -> None:
    """
    Save a HistoryWithAnnotations object to a compressed JSON file.
    The filename should not include the .zip extension.
    """
    serialized_data = NewSumoSerializer._serialize_history_with_ann(history)
    NewSumoSerializer.save_to_zip(serialized_data, filename)
    print(f"Successfully saved history to {filename}.zip")

def load_history_with_annotations(filename: str) -> HistoryWithAnnotations:
    """
    Load a HistoryWithAnnotations object from a compressed JSON file.
    The filename should not include the .zip extension.
    """
    data = NewSumoSerializer.load_from_zip(filename)
    return NewSumoSerializer.deserialize_history_with_ann(data)
