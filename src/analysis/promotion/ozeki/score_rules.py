"""Orchestrate the seven requested rule evaluations and rank their F1 scores."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from .evaluate_rule import OUTPUT_ROOT, save_evaluation

COMBINATIONS = [(rule, n) for rule in ('A', 'B') for n in (31, 32, 33)] + [('C', 33)]


def run_comparison(history, output_dir, *, source='live_store'):
    """Use one History snapshot; build the report from the saved JSON results."""
    output_dir = Path(output_dir)
    results = []
    for rule, n in COMBINATIONS:
        path = save_evaluation(history, rule, n, output_dir, source=source)
        results.append(json.loads(path.read_text(encoding='utf-8')))
    results.sort(key=lambda row: (-row['f1'], row['name']))
    best = results[0]['f1']
    winners = [r['name'] for r in results if r['f1'] == best]
    lines = ['# Ozeki promotion rule comparison', '',
             f"Highest F1: **{', '.join(winners)} — {best:.2%}**.", '',
             f"Promotion banzuke: 1958/07 through {results[0]['history_last_basho']}.",
             'Immediate ozekiwake reinstatements are excluded. All other qualifying promotions form one population.',
             'A: all three basho K/S. B: first may be M, next two K/S. C: all K/S and >=10 wins each.',
             'The number in each rule name is its minimum three-basho win total.', '',
             '| Rule | TP | FP | FN | Precision | Recall | F1 |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for r in results:
        lines.append(f"| [{r['name']}]({r['name']}.json) | {r['tp']} | {r['fp']} | {r['fn']} | {r['precision']:.2%} | {r['recall']:.2%} | {r['f1']:.2%} |")
    lines += ['', 'F1 = 2TP / (2TP + FP + FN). Overlapping windows count separately.',
              'These are descriptive scores on the same historical sample used to compare rules, not held-out predictive performance.',
              'Missing historical results may undercount qualifying windows. Outcomes with no next rank/banzuke are unresolved.',
              'Each JSON retains definitions, coverage, metrics, qualifying windows and false-negative events.']
    report = output_dir / 'report.md'
    report.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    out = args.output_dir or OUTPUT_ROOT / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ_rules')
    from src.infra.live_store.api import get_history
    report = run_comparison(get_history(), out)
    print(report.resolve())
    print(report.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
