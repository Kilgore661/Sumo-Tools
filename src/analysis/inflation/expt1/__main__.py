"""Replay live History and report unnormalised turnover accounting."""
from pathlib import Path
import argparse
import csv
import json
import sqlite3

from src.analysis.inflation.expt2 import __main__ as replay
from src.analysis.inflation.expt2.audit import audit

DEFAULT_ROOT = Path('files/output/analysis/inflation/expt1')


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def report(run, output, membership):
    """Derive flows independently from events and endpoint observations."""
    db = sqlite3.connect(run / 'record.sqlite')
    db.row_factory = sqlite3.Row
    people = {p['idx']: dict(p) for p in db.execute('SELECT * FROM people')}
    dates = [r[0] for r in db.execute('SELECT DISTINCT date FROM observations ORDER BY date')]
    rows, ledger, membership_rows = [], [], []
    previous, previous_banzuke = {}, set()
    errors = []
    for date in dates:
        start = {p['idx']: dict(p) for p in db.execute("SELECT * FROM observations WHERE date=? AND endpoint='start'", (date,))}
        end = {p['idx']: dict(p) for p in db.execute("SELECT * FROM observations WHERE date=? AND endpoint='end'", (date,))}
        literal = membership[date]
        current_ids = {people[i]['rikid'] for i in start}
        for rid in sorted(literal | previous_banzuke | current_ids):
            membership_rows.append(dict(date=date, rikid=rid, on_banzuke=rid in literal,
                in_replay=rid in current_ids, banzuke_join=rid in literal-previous_banzuke,
                banzuke_departure=rid in previous_banzuke-literal))
        r = dict(date=date, previous_date=rows[-1]['date'] if rows else '', initial_stock=not rows,
            count_before=len(previous), count=len(start), banzuke_count=len(literal),
            non_banzuke_count=len(current_ids-literal), joins=0, departures=0,
            first_appearances=0, returns=0, final_departures=0, gap_starts=0,
            points_added=0., points_removed=0., new_allocations=0., gap_points_in=0., gap_points_out=0.,
            final_points_removed=0., final_entry_allocations=0., donor_points=0., above_entry_removed=0.,
            donor_points_new_cohort=0., above_entry_removed_new_cohort=0., bout_mass=0.)
        for e in db.execute('SELECT * FROM events WHERE date=? ORDER BY seq', (date,)):
            kind = e['kind']
            if kind == 'bout':
                r['bout_mass'] += e['delta_a'] + e['delta_b']
                continue
            p = people[e['a']]
            amount = e['amount']
            joining = kind in ('enter', 'gap_end')
            r['joins' if joining else 'departures'] += 1
            r['points_added' if joining else 'points_removed'] += amount
            key = {'enter':'new_allocations','gap_end':'gap_points_in','gap_start':'gap_points_out','leave':'final_points_removed'}[kind]
            r[key] += amount
            r[{'enter':'first_appearances','gap_end':'returns','gap_start':'gap_starts','leave':'final_departures'}[kind]] += 1
            deficit = p['initial'] - amount if kind == 'leave' else 0.
            censored = p['entry_date'] == dates[0]
            if kind == 'leave':
                r['final_entry_allocations'] += p['initial']
                r['donor_points'] += max(deficit, 0)
                r['above_entry_removed'] += max(-deficit, 0)
                if not censored:
                    r['donor_points_new_cohort'] += max(deficit, 0)
                    r['above_entry_removed_new_cohort'] += max(-deficit, 0)
            obs = start[e['a']] if joining else previous[e['a']]
            ledger.append(dict(date=date, kind=kind, rikid=p['rikid'], name=obs['name'],
                chii=obs['chii'], rank_group=obs['rank_group'], rating=amount,
                initial_rating=p['initial'], entry_date=p['entry_date'], initial_cohort=censored,
                final_deficit=deficit if kind == 'leave' else None))
        r['mass_before'] = sum(p['rating'] for p in previous.values())
        r['mass_start'] = sum(p['rating'] for p in start.values())
        r['mass_end'] = sum(p['rating'] for p in end.values())
        r['transition_delta'] = r['points_added'] - r['points_removed']
        r['net_departing_donation'] = r['donor_points'] - r['above_entry_removed']
        r['start_mean'] = r['mass_start']/r['count'] if r['count'] else None
        r['end_mean'] = r['mass_end']/r['count'] if r['count'] else None
        r['mean_before'] = r['mass_before']/len(previous) if previous else None
        r['membership_mean_change'] = r['start_mean']-r['mean_before'] if previous else None
        r['bout_mean_change'] = r['end_mean']-r['start_mean']
        def month(s):
            y, m = map(int, s.split('/'))
            return 12*y+m
        r['months_since_previous'] = month(date)-month(r['previous_date']) if rows else None
        assert r['count'] == len(previous)+r['joins']-r['departures']
        errors.extend([abs(r['mass_start']-r['mass_before']-r['transition_delta']),
            abs(r['mass_end']-r['mass_start']-r['bout_mass']),
            abs(r['transition_delta']-r['net_departing_donation']-r['new_allocations']
                +r['final_entry_allocations']-r['gap_points_in']+r['gap_points_out'])])
        for i in start.keys() & previous.keys():
            errors.append(abs(start[i]['rating']-previous[i]['rating']))
        rows.append(r)
        previous, previous_banzuke = end, literal
    db.close()
    assert max(errors, default=0) < 1e-6, max(errors)
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output/'transitions.csv', rows)
    write_csv(output/'membership_events.csv', ledger)
    write_csv(output/'banzuke_membership.csv', membership_rows)
    write_csv(output/'people.csv', list(people.values()))
    template = Path(__file__).with_name('charts.html').read_text(encoding='utf-8')
    (output/'charts.html').write_text(template.replace('/*DATA*/null',json.dumps(rows)), encoding='utf-8')
    transitions = rows[1:]
    summary = dict(start=dates[0], end=dates[-1], basho=len(rows),
        initial_mean=rows[0]['start_mean'], final_pre_basho_mean=rows[-1]['start_mean'],
        final_end_mean=rows[-1]['end_mean'], initial_count=rows[0]['count'], final_count=rows[-1]['count'],
        max_reconciliation_error=max(errors), non_banzuke_observations=sum(r['non_banzuke_count'] for r in rows))
    for key in ('points_added','points_removed','transition_delta','donor_points','above_entry_removed',
                'net_departing_donation','gap_points_in','gap_points_out','final_departures',
                'donor_points_new_cohort','above_entry_removed_new_cohort'):
        summary[key] = sum(r[key] for r in transitions)
    summary['bout_mass'] = sum(r['bout_mass'] for r in rows)
    (output/'summary.json').write_text(json.dumps(summary, indent=2),encoding='utf-8')
    return summary


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--end', default='2026/07', help='Inclusive endpoint; default matches Experiment 2')
    p.add_argument('--prior', type=Path, default=replay.parser().parse_args([]).prior)
    p.add_argument('--k-config', type=Path, default=replay.parser().parse_args([]).k_config)
    p.add_argument('--output-root', type=Path, default=DEFAULT_ROOT)
    args=p.parse_args(argv)
    if args.output_root.exists() and any(args.output_root.iterdir()):
        raise ValueError('Choose an empty output root; existing runs are immutable')
    from src.analysis.elo89_normalisation.__main__ import load_history
    from src.analysis.elo89_normalisation.inputs import safe_output
    from src.analysis.equelo_population_policy.predict_candidate import load_alpha_prior
    from src.analysis.equelo.expt1.params import load_divisional_k_fn
    safe_output(args.output_root, [args.prior,args.k_config])
    args.history_zip = None  # Live store only; no historical ZIP fallback.
    history, source = load_history(args)
    prior, _ = load_alpha_prior(args.prior)
    hashes={str(p.resolve()):replay.digest(p) for p in (args.prior,args.k_config)}
    run=args.output_root/'run'
    run.mkdir(parents=True)
    result=replay.generate(history, prior, load_divisional_k_fn(args.k_config), run, args.end)
    assert hashes == {p:replay.digest(p) for p in hashes}, 'Inputs changed during replay'
    manifest=dict(model_id='elo89-provenance-persistent-gaps', schema_version=2, experiment='inflation/expt1',
        normalisation=False,q=400,source=source,input_hashes=hashes,**result)
    manifest['outputs']={p.name:dict(bytes=p.stat().st_size,sha256=replay.digest(p)) for p in run.iterdir()}
    (run/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    check=audit(run)
    membership={str(d):{int(r) for r in history[d].banzuke.riks} for d in history}
    summary=report(run,args.output_root/'views',membership)
    manifest['audit']=check
    manifest['summary']=summary
    manifest['code_hashes']={str(p.resolve()):replay.digest(p) for folder in (Path(__file__).parent,Path(replay.__file__).parent)
        for p in folder.iterdir() if p.suffix in ('.py','.html')}
    manifest['report_outputs']={p.name:replay.digest(p) for p in (args.output_root/'views').iterdir()}
    (args.output_root/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    main()
