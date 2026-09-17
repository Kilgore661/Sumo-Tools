"""Audit all observed >=33-win K/S windows against the next banzuke.

Run with python -m src.analysis.promotion.ozeki.candidates.
"""

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path

from src.sumo_core.BasicEnums import MSD, Outcome
from .analysis import analyse_history
from .__main__ import write_csv


def qualifying_windows(history, *, allow_maegashira_start=False, minimum_basho_wins=0,
                       minimum_total_wins=33):
    dates = sorted(history)
    observations = {}
    states = {str(date): history(date) for date in dates}
    for date in dates:
        state = history(date)
        rows = {}
        for rid, rank in state.banzuke.rikchii.items():
            if rank.level in {MSD.KOMUSUBI, MSD.SEKIWAKE} or (allow_maegashira_start and rank.level == MSD.MAEGASHIRA):
                rows[rid] = dict(rank=str(rank), wins=0, recorded_bouts=0,
                                 sanyaku=rank.level in {MSD.KOMUSUBI, MSD.SEKIWAKE}, source='history')
        for day, daily in state.summary.items():
            if int(day) > 15:
                continue
            seen = set()
            for bout in daily.results_lookup.values():
                for rid, outcome in [(bout.rikishi1, bout.outcome1),
                                     (bout.rikishi2, bout.outcome2)]:
                    if rid not in rows:
                        continue
                    if rid in seen:
                        raise ValueError(f'Duplicate result for {rid} on {date} day {day}')
                    seen.add(rid)
                    rows[rid]['recorded_bouts'] += 1
                    rows[rid]['wins'] += outcome in {Outcome.W, Outcome.FS}
        observations[str(date)] = rows
    # Reuse the attributed boundary supplement from the positive-case audit.
    positives = analyse_history(history)
    for row in positives['evidence']:
        if row['source'] == 'user_supplied':
            observations.setdefault(row['basho'], {})[row['rikishi_id']] = row
    ordered = sorted(observations)
    candidates = []
    for i in range(2, len(ordered)):
        window_dates = ordered[i-2:i+1]
        common = set.intersection(*(set(observations[d]) for d in window_dates))
        for rid in sorted(common):
            rows = [observations[d][rid] for d in window_dates]
            if not all(row['sanyaku'] for row in rows[1:]):
                continue
            total = sum(row['wins'] for row in rows)
            if total < minimum_total_wins or any(row['wins'] < minimum_basho_wins for row in rows):
                continue
            next_date = ordered[i+1] if i+1 < len(ordered) else None
            next_rank = states[next_date].banzuke.rikchii.get(rid) if next_date else None
            status = ('unresolved' if next_rank is None else
                      'true_positive' if next_rank.level == MSD.OZEKI else 'false_positive')
            candidates.append(dict(rikishi_id=int(rid),
                                   shikona=str(states[ordered[i]].banzuke.rikshik[rid]),
                                   end_basho=ordered[i], next_basho=next_date,
                                   next_rank=str(next_rank) if next_rank is not None else None,
                                   wins=total,
                                   sequence='; '.join(f"{d} {r['rank']} {r['wins']}" for d, r in zip(window_dates, rows)),
                                   complete_45_bouts=all(r['recorded_bouts'] == 15 for r in rows),
                                   source='user_supplied + history' if any(r['source'] == 'user_supplied' for r in rows) else 'history',
                                   classification=status))
    return candidates


def main():
    from src.infra.live_store.api import get_history
    history = get_history()
    candidates = qualifying_windows(history)
    failures = [r for r in candidates if r['classification'] == 'false_positive']
    out = Path('files/output/analysis/promotion/ozeki') / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ_candidates')
    out.mkdir(parents=True, exist_ok=False)
    write_csv(out / 'qualifying_windows.csv', candidates)
    write_csv(out / 'not_promoted.csv', failures)
    counts = dict(Counter(r['classification'] for r in candidates))
    summary = dict(source='live_store', first_basho=str(min(history)), last_basho=str(max(history)),
                   counts=counts, distinct_not_promoted=len({r['rikishi_id'] for r in failures}),
                   rule='>=33 regular wins including fusensho, three consecutive held basho all K/S; promotion on next banzuke',
                   counting='Overlapping windows count separately; missing next rank/banzuke is unresolved.',
                   supplement='Kotogahama 1957/11 S 10-5 supplied by user', output=str(out.resolve()))
    (out / 'manifest.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    lines = ['# Qualifying runs without promotion', '',
             f"{len(failures)} windows involving {summary['distinct_not_promoted']} distinct rikishi.", '',
             '| Rikishi | Window ends | Preceding ranks and wins | Total | Next rank |',
             '|---|---|---|---:|---|']
    for row in failures:
        lines.append(f"| {row['shikona']} | {row['end_basho']} | {row['sequence']} | {row['wins']} | {row['next_rank']} |")
    lines += ['', 'Overlapping windows count separately. Later promotion does not erase a non-promotion at this boundary.',
              'Missing next banzuke/rank is unresolved. Windows below 33 observed wins are not claimed to be complete negatives.',
              'This is a retrospective test of one uniform benchmark, not a claim about the convention in each era.']
    (out / 'findings.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
