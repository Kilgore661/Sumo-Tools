# src/infra/get_bios/bmi.py

import json
import math
from collections import Counter
from pathlib import Path

from ..parser.parser2 import OUTPUT_DIR


INPUT_JSON = Path(OUTPUT_DIR) / "infra" / "get_bios" / "rikishi_bios.json"
NUM_BINS = 20


def bmi_from_height_weight(height_cm: str, weight_kg: str) -> float:
    height_m = float(height_cm) / 100.0
    weight = float(weight_kg)
    return weight / (height_m * height_m)


def main() -> None:
    if not INPUT_JSON.exists():
        print(f"Input JSON does not exist: {INPUT_JSON}")
        print("Run: py -m src.infra.get_bios.parser")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        bios = json.load(f)

    bmis = []

    for rikid, bio in bios.items():
        height = bio.get("Height")
        weight = bio.get("Weight")

        if height is None or weight is None:
            print(f"WARNING: {rikid}: missing Height or Weight; skipping")
            continue

        try:
            bmi = bmi_from_height_weight(height, weight)
        except (TypeError, ValueError, ZeroDivisionError) as exc:
            print(
                f"WARNING: {rikid}: could not calculate BMI "
                f"from Height={height!r}, Weight={weight!r}: {exc}; skipping"
            )
            continue

        bmis.append((rikid, bmi))

    if not bmis:
        print("No BMI values calculated.")
        return

    values = [bmi for _, bmi in bmis]

    min_bmi = min(values)
    max_bmi = max(values)
    mean_bmi = sum(values) / len(values)

    if len(values) > 1:
        variance = sum((x - mean_bmi) ** 2 for x in values) / (len(values) - 1)
        stdev_bmi = math.sqrt(variance)
    else:
        stdev_bmi = 0.0

    print(f"count: {len(values)}")
    print(f"min:   {min_bmi:.2f}")
    print(f"max:   {max_bmi:.2f}")
    print(f"mean:  {mean_bmi:.2f}")
    print(f"stdev: {stdev_bmi:.2f}")

    print("\nBMI bins:")

    if min_bmi == max_bmi:
        print(f"[{min_bmi:.2f}, {max_bmi:.2f}]: {len(values)}")
        return

    bin_width = (max_bmi - min_bmi) / NUM_BINS
    bins = Counter()

    for bmi in values:
        index = int((bmi - min_bmi) / bin_width)

        if index == NUM_BINS:
            index -= 1

        bins[index] += 1

    for index in range(NUM_BINS):
        lower = min_bmi + index * bin_width
        upper = lower + bin_width

        if index == NUM_BINS - 1:
            bracket = "]"
        else:
            bracket = ")"

        print(f"[{lower:.2f}, {upper:.2f}{bracket}: {bins[index]}")


if __name__ == "__main__":
    main()
