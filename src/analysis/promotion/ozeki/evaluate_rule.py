"""Evaluate one rule: python -m src.analysis.promotion.ozeki.evaluate_rule A 32."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from .analysis import analyse_history
from .candidates import qualifying_windows


OUTPUT_ROOT = Path('files/output/analysis/promotion/ozeki')
FIRST_PROMOTION_BANZUKE = '1958/07'
RULES = {
    'A': 'All three basho at K/S.',
    'B': 'First basho at M/K/S; following two at K/S.',
    'C': 'All three basho at K/S; at least 10 wins in each.',
}


def evaluate_rule(history, rule, n):
    """Score event-level predictions; absent future ranks are unresolved."""
    if rule not in RULES:
        raise ValueError('Rule must be A, B or C')
    if type(n) is not int or not 0 <= n <= 45:
        raise ValueError('Win threshold must be an integer from 0 to 45')
    audit = analyse_history(history)
    positives = [r for r in audit['events']
                 if r['first_ozeki_banzuke'] >= FIRST_PROMOTION_BANZUKE]
    excluded = {(r['rikishi_id'], r['first_ozeki_banzuke']) for r in audit['excluded']}
    actual = {(r['rikishi_id'], r['first_ozeki_banzuke']) for r in positives}
    windows = qualifying_windows(history, allow_maegashira_start=rule == 'B',
                                 minimum_basho_wins=10 if rule == 'C' else 0,
                                 minimum_total_wins=n)
    candidates = [r for r in windows if r['next_basho']
                  and r['next_basho'] >= FIRST_PROMOTION_BANZUKE
                  and r['classification'] != 'unresolved'
                  and (r['rikishi_id'], r['next_basho']) not in excluded]
    predicted = {(r['rikishi_id'], r['next_basho']) for r in candidates}
    tp, fp, fn = len(actual & predicted), len(predicted - actual), len(actual - predicted)
    def ratio(numerator, denominator):
        return numerator / denominator if denominator else 0.0
    return dict(
        schema_version=1, name=f'{rule}{n}', rule=rule, minimum_total_wins=n,
        definition=f'At least {n} regular wins across three consecutive held basho. {RULES[rule]}',
        first_promotion_banzuke=FIRST_PROMOTION_BANZUKE,
        history_first_basho=str(min(history)), history_last_basho=str(max(history)),
        history_basho_count=len(history),
        exclusions='Immediate ozekiwake reinstatements; outcomes before 1958/07; unresolved next rank/banzuke.',
        counting='Promotion opportunities, including overlapping windows; not distinct rikishi. Wins include fusensho, exclude playoffs.',
        limitations='Missing historical results may undercount qualifying windows. Full held-basho coverage is assumed. True negatives are not enumerated.',
        zero_denominator_policy='Undefined precision, recall or F1 is reported as 0.0.',
        tp=tp, fp=fp, fn=fn, actual_promotions=len(actual), predicted_promotions=len(predicted),
        precision=ratio(tp, tp+fp), recall=ratio(tp, tp+fn), f1=ratio(2*tp, 2*tp+fp+fn),
        qualifying_windows=candidates,
        false_negatives=[r for r in positives if (r['rikishi_id'], r['first_ozeki_banzuke']) not in predicted],
        unresolved_windows=[r for r in windows if r['classification'] == 'unresolved'
                            and r['end_basho'] >= FIRST_PROMOTION_BANZUKE],
    )


def save_evaluation(history, rule, n, output_dir, *, source='live_store'):
    result = evaluate_rule(history, rule, n)
    result.update(source=source, generated_at=datetime.now(timezone.utc).isoformat())
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f'{rule}{n}.json'
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rule', choices=RULES)
    parser.add_argument('n', type=int, choices=range(46), metavar='N')
    parser.add_argument('--output-dir', type=Path, default=OUTPUT_ROOT / 'rules')
    args = parser.parse_args()
    from src.infra.live_store.api import get_history
    print(save_evaluation(get_history(), args.rule, args.n, args.output_dir).resolve())


if __name__ == '__main__':
    main()
