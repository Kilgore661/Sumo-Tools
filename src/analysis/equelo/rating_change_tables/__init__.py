"""Production producer for site-facing Rating Changes tables."""

from .model import DEFAULT_WINDOWS, RatingChangeRow, RatingChangesOutputs
from .producer import build_rating_changes_outputs

__all__ = [
    "DEFAULT_WINDOWS",
    "RatingChangeRow",
    "RatingChangesOutputs",
    "build_rating_changes_outputs",
]
