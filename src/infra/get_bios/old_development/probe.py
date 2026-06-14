# src/infra/get_bios/probe.py

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from ..parser.parser2 import OUTPUT_DIR

OUTPUT_ROOT = Path(OUTPUT_DIR) / "infra" / "get_bios"
INPUT_JSON = OUTPUT_ROOT / "rikishi_bios.json"
OUTPUT_CSV = OUTPUT_ROOT / "shusshin_bins.csv"


def main() -> None:
    if not INPUT_JSON.exists():
        print(f"Input JSON does not exist: {INPUT_JSON}")
        print("Run: py -m src.infra.get_bios.parser")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        bios = json.load(f)

    counts = Counter()
    rikids_by_shusshin = defaultdict(list)

    for rikid, bio in bios.items():
        shusshin = bio.get("Shusshin")

        if shusshin is None:
            shusshin = ""

        counts[shusshin] += 1
        rikids_by_shusshin[shusshin].append(rikid)

    rows = []

    for shusshin, count in counts.most_common():
        rows.append({
            "count": count,
            "shusshin": shusshin,
            "rikids": " ".join(rikids_by_shusshin[shusshin]),
        })

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["count", "shusshin", "rikids"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {OUTPUT_CSV}")
    print(f"{len(bios)} rikishi")
    print(f"{len(counts)} distinct shusshin values")


if __name__ == "__main__":
    main()
