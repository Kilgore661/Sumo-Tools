"""Generate the individual holdings record; production ratings are untouched."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import sqlite3
import time

import numpy as np

from .core import Holdings


DEFAULT_ROOT = Path("files/output/analysis/inflation/expt2/run")


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def group(chii):
    if chii is None:
        return "Unknown"
    abbr = chii.level.as_abbreviation()
    return "Sanyaku" if abbr in ("Y", "O", "S", "K") else abbr


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--history-zip", type=Path)
    p.add_argument("--prior", type=Path, default=Path("files/output/analysis/equelo_bkp1/prior.csv"))
    p.add_argument("--k-config", type=Path, default=Path("files/input/elo_fide.json"))
    p.add_argument("--end", help="Inclusive endpoint YYYY/MM; default is latest represented basho")
    p.add_argument("--output-root", type=Path, default=DEFAULT_ROOT)
    return p


SCHEMA = """
CREATE TABLE people (idx INTEGER PRIMARY KEY, rikid INTEGER UNIQUE, name TEXT,
 entry_date TEXT, entry_chii TEXT, entry_group TEXT, initial REAL,
 departure_date TEXT, departure_event INTEGER, departure_rating REAL);
CREATE TABLE observations (date TEXT, endpoint TEXT, idx INTEGER, event_id INTEGER,
 rating REAL, name TEXT, chii TEXT, rank_group TEXT, PRIMARY KEY(date,endpoint,idx));
CREATE TABLE events (seq INTEGER PRIMARY KEY, date TEXT, day INTEGER, kind TEXT,
 a INTEGER, b INTEGER, amount REAL, a_won INTEGER, k_a REAL, k_b REAL,
 probability REAL, rating_a REAL, rating_b REAL, delta_a REAL, delta_b REAL);
CREATE TABLE excluded (date TEXT, rikid INTEGER, name TEXT, chii TEXT,
 PRIMARY KEY(date,rikid));
CREATE TABLE exclusions_by_basho (date TEXT PRIMARY KEY, original_bouts INTEGER,
 excluded_return_bouts INTEGER, included_bouts INTEGER, non_banzuke_count INTEGER);
CREATE TABLE gaps (idx INTEGER, start_date TEXT, start_event INTEGER,
 end_date TEXT, end_event INTEGER, rating REAL, PRIMARY KEY(idx,start_event));
CREATE INDEX events_date ON events(date,seq);
CREATE INDEX observations_person ON observations(idx,date,endpoint);
"""


def generate(history, prior, k_fn, output, end):
    from src.analysis.prediction.bouts import select_rated_bouts

    dates = sorted(d for d in history if "1989/01" <= str(d) and (end is None or str(d) <= end))
    if not dates or str(dates[0]) != "1989/01":
        raise ValueError("History must represent January 1989")
    selection = select_rated_bouts(history, start_date=dates[0], end_date=dates[-1])
    bouts = defaultdict(list)
    populations = {}
    for date in dates:
        populations[date] = set(history[date].banzuke.riks)
    for bout in selection.bouts:
        bouts[bout.contest.id.date].append(bout)
        populations[bout.contest.id.date].update((bout.contest.rikishi_a, bout.contest.rikishi_b))
    ids = sorted(set().union(*populations.values()))
    last_seen = {rid: date for date in dates for rid in populations[date]}
    index = {rid: i for i, rid in enumerate(ids)}
    print(f"{len(dates)} basho, {len(ids)} origins; dense matrix {len(ids)**2*8/1e6:.1f} MB", flush=True)
    state = Holdings(len(ids))
    db = sqlite3.connect(output / "record.sqlite")
    db.executescript(SCHEMA)
    metadata_hash = hashlib.sha256()
    seq = 0
    previous = set()
    included_bouts = gap_count = 0
    returned_ids = set()
    max_row = max_column = 0.0
    transitions = []

    def event(date, kind, a, b=None, amount=None, day=0, a_won=None,
              k_a=None, k_b=None, probability=None, ra=None, rb=None, da=None, dbb=None):
        nonlocal seq
        seq += 1
        db.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   (seq, str(date), day, kind, a, b, amount, a_won,
                    k_a, k_b, probability, ra, rb, da, dbb))

    def observe(date, endpoint, active):
        banzuke = history[date].banzuke
        records = []
        for rid in sorted(active):
            i = index[rid]
            chii = banzuke.rikchii.get(rid)
            name = str(banzuke.rikshik.get(rid, f"Rikishi {int(rid)}"))
            records.append((str(date), endpoint, i, seq, float(state.ratings[i]),
                            name, str(chii) if chii is not None else "", group(chii)))
            db.execute("UPDATE people SET name=? WHERE idx=?", (name, i))
        db.executemany("INSERT INTO observations VALUES (?,?,?,?,?,?,?,?)", records)

    for date in dates:
        active = populations[date]
        banzuke = history[date].banzuke
        departing, entering = previous - active, active - previous
        before_mass = float(state.ratings[state.active].sum())
        added = removed = donation = gap_out = gap_in = new_allocations = 0.0
        for rid in sorted(departing):
            i = index[rid]
            amount = float(state.ratings[i])
            removed += amount
            if last_seen[rid] > date:
                event(date, "gap_start", i, amount=amount)
                db.execute("INSERT INTO gaps VALUES (?,?,?,?,?,?)", (i, str(date), seq, None, None, amount))
                gap_count += 1
                gap_out += amount
            else:
                donation += float(state.allocated[i]) - amount
                event(date, "leave", i, amount=amount)
                db.execute("UPDATE people SET departure_date=?, departure_event=?, departure_rating=? WHERE idx=?",
                           (str(date), seq, amount, i))
            state.leave(i)
        for rid in sorted(entering):
            i = index[rid]
            if state.entered[i]:
                state.resume(i)
                amount = float(state.ratings[i])
                added += amount
                gap_in += amount
                returned_ids.add(rid)
                event(date, "gap_end", i, amount=amount)
                cursor = db.execute("UPDATE gaps SET end_date=?, end_event=? WHERE idx=? AND end_event IS NULL",
                                    (str(date), seq, i))
                if cursor.rowcount != 1:
                    raise ValueError("Return must close exactly one gap")
                continue
            chii = banzuke.rikchii.get(rid)
            rating, _ = prior.rating_for(chii)
            name = str(banzuke.rikshik.get(rid, f"Rikishi {int(rid)}"))
            state.enter(i, rating)
            added += rating
            new_allocations += rating
            event(date, "enter", i, amount=rating)
            db.execute("INSERT INTO people VALUES (?,?,?,?,?,?,?,?,?,?)",
                       (i, int(rid), name, str(date), str(chii) if chii is not None else "",
                        group(chii), rating, None, None, None))
        # Fingerprint all represented membership, chii and selected outcomes,
        # including all returning appearances and bouts.
        metadata_hash.update(json.dumps([str(date), [
            [int(r), str(banzuke.rikchii.get(r)), str(banzuke.rikshik.get(r))]
            for r in sorted(populations[date])]], ensure_ascii=False).encode())
        observe(date, "start", active)
        start_mass = float(state.ratings[state.active].sum())
        if abs(start_mass - before_mass - added + removed) > 1e-6:
            raise ValueError("Membership mass does not reconcile")
        skipped = 0
        bout_mass = 0.0
        for bout in bouts[date]:
            a, b = bout.contest.rikishi_a, bout.contest.rikishi_b
            metadata_hash.update(json.dumps([str(date), int(bout.contest.id.day),
                                            int(a), int(b), bout.a_won]).encode())
            if a not in active or b not in active:
                raise ValueError("Selected bout participant missing from replay population")
            ia, ib = index[a], index[b]
            ca, cb = banzuke.rikchii.get(a), banzuke.rikchii.get(b)
            ka = k_fn(ca.ordinal()) if ca is not None else 35.0
            kb = k_fn(cb.ordinal()) if cb is not None else 35.0
            ra, rb = float(state.ratings[ia]), float(state.ratings[ib])
            probability, da, dbb = state.bout(ia, ib, bout.a_won, ka, kb)
            event(date, "bout", ia, ib, day=int(bout.contest.id.day), a_won=int(bout.a_won),
                  k_a=ka, k_b=kb, probability=probability, ra=ra, rb=rb, da=da, dbb=dbb)
            bout_mass += da + dbb
        included_bouts += len(bouts[date]) - skipped
        db.execute("INSERT INTO exclusions_by_basho VALUES (?,?,?,?,?)", (str(date),
                   len(bouts[date]), skipped, len(bouts[date])-skipped,
                   len(populations[date] - set(banzuke.riks))))
        observe(date, "end", active)
        end_mass = float(state.ratings[state.active].sum())
        if abs(end_mass - start_mass - bout_mass) > 1e-6:
            raise ValueError("Bout mass does not reconcile")
        check = state.audit()
        max_row = max(max_row, check["max_row_error"])
        max_column = max(max_column, check["max_column_error"])
        transitions.append(dict(date=str(date), initial_stock=not bool(previous) and date == dates[0],
            count=len(active), joins=len(entering), departures=len(departing), points_added=added,
            points_removed=removed, transition_delta=added-removed,
            new_allocations=new_allocations, gap_points_out=gap_out, gap_points_in=gap_in,
            net_departing_donation=donation, start_mean=start_mass/len(active) if active else None,
            end_mean=end_mass/len(active) if active else None, bout_mass=bout_mass,
            excluded_return_appearances=0, excluded_return_bouts=skipped))
        db.commit()
        previous = active
        print(f"{date}: {len(active)} active; {included_bouts:,} bouts; row error {max_row:.2g}", flush=True)
    np.save(output / "holdings.npy", state.matrix, allow_pickle=False)
    np.savez(output / "balances.npz", ratings=state.ratings, allocated=state.allocated,
             created=state.created, active=state.active)
    with (output / "transitions.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(transitions[0]))
        writer.writeheader()
        writer.writerows(transitions)
    if included_bouts != selection.rated_bout_count:
        raise ValueError("Every eligible bout must be included")
    if db.execute("SELECT COUNT(*) FROM gaps WHERE end_event IS NULL").fetchone()[0]:
        raise ValueError("Retrospectively identified gaps must all close")
    db.close()
    return dict(start=str(dates[0]), end=str(dates[-1]), basho=len(dates), origins=len(ids),
                matrix_bytes=state.matrix.nbytes, events=seq, included_bouts=included_bouts,
                excluded_return_bouts=0, excluded_return_appearances=0,
                returner_ids=len(returned_ids), gap_count=gap_count,
                original_selection={k: getattr(selection, k) for k in (
                    "raw_result_count", "rated_bout_count", "excluded_fusen_count", "excluded_draw_count")},
                represented_history_sha256=metadata_hash.hexdigest(),
                max_row_error=max_row, max_column_error=max_column)


def main(argv=None):
    args = parser().parse_args(argv)
    # Local import keeps the accounting core independent of History dependencies.
    from src.analysis.elo89_normalisation.__main__ import load_history
    from src.analysis.equelo_population_policy.predict_candidate import load_alpha_prior
    from src.analysis.equelo.expt1.params import load_divisional_k_fn
    from src.analysis.elo89_normalisation.inputs import safe_output

    sources = [args.prior, args.k_config]
    if args.history_zip:
        sources.append(args.history_zip.with_suffix(".zip"))
    safe_output(args.output_root, sources)
    started = time.perf_counter()
    hashes = {str(p.resolve()): digest(p) for p in sources}
    code_hashes = {str(p): digest(p) for p in Path(__file__).parent.glob("*.py")}
    history, source = load_history(args)
    if args.output_root.exists() and any(args.output_root.iterdir()):
        raise ValueError("Choose an empty output directory; existing runs are immutable")
    args.output_root.mkdir(parents=True, exist_ok=True)
    prior, _ = load_alpha_prior(args.prior)
    summary = generate(history, prior, load_divisional_k_fn(args.k_config), args.output_root, args.end)
    for path, expected in hashes.items():
        if digest(path) != expected:
            raise ValueError(f"Source changed during replay: {path}")
    manifest = dict(model_id="elo89-provenance-persistent-gaps", schema_version=2,
                    normalisation=False, return_policy="preserve rating and holdings across gaps; include all eligible bouts",
                    departure_policy="last disappearance with no later appearance in loaded history; not verified retirement",
                    q=400, source=source, input_hashes=hashes, code_hashes=code_hashes,
                    elapsed_seconds=time.perf_counter()-started, **summary)
    manifest["outputs"] = {p.name: dict(bytes=p.stat().st_size, sha256=digest(p))
                           for p in args.output_root.iterdir() if p.is_file()}
    (args.output_root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2), flush=True)


if __name__ == "__main__":
    main()
