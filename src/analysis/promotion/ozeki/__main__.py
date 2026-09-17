"""Run with python -m src.analysis.promotion.ozeki."""

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import subprocess

from .analysis import analyse_history


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8-sig') as stream:
        if rows:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description='Audit observed ozeki promotions against >=33 wins in three K/S basho.')
    parser.add_argument('--history-zip', type=Path)
    parser.add_argument('--output-root', type=Path, default=Path('files/output/analysis/promotion/ozeki'))
    args = parser.parse_args()
    if args.history_zip:
        from src.infra.persistence.annotated_serialiser import load_history_with_annotations
        path = args.history_zip.resolve()
        history = load_history_with_annotations(str(path.with_suffix('')))
        source = dict(kind='history_zip', path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    else:
        from src.infra.live_store.api import get_history, published_name_file
        history = get_history()
        source = dict(kind='live_store', published_name_file=str(published_name_file()))
    result = analyse_history(history)
    out = args.output_root / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out.mkdir(parents=True, exist_ok=False)
    for key, filename in [('events', 'promotions.csv'), ('evidence', 'preceding_basho.csv'), ('boundary', 'boundary_cases.csv'), ('excluded', 'excluded_reinstatements.csv')]:
        write_csv(out / filename, result[key])
    counts = Counter(r['classification'] for r in result['events'])
    lines = ['# Ozeki promotion audit', '',
             f"Source coverage: {result['basho_dates'][0]} to {result['basho_dates'][-1]}.", '',
             'Actual positives only. Predictor: at least 33 wins over the three preceding held basho, all at K/S.',
             'True positives meet that predicate; false negatives are promotions outside it. Unknown means insufficient evidence.',
             'This does not yet test whether meeting the predicate entails promotion.', '',
             f"Excluded immediate reinstatements (ozekiwake): {len(result['excluded'])}.", '',
             '| Event type | True positives | False negatives | Unknown |', '|---|---:|---:|---:|']
    for kind in ['qualification']:
        tally = Counter(r['classification'] for r in result['events'] if r['kind'] == kind)
        lines.append(f"| {kind} | {tally['true_positive']} | {tally['false_negative']} | {tally['unknown']} |")
    lines += ['', '## All observed promotions', '',
              '| First O banzuke | Rikishi (ID) | Type | Preceding basho: rank W–L | Wins | Classification |',
              '|---|---|---|---|---:|---|']
    for row in result['events']:
        lines.append(f"| {row['first_ozeki_banzuke']} | {row['shikona']} ({row['rikishi_id']}) | {row['kind']} | {row['sequence']} | {row['wins_observed']} | {row['classification']} |")
    lines += ['', '## Coverage limitations', '',
              'Promotion dates are inferred from adjacent banzuke, not JSA announcement dates. All retained promotion events form one qualification population.',
              'Previous tenure at ozeki does not distinguish qualifications. Immediate O-to-S-to-O returns with >=10 wins at S are excluded and audited in excluded_reinstatements.csv.',
              'Basho already at O at the source boundary are excluded from confirmed events and listed in boundary_cases.csv.',
              'Missing bouts cannot establish a below-33 total. An observed total >=33 suffices; a non-K/S rank independently disproves the predicate.',
              'Consecutive means consecutive supplied held basho. Cancelled March 2011 and May 2020 are not inserted; May 2011 is retained.',
              'The input is assumed to contain every held basho in its coverage. The manifest lists all dates for audit.',
              'No promotion after the last supplied banzuke can yet be observed.',
              'Kotogahama: 1957/11 S, 10-5 is user-supplied boundary evidence, recorded separately from History in preceding_basho.csv.']
    (out / 'findings.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    manifest = dict(source=source, basho_dates=result['basho_dates'], counts=dict(counts),
                    boundary_cases=len(result['boundary']),
                    supplemental_evidence=[r for r in result['evidence'] if r['source'] == 'user_supplied'],
                    excluded_reinstatements=len(result['excluded']),
                    predicate='>=33 regular wins including fusensho over three preceding held basho, all K/S',
                    git_head=subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip(),
                    git_status=subprocess.run(['git', 'status', '--short'], capture_output=True, text=True).stdout,
                    output_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()})
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(counts=counts, output=str(out.resolve())), indent=2))


if __name__ == '__main__':
    main()
