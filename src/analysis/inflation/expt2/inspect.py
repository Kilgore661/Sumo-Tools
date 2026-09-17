"""Filter a saved individual provenance run without History or a model refit."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sqlite3

import numpy as np

from .core import Holdings
from .__main__ import DEFAULT_ROOT, digest


def open_record(root):
    root = Path(root).resolve()
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if (manifest.get("model_id"), manifest.get("schema_version")) not in (
        ("elo89-provenance-first-stint", 1), ("elo89-provenance-persistent-gaps", 2)):
        raise ValueError("Unsupported provenance run")
    db = sqlite3.connect((root / "record.sqlite").as_uri() + "?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    return db, manifest


def restore(db, size, until):
    """Replay the saved transfer ledger, not the original sumo model or History."""
    state = Holdings(size)
    for e in db.execute("SELECT * FROM events WHERE seq<=? ORDER BY seq", (until,)):
        if e["kind"] == "enter":
            state.enter(e["a"], e["amount"])
        elif e["kind"] in ("leave", "gap_start"):
            state.leave(e["a"])
        elif e["kind"] == "gap_end":
            state.resume(e["a"])
        elif e["kind"] == "bout":
            a, b = e["a"], e["b"]
            if max(abs(state.ratings[a]-e["rating_a"]), abs(state.ratings[b]-e["rating_b"])) > 1e-6:
                raise ValueError("Saved event ratings do not reconcile")
            if e["a_won"]:
                state.transfer(a, b, e["delta_a"], -e["delta_b"])
            else:
                state.transfer(b, a, e["delta_b"], -e["delta_a"])
        else:
            raise ValueError(f"Unknown event: {e['kind']}")
    state.audit()
    return state.matrix


def resolve_person(db, query):
    people = list(db.execute("SELECT idx,rikid,name FROM people ORDER BY rikid"))
    if query.isdigit():
        matches = [p for p in people if p["rikid"] == int(query)]
    else:
        aliases = list(db.execute("SELECT DISTINCT idx,name FROM observations"))
        exact = {r["idx"] for r in aliases if r["name"].casefold() == query.casefold()}
        found = exact or {r["idx"] for r in aliases if query.casefold() in r["name"].casefold()}
        matches = [p for p in people if p["idx"] in found]
    if len(matches) != 1:
        raise ValueError(f"Choose one rikid; matches for {query!r}: " +
                         ", ".join(f"{p['rikid']} {p['name']}" for p in matches))
    return matches[0]


def profile(root, db, manifest, person, date=None, endpoint="end"):
    i = person["idx"]
    if date is None:
        date = db.execute("SELECT MAX(date) FROM observations WHERE idx=? AND endpoint=?",
                          (i, endpoint)).fetchone()[0]
    observation = db.execute("SELECT * FROM observations WHERE idx=? AND date=? AND endpoint=?",
                             (i, date, endpoint)).fetchone()
    if observation is None:
        raise ValueError("Subject is not represented at that endpoint; use its last observed basho")
    until = observation["event_id"]
    if until == manifest["events"]:
        matrix = np.load(Path(root) / "holdings.npy", mmap_mode="r", allow_pickle=False)
    else:
        print(f"Reconstructing saved holdings through {date} {endpoint}...", flush=True)
        matrix = restore(db, manifest["origins"], until)
    if abs(float(matrix[i].sum()) - observation["rating"]) > 1e-6:
        raise ValueError("Selected matrix and observed rating disagree")
    meta = {}
    for o in db.execute("SELECT * FROM observations WHERE event_id<=? ORDER BY date, CASE endpoint WHEN 'start' THEN 0 ELSE 1 END", (until,)):
        meta[o["idx"]] = o
    rows = []
    gap_ids = set()
    if manifest.get("schema_version", 2) >= 2:
        gap_ids = {r[0] for r in db.execute(
            "SELECT idx FROM gaps WHERE start_event<=? AND (end_event IS NULL OR end_event>?)", (until, until))}
    for p in db.execute("SELECT * FROM people ORDER BY idx"):
        j = p["idx"]
        if j not in meta:
            continue
        departed = p["departure_event"] is not None and p["departure_event"] <= until
        deficit = p["initial"] - p["departure_rating"] if departed else None
        status = ("departed donor" if deficit > 0 else "departed non-donor") if departed else "active"
        if j in gap_ids:
            status = "temporary gap"
        m = meta[j]
        held = float(matrix[i, j])
        # Self holdings appear only in received/current composition, not a
        # fictitious self exchange. Preserve an explicit self flag for filters.
        counterpart = float(matrix[j, i]) if j != i else 0.0
        rows.append(dict(rikid=p["rikid"], name=m["name"], self_origin=j == i,
            entry_date=p["entry_date"], entry_chii=p["entry_chii"], entry_group=p["entry_group"],
            last_chii=m["chii"], last_group=m["rank_group"], status=status,
            departure_date=p["departure_date"] if departed else None, deficit=deficit,
            held=held, share=100*held/observation["rating"],
            counterpart=counterpart, removed=counterpart if departed else 0.0,
            net=held-counterpart if j != i else 0.0))
    current = sum(r["held"] for r in rows)
    if abs(current - observation["rating"]) > 1e-6:
        raise ValueError("Profile origins do not sum to selected rating")
    return dict(rikid=person["rikid"], name=observation["name"], date=date, endpoint=endpoint,
                chii=observation["chii"], rating=observation["rating"], rows=rows,
                notes="Counterpart holdings include active holders and frozen departure rows. "
                      "Net is a provenance balance, not a causal or cumulative win/loss contribution. "
                      + ("Departed means final disappearance in the full loaded history, not verified retirement. "
                         "Temporary gaps are classified retrospectively from later returns and are not donor departures."
                         if manifest.get("schema_version", 2) >= 2 else
                         "Departed means end of the retained first stint, not verified retirement."))


def aggregate(rows, by="status"):
    result = {}
    for row in rows:
        key = row[by]
        if key not in result:
            result[key] = dict(label=key, count=0, held=0., counterpart=0., removed=0., net=0., share=0.)
        item = result[key]
        item["count"] += 1
        for field in ("held", "counterpart", "removed", "net", "share"):
            item[field] += row[field]
    return list(result.values())


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        if rows:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def export(output, profiles, source):
    output.mkdir(parents=True, exist_ok=True)
    for p in profiles:
        stem = f"{p['rikid']}_{p['date'].replace('/', '-')}_{p['endpoint']}"
        write_csv(output / f"{stem}_individuals.csv", p["rows"])
        for by in ("status", "entry_group", "last_group"):
            write_csv(output / f"{stem}_{by}.csv", aggregate(p["rows"], by))
    data = json.dumps(dict(profiles=profiles, source=source), ensure_ascii=False, allow_nan=False)
    (output / "profiles.json").write_text(data, encoding="utf-8")
    template = Path(__file__).with_name("explorer.html").read_text(encoding="utf-8")
    (output / "explorer.html").write_text(template.replace("/*DATA*/null", data.replace("<", "\\u003c")), encoding="utf-8")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    p.add_argument("--rikishi", action="append", help="rikid or name; repeat for several subjects")
    p.add_argument("--date", help="YYYY/MM; default is each subject's last represented basho")
    p.add_argument("--endpoint", choices=("start", "end"), default="end")
    p.add_argument("--output-root", type=Path, default=DEFAULT_ROOT.parent / "views")
    args = p.parse_args(argv)
    from src.analysis.elo89_normalisation.inputs import safe_output
    safe_output(args.output_root, [args.root])
    db, manifest = open_record(args.root)
    try:
        for name in ("record.sqlite", "holdings.npy"):
            if digest(args.root / name) != manifest["outputs"][name]["sha256"]:
                raise ValueError(f"Corrupt run artifact: {name}")
        profiles = [profile(args.root, db, manifest, resolve_person(db, query), args.date, args.endpoint)
                    for query in (args.rikishi or ["Onosato"])]
    finally:
        db.close()
    export(args.output_root, profiles, dict(root=str(args.root.resolve()), model=manifest["model_id"],
        return_policy=manifest.get("return_policy"),
        run_manifest_sha256=digest(args.root / "manifest.json"), start=manifest["start"], end=manifest["end"],
        excluded_return_bouts=manifest["excluded_return_bouts"],
        eligible_bouts=manifest["original_selection"]["rated_bout_count"]))
    print(f"Explorer: {(args.output_root / 'explorer.html').resolve()}")


if __name__ == "__main__":
    main()
