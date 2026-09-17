"""Independently check saved scalar events, observations and matrix balances."""

import argparse
import json
import math
from pathlib import Path

import numpy as np

from .__main__ import DEFAULT_ROOT, digest
from .inspect import open_record


def audit(root):
    db, manifest = open_record(root)
    root = Path(root)
    try:
        for name, expected in manifest["outputs"].items():
            if digest(root / name) != expected["sha256"]:
                raise ValueError(f"Output hash changed: {name}")
        ratings = np.zeros(manifest["origins"])
        active = set()
        entered = set()
        maximum = 0.0
        observed = iter(db.execute("SELECT * FROM observations ORDER BY event_id"))
        next_observation = next(observed, None)

        def compare(a, b):
            nonlocal maximum
            maximum = max(maximum, abs(a-b))
            if not math.isfinite(a) or not math.isfinite(b) or abs(a-b) > 1e-6:
                raise ValueError(f"Scalar audit failed: {a} != {b}")

        for e in db.execute("SELECT * FROM events ORDER BY seq"):
            a, b = e["a"], e["b"]
            if e["kind"] == "enter":
                if a in entered:
                    raise ValueError("Initial allocation must occur only once per rikishi")
                entered.add(a)
                active.add(a)
                ratings[a] = e["amount"]
            elif e["kind"] in ("leave", "gap_start"):
                compare(ratings[a], e["amount"])
                active.remove(a)
            elif e["kind"] == "gap_end":
                if a in active or a not in entered:
                    raise ValueError("Invalid gap return")
                compare(ratings[a], e["amount"])
                active.add(a)
            else:
                if a not in active or b not in active:
                    raise ValueError("Inactive participant")
                compare(ratings[a], e["rating_a"])
                compare(ratings[b], e["rating_b"])
                probability = 1/(1+10**((ratings[b]-ratings[a])/manifest["q"]))
                compare(probability, e["probability"])
                residual = e["a_won"] - probability
                da, dbb = e["k_a"]*residual, -e["k_b"]*residual
                compare(da, e["delta_a"])
                compare(dbb, e["delta_b"])
                ratings[a] += da
                ratings[b] += dbb
            while next_observation is not None and next_observation["event_id"] == e["seq"]:
                if next_observation["idx"] not in active:
                    raise ValueError("Snapshot contains inactive wrestler")
                compare(ratings[next_observation["idx"]], next_observation["rating"])
                next_observation = next(observed, None)
        if next_observation is not None:
            raise ValueError("Unreached snapshot")
        matrix = np.load(root / "holdings.npy", mmap_mode="r", allow_pickle=False)
        with np.load(root / "balances.npz", allow_pickle=False) as balances:
            row_error = float(np.max(np.abs(matrix.sum(axis=1)-ratings)))
            column_error = float(np.max(np.abs(matrix.sum(axis=0)-balances["allocated"]-balances["created"])))
            compare(float(np.max(np.abs(balances["ratings"]-ratings))), 0.)
            if set(np.flatnonzero(balances["active"])) != active:
                raise ValueError("Active flags differ")
        if max(row_error, column_error) > 1e-6 or matrix.min() < 0 or not np.isfinite(matrix).all():
            raise ValueError("Matrix balance failure")
        return dict(events=manifest["events"], scalar_max_error=maximum, matrix_row_error=row_error,
                    matrix_column_error=column_error, active=len(active), verified_hashes=True)
    finally:
        db.close()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = p.parse_args(argv)
    print(json.dumps(audit(args.root), indent=2))


if __name__ == "__main__":
    main()
