from __future__ import annotations

import csv
from pathlib import Path

from .types import ChiiRatings


def write_final_ratings_csv(mu: ChiiRatings, output_path: Path) -> Path:
    """Write final converged ratings as ``chii, ordinal, rating`` sorted by ordinal."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(mu.items(), key=lambda item: (item[0].ordinal(), str(item[0])))
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["chii", "ordinal", "rating"])
        for chii, rating in rows:
            writer.writerow([str(chii), chii.ordinal(), rating])
    return output_path
