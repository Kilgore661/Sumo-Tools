# src/infra/get_bios/height_support.py

import json
from collections import Counter, defaultdict
from pathlib import Path

from ..parser.parser2 import OUTPUT_DIR


OUTPUT_ROOT = Path(OUTPUT_DIR) / "infra" / "get_bios"
INPUT_JSON = OUTPUT_ROOT / "rikishi_bios.json"
OUTPUT_CSV = OUTPUT_ROOT / "height_support_bins.csv"


def main() -> None:
    if not INPUT_JSON.exists():
        print(f"Input JSON does not exist: {INPUT_JSON}")
        print("Run: py -m src.infra.get_bios.parser")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        bios = json.load(f)

    support_counts = Counter()
    rikids_by_support = defaultdict(list)

    no_height_by_date = []

    for rikid, bio in bios.items():
        height_by_date = bio.get("Height_by_Date")

        if not height_by_date:
            support = 0
            no_height_by_date.append(rikid)
        else:
            support = len(height_by_date)

        support_counts[support] += 1
        rikids_by_support[support].append(rikid)

    total = sum(support_counts.values())

    print(f"rikishi: {total}")
    print(f"distinct support counts: {len(support_counts)}")

    print("\nHeight support distribution:")
    print("support,count,percent")

    for support in sorted(support_counts):
        count = support_counts[support]
        percent = 100.0 * count / total if total else 0.0
        print(f"{support},{count},{percent:.2f}")

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        f.write("support,count,rikids\n")
        for support in sorted(support_counts):
            rikids = " ".join(rikids_by_support[support])
            f.write(f"{support},{support_counts[support]},{rikids}\n")

    print(f"\nWrote {OUTPUT_CSV}")

    if no_height_by_date:
        print(f"\n{len(no_height_by_date)} rikishi have no Height_by_Date values.")


if __name__ == "__main__":
    main()
